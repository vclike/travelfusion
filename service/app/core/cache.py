"""持久化缓存 —— docs/09 §3 缓存与新鲜度总表的落地。

按能力 TTL（架构合同）：
  flight.status 300s；flight.schedule 3600s；flight.observe 60s
  flight.price 按 expires_at（无则 24h）；ground.route 不缓存（实时）
命中写 meta.cache，agent 可直接转述"缓存命中"。
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

_LOCK = threading.Lock()
_TTL = {"flight.status": 300, "flight.schedule": 3600,
        "flight.observe": 60, "flight.price": 24 * 3600,
        "weather.context": 3 * 3600}


def _conn(db_path: Path) -> sqlite3.Connection:
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS cache(
        cache_key TEXT PRIMARY KEY, payload TEXT NOT NULL,
        created_at REAL NOT NULL, expires_at REAL NOT NULL)""")
    return c


def ttl_for(capability: str) -> int:
    return _TTL.get(capability, 0)


def cache_get(db_path: Path, key: str) -> dict | None:
    if not db_path.exists():
        return None
    now = time.time()
    with _LOCK:
        with _conn(db_path) as c:
            row = c.execute("SELECT payload, expires_at FROM cache "
                            "WHERE cache_key=?", (key,)).fetchone()
    if not row:
        return None
    if row["expires_at"] < now:
        return None
    return json.loads(row["payload"])


def cache_put(db_path: Path, key: str, payload: dict,
              ttl: int, min_ttl: int = 300) -> None:
    if ttl <= 0:
        return
    payload = json.dumps(payload, ensure_ascii=False)
    with _LOCK:
        with _conn(db_path) as c:
            c.execute("INSERT INTO cache(cache_key,payload,created_at,expires_at) "
                      "VALUES(?,?,?,?) ON CONFLICT(cache_key) DO UPDATE SET "
                      "payload=excluded.payload, created_at=excluded.created_at, "
                      "expires_at=excluded.expires_at",
                      (key, payload, time.time(), time.time() + max(ttl, min_ttl)))


def cache_key(capability: str, query: dict) -> str:
    """缓存键：policy 不入键，**除 paid_calibrate 外**——付费校准=独立新鲜数据，
    理应绕开免费缓存（免费结果不应当作付费答案返回）。"""
    slim = {k: v for k, v in query.items() if k != "policy"}
    slim["__paid"] = bool((query.get("policy") or {}).get("paid_calibrate"))
    raw = capability + "|" + json.dumps(slim, ensure_ascii=False, sort_keys=True)
    import hashlib
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()
