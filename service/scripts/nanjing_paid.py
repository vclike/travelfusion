"""成都→南京 付费校准（用户已同意 A 方案）。"""
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


async def main() -> None:
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": KEYS["mcp_api_key"]}) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()
            res = await s.call_tool("flight_price", {
                "origin": "成都", "destination": "南京",
                "date": "2026-11-17",
                "paid_calibrate": True, "confirm_spend": True})
            t = json.loads(res.content[0].text)
            print(json.dumps(t, ensure_ascii=False)[:1200])


asyncio.run(main())
