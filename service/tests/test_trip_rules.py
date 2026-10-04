import pytest

from app.mcp_server import _apply_trip_rules

NORMS = {"trip_rules": {"red_eye_hour_range": [0, 6], "lcc_airlines": ["9C", "FD"]}}

PRICES = [
    {"amount": 800, "airline_iata": "9C",
     "departure_at": "2026-10-03T02:30:00+08:00"},     # LCC + 红眼
    {"amount": 1200, "airline_iata": "CA",
     "departure_at": "2026-10-03T08:00:00+08:00"},     # 正班
    {"amount": 950, "airline_iata": "FD",
     "departure_at": "2026-10-03T07:30:00+07:00"},     # LCC 非红眼
]


def test_flags_always_applied():
    out = _apply_trip_rules([dict(p) for p in PRICES], "personal", NORMS)
    assert out[0]["lcc"] is True and out[0]["red_eye"] is True
    assert out[1]["lcc"] is False and out[1]["red_eye"] is False
    assert out[2]["lcc"] is True and out[2]["red_eye"] is False   # 07:30 当地时间


def test_incentive_sorts_lcc_and_redeye_last():
    out = _apply_trip_rules([dict(p) for p in PRICES], "incentive", NORMS)
    assert out[0]["airline_iata"] == "CA"          # 正班最前
    assert out[-1]["airline_iata"] == "9C"         # LCC+红眼 垫底


def test_personal_keeps_price_order():
    out = _apply_trip_rules([dict(p) for p in PRICES], "personal", NORMS)
    assert [p["amount"] for p in out] == [800, 1200, 950]


def test_missing_norms_is_tolerant():
    out = _apply_trip_rules([dict(PRICES[0])], "incentive", {})
    assert out[0]["lcc"] is False and out[0]["red_eye"] is True   # 02:30 仍判红眼
