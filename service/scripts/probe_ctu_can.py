"""成都→广州 2026-10-02：flight_price（VF 校准源带时刻表）全量取证。"""
import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)
import yaml
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

KEYS = yaml.safe_load(open("data/keys.yaml", encoding="utf-8"))
MCP_KEY = KEYS["mcp_api_key"]


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("flight_price", {
                "origin": "成都", "destination": "广州",
                "date": "2026-10-02", "trip_type": "personal"})
            t = json.loads(res.content[0].text)
            card = t.get("meta", {}).get("card") or {}
            rows = (card.get("payload") or {}).get("prices") or []
            print(f"rows: {len(rows)}")
            for row in rows:
                print(json.dumps(row, ensure_ascii=False))
            print("notices:", json.dumps(card.get("notices"), ensure_ascii=False))
            print("sources:", json.dumps(
                t.get("meta", {}).get("sources"), ensure_ascii=False))
            print("cost:", json.dumps(t.get("meta", {}).get("cost"),
                                      ensure_ascii=False))
            print("error:", t.get("error"))

asyncio.run(main())
