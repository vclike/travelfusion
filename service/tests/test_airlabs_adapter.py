import json

import httpx
import pytest

from app.providers.airlabs.adapter import Adapter, ProviderError

SCHED = {"response": [{"flight_iata": "TG615", "dep_iata": "PEK", "arr_iata": "BKK",
                       "dep_time_ts": 1790672700, "arr_time_ts": 1790691300,
                       "dep_delayed": 367, "arr_delayed": 343,
                       "dep_time_utc": "2026-09-29 09:05", "status": "active"}]}
FL = {"response": [{"flight_iata": "TG615", "dep_iata": "PEK", "arr_iata": "BKK",
                    "dep_actual": 1790694400, "arr_actual": 1790710000,
                    "dep_estimated": 1790694400, "arr_estimated": 1790710000,
                    "dep_gate": "E3", "baggage": "8", "duration": 520,
                    "status": "en-route"}]}
EMPTY = {"response": []}


def _adapter(sched=SCHED, fl=FL):
    def handler(req: httpx.Request) -> httpx.Response:
        body = SCHED if "/schedules" in str(req.url) else FL
        return httpx.Response(200, content=json.dumps(body).encode())
    return Adapter(api_key="test", http=httpx.Client(transport=httpx.MockTransport(handler)))


def test_merge_full_trio():
    out = _adapter().fetch("flight.status", {"flight_no": "TG615", "policy": {}})
    f = out["data"]["flights"][0]
    # scheduled 来自 /schedules 的时间戳
    assert f["times"]["dep"]["scheduled_utc"] is not None
    # actual 来自 /flights
    assert f["times"]["dep"]["actual_utc"] is not None
    assert f["times"]["arr"]["actual_utc"] is not None
    # 延误来自 /schedules，gate/baggage 来自 /flights
    assert f["status"]["dep_delay_min"] == 367
    assert f["status"]["gate"]["dep"] == "E3"
    assert f["status"]["baggage"] == "8"
    # 状态取 /flights 实时值，en-route → active
    assert f["status"]["value"] == "active"
    assert "双端点合并" in out["data"]["coverage_note"]


def test_en_route_flight_gets_scheduled_from_schedules():
    """免费档 /flights 在飞航班时间字段为空——合并后 scheduled 不得丢。"""
    out = _adapter().fetch("flight.status", {"flight_no": "TG615", "policy": {}})
    f = out["data"]["flights"][0]
    assert f["times"]["dep"]["scheduled_utc"] == "2026-09-29T09:05:00Z"
    assert f["times"]["arr"]["scheduled_utc"] == "2026-09-29T14:15:00Z"


def test_both_empty_is_no_match():
    a = _adapter(sched=EMPTY, fl=EMPTY)
    with pytest.raises(ProviderError) as ei:
        a.fetch("flight.status", {"flight_no": "XX999", "policy": {}})
    assert ei.value.code == "NO_MATCH"


def test_auth_failure_raises_immediately():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(401, content=json.dumps(
            {"error": {"code": "ACCESS_RESTRICTED"}}).encode())
    a = Adapter(api_key="bad", http=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(ProviderError) as ei:
        a.fetch("flight.status", {"flight_no": "TG615", "policy": {}})
    assert ei.value.code == "AUTH_REQUIRED"


def test_non_today_date_honest_rejection():
    """2026-10-01 窗口放开后：核验窗 = 当日 + 明日；后天起诚实拒绝（NOT_VERIFIABLE_FREE）。"""
    import time as _t
    day_after = _t.strftime("%Y-%m-%d", _t.localtime(_t.time() + 2 * 86400))
    with pytest.raises(ProviderError) as ei:
        _adapter().fetch("flight.status",
                         {"flight_no": "TG615", "date": day_after, "policy": {}})
    assert ei.value.code == "NOT_VERIFIABLE_FREE"
    assert "核验窗" in ei.value.hint


def test_tomorrow_uses_schedules_only_never_today_flights():
    """明日查询不得调 /flights——该端点不辨日期，会拿今天的同名班次冒充（防错位）。"""
    import time as _t
    calls: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        calls.append("schedules" if "/schedules" in url else "flights")
        body = SCHED if "/schedules" in url else FL
        return httpx.Response(200, content=json.dumps(body).encode())

    a = Adapter(api_key="test",
                http=httpx.Client(transport=httpx.MockTransport(handler)))
    tomorrow = _t.strftime("%Y-%m-%d", _t.localtime(_t.time() + 86400))
    out = a.fetch("flight.status",
                  {"flight_no": "TG615", "date": tomorrow, "policy": {}})
    assert calls == ["schedules"]                      # /flights 必须被跳过
    assert "仅 schedules" in out["data"]["coverage_note"]
