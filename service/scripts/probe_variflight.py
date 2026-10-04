"""VariFlight MCP 端点/钥匙 探测矩阵：2 keys × 2 servers。"""
import asyncio
import os

for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)

from mcp import ClientSession  # noqa: E402
from mcp.client.streamable_http import streamablehttp_client  # noqa: E402

KEYS = {
    "sk-DxhL…(新)": "sk-DxhL1cxavlxrBmiA0eIYjIgktYUscupxhZH0HFTsSVY",
    "sk_phone_…(旧)": "sk_phone_mcuc4wztmf163leudd9g6g8zfntpu64x",
}
SERVERS = ["aviation", "tripmatch"]


async def probe(server: str, key_name: str, key: str) -> None:
    url = f"https://ai.variflight.com/servers/{server}/mcp"
    try:
        async with streamablehttp_client(
                url, headers={"X-API-Key": key}, timeout=15) as (read, write, _):
            async with ClientSession(read, write) as s:
                init = await s.initialize()
                info = init.serverInfo.name if init and init.serverInfo else "?"
                tools = (await s.list_tools()).tools
                print(f"OK   {server:9s} {key_name:14s} serverInfo={info} "
                      f"tools={[t.name for t in tools]}")
    except Exception as e:                                # noqa: BLE001
        msg = str(e).replace("\n", " ")[:110]
        print(f"FAIL {server:9s} {key_name:14s} {msg}")


async def main() -> None:
    for server in SERVERS:
        for name, key in KEYS.items():
            await probe(server, name, key)


asyncio.run(main())
