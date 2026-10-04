import json

import httpx
import pytest

from app.providers.amap.adapter import Adapter, wgs2gcj

SAMPLE = {"status": "1", "infocode": "10000",
          "route": {"taxi_cost": "414",
                    "paths": [{"distance": "140448",
                               "cost": {"duration": "5856", "tolls": "54",
                                        "toll_distance": "133738",
                                        "traffic_lights": "5"},
                               "steps": [
                                   {"instruction": "向南行驶100米左转",
                                    "step_distance": "100", "road_name": ""},
                                   {"instruction": "沿滨河路向东行驶3千米右转",
                                    "step_distance": "3000", "road_name": "滨河路"},
                                   {"instruction": "沿白家立交途径G5京昆高速向南行驶130千米",
                                    "step_distance": "130000", "road_name": "白家立交",
                                    "cost": {"toll_road": "G5京昆高速"}},
                                   {"instruction": "沿内环快速向东行驶7.3千米到达",
                                    "step_distance": "7348", "road_name": "内环快速"}]}]}}


def test_wgs2gcj_small_east_shift_in_china():
    lng, lat = wgs2gcj(104.0668, 30.5728)      # 成都
    assert 0.0005 < lng - 104.0668 < 0.02      # 向东偏（境内典型）
    assert abs(lat - 30.5728) < 0.02


def test_wgs2gcj_passthrough_outside_china():
    assert wgs2gcj(-0.1276, 51.5072) == (-0.1276, 51.5072)   # 伦敦原样


def _adapter_with(body: dict) -> Adapter:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, content=json.dumps(body).encode()))
    return Adapter(api_key="test", http=httpx.Client(transport=transport))


def test_driving_normalize():
    out = _adapter_with(SAMPLE).fetch(
        "ground.route",
        {"origin_wgs": [104.0668, 30.5728], "destination_wgs": [103.7656, 29.5521],
         "ev_rated_range_km": 400, "policy": {}})
    d = out["data"]
    assert d["distance_km"] == 140.4
    assert d["duration_min"] == 98               # 5856s
    assert d["tolls_cny"] == 54.0
    assert d["taxi_estimate_cny"] == 414.0       # 官方估价优先
    assert d["taxi_estimate_basis"] == "高德官方估价"
    assert d["ev_plan"]["charge_stops_needed"] == 0     # 140km < 400km 续航


def test_driving_segments_highway_pct_and_roads():
    out = _adapter_with(SAMPLE).fetch(
        "ground.route",
        {"origin_wgs": [104.0668, 30.5728], "destination_wgs": [103.7656, 29.5521],
         "policy": {}})
    d = out["data"]
    assert d["highway_pct"] == 95.2              # 133.738/140.448
    segs = d["segments"]
    # <5km 衔接段（市区道路+滨河路 3.1km）并入「其他路段」，按行驶顺序排列
    assert [s["name"] for s in segs] == ["G5京昆高速", "内环快速", "其他路段"]
    assert segs[0] == {"name": "G5京昆高速", "km": 130.0, "pct": 92.6}
    assert segs[1]["km"] == 7.3 and segs[1]["pct"] == 5.2
    assert segs[2] == {"name": "其他路段", "km": 3.1, "pct": 2.2}
    # roads 兼容字段：v5 步距字段 step_distance 已被正确读取（按 road_name 聚合）
    assert d["roads"][0] == {"name": "白家立交", "km": 130.0}


def test_segments_merge_consecutive_same_road():
    body = {"status": "1", "infocode": "10000",
            "route": {"paths": [{"distance": "10000",
                                 "cost": {"duration": "600", "tolls": "0",
                                          "toll_distance": "0"},
                                 "steps": [
                                     {"step_distance": "4000",
                                      "road_name": "内环快速"},
                                     {"step_distance": "6000",
                                      "road_name": "内环快速"}]}]}}
    out = _adapter_with(body).fetch(
        "ground.route",
        {"origin_wgs": [104, 30], "destination_wgs": [103, 29], "policy": {}})
    segs = out["data"]["segments"]
    assert len(segs) == 1
    assert segs[0] == {"name": "内环快速", "km": 10.0, "pct": 100.0}
    assert out["data"]["highway_pct"] is None     # 无收费里程不编造


