"""VF MCP 直探：getFlightPriceByCities 国内 vs 国际 + searchFlightItineraries 国际。"""
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
vf = KEYS.get("variflight") or {}
VF_KEY = vf.get("api_key") or vf.get("key")
VF_URL = vf.get("url") or "https://ai.variflight.com/servers/aviation/mcp"


async def main():
    async with streamablehttp_client(
            VF_URL, headers={"X-API-Key": VF_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()

            async def call(name, args):
                try:
                    res = await s.call_tool(name, args)
                    txt = res.content[0].text if res.content else "(empty)"
                    return txt[:300]
                except Exception as e:
                    return f"EXC: {e}"

            print("== 国内 SHA→PEK getFlightPriceByCities 2026-10-08")
            print((await call("getFlightPriceByCities",
                              {"dep_city": "SHA", "arr_city": "PEK",
                               "dep_date": "2026-10-08"}))[:260])
            print("== 国际 SHA→TYO getFlightPriceByCities 2026-10-08")
            print((await call("getFlightPriceByCities",
                              {"dep_city": "SHA", "arr_city": "TYO",
                               "dep_date": "2026-10-08"}))[:260])
            print("== 国际 SHA→TYO searchFlightItineraries 2026-10-08")
            print((await call("searchFlightItineraries",
                              {"dep_city": "SHA", "arr_city": "TYO",
                               "date": "2026-10-08"}))[:400])


asyncio.run(main())
