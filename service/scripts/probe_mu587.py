"""取证：aviationstack 原始报文 vs 本服务归一化输出（MU587）。"""
import asyncio
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)

import yaml
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

KEYS = yaml.safe_load(open("data/keys.yaml", encoding="utf-8"))
_ap = (KEYS.get("providers") or {}).get("aviationstack") or KEYS.get("aviationstack")
AS_KEY = _ap.get("access_key") if isinstance(_ap, dict) else _ap
MCP_KEY = KEYS["mcp_api_key"]

print("== 1) aviationstack 原始报文（MU587）==")
url = (f"http://api.aviationstack.com/v1/flights?access_key={AS_KEY}"
       f"&flight_iata=MU587&limit=3")
try:
    raw = json.load(urllib.request.urlopen(url, timeout=20))
    for f in (raw.get("data") or [])[:3]:
        dep, arr = f.get("departure") or {}, f.get("arrival") or {}
        print(f"flight_date={f.get('flight_date')} status={f.get('flight_status')}")
        print(f"  dep: airport={dep.get('airport')} scheduled={dep.get('scheduled')!r} tz={dep.get('timezone')}")
        print(f"  arr: airport={arr.get('airport')} scheduled={arr.get('scheduled')!r} tz={arr.get('timezone')}")
except Exception as e:
    print("aviationstack probe failed:", e)

print()
print("== 2) 本服务 flight_status 归一化输出（MU587）==")

async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("flight_status", {"flight_no": "MU587"})
            t = json.loads(res.content[0].text)
            times = ((t.get("data") or {}).get("flights") or [{}])[0].get("times")
            print("times:", json.dumps(times, ensure_ascii=False))
            print("source:", json.dumps(t.get("meta", {}).get("sources"), ensure_ascii=False))

asyncio.run(main())
