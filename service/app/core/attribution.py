"""缓存价归属 lint —— 免费比价缓存结构缺陷的确定性防线（2026-10-01 立项）。

实测背景（双盲控制实验，本会话）：Travelpayouts 缓存对国际中转组合，会把
「首段承运人+班号+出发时刻」标到整程价格上——
  · HO1120（实为成都→上海虹桥）被标为成都→悉尼 13:00 出发
  · CZ3832（实为广州→浦东）被标为上海→悉尼 22:30 出发
两条均带 return_at（往返捆绑口径）。结论：价格量级可信，归属字段结构性不可信。

规则（全部零上游调用；L2 依赖一次性可缓存的本地直飞表）：
  L1 roundtrip_bundle      单程查询返回带 return_at → 往返捆绑口径
  L2 carrier_not_on_route  命中 known_direct 表且承运人不在直飞名单 → 归属错位
  L3 duration_conflict     双端时刻齐全且时长 < 大圆距离理论最短时长 × 0.75
命中 → 条目标 attribution_trust=low，meta.flags 汇总；只降级、不删数据——
agent 仍可转述「缓存价显示 HO1120」，但必须带「归属未核验」限定语。
"""
from __future__ import annotations

from pathlib import Path

import yaml

FLAG_L1 = "roundtrip_bundle"
FLAG_L2 = "carrier_not_on_route"
FLAG_L3 = "duration_conflict"

# 大圆距离 → 理论最短空中时长（巡航 ≈850km/h 保守取速；低于 0.75× 视为错位）
_CRUISE_KMH = 850.0
_MIN_RATIO = 0.75


def load_known_direct(path: Path) -> dict:
    """known_direct.yaml → {pair: {carriers, as_of, source}}；文件缺失/损坏 = 空表（不判罚）。"""
    try:
        return (yaml.safe_load(Path(path).read_text(encoding="utf-8"))
                or {}).get("pairs", {}) or {}
    except Exception:
        return {}


def lint_prices(prices: list[dict], *, origin_code: str, destination_code: str,
                distance_km: float | None,
                known_direct: dict) -> list[str]:
    """逐条打标（就地写 attribution_trust / attribution_flags），返回去重 flag 集。

    未知城市对、缺时刻、无坐标距离——一律不判罚（lint 只抓「确定性矛盾」）。
    """
    pair = f"{origin_code}-{destination_code}"
    known = known_direct.get(pair) or {}
    known_carriers = {str(c).upper() for c in (known.get("carriers") or [])}
    implied_min_h = (float(distance_km) / _CRUISE_KMH) if distance_km else None

    flags: list[str] = []
    for pr in prices or []:
        hit: list[str] = []
        # L1 往返捆绑：flight_price 工具恒为单程口径，带 return_at 即异常
        if pr.get("return_at"):
            hit.append(FLAG_L1)
        # L2 已知直飞线上的陌生承运人
        if known_carriers and (pr.get("airline_iata") or "").upper() not in known_carriers:
            hit.append(FLAG_L2)
        # L3 时长矛盾：双端时刻齐全且远短于理论最短
        if implied_min_h:
            dep, arr = pr.get("departure_at"), (pr.get("arrival_at")
                                                or pr.get("arr_at"))
            if dep and arr:
                try:
                    from datetime import datetime
                    d1 = datetime.fromisoformat(str(dep).replace("Z", "+00:00"))
                    d2 = datetime.fromisoformat(str(arr).replace("Z", "+00:00"))
                    hrs = (d2 - d1).total_seconds() / 3600.0
                    if hrs > 0 and hrs < _MIN_RATIO * implied_min_h:
                        hit.append(FLAG_L3)
                except ValueError:
                    pass                      # 时刻格式异常不判罚（诚实边界）
        if hit:
            pr["attribution_trust"] = "low"
            pr["attribution_flags"] = sorted(set(hit))
            flags.extend(pr["attribution_flags"])
    return sorted(set(flags))
