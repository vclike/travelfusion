"""管理面板 API 测试——函数级直调（不走 HTTP/lifespan，避免与 MCP 会话管理器互踩）。

路由函数只依赖 request.headers，用桩 Request 即可覆盖全部业务语义；
HTTP 层（状态码/掩码头）由 /admin 真机验收覆盖。
"""
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.admin_api import (admin_config, admin_neg_clear_one, admin_neg_list,
                           admin_page, admin_provider_enabled, admin_put_key,
                           admin_put_profile, admin_test_key)
from app.core import negmark


class Req:
    """桩 Request：路由只读 headers。"""

    def __init__(self, key=None):
        self.headers = {"x-admin-key": key} if key else {}


KEY = "test-admin-key"


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    dd = tmp_path_factory.mktemp("tfdata") / "data"
    dd.mkdir(parents=True)
    import json as _json
    (dd / "manifests.json").write_text(_json.dumps({"providers": [
        {"id": "amap", "status": "active", "tier": "free", "costPerCall": 0,
         "capabilities": ["ground.route"], "quota": {"group": "g", "period": "month"}},
        {"id": "airlabs", "status": "active", "tier": "free", "costPerCall": 0,
         "capabilities": ["flight.status"], "quota": {"group": "g", "period": "month"}},
    ]}, ensure_ascii=False), encoding="utf-8")
    with pytest.MonkeyPatch.context() as m:
        m.setenv("TF_DATA_DIR", str(dd))
        m.setenv("TF_ADMIN_KEY", KEY)
        yield dd


def test_admin_page_file_exists(env):
    r = admin_page()
    assert Path(r.path).exists()


def test_config_requires_key(env):
    with pytest.raises(HTTPException) as ei:
        admin_config(Req())
    assert ei.value.status_code == 401
    cfg = admin_config(Req(KEY))
    assert cfg["open_mode"] is False and "amap" in cfg["keys"]


def test_profile_roundtrip_and_settings_split(env):
    r = admin_put_profile(Req(KEY), {
        "addresses": [{"alias": "家", "text": "军安卫士花园"}],
        "plate": "川A12345F", "ev_range_km": 510})
    assert r["ok"] and r["addresses"] == 1
    prof = admin_config(Req(KEY))["profile"]
    assert prof["addresses"][0]["alias"] == "家"
    import yaml
    s = yaml.safe_load((env / "settings.yaml").read_text(encoding="utf-8"))
    assert s["plate"] == "川A12345F" and s["ev_rated_range_km"] == 510


def test_profile_validation_rejects_422(env):
    with pytest.raises(HTTPException) as ei:
        admin_put_profile(Req(KEY), {"addresses": [
            {"alias": "x"}, {"alias": "x"}]})
    assert ei.value.status_code == 422


def test_key_save_masks_in_config(env):
    r = admin_put_key("amap", Req(KEY), {"key": "abcd1234wxyz"})
    assert r["masked"].startswith("abcd")
    cfg = admin_config(Req(KEY))
    assert cfg["keys"]["amap"].startswith("abcd") and "••••" in cfg["keys"]["amap"]
    assert "1234wxyz" not in cfg["keys"]["amap"]          # 明文不回显
    import yaml
    k = yaml.safe_load((env / "keys.yaml").read_text(encoding="utf-8"))
    assert k["amap"]["api_key"] == "abcd1234wxyz"          # dict 形态保留


def test_provider_toggle_updates_manifest(env):
    r = admin_provider_enabled("amap", Req(KEY), {"enabled": False})
    assert r["status"] == "disabled"
    import json
    m = json.loads((env / "manifests.json").read_text(encoding="utf-8"))
    assert m["providers"][0]["status"] == "disabled"
    r2 = admin_provider_enabled("amap", Req(KEY), {"enabled": True})
    assert r2["status"] == "active"


def test_negmark_list_and_clear(env):
    db = env / "negmark.db"
    negmark.record_failure(db, "googlemaps", "ground.route.intl", reason="x")
    rows = admin_neg_list(Req(KEY))
    assert rows and rows[0]["provider"] == "googlemaps"
    r = admin_neg_clear_one("googlemaps", Req(KEY), capability="ground.route.intl")
    assert r["ok"]
    assert admin_neg_list(Req(KEY)) == []
