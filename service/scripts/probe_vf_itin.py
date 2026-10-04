"""VF itineraries 驼峰参数重试 + 价格窗口边缘探测。"""
import asyncio
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)
import yaml  # noqa: E402
from mcp.client.streamable_http import streamablehttp_client  # noqa: E402
from mcp import ClientSession  # noqa: E402

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
                    return (res.content[0].text if res.content else "(empty)")
                except Exception as e:
                    return f"EXC: {str(e)[:200]}"

            print("== searchFlightItineraries 驼峰参数 SHA→TYO 2026-10-08")
            print((await call("searchFlightItineraries", {
                "depCityCode": "SHA", "arrCityCode": "TYO",
                "date": "2026-10-08"}))[:600])
            print()
            print("== searchFlightItineraries SHA→TYO 2026-10-18")
            print((await call("searchFlightItineraries", {
                "depCityCode": "SHA", "arrCityCode": "TYO",
                "date": "2026-10-18"}))[:600])
            print()
            for d in ("2026-10-03", "2026-10-05", "2026-10-15"):
                out = await call("getFlightPriceByCities",
                                 {"dep_city": "SHA", "arr_city": "PEK",
                                  "dep_date": d})
                flag = "有数据" if "暂无数据" not in out else "暂无"
                print(f"getFlightPriceByCities SHA→PEK {d}: {flag} | {out[:120]}")


import os  # noqa: E402

asyncio.run(main())
