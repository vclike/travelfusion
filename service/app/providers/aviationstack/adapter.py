"""Aviationstack adapter —— 状态备用源（AirLabs 降级链第二位）。

免费档约束（docs/07 §3）：100 请求/月；**仅 HTTP**（HTTPS 需付费，实测http可用）
认证：query_param access_key；错误藏在 HTTP 200 的 error 字段（假-200 坑，已处理）
"""
from __future__ import annotations

from app.core.errors import ProviderError

from datetime import datetime, timezone

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE, E_NO_MATCH,
                            E_QUOTA_LIMIT, E_UPSTREAM_FAILURE)

BASE = "http://api.aviationstack.com/v1"

_STATUS_MAP = {"scheduled": "scheduled", "active": "active", "landed": "landed",
               "cancelled": "cancelled", "incident": "incident", "diverted": "diverted"}




def _iso_utc(s) -> str | None:
    """Aviationstack ISO 带偏移（如 2026-09-29T09:05:00+00:00）→ 规整 UTC Z。"""
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s)).astimezone(timezone.utc)\
            .strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def _normalize(f: dict, want: str) -> dict:
    dep, arr = f.get("departure") or {}, f.get("arrival") or {}
    dep_sched, arr_sched = _iso_utc(dep.get("scheduled")), _iso_utc(arr.get("scheduled"))
    day_offset = 0
    if dep_sched and arr_sched:
        day_offset = max(0, (datetime.fromisoformat(arr_sched.replace("Z", "+00:00"))
                             - datetime.fromisoformat(dep_sched.replace("Z", "+00:00"))).days)
    status_raw = (f.get("flight_status") or "").lower()
    return {
        "flight_no": (f.get("flight") or {}).get("iata") or want,
        "airline_iata": (f.get("airline") or {}).get("iata"),
        "dep_iata": dep.get("iata"), "arr_iata": arr.get("iata"),
        "dep_terminal": dep.get("terminal"), "arr_terminal": arr.get("terminal"),
        "times": {
            "dep": {"scheduled_utc": dep_sched,
                    "estimated_utc": _iso_utc(dep.get("estimated")),
                    "actual_utc": _iso_utc(dep.get("actual"))},
            "arr": {"scheduled_utc": arr_sched,
                    "estimated_utc": _iso_utc(arr.get("estimated")),
                    "actual_utc": _iso_utc(arr.get("actual")),
                    "day_offset": day_offset},
        },
        "duration_min": None,                 # aviationstack 无 duration 字段
        "status": {
            "value": _STATUS_MAP.get(status_raw, f"raw:{status_raw}" if status_raw else "unknown"),
            "dep_delay_min": dep.get("delay"),
            "arr_delay_min": arr.get("delay"),
            "gate": {"dep": dep.get("gate"), "arr": arr.get("gate")},
            "baggage": arr.get("baggage"),
        },
    }


class Adapter:
    id = "aviationstack"
    capabilities = ["flight.status", "airport.db", "airline.db"]

    def __init__(self, api_key: str | None, http: httpx.Client | None = None):
        self.k = api_key
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        r = self.http.get(f"{BASE}/flights",
                          params={"access_key": self.k, "limit": 1})
        j = r.json() if r.status_code == 200 else {}
        return {"status": r.status_code, "ok": not j.get("error")}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "flight.status":
            return self._flight_status(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"aviationstack 未实现 {capability}", self.id)

    def _flight_status(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "aviationstack access_key 未配置", self.id)
        params: dict = {"access_key": self.k, "limit": 1}
        if q.get("flight_no"):
            params["flight_iata"] = str(q["flight_no"]).strip().upper().replace(" ", "")
        else:
            params["dep_iata"] = q.get("origin")
            params["arr_iata"] = q.get("destination")
        r = self.http.get(f"{BASE}/flights", params=params)
        j = r.json() if r.status_code == 200 else {}
        err = j.get("error") or {}
        if err:
            code = str(err.get("code", ""))
            if code in ("101", "invalid_access_key", "missing_access_key"):
                raise ProviderError(E_AUTH_REQUIRED, str(err.get("message", ""))[:120], self.id)
            if code == "104":        # usage_limit（月额度）
                raise ProviderError(E_QUOTA_LIMIT, str(err.get("message", ""))[:120], self.id)
            raise ProviderError(E_UPSTREAM_FAILURE, str(err.get("message", code))[:120], self.id)
        rows = j.get("data") or []
        if q.get("flight_no"):
            want = str(q["flight_no"]).strip().upper().replace(" ", "")
            rows = [f for f in rows
                    if ((f.get("flight") or {}).get("iata") or "").upper() == want]
        if not rows:
            raise ProviderError(E_NO_MATCH, "aviationstack 当日无此航班记录", self.id)
        return {"data": {"flights": [_normalize(f, q.get("flight_no") or "") for f in rows],
                         "coverage_note": "aviationstack 免费层（HTTP，状态/延误备用源）"},
                "cost_calls": 1}
