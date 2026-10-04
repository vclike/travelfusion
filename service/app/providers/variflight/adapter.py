"""飞常准 adapter —— Phase 3 付费校准源（tier=paid，永不自动调用）。

官方 Aviation MCP（streamable HTTP）：https://ai.variflight.com/servers/aviation/mcp
鉴权：X-API-Key（sk- 形态，两把 key 均实测可用，2026-09-30）。
本 adapter 用 httpx 裸实现 MCP 三步握手（initialize→initialized→tools/call），
保持 dispatch 全同步链路。默认工具：
  flight.status → searchFlightsByNumber {fnum, date}
  flight.price  → getFlightPriceByCities {dep_city, arr_city, dep_date}
输出：raw 透传（Phase 3 v1），带 source 标注；正式归一化等首批真实响应定形。
"""
from __future__ import annotations

from app.core.errors import ProviderError

import datetime as _dt

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE,
                            E_NO_MATCH, E_QUOTA_LIMIT, E_UPSTREAM_FAILURE)

BASE = "https://ai.variflight.com/servers/aviation/mcp"
_PROTO = "2025-03-26"




def _parse_body(r: httpx.Response) -> dict:
    """MCP streamable 响应兼容 JSON 与 SSE 两种载体。"""
    ct = (r.headers.get("content-type") or "").lower()
    if r.status_code in (401, 403):
        raise ProviderError(E_AUTH_REQUIRED, f"variflight 鉴权失败 {r.status_code}", "variflight")
    if r.status_code == 429:
        raise ProviderError(E_QUOTA_LIMIT, "variflight 限流", "variflight")
    if r.status_code >= 400:
        raise ProviderError(E_UPSTREAM_FAILURE, f"variflight {r.status_code}", "variflight")
    text = r.text
    if "text/event-stream" in ct:
        for line in reversed(text.splitlines()):
            if line.startswith("data:"):
                try:
                    return json_loads(line[5:].strip())
                except Exception:                     # noqa: BLE001
                    break
        raise ProviderError(E_UPSTREAM_FAILURE, "variflight SSE 无有效 data", "variflight")
    try:
        return json_loads(text)
    except Exception as e:                            # noqa: BLE001
        raise ProviderError(E_UPSTREAM_FAILURE, f"variflight 非 JSON: {e}", "variflight")


def json_loads(s: str) -> dict:
    import json
    return json.loads(s)


