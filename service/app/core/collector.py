"""7×24 基线采集器 —— 软路由部署的核心价值：非使用时段持续攒 L3 基线。

watchlist 来自 data/settings.yaml（baseline_watchlist），形如：
  baseline_watchlist:
    - {origin: 成都, destination: 曼谷}
    - {origin: 北京, destination: 东京}
采集：逐条走 dispatch flight.price（免费层，缓存命中零消耗）→ baseline.record。
由 app.main 的 lifespan 周期任务驱动（asyncio.to_thread 包同步调度）。
"""
from __future__ import annotations

from pathlib import Path

import yaml

from app.core import baseline, dispatch


def watchlist(data_dir: Path) -> list[dict]:
    f = Path(data_dir) / "settings.yaml"
    if not f.exists():
        return []
    cfg = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    out = []
    for item in cfg.get("baseline_watchlist") or []:
        if item.get("origin") and item.get("destination"):
            out.append({"origin": item["origin"], "destination": item["destination"]})
    return out


def interval_hours(data_dir: Path, default: float = 6.0) -> float:
    f = Path(data_dir) / "settings.yaml"
    if not f.exists():
        return default
    cfg = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    try:
        return max(1.0, float(cfg.get("baseline_interval_hours", default)))
    except (TypeError, ValueError):
        return default


def _iata(data_dir: Path, name: str) -> str | None:
    f = Path(data_dir) / "city_coords.yaml"
    if not f.exists():
        return None
    cities = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("cities") or {}
    c = cities.get(name)
    return (c or {}).get("iata")


def collect_once(data_dir: Path, settings=None) -> dict:
    """跑一轮采集，返回摘要（写入条数/跳过原因）。"""
    p = Path(data_dir)
    routes = watchlist(p)
    summary = {"routes": len(routes), "recorded": 0, "skipped": []}
    if not routes:
        return summary
    for r in routes:
        ocode, dcode = _iata(p, r["origin"]), _iata(p, r["destination"])
        if not (ocode and dcode):
            summary["skipped"].append({"route": f"{r['origin']}→{r['destination']}",
                                       "code": "NO_IATA"})
            continue
        out = dispatch.call_capability(
            "flight.price",
            {"origin": r["origin"], "destination": r["destination"],
             "origin_code": ocode, "destination_code": dcode,
             "policy": {}},
            data_dir=p, settings=settings)
        if out.get("error"):
            summary["skipped"].append(
                {"route": f"{r['origin']}→{r['destination']}",
                 "code": out["error"]["code"]})
            continue
        prices = (out.get("data") or {}).get("prices") or []
        # 2026-10-02 修复：缓存命中 = 同一观测的重复读取，不再写入新基线样本
        if (out.get("meta") or {}).get("cache") == "hit":
            summary["skipped"].append(
                {"route": f"{r['origin']}→{r['destination']}",
                 "code": "CACHE_HIT_NO_NEW_SAMPLE"})
            continue
        n = baseline.record(p / "baseline.db", ocode, dcode, prices)
        summary["recorded"] += n
    baseline.prune(p / "baseline.db")
    return summary
