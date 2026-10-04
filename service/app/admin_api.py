"""管理面板路由（/admin）——独立 APIRouter，便于单独测试与演进。

铁律：面板只写配置文件（keys.yaml / settings.yaml / manifests.json / profile.yaml /
negmark.db），不碰业务逻辑；key 永不明文回显；写操作带 by=admin-panel 审计。
"""
from __future__ import annotations

import os as _os
import tempfile as _tempfile

import httpx as _httpx
import yaml as _yaml
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from app.config import APP_DIR, data_dir
from app.core import keys as _keysmod
from app.core import negmark as _negmark, profile as _profile, registry as _registry
from app.core import rollinggo as _rgh

router = APIRouter(prefix="/admin")

_ADMIN_PROVIDERS = ["amap", "airlabs", "variflight", "travelpayouts",
                    "googlemaps", "opensky", "aviationstack", "openmeteo"]


@router.get("", response_class=HTMLResponse)
def admin_page():
    """管理面板单页（登录后 X-Admin-Key 访问 /admin/api/*）。"""
    return FileResponse(APP_DIR / "admin" / "index.html", media_type="text/html")


def _admin_guard(request: Request) -> None:
    """X-Admin-Key 校验；服务端未配置 admin_key = 开放模式（与 provider_admin 同权，
    面板页脚提示仅限局域网）。"""
    want = _keysmod.auth_config(data_dir()).get("admin_key")
    if want and request.headers.get("x-admin-key") != want:
        raise HTTPException(status_code=401, detail="需要管理密码")


