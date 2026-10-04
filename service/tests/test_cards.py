"""卡片编排器单元测试（travelfusion-card/v1）。"""
from app.core import cards

NORMS = {"trip_rules": {"red_eye_hour_range": [0, 6], "lcc_airlines": ["FD"]},
         "norms": {"lcc": {"carry_on": "7kg 或更小", "meals": "无免费餐食",
                           "seat_selection": "普遍收费"}}}


def _price_out(trip_type="personal"):
    return {"data": {"prices": [
        {"amount": 1153, "currency": "CNY", "airline_iata": "FD",
         "departure_at": "2027-02-17T02:50:00+08:00", "lcc": True, "red_eye": True,
         "price_type": "cached"}],
        "price_type": "cached"},
        "meta": {"sources": [{"provider": "travelpayouts"}],
                 "cost": {"free_calls": 1, "paid_cny": 0},
                 "baseline_90d": {"min_cny": 1153, "samples": 5}}}


def test_price_card_flags_and_notice():
    out = _price_out()
    cards.price_card(out, od="成都→曼谷", trip_type="incentive", norms=NORMS)
    card = out["meta"]["card"]
    assert card["schema"] == "travelfusion-card/v1"
    assert card["type"] == "price.single"          # 单条退化
    assert card["payload"]["prices"][0]["recommended"] is True
    icons = [n["icon"] for n in card["notices"]]
    assert "lcc" in icons and "redeye" in icons and "policy" in icons
    lcc_notice = next(n for n in card["notices"] if n["icon"] == "lcc")
    assert "无免费餐食" in lcc_notice["text"]      # norms.lcc 基线渲染进提示
    assert card["meta"]["baseline"]["samples"] == 5


def test_status_card_shape():
    out = {"data": {"flights": [{
        "flight_no": "CA165", "airline_iata": "CA", "dep_iata": "PEK",
        "arr_iata": "MEL", "duration_min": 685,
        "times": {"dep": {"scheduled_utc": "x"}, "arr": {"scheduled_utc": "y"}},
        "status": {"value": "active", "dep_delay_min": 12, "gate": {"dep": "T3"}}}]},
        "meta": {"sources": []}}
    cards.status_card(out)
    card = out["meta"]["card"]
    assert card["type"] == "status"
    assert card["payload"]["dep_delay_min"] == 12
    assert "PEK" not in card["payload"]["route"]      # 机场码已被译名替代
    assert "北京" in card["payload"]["route"]
    acts = {a["id"]: a for a in card["actions"]}      # 复核直链（2026-10-02 实测模板）
    assert acts["review_fr24"]["url"] == "https://www.flightradar24.com/data/flights/ca165"
    assert acts["review_fa"]["url"] == "https://www.flightaware.com/live/flight/CA165"
    assert acts["verify"]["instruction"].startswith("flight_verify")


def test_review_actions_templates():
    acts = cards.review_actions("MU587")
    assert [a["id"] for a in acts] == ["review_fr24", "review_fa"]
    assert acts[0]["url"] == "https://www.flightradar24.com/data/flights/mu587"
    assert acts[1]["url"] == "https://www.flightaware.com/live/flight/MU587"
    assert cards.review_actions("") == []
    assert cards.review_actions(None) == []


def test_review_actions_flightera_date_direct():
    """日期直达链：URL 编码 航班号+起飞地当地日期（2026-10-02 实测 200）。"""
    acts = cards.review_actions("CA2690", dep_local_date="2026-10-02")
    assert [a["id"] for a in acts] == ["review_flightera", "review_fr24",
                                       "review_fa"]
    assert acts[0]["url"] == "https://www.flightera.net/en/flight/CA2690/2026-10-02"


def test_status_card_flightera_uses_departure_local_date():
    """UTC 16:35Z → 北京时间次日 00:35：日期直达链用起飞地当地日期，不串日。"""
    out = {"data": {"flights": [{
        "flight_no": "CA2690", "airline_iata": "CA", "dep_iata": "PEK",
        "arr_iata": "MEL", "duration_min": 685,
        "times": {"dep": {"scheduled_utc": "2026-10-02T16:35:00Z"},
                  "arr": {"scheduled_utc": "2026-10-03T03:20:00Z"}},
        "status": {"value": "scheduled"}}]},
        "meta": {"sources": []}}
    cards.status_card(out)
    acts = {a["id"]: a for a in out["meta"]["card"]["actions"]}
    assert acts["review_flightera"]["url"].endswith("/CA2690/2026-10-03")


