"""高德 adapter —— 境内地面交通底座（驾车路径规划）。

坐标系不变量（架构铁律）：高德全部接口使用 GCJ-02；本服务内部与其它源统一 WGS-84。
⇒ 入参 WGS-84，adapter 内部转 GCJ-02 调 API，输出一律 WGS-84。
个人认证配额（docs/07 §6）：驾车 150,000 次/月——够用。
"""
from __future__ import annotations

import re

from app.core.errors import ProviderError

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE, E_NO_MATCH,
                            E_QUOTA_LIMIT, E_UPSTREAM_FAILURE)

GEO = "https://restapi.amap.com/v3/geocode/geo"
DRIVING = "https://restapi.amap.com/v5/direction/driving"
DRIVING_V3 = "https://restapi.amap.com/v3/direction/driving"  # extensions=all 带 polyline（v5 steps 无几何）
PLACE_TEXT = "https://restapi.amap.com/v3/place/text"
PLACE_AROUND = "https://restapi.amap.com/v3/place/around"

_A = 6378245.0
_EE = 0.00669342162296594323




def _out_of_china(lng: float, lat: float) -> bool:
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def _tlat(x: float, y: float) -> float:
    ret = (-100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y
           + 0.2 * abs(x))
    ret += (20.0 * (6.0 * y * 3.141592653589793 / 180) ** 2
            * (1 - 2 * ((y * 3.141592653589793 / 180) % 1) ** 0.1)) * 2.0 / 3.0
    return ret


def _tlng(x: float, y: float) -> float:
    ret = (300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * abs(x))
    ret += (20.0 * (6.0 * x * 3.141592653589793 / 180) ** 2
            * (1 - 2 * ((x * 3.141592653589793 / 180) % 1) ** 0.1)) * 2.0 / 3.0
    return ret


