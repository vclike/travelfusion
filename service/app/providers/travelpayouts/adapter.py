"""Travelpayouts adapter —— 国际机票免费缓存价（价格梯队 L1 唯一免费源）。

Data API: api.travelpayouts.com；认证 header X-Access-Token
/v1/prices/cheap 返回缓存价（价格语义 = cached，带 expires_at）
今日已实测：success=true + 真实数据返回。
"""
from __future__ import annotations

from app.core.errors import ProviderError

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE, E_NO_MATCH,
                            E_UPSTREAM_FAILURE)




BASE = "https://api.travelpayouts.com"


class Adapter:
    id = "travelpayouts"
    capabilities = ["flight.price", "price.calendar"]

    def __init__(self, api_key: str | None, http: httpx.Client | None = None):
        self.k = api_key
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        r = self.http.get(f"{BASE}/v1/prices/cheap",
                          params={"origin": "MOW", "destination": "LED", "token": self.k})
        return {"status": r.status_code, "ok": r.status_code == 200}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "flight.price":
            return self._cheap(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"travelpayouts 未实现 {capability}", self.id)

    def _cheap(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "travelpayouts token 未配置", self.id)
        params = {"origin": q["origin_code"], "destination": q["destination_code"],
                  "currency": q.get("currency", "CNY"), "token": self.k}
        if q.get("date"):                      # 具体日 → cheapest_tickets
            params["depart_date"] = q["date"]
        r = self.http.get(f"{BASE}/v1/prices/cheap", params=params)
        if r.status_code in (401, 403):
            raise ProviderError(E_AUTH_REQUIRED, f"travelpayouts 鉴权失败 {r.status_code}", self.id)
        try:
            j = r.json()
        except ValueError:
            raise ProviderError(E_UPSTREAM_FAILURE, f"非 JSON {r.status_code}", self.id)
        if not j.get("success"):
            raise ProviderError(E_UPSTREAM_FAILURE, str(j)[:120], self.id)
        data = j.get("data") or {}
        if not data:
            raise ProviderError(E_NO_MATCH, "该 OD 无缓存价（可能航线过冷或首查）", self.id)
        currency = j.get("currency", q.get("currency", "CNY"))
        prices, expires_min = [], None
        for dest, tiers in data.items():
            for tier_key, t in (tiers or {}).items():
                prices.append({
                    "destination_code": dest, "tier": tier_key,
                    "airline_iata": t.get("airline"),
                    "flight_number": t.get("flight_number"),
                    "departure_at": t.get("departure_at"),
                    "return_at": t.get("return_at"),
                    "amount": t.get("price"),
                    "currency": currency,
                    "cabin_class": "economy",     # TP 缓存价基本为经济向参考价
                    "price_type": "cached",
                    "expires_at": t.get("expires_at"),
                })
                if t.get("expires_at"):
                    expires_min = min(expires_min or t["expires_at"], t["expires_at"])
        if not prices:
            raise ProviderError(E_NO_MATCH, "无有效价格行", self.id)
        return {"data": {"price_type": "cached",
                         "note": "缓存参考价：经济向、非可成交价；精确价走付费校准",
                         "prices": prices},
                "cost_calls": 1}
