"""OpenSky adapter —— ADS-B 观测复核（flight_verify 的观测层）。

已实测（2026-09-29）：OAuth client_credentials ✓；ZBAA 包围盒有观测（境内覆盖确认）。
观测语义：best-effort——未捕获 = ADS-B 覆盖缺口 ≠ 航班异常（诚实不变量，docs/07 §4）。
"""
from __future__ import annotations

from app.core.errors import ProviderError

import time

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE, E_NO_MATCH,
                            E_QUOTA_LIMIT, E_UPSTREAM_FAILURE)

TOKEN_URL = ("https://auth.opensky-network.org/auth/realms/opensky-network/"
             "protocol/openid-connect/token")
STATES = "https://opensky-network.org/api/states/all"

_TOKEN_CACHE: dict[str, tuple[str, float]] = {}   # client_id → (token, expiry)




def _norm_state(s: list) -> dict:
    return {"icao24": s[0], "callsign": (s[1] or "").strip(), "origin_country": s[2],
            "lon": s[5], "lat": s[6], "baro_altitude_m": s[7], "on_ground": s[8],
            "velocity_ms": s[9], "true_track_deg": s[10],
            "vertical_rate_ms": s[11], "geo_altitude_m": s[13],
            "last_contact_epoch": s[4]}


class Adapter:
    id = "opensky"
    capabilities = ["flight.observe"]

    def __init__(self, api_key, http: httpx.Client | None = None):
        # dispatch 对 oauth2 源传入完整凭据块 {client_id, client_secret}
        self.k = api_key if isinstance(api_key, dict) else {}
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        try:
            self._token()
            return {"ok": True}
        except ProviderError as e:
            return {"ok": False, "hint": e.hint}

    def _token(self) -> str:
        cid = (self.k or {}).get("client_id")
        sec = (self.k or {}).get("client_secret")
        if not cid or not sec:
            raise ProviderError(E_AUTH_REQUIRED, "opensky client_id/secret 未配置", self.id)
        cached = _TOKEN_CACHE.get(cid)
        if cached and cached[1] > time.time() + 30:
            return cached[0]
        r = self.http.post(TOKEN_URL, data={
            "grant_type": "client_credentials", "client_id": cid, "client_secret": sec})
        if r.status_code != 200:
            raise ProviderError(E_AUTH_REQUIRED, f"opensky token {r.status_code}", self.id)
        j = r.json()
        tok = j["access_token"]
        _TOKEN_CACHE[cid] = (tok, time.time() + int(j.get("expires_in", 1800)))
        return tok

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "flight.observe":
            return self._observe(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"opensky 未实现 {capability}", self.id)

    def _observe(self, q: dict) -> dict:
        callsign = str(q.get("callsign") or "").strip().upper()
        if not callsign:
            raise ProviderError(E_NO_MATCH,
                                "缺少 callsign（ICAO 呼号，通常=flight_icao）", self.id)
        tok = self._token()
        r = self.http.get(STATES, params={"callsign": callsign},
                          headers={"Authorization": f"Bearer {tok}"})
        if r.status_code == 429:
            raise ProviderError(E_QUOTA_LIMIT, "opensky credits 限流", self.id)
        if r.status_code >= 400:
            raise ProviderError(E_DATA_UNAVAILABLE,
                                f"opensky states {r.status_code}"
                                f"（如不支持 callsign 过滤则需机场坐标 bbox）", self.id)
        states = (r.json() or {}).get("states") or []
        hits = [_norm_state(s) for s in states
                if (s[1] or "").strip().upper().startswith(callsign)]
        if not hits:
            return {"data": {"observed": False, "aircraft": [],
                             "note": "观测层未捕获（ADS-B 覆盖缺口 ≠ 航班异常）"},
                    "cost_calls": 1}
        return {"data": {"observed": True, "aircraft": hits,
                         "note": "观测与计划层来源独立（ADS-B vs 数据库）"},
                "cost_calls": 1}