def wgs2gcj(lng: float, lat: float) -> tuple[float, float]:
    """WGS-84 → GCJ-02（标准偏移算法；境外原样返回）。"""
    import math
    if _out_of_china(lng, lat):
        return lng, lat
    dlat = _tlat(lng - 105.0, lat - 25.0)
    dlng = _tlng(lng - 105.0, lat - 25.0)
    radlat = lat / 180.0 * math.pi
    magic = 1 - _EE * (math.sin(radlat) ** 2)
    sqrtmagic = magic ** 0.5
    dlat = (dlat * 180.0) / ((_A * (1 - _EE)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (_A / sqrtmagic * math.cos(radlat) * math.pi)
    return lng + dlng, lat + dlat


def gcj2wgs(lng: float, lat: float) -> tuple[float, float]:
    """GCJ-02 → WGS-84（单次反向近似，误差 ~1m，满足卡面 SVG 精度）。"""
    if _out_of_china(lng, lat):
        return lng, lat
    glng, glat = wgs2gcj(lng, lat)
    return lng * 2 - glng, lat * 2 - glat


def _check_status(j: dict, provider: str):
    if str(j.get("status")) != "1":
        infocode = str(j.get("infocode", ""))
        info = str(j.get("info", ""))[:120]
        if infocode in ("10001", "10002"):
            raise ProviderError(E_AUTH_REQUIRED, f"{infocode} {info}", provider)
        if infocode in ("10003", "10004", "10009", "10014", "10019"):
            raise ProviderError(E_QUOTA_LIMIT, f"{infocode} {info}", provider)
        if infocode in ("30001", "30003"):       # 请求参数异常
            raise ProviderError(E_NO_MATCH, f"{infocode} {info}", provider)
        raise ProviderError(E_UPSTREAM_FAILURE, f"{infocode} {info}", provider)


def _via_highway(instruction: str) -> str | None:
    """从 instruction「途径X、Y向东南行驶…」截取第一个高速/环线名（方向动词处截断）。"""
    m = re.search(r"途径([^，。；]+)", str(instruction or ""))
    if not m:
        return None
    for part in m.group(1).split("、"):
        part = part.split("向")[0].strip()
        if "高速" in part or "环线" in part:
            return part
    return None


def _seg_key(st: dict) -> str:
    """导航步骤 → 干线段名：收费路(高速/环线) > instruction「途径」高速 >
    道路名(高速/环线/快速，排除「出口/入口」引道名) > 道路名 > 市区道路。"""
    cost = st.get("cost") or {}
    tr = str(cost.get("toll_road") or "").strip()
    if tr and ("高速" in tr or "环线" in tr):
        return tr
    if name := _via_highway(st.get("instruction")):
        return name
    rn = str(st.get("road_name") or "").strip()
    if ("高速" in rn or "环线" in rn or "快速" in rn) \
            and not re.search(r"(出口|入口)$", rn):
        return rn
    return rn or "市区道路"


class Adapter:
    id = "amap"
    capabilities = ["ground.route", "place.search", "weather.cn",
                    "poi.search", "poi.around"]

    def __init__(self, api_key: str | None, http: httpx.Client | None = None):
        self.k = api_key
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        r = self.http.get(GEO, params={"address": "北京市", "key": self.k})
        j = r.json()
        return {"status": r.status_code, "ok": j.get("status") == "1"}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "ground.route":
            return self._driving(query)
        if capability == "poi.search":
            return self._poi_text(query)
        if capability == "poi.around":
            return self._poi_around(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"amap 未实现 {capability}", self.id)

    def _poi_parse(self, pois: list) -> list[dict]:
        """v3 POI → [{name, address, lat, lon(WGS), type}]。"""
        out = []
        for p in (pois or [])[:8]:
            loc = (p.get("location") or "").split(",")
            if len(loc) != 2:
                continue
            try:
                lon2, lat2 = gcj2wgs(float(loc[0]), float(loc[1]))
            except (ValueError, TypeError):
                continue
            out.append({"name": p.get("name"),
                        "address": (p.get("address") or "").strip(),
                        "lat": round(lat2, 5), "lon": round(lon2, 5),
                        "type": p.get("type") or ""})
        return out

    def _poi_text(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "amap key 未配置", self.id)
        kw = str(q.get("keywords") or "").strip()
        if not kw:
            raise ProviderError(E_NO_MATCH, "缺少 keywords", self.id)
        params = {"key": self.k, "keywords": kw, "offset": 8, "page": 1}
        if q.get("city"):
            params["city"] = str(q["city"])
        r = self.http.get(PLACE_TEXT, params=params)
        j = r.json()
        _check_status(j, self.id)
        return {"data": {"pois": self._poi_parse(j.get("pois") or []),
                         "keywords": kw},
                "cost_calls": 1}

    def _poi_around(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "amap key 未配置", self.id)
        loc = q.get("location_wgs")
        kw = str(q.get("keywords") or "景点").strip()
        if not loc:
            raise ProviderError(E_NO_MATCH, "缺少 location_wgs", self.id)
        g = wgs2gcj(float(loc[0]), float(loc[1]))
        params = {"key": self.k, "location": f"{g[0]:.6f},{g[1]:.6f}",
                  "keywords": kw, "radius": int(q.get("radius_m") or 20000),
                  "offset": 8, "page": 1,
                  "types": "110000|100000"}            # 风景名胜/公园广场默认
        if q.get("types"):
            params["types"] = str(q["types"])
        r = self.http.get(PLACE_AROUND, params=params)
        j = r.json()
        _check_status(j, self.id)
        return {"data": {"pois": self._poi_parse(j.get("pois") or []),
                         "keywords": kw},
                "cost_calls": 1}

    def _driving(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "amap key 未配置", self.id)
        o, d = q.get("origin_wgs"), q.get("destination_wgs")
        if not o or not d:
            raise ProviderError(E_NO_MATCH, "缺少 origin_wgs/destination_wgs 坐标", self.id)
        o_g = wgs2gcj(float(o[0]), float(o[1]))
        d_g = wgs2gcj(float(d[0]), float(d[1]))
        params = {"key": self.k,
                  "origin": f"{o_g[0]:.6f},{o_g[1]:.6f}",
                  "destination": f"{d_g[0]:.6f},{d_g[1]:.6f}",
                  "strategy": "0",                    # 默认（速度优先）
                  "show_fields": "cost,steps"}        # v5：steps 带道路名+几何
        if q.get("plate"):
            params["plate"] = q["plate"]              # v5 原生尾号限行规避
        r = self.http.get(DRIVING, params=params)
        try:
            j = r.json()
        except ValueError:
            raise ProviderError(E_UPSTREAM_FAILURE, f"amap 非 JSON {r.status_code}", self.id)
        _check_status(j, self.id)
        route = j.get("route") or {}
        paths = route.get("paths") or []
        if not paths:
            raise ProviderError(E_NO_MATCH, "高德未返回可行驾车路径", self.id)
        p = paths[0]
        cost = p.get("cost") or {}
        dist_m = float(p.get("distance", 0) or 0)
        dur_s = float(cost.get("duration", p.get("duration", 0)) or 0)
        km = round(dist_m / 1000.0, 1)
        minutes = round(dur_s / 60.0)
        tolls = cost.get("tolls")
        # 官方打车价（route.taxi_cost）优先；缺失时通用估算兜底（明确标注）
        official_taxi = route.get("taxi_cost")
        if official_taxi not in (None, ""):
            taxi, basis = float(official_taxi), "高德官方估价"
        else:
            taxi = round(max(14.0, 8.0 + 2.3 * km)) if km else None
            basis = "通用估算：起步8元+2.3元/km（各城市有差异，非报价）"
        out = {
            "mode": "driving",
            "distance_km": km,
            "duration_min": minutes,
            "tolls_cny": float(tolls) if tolls not in (None, "") else None,
            "toll_distance_km": round(float(cost.get("toll_distance", 0) or 0) / 1000.0, 1)
            or None,
            "traffic_lights": cost.get("traffic_lights"),
            "taxi_estimate_cny": taxi,
            "taxi_estimate_basis": basis,
            "coords_wgs84": {"origin": [o[0], o[1]], "destination": [d[0], d[1]]},
        }

        # ── 路段 + 路线形状（自驾卡 v3：有序干线段占比 + 高速占比）──
        steps = p.get("steps") or []
        road_km: dict[str, float] = {}
        unnamed = 0.0
        segs: list[dict] = []                     # 有序干线段（连续同名合并）
        shape: list[list[float]] = []
        for st in steps:
            rd = (st.get("road_name") or "").strip()
            # v5 步距字段为 step_distance（v3 才叫 distance）
            dist = float(st.get("step_distance") or st.get("distance") or 0) / 1000.0
            if rd:
                road_km[rd] = road_km.get(rd, 0.0) + dist
            else:
                unnamed += dist
            if dist > 0:
                name = _seg_key(st)
                if segs and segs[-1]["name"] == name:
                    segs[-1]["km"] += dist
                else:
                    segs.append({"name": name, "km": dist})
        # v5 steps 无几何——路线形状走 v3 extensions=all 的 polyline（GCJ→WGS）
        calls = 1
        try:
            v3p = {"key": self.k,
                   "origin": f"{o_g[0]:.6f},{o_g[1]:.6f}",
                   "destination": f"{d_g[0]:.6f},{d_g[1]:.6f}",
                   "strategy": "0", "extensions": "all"}
            r3 = self.http.get(DRIVING_V3, params=v3p)
            j3 = r3.json()
            p3 = ((j3.get("route") or {}).get("paths") or [{}])[0]
            polyline = ";".join(
                (st.get("polyline") or "") for st in (p3.get("steps") or []))
            for pair in polyline.split(";"):
                if not pair or "," not in pair:
                    continue
                lon_s, lat_s = pair.split(",")[:2]
                try:
                    lng2, lat2 = gcj2wgs(float(lon_s), float(lat_s))
                    if len(shape) == 0 or abs(shape[-1][0] - lat2) > 0.004 \
                            or abs(shape[-1][1] - lng2) > 0.004:
                        shape.append([round(lat2, 4), round(lng2, 4)])
                except (ValueError, TypeError):
                    continue
            calls = 2
        except Exception:
            shape = []                                # v3 失败：降级无形状
        if len(shape) > 60:                       # 采样压缩到 ≤60 点
            step_n = len(shape) / 60.0
            shape = [shape[int(i * step_n)] for i in range(60)]
        # 夹心合并：同名干线段被 <5km 衔接段（如「龙泉山1号隧道」步）打断时并回首现段
        merged: list[dict] = []
        for s in segs:
            if merged and merged[-1]["name"] == s["name"]:
                merged[-1]["km"] += s["km"]
                continue
            idx = next((i for i, m2 in enumerate(merged)
                        if m2["name"] == s["name"]), None)
            gap = (sum(x["km"] for x in merged[idx + 1:])
                   if idx is not None else None)
            if idx is not None and gap < 5.0:
                merged[idx]["km"] += s["km"]
            else:
                merged.append(s)
        segs = merged
        total_km = dist_m / 1000.0 or sum(s["km"] for s in segs) or 1.0
        segments: list[dict] = []
        other = 0.0
        for s in segs:                            # <5km 衔接段并入「其他」
            if s["km"] >= 5.0:
                segments.append({"name": s["name"], "km": round(s["km"], 1),
                                 "pct": round(s["km"] / total_km * 100, 1)})
            else:
                other += s["km"]
        if other > 0.05:
            segments.append({"name": "其他路段", "km": round(other, 1),
                             "pct": round(other / total_km * 100, 1)})
        out["segments"] = segments
        toll_km_val = float(cost.get("toll_distance", 0) or 0) / 1000.0
        out["highway_pct"] = (round(toll_km_val / total_km * 100, 1)
                              if toll_km_val > 0 and total_km > 0 else None)
        roads = sorted(
            ({"name": k, "km": round(v, 1)} for k, v in road_km.items()),
            key=lambda x: -x["km"])
        main_roads = roads[:6]
        rest = round(sum(x["km"] for x in roads[6:]) + unnamed, 1)
        if roads[6:]:
            main_roads.append({"name": "其他道路", "km": rest})
        out["roads"] = main_roads
        if len(shape) >= 2:
            out["shape"] = shape
        rng = q.get("ev_rated_range_km") or 0
        if rng:
            stops = max(0, -(-int(km) // int(rng)) - 1)
            out["ev_plan"] = {
                "rated_range_km": rng, "charge_stops_needed": stops,
                "note": ("无需中途充电" if stops == 0
                         else f"理论需 {stops} 次中途充电；充电站选址属 Phase 2 POI 细化"),
            }
        return {"data": out, "cost_calls": calls}
