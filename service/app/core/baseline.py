"""L3 价格基线 —— 查询即采集 + 定时采集（软路由 7×24 的核心价值）。

回答的问题：「这条航线，历史便宜到过多少？现在贵不贵？」
存储：SQLite baseline 表，按 (origin,dest) 聚合，90 天窗口统计。
"""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

_LOCK = threading.Lock()


def _conn(db_path: Path) -> sqlite3.Connection:
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS baseline(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT NOT NULL, dest TEXT NOT NULL,
        captured_at REAL NOT NULL,
        price REAL NOT NULL, currency TEXT NOT NULL,
        airline TEXT, depart_at TEXT, expires_at TEXT,
        source TEXT DEFAULT 'travelpayouts')""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_route ON baseline(origin,dest,captured_at)")
    return c


def record(db_path: Path, origin: str, dest: str, prices: list[dict],
           source: str = "travelpayouts") -> int:
    """从 flight.price 的 cached 价列表采集入库，返回写入行数。"""
    now = time.time()
    rows = [(origin.upper(), dest.upper(), now, float(p["amount"]),
             p.get("currency", "CNY"), p.get("airline_iata"),
             p.get("departure_at"), p.get("expires_at"), source)
            for p in prices if p.get("amount") is not None]
    if not rows:
        return 0
    with _LOCK, _conn(db_path) as c:
        c.executemany("INSERT INTO baseline(origin,dest,captured_at,price,currency,"
                      "airline,depart_at,expires_at,source) VALUES(?,?,?,?,?,?,?,?,?)",
                      rows)
    return len(rows)


def stats(db_path: Path, origin: str, dest: str, days: int = 90) -> dict | None:
    """窗口内 min/avg/count/latest——样本 <5 时返回 None（样本不足不下结论）。"""
    cutoff = time.time() - days * 86400
    with _LOCK, _conn(db_path) as c:
        row = c.execute(
            "SELECT MIN(price) lo, AVG(price) avg_p, COUNT(*) n, "
            "MAX(captured_at) last FROM baseline "
            "WHERE origin=? AND dest=? AND captured_at>=?", (
                origin.upper(), dest.upper(), cutoff)).fetchone()
        latest = c.execute(
            "SELECT price, captured_at FROM baseline WHERE origin=? AND dest=? "
            "ORDER BY captured_at DESC LIMIT 1", (
                origin.upper(), dest.upper())).fetchone()
    if not row or row["n"] < 5:
        return None
    out = {"window_days": days, "samples": row["n"],
           "min_cny": round(row["lo"], 0), "avg_cny": round(row["avg_p"], 0)}
    if latest:
        out["latest_cny"] = round(latest["price"], 0)
        out["vs_min"] = (round((latest["price"] - row["lo"]) / row["lo"] * 100)
                         if row["lo"] else None)
        out["last_captured_at"] = latest["captured_at"]
    return out


def prune(db_path: Path, keep_days: int = 400) -> int:
    cutoff = time.time() - keep_days * 86400
    with _LOCK, _conn(db_path) as c:
        cur = c.execute("DELETE FROM baseline WHERE captured_at<?", (cutoff,))
        return cur.rowcount
