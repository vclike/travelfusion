"""负标系统（移植自 searchfusion negmark 思想）——运行时声誉层。

manifest 管静态策略；本模块管"此刻还灵不灵"：
  失败 → 计数升级冷却（1h→2h→4h…封顶24h）
  成功 → 立即解封并清零
按 (provider, capability) 组合隔离：AirLabs 查状态被限流不代表它查机场库也坏了。
"""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

# RLock：record_failure 持锁期间调用 _conn()，_conn 内部再次拿锁——必须可重入
_LOCK = threading.RLock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS negmark (
  provider     TEXT NOT NULL,
  capability   TEXT NOT NULL,
  fail_count   INTEGER NOT NULL DEFAULT 0,
  banned_until REAL NOT NULL DEFAULT 0,
  last_reason  TEXT,
  PRIMARY KEY (provider, capability)
);
"""

BASE_BAN_S = 3600        # 首次冷却 1h
MAX_BAN_S = 86400        # 封顶 24h


def _conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    with _LOCK:
        conn.executescript(_SCHEMA)
    return conn


def _ban_seconds(prior_fail_count: int) -> int:
    """prior_fail_count = 本次失败前的累计失败次数：首败 1h，二败 2h，三败 4h…封顶 24h。"""
    return min(BASE_BAN_S * (2 ** max(0, prior_fail_count)), MAX_BAN_S)


def record_failure(db_path: Path, provider: str, capability: str, reason: str = "",
                   now: float | None = None) -> float:
    now = now if now is not None else time.time()
    with _LOCK, _conn(db_path) as c:
        c.execute("INSERT INTO negmark(provider,capability,fail_count,banned_until) "
                  "VALUES(?,?,0,0) ON CONFLICT(provider,capability) DO NOTHING",
                  (provider, capability))
        c.execute("UPDATE negmark SET fail_count=fail_count+1, last_reason=?, "
                  "banned_until=? WHERE provider=? AND capability=?",
                  (reason, now + _ban_seconds(
                      c.execute("SELECT fail_count FROM negmark WHERE provider=? AND "
                                "capability=?", (provider, capability)).fetchone()["fail_count"]),
                  provider, capability))
        row = c.execute("SELECT banned_until FROM negmark WHERE provider=? AND capability=?",
                        (provider, capability)).fetchone()
        return float(row["banned_until"])


def record_success(db_path: Path, provider: str, capability: str) -> None:
    """成功一次 → 解封清零。"""
    with _LOCK, _conn(db_path) as c:
        c.execute("DELETE FROM negmark WHERE provider=? AND capability=?",
                  (provider, capability))


def is_banned(db_path: Path, provider: str, capability: str,
              now: float | None = None) -> bool:
    now = now if now is not None else time.time()
    with _LOCK, _conn(db_path) as c:
        row = c.execute("SELECT banned_until FROM negmark WHERE provider=? AND capability=?",
                        (provider, capability)).fetchone()
        return bool(row) and row["banned_until"] > now


def banned_providers(db_path: Path, capability: str, now: float | None = None) -> set[str]:
    now = now if now is not None else time.time()
    with _LOCK, _conn(db_path) as c:
        rows = c.execute("SELECT provider, banned_until FROM negmark WHERE capability=?",
                         (capability,)).fetchall()
        return {r["provider"] for r in rows if r["banned_until"] > now}


def list_banned(db_path: Path, now: float | None = None) -> list[dict]:
    """管理面板：当前生效中的拉黑项（含剩余分钟）。"""
    now = now if now is not None else time.time()
    with _LOCK, _conn(db_path) as c:
        rows = c.execute("SELECT provider, capability, fail_count, banned_until, "
                         "last_reason FROM negmark WHERE banned_until>? "
                         "ORDER BY banned_until", (now,)).fetchall()
    return [{"provider": r["provider"], "capability": r["capability"],
             "fail_count": r["fail_count"], "last_reason": r["last_reason"] or "",
             "eta_min": max(0, round((r["banned_until"] - now) / 60))}
            for r in rows]


def clear(db_path: Path, provider: str | None = None,
          capability: str | None = None) -> int:
    """管理面板手动解除；provider/capability 缺省 = 全清。返回清除行数。"""
    with _LOCK, _conn(db_path) as c:
        if provider and capability:
            cur = c.execute("DELETE FROM negmark WHERE provider=? AND capability=?",
                            (provider, capability))
        elif provider:
            cur = c.execute("DELETE FROM negmark WHERE provider=?", (provider,))
        else:
            cur = c.execute("DELETE FROM negmark")
        return cur.rowcount
