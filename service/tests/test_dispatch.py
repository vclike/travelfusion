import json
from pathlib import Path

from app.core import dispatch, ledger


def _seed(tmp_path: Path, providers: list[dict], order: dict | None = None) -> Path:
    d = tmp_path / "data"
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifests.json").write_text(json.dumps(
        {"providers": providers, "order": order or {}}, ensure_ascii=False), encoding="utf-8")
    return d


PAID = {"id": "variflight", "status": "active", "tier": "paid", "costPerCall": 0.5,
        "capabilities": ["flight.status"], "auth": "bearer",
        "quota": {"group": "paid", "period": "total", "limit": None}}


class FakeAdapter:
    id = "variflight"

    def __init__(self, api_key=None, http=None):
        pass

    def fetch(self, capability, query):
        return {"data": {"from": "fake-paid"}, "cost_calls": 1}


def test_paid_gate_blocks_unrequested_calibration(tmp_path, monkeypatch):
    d = _seed(tmp_path, [PAID])
    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: FakeAdapter)
    out = dispatch.call_capability("flight.status", {"policy": {}}, data_dir=d)
    assert out["error"]["code"] == "DATA_UNAVAILABLE"
    assert "paid_calibrate" in out["error"]["hint"]


def test_paid_gate_passes_with_explicit_flag(tmp_path, monkeypatch):
    d = _seed(tmp_path, [PAID])
    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: FakeAdapter)
    out = dispatch.call_capability("flight.status",
                                   {"policy": {"paid_calibrate": True}}, data_dir=d)
    assert out["data"]["from"] == "fake-paid"
    assert out["meta"]["sources"][0]["provider"] == "variflight"


def test_quota_exhausted_moves_to_next_source(tmp_path, monkeypatch):
    exhausted = dict(PAID, id="p1", tier="free", quota={"period": "month", "limit": 5})
    fresh = dict(PAID, id="p2", tier="free", quota={"period": "month", "limit": 5})

    class P1:
        id = "p1"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            from app.providers.airlabs.adapter import ProviderError
            from app.core.canon import E_QUOTA_LIMIT
            raise ProviderError(E_QUOTA_LIMIT, "free quota used", "p1")

    class P2:
        id = "p2"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            return {"data": {"from": "p2"}, "cost_calls": 1}

    d = _seed(tmp_path, [exhausted, fresh])
    led = ledger.QuotaLedger(d / "ledger.db")
    led.consume_free("p1", "month", 5)          # 打满
    monkeypatch.setattr(dispatch, "get_adapter",
                        lambda pid: P1 if pid == "p1" else P2)
    out = dispatch.call_capability("flight.status", {"policy": {}}, data_dir=d)
    assert out["data"]["from"] == "p2"
    assert out["meta"]["sources"][0]["provider"] == "p2"


def test_cache_hit_consumes_upstream_once(tmp_path, monkeypatch):
    free = dict(PAID, tier="free", quota={"period": "month", "limit": None})
    d = _seed(tmp_path, [free])
    calls = {"n": 0}

    class Fake:
        id = "variflight"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            calls["n"] += 1
            return {"data": {"v": calls["n"]}, "cost_calls": 1}

    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: Fake)
    q = {"flight_no": "XX001", "policy": {}}      # policy 不入缓存键
    out1 = dispatch.call_capability("flight.status", q, data_dir=d)
    out2 = dispatch.call_capability("flight.status", q, data_dir=d)
    assert calls["n"] == 1                        # 上游只打一次
    assert out1["data"]["v"] == out2["data"]["v"]
    assert out2["meta"]["cache"] == "hit"
    assert any("缓存命中" in n for n in out2["meta"]["notes"])


def test_cache_distinguishes_paid_calibration(tmp_path, monkeypatch):
    """付费校准必须绕开免费缓存（用户花钱买的是新鲜/精确，不是缓存复制品）。"""
    free = dict(PAID, tier="free", quota={"period": "month", "limit": None})
    d = _seed(tmp_path, [free])
    calls = {"n": 0}

    class Fake:
        id = "variflight"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            calls["n"] += 1
            return {"data": {"n": calls["n"],
                             "paid": query["policy"].get("paid_calibrate", False)},
                    "cost_calls": 1}

    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: Fake)
    out_free = dispatch.call_capability(
        "flight.status", {"flight_no": "XX2", "policy": {}}, data_dir=d)
    out_paid = dispatch.call_capability(
        "flight.status",
        {"flight_no": "XX2", "policy": {"paid_calibrate": True}}, data_dir=d)
    assert calls["n"] == 2                        # 付费绕开免费缓存，独立拉取
    assert out_free["data"]["paid"] is False
    assert out_paid["data"]["paid"] is True
    # 免费→免费 仍然命中缓存
    out_free2 = dispatch.call_capability(
        "flight.status", {"flight_no": "XX2", "policy": {}}, data_dir=d)
    assert calls["n"] == 2
    assert out_free2["meta"]["cache"] == "hit"


