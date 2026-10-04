"""到发间隔异常 → 只打 warn 标记，时间原样展示（不自动改数）。"""
from app.core import cards


def test_suspicious_gap_flags_but_preserves():
    out = {"data": {"flights": [{
        "flight_no": "MU587", "airline_iata": "MU", "dep_iata": "PVG",
        "arr_iata": "JFK", "duration_min": 175,
        "times": {"dep": {"scheduled_utc": "2026-09-29T11:30:00Z"},
                  "arr": {"scheduled_utc": "2026-09-29T14:25:00Z"}},
        "status": {"value": "landed"}},
        ]},
        "meta": {"sources": []}}
    cards.status_card(out)
    card = out["meta"]["card"]
    arr = card["payload"]["timeline"]["arr"]["scheduled_utc"]
    assert arr == "2026-09-29T14:25:00Z", arr          # 原样保留，不改数
    warn = [n["text"] for n in card["notices"] if n["level"] == "warn"]
    assert any("源数据异常" in w for w in warn)          # 透明黄牌（间隔可疑）
    assert any("最近已完成班次" in w for w in warn)       # 陈旧班次告警共存


def test_normal_gap_no_warn():
    out = {"data": {"flights": [{
        "flight_no": "MU587", "airline_iata": "MU", "dep_iata": "PVG",
        "arr_iata": "JFK", "duration_min": 895,
        "times": {"dep": {"scheduled_utc": "2026-09-29T11:30:00Z"},
                  "arr": {"scheduled_utc": "2026-09-30T02:25:00Z"}},
        "status": {"value": "scheduled"}},
        ]},
        "meta": {"sources": []}}
    cards.status_card(out)
    card = out["meta"]["card"]
    assert not [n for n in card["notices"] if n["level"] == "warn"]
