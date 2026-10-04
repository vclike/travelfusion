"""route_ground 自驾卡数据质量取证：成都→重庆。"""
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
            res = await s.call_tool("route_ground", {
                "origin": "成都", "destination": "重庆"})
            t = json.loads(res.content[0].text)
            card = t.get("meta", {}).get("card") or {}
            print("type:", card.get("type"))
            print("title:", card.get("title"))
            print("payload:", json.dumps(card.get("payload"),
                                         ensure_ascii=False)[:800])
            print("map:", json.dumps((card.get("payload") or {}).get("map"),
                                     ensure_ascii=False)[:300])
            print("tz/route:", t.get("data", {}).get("mode"),
                  t.get("data", {}).get("distance_km"),
                  t.get("data", {}).get("duration_min"))

asyncio.run(main())
