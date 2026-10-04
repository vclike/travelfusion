"""配额账本 —— SQLite，惰性周期重置（读时判 period_key），持久化跨重启。

三计费模式（searchfusion 三分类）:
  monthly  月度刷新（每月1号惰性归零）
  day      按日刷新（每日归零）
  total    总量制（不自动重置；充值制=人工加额）
"""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

_LOCK = threading.Lock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS ledger (
  provider   TEXT PRIMARY KEY,
  period_key TEXT NOT NULL,        -- "2026-09"(月) / "2026-09-29"(日) / "total"
  period     TEXT NOT NULL,
  free_used  INTEGER NOT NULL DEFAULT 0,
  paid_cny   REAL    NOT NULL DEFAULT 0,
  attempts   INTEGER NOT NULL DEFAULT 0,
  billed     INTEGER NOT NULL DEFAULT 0
);
"""


def _period_key(period: str, now: float) -> str:
    t = time.gmtime(now)
    if period == "month":
        return f"{t.tm_year:04d}-{t.tm_mon:02d}"
    if period == "day":
        return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
    return "total"


class QuotaLedger:
    def __init__(self, db_path: Path, now_fn=time.time):
        self.db_path = Path(db_path)
        self.now_fn = now_fn
        with _LOCK, self._conn() as c:
            c.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _row(self, c: sqlite3.Connection, provider: str, period: str) -> sqlite3.Row:
        """惰性重置：period_key 与当前周期不符时归零换新周期。"""
        key = _period_key(period, self.now_fn())
        c.execute(
            "INSERT INTO ledger(provider, period_key, period) VALUES(?,?,?) "
            "ON CONFLICT(provider) DO NOTHING", (provider, key, period))
        row = c.execute("SELECT * FROM ledger WHERE provider=?", (provider,)).fetchone()
        if row["period_key"] != key and period != "total":
            c.execute("UPDATE ledger SET period_key=?, free_used=0, paid_cny=0 "
                      "WHERE provider=?", (key, provider))
            row = c.execute("SELECT * FROM ledger WHERE provider=?", (provider,)).fetchone()
        return row

    def remaining(self, provider: str, period: str, limit: int) -> int | None:
        """剩余免费额度；unlimited/total 制返回 None（无周期性上限）。"""
        if period in ("total", "unlimited"):
            return None
        with _LOCK, self._conn() as c:
            row = self._row(c, provider, period)
            return max(0, limit - row["free_used"])

    def consume_free(self, provider: str, period: str, calls: int = 1) -> int:
        """记免费调用；返回本次之后的 free_used。"""
        with _LOCK, self._conn() as c:
            row = self._row(c, provider, period)
            used = row["free_used"] + calls
            c.execute("UPDATE ledger SET free_used=?, attempts=attempts+1 WHERE provider=?",
                      (used, provider))
            return used

    def consume_paid(self, provider: str, cny: float, calls: int = 1) -> float:
        """记付费消耗；付费挂 total 桶累计（跨月不清零），返回累计 paid_cny。

        2026-10-04 补完 total 制语义：此前（10-02 NAS 侧半成品）月度桶写入与
        #legacy-total 迁移混杂、return 后残留不可达代码。注意：混用免费+付费的
        provider 暂不支持（schema 单行/主键=provider，付费会落在原周期行上），
        当前清单内付费源均为纯 paygo（variflight），无此场景。
        """
        with _LOCK, self._conn() as c:
            row = self._row(c, provider, "total")
            c.execute("UPDATE ledger SET paid_cny=paid_cny+?, attempts=attempts+1, "
                      "billed=billed+? WHERE provider=?", (cny, calls, provider))
            return float(row["paid_cny"]) + cny

    def paid_month_cny(self, month_key: str | None = None) -> float:
        """付费消耗合计（跨 provider 汇总；total 桶按累计口径计入当月预算判定）。"""
        key = month_key or _period_key("month", self.now_fn())
        with _LOCK, self._conn() as c:
            row = c.execute(
                "SELECT COALESCE(SUM(paid_cny),0) s FROM ledger "
                "WHERE period='total' OR (period='month' AND period_key=?)",
                (key,)).fetchone()
            return float(row["s"])

    def status(self) -> list[dict]:
        with _LOCK, self._conn() as c:
            rows = c.execute("SELECT * FROM ledger ORDER BY provider").fetchall()
            return [dict(r) for r in rows]
