"""交通方式资格引擎 —— 确定性规则，零 AI、零外部调用。

规则（v3-1）：距离带 + 端点设施存在性 + 跨境判定 → 模式资格矩阵（含理由）。
护栏语义：flight 类查询先过本引擎，不合格未 force → NOT_APPLICABLE，配额消耗 0。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

MODES = ("air", "rail", "drive")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@dataclass
class EligibilityResult:
    distance_km: float
    cross_border: bool
    eligible: dict[str, bool] = field(default_factory=dict)
    reasons: dict[str, str] = field(default_factory=dict)
    rank: list[str] = field(default_factory=list)   # 建议查询顺序

    def blocked(self, mode: str) -> bool:
        return not self.eligible.get(mode, False)


def decide(distance_km: float, cross_border: bool,
           has_airport: bool = True, has_station: bool = True,
           band_short: int = 300, band_mid: int = 1000,
           band_long: int = 3000, same_place: bool = False) -> EligibilityResult:
    res = EligibilityResult(distance_km=round(distance_km, 1),
                            cross_border=cross_border)
    if same_place:
        for m in MODES:
            res.eligible[m] = False
            res.reasons[m] = "起终点同城，无城际交通需求"
        return res

    if cross_border:
        res.eligible = {"air": has_airport, "rail": False, "drive": False}
        res.reasons["air"] = "" if has_airport else "目的地无商业机场"
        res.reasons["rail"] = "跨境：铁路不在本服务范围（12306 仅境内）"
        res.reasons["drive"] = "跨境：自驾出境规划不在本服务范围"
        res.rank = (["air"] if has_airport else [])
        return res

    d = distance_km
    if d < band_short:
        band = f"距离{d:.0f}km（<{band_short}km 短途带）"
        res.eligible = {"air": False, "rail": has_station, "drive": True}
        res.reasons["air"] = f"{band}：门到门时间不如高铁，无商业航空价值"
        res.reasons["rail"] = "" if has_station else "目的地无火车站"
        res.rank = ["rail", "drive"]
    elif d < band_mid:
        res.eligible = {"air": True, "rail": has_station, "drive": True}
        res.reasons["rail"] = "中距离带：高铁优先"
        res.reasons["air"] = "中距离带：航班低优先（仅显式要求或高铁无果时查询）"
        res.rank = ["rail", "drive", "air"]
    elif d < band_long:
        res.eligible = {"air": has_airport, "rail": has_station, "drive": d < 2000}
        res.reasons["air"] = "" if has_airport else "目的地无商业机场"
        res.reasons["drive"] = "" if d < 2000 else f"距离{d:.0f}km：自驾不现实"
        res.rank = ["air", "rail"]
    else:
        res.eligible = {"air": has_airport, "rail": has_station, "drive": False}
        res.reasons["air"] = "" if has_airport else "两端均无商业机场"
        res.reasons["drive"] = f"距离{d:.0f}km：自驾不现实"
        res.rank = ["air", "rail"]
    return res
