"""ChinaTravel 景点知识库（LAMDA-NeSy 沙盒数据的本地集成）。

数据策略（advisory，非 authoritative）：
- 来源 HuggingFace LAMDA-NeSy/ChinaTravel-Sandbox（CC BY 4.0，月更节奏）
- 覆盖 10 城头部景点：杭州/上海/苏州/重庆/广州/北京/武汉/成都/南京/深圳
- 校验结论只出黄牌建议，不阻断行程；城市/景点缺位静默跳过
- 自动更新：数据缺失或超龄（>UPDATE_INTERVAL 天）时后台拉取新版本
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

import httpx

HF_URL = ("https://hf-mirror.com/datasets/LAMDA-NeSy/ChinaTravel-Sandbox/"
          "resolve/main/data/zh/attractions.parquet")  # 国内镜像（直连被墙）
UPDATE_INTERVAL = 30 * 86400
CITIES = ["杭州", "上海", "苏州", "重庆", "广州", "北京", "武汉", "成都",
          "南京", "深圳"]

_default: "ChinaTravel | None" = None


def get_store(data_dir: Path) -> "ChinaTravel":
    """进程级单例（mcp_server 与启动更新循环共用）。"""
    global _default
    if _default is None:
        _default = ChinaTravel(Path(data_dir))
    return _default


def _hms(v) -> str:
    return f"{float(v):g}h" if v is not None else "?"


class ChinaTravel:
    """SQLite 存储的景点知识库（零外部服务依赖，查询确定性）。"""

    def __init__(self, data_dir: Path):
        self.dir = Path(data_dir)
        self.db = self.dir / "chinatravel.sqlite"
        self.meta_path = self.dir / "chinatravel_meta.json"
        self._lock = threading.Lock()

    # ── 元信息 ────────────────────────────────────────────────────────
    def meta(self) -> dict:
        try:
            return json.loads(self.meta_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def age_days(self) -> float | None:
        m = self.meta()
        ts = m.get("updated_ts")
        return (time.time() - ts) / 86400 if ts else None

    def needs_update(self) -> bool:
        if not self.db.exists():
            return True
        age = self.age_days()
        return age is None or age * 86400 > UPDATE_INTERVAL

    # ── 更新（下载 parquet → 落 SQLite） ─────────────────────────────
    def update(self) -> dict:
        import datetime as _dt

        import pyarrow.parquet as pq  # 容器 requirements 提供
        with self._lock:
            raw = httpx.get(HF_URL, timeout=45, follow_redirects=True).read()
            tmp = self.dir / "chinatravel_tmp.parquet"
            tmp.write_bytes(raw)
            tbl = pq.read_table(tmp)
            rows = tbl.to_pylist()
            tmp.unlink()
            con = sqlite3.connect(self.db)
            con.execute("DROP TABLE IF EXISTS attractions")
            con.execute(
                "CREATE TABLE attractions (city TEXT, name TEXT, type TEXT,"
                " lat REAL, lon REAL, opentime TEXT, endtime TEXT,"
                " price REAL, recommendmin REAL, recommendmax REAL)")
            con.executemany(
                "INSERT INTO attractions VALUES (?,?,?,?,?,?,?,?,?,?)",
                [(r.get("city"), r.get("name"), r.get("type"), r.get("lat"),
                  r.get("lon"), str(r.get("opentime") or ""),
                  str(r.get("endtime") or ""), r.get("price") or 0,
                  r.get("recommendmintime") or 0,
                  r.get("recommendmaxtime") or 0) for r in rows])
            con.commit()
            con.close()
            meta = {"updated_at": _dt.datetime.now().isoformat(timespec="seconds"),
                    "updated_ts": time.time(), "rows": len(rows),
                    "source": "LAMDA-NeSy/ChinaTravel-Sandbox (CC BY 4.0)",
                    "cities": sorted({r.get("city") for r in rows})}
            self.meta_path.write_text(json.dumps(meta, ensure_ascii=False),
                                      encoding="utf-8")
            return meta

    def ensure(self) -> dict | None:
        """缺数据或超龄才更新（供启动后台任务调用）。"""
        if self.needs_update():
            try:
                return self.update()
            except Exception:
                return None
        return None

    # ── 查询 ─────────────────────────────────────────────────────────
    def _con(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db)

    def search(self, city: str, keyword: str = "", limit: int = 10) -> list[dict]:
        if not self.db.exists():
            return []
        con = self._con()
        rows = con.execute(
            "SELECT name, type, lat, lon, opentime, endtime, price,"
            " recommendmin, recommendmax FROM attractions"
            " WHERE city = ? AND name LIKE ? ORDER BY price DESC LIMIT ?",
            (city, f"%{keyword}%" if keyword else "%", limit)).fetchall()
        con.close()
        return [dict(zip(("name", "type", "lat", "lon", "opentime", "endtime",
                          "price", "recommendmin", "recommendmax"), r))
                for r in rows]

    def coverage(self, city: str) -> int:
        if not self.db.exists():
            return 0
        con = self._con()
        n = con.execute("SELECT COUNT(*) FROM attractions WHERE city = ?",
                        (city,)).fetchone()[0]
        con.close()
        return n

    # ── 可行性校验（advisory：只出违规清单，绝不阻断） ─────────────────
    def validate_day(self, city: str, items: list[dict],
                     day_start: str = "08:00",
                     day_end: str = "18:00") -> dict:
        """items: [{name, start_time?: 'HH:MM', end_time?: 'HH:MM',
        minutes?: 数}]. 校验：存在性 / 开闭园 / 建议时长 vs 排入时长 /
        当日合计 vs 时间窗。"""
        result: dict = {"city": city, "checked": 0, "skipped": [],
                        "violations": [], "window": [day_start, day_end]}
        if not self.db.exists():
            result["skipped"] = "知识库未初始化"
            return result
        if self.coverage(city) == 0:
            result["skipped"] = f"{city} 不在知识库覆盖城市（{('/'.join(CITIES))}）"
            return result
        con = self._con()
        total_rec = 0.0
        for it in items or []:
            name = str(it.get("name") or "").strip()
            if not name:
                continue
            row = con.execute(
                "SELECT name, opentime, endtime, recommendmin, recommendmax"
                " FROM attractions WHERE city = ? AND name = ?",
                (city, name)).fetchone()
            if row is None:
                row = con.execute(
                    "SELECT name, opentime, endtime, recommendmin, recommendmax"
                    " FROM attractions WHERE city = ? AND name LIKE ? LIMIT 1",
                    (city, f"%{name}%")).fetchone()
            if row is None:
                result["skipped"].append(name)
                continue
            checked_name, opentime, endtime, rec_min, rec_max = row
            result["checked"] += 1
            total_rec += float(rec_min or 0)
            st, en = it.get("start_time"), it.get("end_time")
            if st and opentime and st < str(opentime):
                result["violations"].append({
                    "level": "error", "about": checked_name,
                    "text": f"{checked_name} {opentime} 才开放，你排 {st} 到达"})
            if en and endtime and en > str(endtime):
                result["violations"].append({
                    "level": "error", "about": checked_name,
                    "text": f"{checked_name} {endtime} 闭园，你排 {en} 离开"})
            if it.get("minutes") and rec_min and float(it["minutes"]) < float(rec_min) * 60:
                result["violations"].append({
                    "level": "warn", "about": checked_name,
                    "text": f"{checked_name} 建议至少游览 "
                            f"{_hms(rec_min)}，你只排了 {_hms(it['minutes'] / 60)}"})
        con.close()
        window = _hm(day_end) - _hm(day_start)
        if total_rec > window:
            result["violations"].append({
                "level": "error", "about": city,
                "text": f"{city} 当日景点建议游览时长合计 {_hms(total_rec)}"
                        f" > 时间窗 {_hms(window)} —— 不可行，建议删减或拆分"})
        return result


def _hm(v) -> float:
    h, _, m = str(v).partition(":")
    return float(h or 0) + float(m or 0) / 60.0