def test_route_card_includes_map_when_coords():
    out = {"data": {"mode": "driving", "distance_km": 136.8, "duration_min": 93,
                    "tolls_cny": 52, "taxi_estimate_cny": 445,
                    "toll_distance_km": 120.5, "highway_pct": 88.1,
                    "segments": [{"name": "成渝环线高速", "km": 120.5, "pct": 88.1}],
                    "attractions": [{"name": "大足石刻", "note": "世界文化遗产"}]},
           "meta": {}}
    o = {"name": "成都", "lat": 30.57, "lon": 104.07, "country": "CN"}
    d = {"name": "乐山", "lat": 29.55, "lon": 103.77, "country": "CN"}
    cards.route_card(out, o_name="成都", d_name="乐山", o=o, d=d, intl=False)
    card = out["meta"]["card"]
    assert card["type"] == "route.cn"
    assert card["payload"]["map"]["points"][0]["name"] == "成都"
    assert card["payload"]["map"]["lines"][0]["label"] == "136.8km·93min"
    # 自驾卡 v3：自驾关心的字段全量进卡
    assert card["payload"]["duration_text"] == "1小时33分"
    assert card["payload"]["highway_pct"] == 88.1
    assert card["payload"]["toll_distance_km"] == 120.5
    assert card["payload"]["segments"][0]["name"] == "成渝环线高速"
    assert card["payload"]["attractions"][0]["name"] == "大足石刻"


def test_route_card_duration_text_short_and_missing():
    out = {"data": {"mode": "driving", "distance_km": 30.0, "duration_min": 45,
                    "tolls_cny": 0}, "meta": {}}
    cards.route_card(out, o_name="甲", d_name="乙",
                     o={"name": "甲"}, d={"name": "乙"}, intl=False)
    assert out["meta"]["card"]["payload"]["duration_text"] == "45分钟"
    out2 = {"data": {"mode": "driving", "distance_km": 30.0}, "meta": {}}
    cards.route_card(out2, o_name="甲", d_name="乙",
                     o={"name": "甲"}, d={"name": "乙"}, intl=False)
    assert out2["meta"]["card"]["payload"]["duration_text"] is None


def test_confirm_card_has_approve_action():
    out = {"error": {"code": "CONFIRM_REQUIRED",
                     "hint": "单次约 ¥0.5 超过确认阈值", "provider": "variflight"},
           "meta": {}}
    cards.confirm_card(out, od="成都→南京")
    card = out["meta"]["card"]
    assert card["type"] == "confirm"
    assert card["actions"][0]["confirm"] is True


def test_quota_card_rows():
    out = {"data": {"providers": [
        {"provider": "amap", "tier": "free",
         "quota": {"remaining_free": 149988, "limit": 150000}},
        {"provider": "variflight", "tier": "paid",
         "quota": {"period": "total", "limit": None},
         "paid": {"month_cny": 0.5}}],
        "paid": {"month_cny": 0.5}}}
    cards.quota_card(out)
    rows = out["meta"]["card"]["payload"]["rows"]
    assert {"provider": "variflight", "tier": "paid", "remaining": None,
            "limit": None, "used": None, "paid_month_cny": 0.5} in rows


def test_price_card_carries_paid_calibrate_action():
    """免费缓存价卡必须挂「付费校准」动作（confirm 门 + 可回放参数）。"""
    out = _price_out()
    cards.price_card(out, od="成都→悉尼", trip_type="personal", norms=NORMS,
                     origin="成都", destination="悉尼", date="2026-11-02")
    acts = out["meta"]["card"]["actions"]
    act = next(a for a in acts if a["id"] == "paid_calibrate")
    assert act["confirm"] is True
    assert act["args"]["origin"] == "成都"
    assert act["args"]["destination"] == "悉尼"
    assert act["args"]["date"] == "2026-11-02"
    assert act["args"]["paid_calibrate"] is True
    assert "¥0.5" in act["instruction"]


def test_price_card_calibrated_no_recursive_action():
    """已是付费校准结果 → 不再挂校准动作（防递归推销）。"""
    out = _price_out()
    out["data"]["prices"][0]["price_type"] = "calibrated"
    out["data"]["price_type"] = "calibrated"
    cards.price_card(out, od="成都→悉尼", trip_type="personal", norms=NORMS,
                     origin="成都", destination="悉尼", date="2026-11-02")
    acts = out["meta"]["card"]["actions"]
    assert not [a for a in acts if a["id"] == "paid_calibrate"]


def test_empty_card_actions_passthrough():
    """空态卡支持挂动作——国内无免费价源场景的一键校准入口。"""
    out = {"error": {"code": "DATA_UNAVAILABLE", "hint": "国内无免费价格源"}}
    cards.empty_card(out, title="机票价格暂不可得", hint="国内无免费价格源",
                     actions=[{"id": "paid_calibrate", "label": "💰 付费校准",
                               "confirm": True,
                               "args": {"origin": "成都", "destination": "西安",
                                        "date": "2026-11-02",
                                        "paid_calibrate": True}}])
    card = out["meta"]["card"]
    assert card["type"] == "empty"
    assert card["actions"][0]["args"]["destination"] == "西安"
