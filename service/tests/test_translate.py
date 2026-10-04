"""卡片翻译层测试：IATA 码 → 普通人可读名。"""
from app.core import cards


def test_airline_name_known():
    assert cards.airline_name("FD") == "泰亚航"
    assert cards.airline_name("CA") == "中国国航"


def test_airline_name_unknown_falls_back_to_code():
    assert cards.airline_name("XX") == "XX"
    assert cards.airline_name(None) == ""


def test_city_name_from_city_table():
    # 城表：东京 iata=TYO（真机数据）
    assert cards.city_name("TYO") == "东京"


def test_city_name_unknown_falls_back():
    assert cards.city_name("XYZ") == "XYZ"


def test_status_card_uses_translated_names():
    out = {"data": {"flights": [{
        "flight_no": "CA165", "airline_iata": "CA", "dep_iata": "PEK",
        "arr_iata": "MEL", "dep_terminal": "T3", "arr_terminal": "T2",
        "duration_min": 685,
        "times": {"dep": {"scheduled_utc": "x"}, "arr": {"scheduled_utc": "y"}},
        "status": {"value": "landed"}},
        ]},
        "meta": {"sources": []}}
    cards.status_card(out)
    card = out["meta"]["card"]
    # 城表有北京/墨尔本则用译名；没有则回退码——两种都算合规，关键是 airline_name 生效
    assert card["payload"]["airline_name"] == "中国国航"
    assert "→" in card["title"]