def _atomic_yaml_write(p, doc: dict) -> None:
    fd, tmp = _tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with _os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(_yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
        _os.replace(tmp, p)
    finally:
        if _os.path.exists(tmp):
            _os.unlink(tmp)


def _settings_put(dd, updates: dict) -> None:
    p = dd / "settings.yaml"
    cur = {}
    if p.exists():
        cur = _yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    cur.update(updates)
    _atomic_yaml_write(p, cur)


def _mask(v: str) -> str:
    return (v[:4] + "••••" + v[-4:]) if v else ""


def _probe(provider: str, key: str) -> dict:
    """轻量连通探针——尽量不消耗计费额度。"""
    try:
        with _httpx.Client(timeout=12) as c:
            if provider == "amap":
                j = c.get("https://restapi.amap.com/v3/ip",
                          params={"key": key}).json()
                ok = j.get("status") == "1"
                return {"ok": ok, "error": None if ok else str(j.get("info"))[:80]}
            if provider == "airlabs":
                r = c.get("https://airlabs.co/api/v9/ping", params={"api_key": key})
                return {"ok": r.status_code == 200,
                        "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}
            if provider == "travelpayouts":
                r = c.get("https://api.travelpayouts.com/v2/prices/latest",
                          params={"currency": "cny", "token": key})
                return {"ok": r.status_code == 200,
                        "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}
            if provider == "aviationstack":
                j = c.get("https://api.aviationstack.com/v1/flights",
                          params={"access_key": key, "limit": 1}).json()
                ok = "error" not in j
                return {"ok": ok, "error": None if ok else str(j.get("error"))[:80]}
            if provider == "opensky":
                return {"ok": True, "note": "匿名可用——Key 用于提升额度"}
            if provider == "openmeteo":
                return {"ok": True, "note": "OpenMeteo 免 key"}
            if provider == "googlemaps":
                r = c.post(
                    "https://routes.googleapis.com/directions/v2:computeRoutes",
                    headers={"X-Goog-Api-Key": key,
                             "X-Goog-FieldMask": "routes.duration"},
                    json={"origin": {"location": {"latLng": {
                        "latitude": 35.6, "longitude": 139.7}}},
                        "destination": {"location": {"latLng": {
                            "latitude": 34.6, "longitude": 135.5}}},
                        "travelMode": "DRIVE"})
                return {"ok": r.status_code == 200,
                        "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}
            if provider == "variflight":
                return {"ok": None, "note": "付费源无轻量探针——保存后实际查询时验证"}
    except Exception as e:  # 网络异常也算探针结果
        return {"ok": False, "error": str(e)[:120]}
    return {"ok": None, "note": "无探针"}


@router.get("/api/config")
def admin_config(request: Request) -> dict:
    _admin_guard(request)
    dd = data_dir()
    raw_keys = _keysmod.load_keys(dd)
    man = _registry.load(dd / "manifests.json")

    def _extract(k):
        if isinstance(k, dict):
            return k.get("api_key") or k.get("access_key") or k.get("token") or k.get("key") or ""
        return k or ""

    # 数据驱动：只列 manifests 里真实存在的 provider（前端不写死清单）
    ids = [e["id"] for e in man.get("providers", [])]
    keys_view = {pid: _mask(_extract(raw_keys.get(pid))) for pid in ids}
    providers = {e["id"]: {"enabled": e["status"] == "active"}
                 for e in man.get("providers", [])}
    return {"profile": _profile.load_profile(dd), "keys": keys_view,
            "providers": providers,
            "negmarks": _negmark.list_banned(dd / "negmark.db"),
            "open_mode": not _keysmod.auth_config(dd).get("admin_key")}


@router.put("/api/profile")
def admin_put_profile(request: Request, body: dict) -> dict:
    """地址簿 → profile.yaml；车牌/EV 续航 → settings.yaml（车辆画像归 settings）。"""
    _admin_guard(request)
    dd = data_dir()
    try:
        doc = _profile.save_profile(dd, {"addresses": (body or {}).get("addresses") or []},
                                    by="admin-panel")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    _settings_put(dd, {"plate": str((body or {}).get("plate") or ""),
                       "ev_rated_range_km": (body or {}).get("ev_range_km") or 600})
    return {"ok": True, "addresses": len(doc["addresses"])}


@router.put("/api/keys/{provider}")
def admin_put_key(provider: str, request: Request, body: dict) -> dict:
    _admin_guard(request)
    key = str((body or {}).get("key") or "").strip()
    if not key:
        raise HTTPException(status_code=422, detail="key 不能为空")
    dd = data_dir()
    raw = _keysmod.load_keys(dd)
    entry = raw.get(provider)
    if isinstance(entry, dict):
        entry["api_key"] = key
    else:
        raw[provider] = {"api_key": key}
    _atomic_yaml_write(dd / "keys.yaml", raw)
    return {"ok": True, "masked": _mask(key)}


@router.post("/api/keys/{provider}/test")
def admin_test_key(provider: str, request: Request, body: dict = None) -> dict:
    _admin_guard(request)
    candidate = str(((body or {}).get("candidate")) or "").strip()
    key = candidate or (_keysmod.provider_key(data_dir(), provider) or "")
    if not key:
        return {"ok": False, "error": "该源尚未配置 Key"}
    return _probe(provider, key)


@router.put("/api/providers/{provider}/enabled")
def admin_provider_enabled(provider: str, request: Request, body: dict) -> dict:
    _admin_guard(request)
    dd = data_dir()
    man = _registry.load(dd / "manifests.json")
    e = _registry.by_id(man, provider)
    if not e:
        raise HTTPException(status_code=404, detail="未知 provider")
    e["status"] = "active" if (body or {}).get("enabled") else "disabled"
    _registry.save(dd / "manifests.json", man)
    return {"ok": True, "status": e["status"]}


@router.get("/api/rgh/status")
def admin_rgh_status(request: Request) -> dict:
    """RollingGo 登录状态（token 文件存在且含 access_token）。"""
    _admin_guard(request)
    return {"logged_in": _rgh.logged_in(data_dir())}


@router.post("/api/rgh/login")
def admin_rgh_login(request: Request) -> dict:
    """发起 RollingGo OAuth：返回授权链接（面板展示给用户点开）。"""
    _admin_guard(request)
    return _rgh.start_login(data_dir())


@router.get("/api/rgh/login/status")
def admin_rgh_login_status(request: Request) -> dict:
    """授权轮询：前端每 2-3 秒调一次；success 时服务端已收下 token。"""
    _admin_guard(request)
    return _rgh.login_status(data_dir())


@router.post("/api/rgh/logout")
def admin_rgh_logout(request: Request) -> dict:
    _admin_guard(request)
    return {"ok": _rgh.logout(data_dir())}


@router.get("/api/negmarks")
def admin_neg_list(request: Request) -> list[dict]:
    _admin_guard(request)
    return _negmark.list_banned(data_dir() / "negmark.db")


@router.delete("/api/negmarks")
def admin_neg_clear_all(request: Request) -> dict:
    _admin_guard(request)
    n = _negmark.clear(data_dir() / "negmark.db")
    return {"ok": True, "cleared": n}


@router.delete("/api/negmarks/{provider}")
def admin_neg_clear_one(provider: str, request: Request,
                        capability: str = "") -> dict:
    _admin_guard(request)
    n = _negmark.clear(data_dir() / "negmark.db", provider, capability)
    return {"ok": True, "cleared": n}
