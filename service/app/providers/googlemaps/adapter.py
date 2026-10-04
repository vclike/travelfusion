"""Google Maps adapter —— 境外地面交通（与高德互补：高德境内 / Google 境外）。

覆盖决策（2026-09-30）：出境游境外段门到门是项目一半场景，高德境外数据不可用。
坐标系：Google 原生 WGS-84 —— 与本服务一致，零转换（对比高德 GCJ-02）。
计费：月免费额度内个人用量足够；key 在 data/keys.yaml googlemaps.key。
API：**Routes API v2**（computeRoutes）——legacy Directions REST 对新项目已停用
（实测 2026-09-30："legacy API not enabled for your project"）。
"""
from __future__ import annotations

from app.core.errors import ProviderError

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_NO_MATCH, E_QUOTA_LIMIT,
                            E_UPSTREAM_FAILURE)

BASE = "https://routes.googleapis.com/directions/v2:computeRoutes"
_FIELDMASK = ("routes.distanceMeters,routes.duration,"
              "routes.legs.steps.transitDetails")

_MODES = {"driving": "DRIVE", "transit": "TRANSIT",
          "walking": "WALK", "bicycling": "BICYCLE"}




class Adapter:
    id = "googlemaps"
    capabilities = ["ground.route.intl"]

    def __init__(self, api_key: str | None, http: httpx.Client | None = None):
        self.k = api_key
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        try:
            self._route({"origin_wgs": [135.7681, 35.0116],
                         "destination_wgs": [135.5023, 34.6937],
                         "mode": "transit", "policy": {}})
            return {"ok": True}
        except ProviderError as e:
            return {"ok": e.code in (E_NO_MATCH,), "hint": e.hint}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "ground.route.intl":
            return self._route(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"googlemaps 未实现 {capability}", self.id)

    def _route(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "googlemaps key 未配置", self.id)
        o, d = q.get("origin_wgs"), q.get("destination_wgs")
        mode = (q.get("mode") or "transit").lower()
        if mode not in _MODES:
            mode = "transit"
        if not o or not d:
            raise ProviderError(E_NO_MATCH, "缺少 origin/destination 坐标", self.id)
        body = {
            "origin": {"location": {"latLng": {"latitude": o[1], "longitude": o[0]}}},
            "destination": {"location": {"latLng": {"latitude": d[1], "longitude": d[0]}}},
            "travelMode": _MODES[mode],
        }
        r = self.http.post(BASE, params={}, json=body, headers={
            "X-Goog-Api-Key": self.k,
            "X-Goog-FieldMask": _FIELDMASK,
            "Content-Type": "application/json"})
        try:
            j = r.json()
        except ValueError:
            raise ProviderError(E_UPSTREAM_FAILURE, f"google 非 JSON {r.status_code}", self.id)
        if r.status_code == 403 or j.get("error", {}).get("status") in (
                "PERMISSION_DENIED",):
            raise ProviderError(E_AUTH_REQUIRED,
                                str(j.get("error", {}).get("message", ""))[:120], self.id)
        if r.status_code == 429:
            raise ProviderError(E_QUOTA_LIMIT, "google 配额限流", self.id)
        if r.status_code >= 400:
            raise ProviderError(E_UPSTREAM_FAILURE,
                                str(j.get("error", {}).get("message",
                                    r.status_code))[:120], self.id)
        routes = j.get("routes") or []
        if not routes:
            raise ProviderError(E_NO_MATCH,
                                f"google 无 {mode} 路线（短线/无该交通方式）", self.id)
        route0 = routes[0]
        km = round(float(route0.get("distanceMeters", 0) or 0) / 1000.0, 1)
        dur = str(route0.get("duration", "0s")).rstrip("s")
        minutes = round(float(dur or 0) / 60.0)
        lines, walk_min = [], 0
        for leg in route0.get("legs") or []:
            for step in (leg.get("steps") or []):
                td = step.get("transitDetails")
                if td:
                    line = td.get("transitLine") or {}
                    name = line.get("short_name") or line.get("name") or ""
                    vehicle = (line.get("vehicle") or {}).get("name", "")
                    lines.append(f"{vehicle} {name}".strip())
                elif (step.get("travel_mode") or "").upper() == "WALK":
                    walk_min += round(float(
                        (step.get("staticDuration") or "0s").rstrip("s") or 0) / 60)
        return {"data": {
            "mode": mode,
            "distance_km": km,
            "duration_min": minutes,
            "transit_lines": lines[:6],
            "walk_min_total": walk_min or None,
            "coords_wgs84": {"origin": [o[0], o[1]], "destination": [d[0], d[1]]},
        }, "cost_calls": 1}
