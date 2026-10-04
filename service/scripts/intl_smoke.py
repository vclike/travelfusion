"""国际+境内 route_ground 冒烟。"""
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

CASES = [
    ("大阪", "东京", "driving"),
    ("曼谷", "芭提雅", "driving"),
    ("东京", "大阪", "transit"),        # Routes API transit 覆盖有限→诚实 NO_MATCH
    ("成都", "乐山", "auto"),           # CN 回归（高德）
]


async def main() -> None:
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()
            for o, d, m in CASES:
                res = await s.call_tool("route_ground",
                                        {"origin": o, "destination": d, "mode": m})
                try:
                    j = json.loads(res.content[0].text)
                    dd = j.get("data") or {}
                    print(f"{o}→{d} [{dd.get('mode')}]: "
                          f"{dd.get('distance_km')}km {dd.get('duration_min')}min "
                          f"{dd.get('transit_lines') or ''}"
                          f"{('err=' + j['error']['code']) if j.get('error') else ''}")
                except Exception:                         # noqa: BLE001
                    print(f"{o}→{d}: {res.content[0].text[:150]}")


asyncio.run(main())
