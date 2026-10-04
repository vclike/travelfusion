"""MCP 客户端终极冒烟：带 API key 完整握手 → 列工具 → 真调用 → 401 负向验证。"""
import asyncio
import os
import sys
from pathlib import Path

for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)

import httpx  # noqa: E402
import yaml  # noqa: E402

from mcp import ClientSession  # noqa: E402
from mcp.client.streamable_http import streamablehttp_client  # noqa: E402

URL = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.100.1:8900/mcp"
KEYS = yaml.safe_load((Path(__file__).resolve().parent.parent
                       / "data" / "keys.yaml").read_text(encoding="utf-8"))
MCP_KEY = KEYS["mcp_api_key"]


async def main() -> None:
    # 负向：无 key 必须 401
    r = httpx.post(URL, json={"jsonrpc": "2.0", "id": 0, "method": "initialize",
                              "params": {}}, timeout=10)
    print(f"NO-KEY: {r.status_code} (期望 401)")
    assert r.status_code == 401, "无 key 未被拒绝——鉴权未生效！"

    async with streamablehttp_client(URL, headers={"X-API-Key": MCP_KEY}) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("TOOLS:", [t.name for t in tools])
            r = await s.call_tool("flight_status", {"flight_no": "CA165"})
            print("FLIGHT_STATUS ok:", "error" not in r.content[0].text[:80])
            r2 = await s.call_tool("route_ground",
                                   {"origin": "成都", "destination": "乐山",
                                    "ev_rated_range_km": 400})
            print("ROUTE_GROUND ok:", "distance_km" in r2.content[0].text)
            r3 = await s.call_tool("weather_context", {"location": "曼谷",
                                                       "date": "2026-10-03"})
            print("WEATHER ok:", "forecast" in r3.content[0].text or "layer" in r3.content[0].text)
            r4 = await s.call_tool("quota_status", {})
            print("QUOTA ok:", "providers" in r4.content[0].text)


asyncio.run(main())
