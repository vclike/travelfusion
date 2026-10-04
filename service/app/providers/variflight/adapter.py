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

import ast
import datetime as _dt

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE,
                            E_NO_MATCH, E_QUOTA_LIMIT, E_UPSTREAM_FAILURE)
from app.core.tzcn import today_cn  # B3：北京时间口径

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

    @staticmethod
    def _parse_flight_details(text: str) -> dict | None:
        """从 MCP 文本载体提取 'Flight details: {...}' dict（受限 literal_eval，
        不使用 eval；解析失败返回 None，由上层诚实标注而非猜字段）。"""
        marker = "Flight details:"
        i = text.find(marker)
        if i < 0:
            return None
        try:
            payload = ast.literal_eval(text[i + len(marker):].strip())
        except (ValueError, SyntaxError, MemoryError, RecursionError):
            return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _iso_local(plan: str, tz_seconds) -> str | None:
        """'YYYY-MM-DD HH:MM:SS' + 上游时区秒偏移 → ISO8601（无时区假设）。"""
        try:
            dt = _dt.datetime.strptime(str(plan).strip(), "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=_dt.timezone(
                _dt.timedelta(seconds=int(tz_seconds)))).isoformat()
        except (ValueError, TypeError, OverflowError):
            return None

    def _status(self, q: dict) -> dict:
        fnum = str(q.get("flight_no") or "").strip().upper().replace(" ", "")
        if not fnum:
            raise ProviderError(E_NO_MATCH, "缺少航班号", self.id)
        args: dict = {"fnum": fnum}
        # VF 工具要求显式日期；缺省=今天（北京时间口径按其服务端为准）
        args["date"] = q.get("date") or today_cn()
        out = self._call_tool("searchFlightsByNumber", args)
        row: dict = {"source": "variflight", "flight_no": fnum,
                     "raw_text": out["text"][:4000],
                     "structured": out["structured"], "parse_ok": False}
        # 2026-10-02 修复：付费结果必须在 provider 边界归一化——此前 raw 透传
        # 导致上层航线过滤误杀真实航班（"航线不符"）。
        payload = self._parse_flight_details(out["text"])
        items = (payload or {}).get("data")
        if isinstance(items, list) and items and isinstance(items[0], dict):
            d0 = items[0]
            row.update({
                "parse_ok": True,
                "dep_iata": str(d0.get("FlightDepcode") or "").strip().upper() or None,
                "arr_iata": str(d0.get("FlightArrcode") or "").strip().upper() or None,
                "airline_name": d0.get("FlightCompany") or None,
                "dep_terminal": d0.get("FlightHTerminal") or None,
                "arr_terminal": d0.get("FlightTerminal") or None,
                "aircraft": d0.get("ftype") or None,
                "state": d0.get("FlightState") or None})
            dep_plan = d0.get("FlightDeptimePlanDate")
            arr_plan = d0.get("FlightArrtimePlanDate")
            duration = d0.get("FlightDuration")
            row["times"] = {
                "dep": {"scheduled_local": dep_plan or None,
                        "scheduled_utc": self._iso_local(dep_plan,
                                                         d0.get("org_timezone"))},
                "arr": {"scheduled_local": arr_plan or None,
                        "scheduled_utc": self._iso_local(arr_plan,
                                                         d0.get("dst_timezone"))},
                "duration_min": int(duration)
                if str(duration or "").isdigit() else None,
                "tz_source": "upstream org/dst_timezone"}
        return {"data": {"flights": [row],
                         "coverage_note": "variflight 官方 MCP（付费校准源；"
                                          "已按上游时区归一化，raw 保留）"},
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