def test_segments_real_world_noise_rules():
    """回归（2026-09-29 真机成都→重庆）：途径截断/出口引道/夹心同名段。"""
    body = {"status": "1", "infocode": "10000",
            "route": {"paths": [{"distance": "93397",
                                 "cost": {"duration": "6000", "tolls": "60",
                                          "toll_distance": "90000"},
                                 "steps": [
                                     {"instruction": "沿白鹭湾枢纽互通途径S3天府国际机场高速、新兴特大桥向东南行驶18.8千米",
                                      "step_distance": "18800",
                                      "road_name": "白鹭湾枢纽互通",
                                      "cost": {"toll_road": "新兴特大桥"}},
                                     # 无「途径」的隧道步：成为衔接段，S3 应夹心合并
                                     {"instruction": "沿龙泉山1号隧道向东南行驶2.4千米直行进入隧道",
                                      "step_distance": "2353",
                                      "road_name": "龙泉山1号隧道"},
                                     {"instruction": "沿龙泉山2号隧道途径S3天府国际机场高速向东行驶19.4千米向右前方行驶",
                                      "step_distance": "19414",
                                      "road_name": "龙泉山2号隧道",
                                      "cost": {"toll_road": "S3天府国际机场高速"}},
                                     # 途径截断：路名不得吃进「向东南行驶…」尾巴
                                     {"instruction": "沿云雾山隧道途径G93成渝环线高速向东南行驶5.8千米靠左沿主路行驶",
                                      "step_distance": "5800",
                                      "road_name": "云雾山隧道"},
                                     {"instruction": "沿G93成渝环线高速途径皮家槽大桥向东南行驶17.5千米",
                                      "step_distance": "17500",
                                      "road_name": "G93成渝环线高速"},
                                     # 「出口」引道名 → 取途径里的真实高速 S48
                                     {"instruction": "沿G5013渝蓉高速出口途径扎营坪大桥、S48铜荥高速、月亮坝大桥向东行驶29.5千米直行进入隧道",
                                      "step_distance": "29530",
                                      "road_name": "G5013渝蓉高速出口"}]}]}}
    out = _adapter_with(body).fetch(
        "ground.route",
        {"origin_wgs": [104, 30], "destination_wgs": [103, 29], "policy": {}})
    segs = out["data"]["segments"]
    assert [s["name"] for s in segs] == [
        "S3天府国际机场高速", "G93成渝环线高速", "S48铜荥高速", "其他路段"]
    assert segs[0] == {"name": "S3天府国际机场高速", "km": 38.2, "pct": 40.9}
    assert segs[1] == {"name": "G93成渝环线高速", "km": 23.3, "pct": 24.9}
    assert segs[2] == {"name": "S48铜荥高速", "km": 29.5, "pct": 31.6}
    assert segs[3] == {"name": "其他路段", "km": 2.4, "pct": 2.5}
    assert out["data"]["highway_pct"] == 96.4     # 90/93.397


def test_ev_needs_stops_when_distance_exceeds_range():
    out = _adapter_with(SAMPLE).fetch(
        "ground.route",
        {"origin_wgs": [104.0668, 30.5728], "destination_wgs": [103.7656, 29.5521],
         "ev_rated_range_km": 80, "policy": {}})
    assert out["data"]["ev_plan"]["charge_stops_needed"] >= 1


def test_error_status_maps():
    with pytest.raises(Exception) as ei:
        _adapter_with({"status": "0", "infocode": "10001",
                       "info": "INVALID_USER_KEY"}).fetch(
            "ground.route", {"origin_wgs": [104, 30], "destination_wgs": [103, 29],
                             "policy": {}})
    assert "AUTH" in str(ei.value) or "10001" in str(ei.value)
