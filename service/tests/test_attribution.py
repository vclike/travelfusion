"""attribution lint 单测 —— 用 2026-10-01 实测的真实错位样本做回归。"""
from pathlib import Path

from app.core import attribution

KNOWN = attribution.load_known_direct(
    Path(__file__).resolve().parents[1] / "app" / "data" / "known_direct.yaml")


def test_l1_roundtrip_bundle_flags_real_sample():
    """实测样本：HO1120 成都→悉尼缓存价带 return_at（往返捆绑）。"""
    prices = [{"airline_iata": "HO", "flight_number": 1120,
               "departure_at": "2026-11-02T13:00:00+08:00",
               "return_at": "2026-11-09T08:50:00+11:00", "amount": 3962}]
    flags = attribution.lint_prices(prices, origin_code="CTU", destination_code="SYD",
                                    distance_km=8658, known_direct=KNOWN)
    assert attribution.FLAG_L1 in flags
    assert prices[0]["attribution_trust"] == "low"
    assert prices[0]["attribution_flags"] == sorted(
        [attribution.FLAG_L1, attribution.FLAG_L2])


def test_l2_known_direct_carrier_mismatch():
    """成都→悉尼已知直飞只有 3U；HO 出现即归属错位。"""
    prices = [{"airline_iata": "HO", "flight_number": 1120,
               "departure_at": "2026-11-02T13:00:00+08:00", "amount": 3962}]
    flags = attribution.lint_prices(prices, origin_code="CTU", destination_code="SYD",
                                    distance_km=8658, known_direct=KNOWN)
    assert attribution.FLAG_L2 in flags


def test_l2_known_direct_carrier_match_not_flagged():
    prices = [{"airline_iata": "3U", "departure_at": "2026-11-02T01:20:00+08:00",
               "amount": 3500}]
    flags = attribution.lint_prices(prices, origin_code="CTU", destination_code="SYD",
                                    distance_km=8658, known_direct=KNOWN)
    assert flags == []
    assert "attribution_trust" not in prices[0]


def test_l3_duration_conflict():
    """17000km 航线报 2.5h「直达」→ 时长矛盾。"""
    prices = [{"airline_iata": "XX",
               "departure_at": "2026-11-02T13:00:00+08:00",
               "arrival_at": "2026-11-02T15:30:00+08:00", "amount": 3000}]
    flags = attribution.lint_prices(prices, origin_code="LON", destination_code="SYD",
                                    distance_km=17000, known_direct={})
    assert attribution.FLAG_L3 in flags


def test_unknown_pair_and_missing_data_not_punished():
    """未知城市对 / 无距离 / 缺时刻——一律不判罚（防误杀）。"""
    prices = [{"airline_iata": "ZZ", "departure_at": "2026-11-02T10:00:00+08:00",
               "amount": 2000}]
    flags = attribution.lint_prices(prices, origin_code="CTU", destination_code="XXX",
                                    distance_km=None, known_direct=KNOWN)
    assert flags == []
    flags2 = attribution.lint_prices(prices, origin_code="AAA", destination_code="BBB",
                                     distance_km=5000, known_direct={})
    assert flags2 == []
    assert "attribution_trust" not in prices[0]


def test_broken_known_direct_file_returns_empty():
    assert attribution.load_known_direct(Path("Z:/definitely/not/here.yaml")) == {}
