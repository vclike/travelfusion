"""全程行程卡测试：锚点反推 deadline / 最迟出发 / 时长 / 地图点。"""
from app.core import cards

NORMS = {"buffers": {"flight_min": 60, "rail_min": 30}}
LEGS = [
    {"mode": "drive", "from": "成都", "to": "重庆",
     "depart": "2026-10-02T07:00:00+08:00",
     "arrive": "2026-10-02T11:00:00+08:00"},
    {"mode": "flight", "from": "重庆", "to": "上海",
     "depart": "2026-10-02T14:00:00+08:00",
     "arrive": "2026-10-02T16:30:00+08:00"},
]


def test_itinerary_deadlines():
    out = {"data": {"legs": LEGS}, "meta": {"sources": []}}
    cards.itinerary_card(out, legs=LEGS, norms=NORMS)
    card = out["meta"]["card"]
    drive, flight = card["payload"]["legs"]
    assert drive["must_arrive_by"] == "2026-10-02T13:00:00+08:00"  # 14:00-60
    assert drive["latest_depart"] == "2026-10-02T09:00:00+08:00"   # 13:00-4h
    assert flight["fixed"] is True and drive["fixed"] is False
    assert flight["duration_min"] == 150
    assert card["payload"]["span_min"] == 570                      # 7:00→16:30


def test_itinerary_map_suppressed_for_flights():
    """含 ✈️ 航段的跨城行程：点分属两城，同图投影无意义 → 不配地图。"""
    out = {"data": {"legs": LEGS}, "meta": {"sources": []}}
    cards.itinerary_card(out, legs=LEGS, norms=NORMS)
    assert out["meta"]["card"]["payload"]["map"] is None


def test_itinerary_map_present_ground_only():
    """纯地面行程保留地图（点位同城/邻近）。"""
    legs = [{"mode": "drive", "from": "成都", "to": "重庆",
             "depart": "2026-10-02T07:00:00+08:00",
             "arrive": "2026-10-02T11:00:00+08:00"}]
    out = {"data": {"legs": legs}, "meta": {"sources": []}}
    cards.itinerary_card(out, legs=legs, norms=NORMS)
    pts = out["meta"]["card"]["payload"]["map"]["points"]
    names = [x["name"] for x in pts]
    assert "成都" in names and "重庆" in names
