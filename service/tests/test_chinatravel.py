"""ChinaTravel 校验器规则测试（本地 fixture SQLite，无网络）。"""
import sqlite3

import pytest

from app.core import chinatravel


@pytest.fixture()
def store(tmp_path):
    st = chinatravel.ChinaTravel(tmp_path)
    con = sqlite3.connect(st.db)
    con.execute("CREATE TABLE attractions (city TEXT, name TEXT, type TEXT,"
                " lat REAL, lon REAL, opentime TEXT, endtime TEXT,"
                " price REAL, recommendmin REAL, recommendmax REAL)")
    con.executemany(
        "INSERT INTO attractions VALUES (?,?,?,?,?,?,?,?,?,?)",
        [("西安", "秦始皇兵马俑博物馆", "历史遗迹", 34.38, 109.27,
          "08:30", "18:00", 120.0, 3.0, 5.0),
         ("西安", "西安城墙", "古建筑", 34.26, 108.94,
          "08:00", "22:00", 54.0, 2.0, 3.0)])
    con.commit()
    con.close()
    return st


def test_validate_duration_violation(store):
    r = store.validate_day("西安", [
        {"name": "秦始皇兵马俑博物馆", "start_time": "10:00",
         "end_time": "11:00", "minutes": 60},
        {"name": "西安城墙", "minutes": 150},
    ], "08:00", "18:00")
    texts = [v["text"] for v in r["violations"]]
    assert any("兵马俑" in t and "建议至少" in t for t in texts)
    assert r["checked"] == 2


def test_validate_opentime_violation(store):
    r = store.validate_day("西安", [
        {"name": "秦始皇兵马俑博物馆", "start_time": "07:00",
         "end_time": "12:00", "minutes": 240},
    ], "08:00", "18:00")
    texts = [v["text"] for v in r["violations"]]
    assert any("08:30 才开放" in t for t in texts)


def test_validate_city_uncovered(store):
    r = store.validate_day("上海", [{"name": "外滩", "minutes": 60}])
    assert "不在知识库覆盖城市" in r["skipped"]
    assert r["violations"] == []


def test_validate_all_fit_no_warn(store):
    r = store.validate_day("西安", [
        {"name": "秦始皇兵马俑博物馆", "start_time": "09:00",
         "end_time": "13:00", "minutes": 240},
    ], "08:00", "18:00")
    assert r["violations"] == []
    assert r["checked"] == 1