def _settings(monthly=20.0, confirm=3.0):
    from types import SimpleNamespace
    return SimpleNamespace(monthly_paid_budget_cny=monthly,
                           confirm_threshold_cny=confirm, extra={})


def test_budget_exhausted_blocks_paid(tmp_path, monkeypatch):
    d = _seed(tmp_path, [dict(PAID, quota={"period": "total", "limit": None})])
    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: FakeAdapter)
    out = dispatch.call_capability(
        "flight.status",
        {"policy": {"paid_calibrate": True, "confirm_spend": True}},
        data_dir=d, settings=_settings(monthly=0.4))      # 0.5 > 0.4
    assert out["error"]["code"] == "BUDGET_EXHAUSTED"


def test_confirm_required_then_spend_deducts(tmp_path, monkeypatch):
    d = _seed(tmp_path, [dict(PAID, costPerCall=5.0,
                              quota={"period": "total", "limit": None})])
    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: FakeAdapter)
    # 5 元 > 确认阈值 3 元：不带 confirm_spend → 要求确认
    out = dispatch.call_capability(
        "flight.status",
        {"policy": {"paid_calibrate": True}}, data_dir=d,
        settings=_settings(confirm=3.0))
    assert out["error"]["code"] == "CONFIRM_REQUIRED"
    # 用户知情放行 → 服务 + 预算扣费
    out2 = dispatch.call_capability(
        "flight.status",
        {"policy": {"paid_calibrate": True, "confirm_spend": True}},
        data_dir=d, settings=_settings(confirm=3.0))
    assert out2["data"]["from"] == "fake-paid"
    assert out2["meta"]["cost"]["paid_cny"] == 5.0
    led = ledger.QuotaLedger(d / "ledger.db")
    assert led.paid_month_cny() == 5.0


FREE_TP = {"id": "tp", "status": "active", "tier": "free", "costPerCall": 1,
           "capabilities": ["flight.price"], "auth": "bearer",
           "quota": {"period": "day", "limit": None}}
PAID_VF = {"id": "vf", "status": "active", "tier": "paid", "costPerCall": 0.5,
           "capabilities": ["flight.price"], "auth": "bearer",
           "quota": {"period": "total", "limit": None}}
ORDER = {"flight.price": ["tp", "vf"]}


def test_paid_calibrate_in_chain_prefers_paid_then_falls_back(tmp_path, monkeypatch):
    """核心 bug 回归（2026-10-01）：付费源必须真入降级链——
    付费旗标 → paid 置前成交；paid 失败 → 回退免费且显式标注 calibration_fallback。"""
    d = _seed(tmp_path, [FREE_TP, PAID_VF], ORDER)

    class TP:
        id = "tp"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            return {"data": {"price_type": "cached", "from": "tp"}, "cost_calls": 1}

    class VF:
        id = "vf"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            return {"data": {"price_type": "calibrated", "from": "vf"},
                    "cost_calls": 1}

    impl = {"tp": TP, "vf": VF}
    monkeypatch.setattr(dispatch, "get_adapter", lambda pid: impl[pid])

    # ① 不带付费旗标 → 免费源照常服务（付费源被闸门跳过，行为不变）
    out_free = dispatch.call_capability(
        "flight.price",
        {"origin_code": "CTU", "destination_code": "SYD", "policy": {}},
        data_dir=d)
    assert out_free["data"]["from"] == "tp"
    assert "calibration_fallback" not in out_free["meta"]

    # ② 带付费旗标 → 付费源置前成交，预算扣费
    out_paid = dispatch.call_capability(
        "flight.price",
        {"origin_code": "CTU", "destination_code": "SYD",
         "policy": {"paid_calibrate": True}}, data_dir=d)
    assert out_paid["data"]["from"] == "vf"
    assert out_paid["meta"]["cost"]["paid_cny"] == 0.5

    # ③ 付费源失败（如超 45 天价格窗）→ 回退免费，attempted 透出 + 显式标注
    class VFDead:
        id = "vf"

        def __init__(self, api_key=None, http=None):
            pass

        def fetch(self, capability, query):
            from app.core.canon import E_NO_MATCH
            from app.providers.airlabs.adapter import ProviderError
            raise ProviderError(E_NO_MATCH, "超 45 天价格窗", "vf")

    impl["vf"] = VFDead
    d2 = _seed(tmp_path / "sub", [FREE_TP, PAID_VF], ORDER)   # 换数据目录避缓存
    out_fb = dispatch.call_capability(
        "flight.price",
        {"origin_code": "CTU", "destination_code": "SYD",
         "policy": {"paid_calibrate": True}}, data_dir=d2)
    assert out_fb["data"]["from"] == "tp"
    assert "calibration_fallback" in out_fb["meta"]
    assert any(a["provider"] == "vf" for a in out_fb["meta"]["attempted"])
