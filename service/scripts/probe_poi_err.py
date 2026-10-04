"""poi_search 原始错误取证。"""
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
MK = KEYS["mcp_api_key"]


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MK}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("poi_search",
                                    {"keywords": "成都天府国际机场"})
            t = json.loads(res.content[0].text)
            print(json.dumps(t, ensure_ascii=False)[:600])


asyncio.run(main())
