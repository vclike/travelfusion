"""付费校准冒烟：CONFIRM_REQUIRED 负向 → confirm_spend 放行 → 真实飞常准数据。"""
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
URL = "http://192.168.100.1:8900/mcp"


async def main() -> None:
    async with streamablehttp_client(URL, headers={"X-API-Key": MCP_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            # 0.5 元/次 < 确认阈值 3 元 → 直接放行（闸门逻辑由单测覆盖 5 元场景）
            r1 = await s.call_tool("flight_status",
                                   {"flight_no": "CA165",
                                    "paid_calibrate": True,
                                    "confirm_spend": True})
            t1 = json.loads(r1.content[0].text)
            src = t1.get("meta", {}).get("sources", [])
            print("paid source:", [x.get("provider") for x in src])
            print("paid_cny:", t1.get("meta", {}).get("cost", {}).get("paid_cny"))
            vf = (t1.get("data", {}).get("flights") or [{}])[0]
            print("vf raw head:", (vf.get("raw_text") or "")[:300])
            return


asyncio.run(main())
