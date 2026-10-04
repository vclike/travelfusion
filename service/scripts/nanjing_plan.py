"""成都→南京 5 天（11 月下半旬）规划数据拉取。"""
import asyncio
import json
import os
from pathlib import Path

for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)

import yaml  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.streamable_http import streamablehttp_client  # noqa: E402

KEYS = yaml.safe_load((Path(__file__).resolve().parent.parent
                       / "data" / "keys.yaml").read_text(encoding="utf-8"))
MCP_KEY = KEYS["mcp_api_key"]


def show(tag: str, j: dict, keys_to_show=None) -> None:
    if j.get("error"):
        print(f"[{tag}] err={j['error']['code']}  {j['error']['hint'][:80]}")
        if j.get("meta", {}).get("attempted"):
            print("   attempted:", json.dumps(j["meta"]["attempted"],
                                              ensure_ascii=False))
        return
    d = j.get("data") or {}
    print(f"[{tag}]", json.dumps(d, ensure_ascii=False)[:500])
    m = j.get("meta") or {}
    if m.get("baseline_90d"):
        print("   baseline:", json.dumps(m["baseline_90d"], ensure_ascii=False))
    if m.get("cache"):
        print("   cache:", m["cache"])


async def main() -> None:
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()

            j = _j = await s.call_tool("flight_price", {
                "origin": "成都", "destination": "南京",
                "date": "2026-11-17", "trip_type": "personal"})
            show("1 flight_price CTU→NKG", json.loads(j.content[0].text))

            j = await s.call_tool("weather_context",
                                  {"location": "南京", "date": "2026-11-20"})
            show("2 weather 南京 11-20", json.loads(j.content[0].text))

            j = await s.call_tool("route_ground",
                                  {"origin": "南京", "destination": "扬州",
                                   "mode": "driving"})
            show("3 route 南京→扬州", json.loads(j.content[0].text))

            j = await s.call_tool("quota_status", {})
            qs = json.loads(j.content[0].text)
            for p in qs["data"]["providers"]:
                q = p.get("quota") or {}
                if q.get("remaining_free") is not None:
                    print(f"[quota] {p['provider']}: {q.get('remaining_free')} left")


asyncio.run(main())
