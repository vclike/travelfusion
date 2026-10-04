"""拿 VariFlight aviation 关键工具的 inputSchema。"""
import asyncio
import json
import os

for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)

from mcp import ClientSession  # noqa: E402
from mcp.client.streamable_http import streamablehttp_client  # noqa: E402

KEY = "sk-DxhL1cxavlxrBmiA0eIYjIgktYUscupxhZH0HFTsSVY"
WANT = {"searchFlightsByNumber", "getFlightPriceByCities",
        "searchFlightsByDepArr"}


async def main() -> None:
    async with streamablehttp_client(
            "https://ai.variflight.com/servers/aviation/mcp",
            headers={"X-API-Key": KEY}) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()
            for t in (await s.list_tools()).tools:
                if t.name in WANT:
                    print("=== " + t.name + " ===")
                    print(json.dumps(t.inputSchema, ensure_ascii=False)[:600])


asyncio.run(main())