class Adapter:
    id = "variflight"
    capabilities = ["flight.status", "flight.price"]

    def __init__(self, api_key: str | None, http: httpx.Client | None = None):
        self.k = api_key
        self.http = http or httpx.Client(timeout=30)

    def probe(self) -> dict:
        try:
            self._session()
            return {"ok": True}
        except ProviderError as e:
            return {"ok": False, "hint": e.hint}

    def _session(self) -> str | None:
        """initialize → Mcp-Session-Id（无状态服务端可能不返回 → None 可接受）。"""
        r = self.http.post(BASE, headers={"X-API-Key": self.k,
                                          "Accept": "application/json, text/event-stream"},
                           json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                 "params": {"protocolVersion": _PROTO, "capabilities": {},
                                            "clientInfo": {"name": "travelfusion",
                                                           "version": "0.2.0"}}})
        j = _parse_body(r)
        if j.get("id") != 1 or "result" not in j:
            raise ProviderError(E_UPSTREAM_FAILURE, f"initialize 异常 {str(j)[:100]}", "variflight")
        sid = r.headers.get("mcp-session-id") or (j.get("result") or {}).get("sessionId")
        if sid:
            self.http.post(BASE, headers={"X-API-Key": self.k, "mcp-session-id": sid,
                                          "Accept": "application/json, text/event-stream"},
                           json={"jsonrpc": "2.0", "method": "notifications/initialized"})
        return sid

    def _call_tool(self, name: str, arguments: dict) -> dict:
        try:
            sid = self._session()
        except ProviderError as e:
            if e.code not in (E_UPSTREAM_FAILURE,):
                raise
            sid = None                       # 无状态端点：initialize 缺头不算致命
        headers = {"X-API-Key": self.k,
                   "Accept": "application/json, text/event-stream"}
        if sid:
            headers["mcp-session-id"] = sid
        r = self.http.post(BASE, headers=headers,
                           json={"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                 "params": {"name": name, "arguments": arguments}})
        j = _parse_body(r)
        result = j.get("result") or {}
        if result.get("isError"):
            raise ProviderError(E_UPSTREAM_FAILURE,
                                str(result.get("content"))[:150], "variflight")
        contents = result.get("content") or []
        texts = [c.get("text", "") for c in contents if c.get("type") == "text"]
        return {"text": "\n".join(texts), "structured": result.get("structuredContent")}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "flight.status":
            return self._status(query)
        if capability == "flight.price":
            return self._price(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"variflight 未实现 {capability}", self.id)

    def _status(self, q: dict) -> dict:
        fnum = str(q.get("flight_no") or "").strip().upper().replace(" ", "")
        if not fnum:
            raise ProviderError(E_NO_MATCH, "缺少航班号", self.id)
        args: dict = {"fnum": fnum}
        # VF 工具要求显式日期；缺省=今天（北京时间口径按其服务端为准）
        args["date"] = q.get("date") or _dt.date.today().strftime("%Y-%m-%d")
        out = self._call_tool("searchFlightsByNumber", args)
        return {"data": {"flights": [{"source": "variflight",
                                      "flight_no": fnum,
                                      "raw_text": out["text"][:4000],
                                      "structured": out["structured"]}],
                         "coverage_note": "variflight 官方 MCP（付费校准源，raw 透传）"},
                "cost_calls": 1}

    def _price(self, q: dict) -> dict:
        dep, arr = q.get("origin_code"), q.get("destination_code")
        if not dep or not arr:
            raise ProviderError(E_NO_MATCH, "缺少城市码", self.id)
        args: dict = {"dep_city": dep, "arr_city": arr}
        if q.get("date"):
            args["dep_date"] = q["date"]
        out = self._call_tool("getFlightPriceByCities", args)
        # 空数据（如日期超出价格窗口 ~45 天）→ 诚实 NO_MATCH 而非 success 透传
        if "'error_code': 10" in out["text"] or "暂无数据" in out["text"]:
            raise ProviderError(
                E_NO_MATCH,
                "飞常准该日期暂无价格数据（通常日期超出 ~45 天窗口，临近再校准）", self.id)
        prices = _normalize_vf_prices(out["text"])
        if not prices:
            raise ProviderError(E_NO_MATCH, "飞常准返回无可售舱位", self.id)
        return {"data": {"price_type": "calibrated",
                         "note": "variflight 官方票价（付费校准层）",
                         "prices": prices},
                "cost_calls": 1}


def _normalize_vf_prices(text: str) -> list[dict]:
    """VF MCP 文本（Python dict repr）→ 与 TP 同构的 prices 列表。"""
    import ast
    import re
    from datetime import datetime, timezone, timedelta
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        data = ast.literal_eval(m.group(0)).get("data") or []
    except (ValueError, SyntaxError):
        return []
    cst = timezone(timedelta(hours=8))
    prices = []
    for f in data if isinstance(data, list) else []:
        dep_epoch = f.get("flightdeptimeplandate")
        dep_iso = (datetime.fromtimestamp(int(dep_epoch), cst)
                   .strftime("%Y-%m-%dT%H:%M:%S+08:00")
                   if dep_epoch else None)
        for c in f.get("cabins") or []:
            prices.append({
                "amount": c.get("price"),
                "currency": "CNY",
                "airline_iata": (f.get("flightno") or "")[:2],
                "flight_number": f.get("flightno"),
                "departure_at": dep_iso,
                "cabin_class": c.get("classname"),
                "cabin_code": c.get("cabincode"),
                "discount": c.get("discount"),
                "seatnum": c.get("seatnum"),
                "dep_terminal": f.get("flighthterminal"),
                "arr_terminal": f.get("flightterminal"),
                "stop_city": (f.get("stopcityname") or None)
                    if f.get("stopflag") else None,
                "meal": f.get("food") or None,
                "aircraft": f.get("generic") or None,
                "distance_km": f.get("distance"),
                "price_type": "calibrated",
                "expires_at": None,
            })
    return prices
