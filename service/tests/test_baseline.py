import json

from app.core import baseline, collector


def test_record_and_stats(tmp_path):
    db = tmp_path / "baseline.db"
    prices = [{"amount": 3000, "currency": "CNY", "airline_iata": "TG",
               "departure_at": "2026-10-03", "expires_at": "2026-09-30"},
              {"amount": 3600, "currency": "CNY"}]
    assert baseline.record(db, "成都", "曼谷", prices) == 2
    s = baseline.stats(db, "成都", "曼谷")
    assert s is None                            # 样本 <5 不下结论


def test_stats_after_enough_samples(tmp_path):
    import time
    db = tmp_path / "baseline.db"
    t = time.time()
    for i in range(7):                          # 7 个历史批次
        baseline.record(db, "CTU", "BKK", [{"amount": 3000 + i * 100,
                                            "currency": "CNY"}])
        # 手动把 captured_at 往前推，制造时间分布
        with baseline._LOCK, baseline._conn(db) as c:
            c.execute("UPDATE baseline SET captured_at=? WHERE rowid="
                      "(SELECT MAX(rowid) FROM baseline)", (t - (7 - i) * 86400,))
    s = baseline.stats(db, "CTU", "BKK")
    assert s["samples"] == 7
    assert s["min_cny"] == 3000
    assert s["avg_cny"] == 3300
    assert s["vs_min"] == 20                    # 最新 3600 vs 最低 3000


def test_route_isolation(tmp_path):
    db = tmp_path / "baseline.db"
    for i in range(6):
        baseline.record(db, "CTU", "BKK", [{"amount": 3000, "currency": "CNY"}])
    assert baseline.stats(db, "CTU", "TYO") is None


def test_watchlist_parse(tmp_path):
    d = tmp_path
    (d / "settings.yaml").write_text(
        "baseline_interval_hours: 3\n"
        "baseline_watchlist:\n"
        "  - {origin: 成都, destination: 曼谷}\n"
        "  - {origin: 北京}\n", encoding="utf-8")   # 残缺条目应被丢弃
    wl = collector.watchlist(d)
    assert wl == [{"origin": "成都", "destination": "曼谷"}]
    assert collector.interval_hours(d) == 3.0


def test_collect_once_records_via_dispatch(tmp_path, monkeypatch):
    d = tmp_path
    (d / "settings.yaml").write_text(
        "baseline_watchlist:\n  - {origin: 成都, destination: 曼谷}\n",
        encoding="utf-8")
    (d / "city_coords.yaml").write_text(
        "cities:\n"
        "  成都: {lat: 30.57, lon: 104.06, country: CN, iata: CTU}\n"
        "  曼谷: {lat: 13.75, lon: 100.51, country: TH, iata: BKK}\n",
        encoding="utf-8")

    def fake_dispatch(cap, q, *, data_dir, settings=None):
        return {"data": {"prices": [{"amount": 3500, "currency": "CNY",
                                     "airline_iata": "TG"}]}, "meta": {}}

    monkeypatch.setattr(collector.dispatch, "call_capability", fake_dispatch)
    s = collector.collect_once(d)
    assert s["recorded"] == 1 and s["routes"] == 1
    import json
    assert json.loads(json.dumps(s))["recorded"] == 1
    # 基线确实落库
    assert baseline.stats(d / "baseline.db", "成都", "曼谷") is None  # 仅1样本
