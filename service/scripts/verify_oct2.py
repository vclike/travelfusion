"""三源交叉核验：携程班期 vs travelfusion(aviationstack/airlabs) 10-02 班次。"""
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
MCP_KEY = KEYS["mcp_api_key"]
SAMPLES = [("3U6701", "08:00 TFU→10:25 CAN"),
           ("CZ3414", "09:00 CTU→11:40 CAN"),
           ("3U8735", "16:30 CTU→19:15 CAN")]


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for flight_no, sched in SAMPLES:
                print(f"== {flight_no}（携程班期: {sched}）")
                try:
                    res = await s.call_tool("flight_status", {
                        "flight_no": flight_no, "date": "2026-10-02"})
                    t = json.loads(res.content[0].text)
                    if t.get("error"):
                        print(f"   error: {t['error'].get('code')} "
                              f"{t['error'].get('hint', '')[:60]}")
                        continue
                    f = (t.get("data") or {}).get("flights") or [{}]
                    f = f[0]
                    times = f.get("times") or {}
                    st = f.get("status") or {}
                    print(f"   源: {json.dumps(t.get('meta', {}).get('sources'), ensure_ascii=False)}")
                    print(f"   dep_utc: {json.dumps(times.get('dep'), ensure_ascii=False)}")
                    print(f"   arr_utc: {json.dumps(times.get('arr'), ensure_ascii=False)}")
                    print(f"   status: {st.get('value')} delay={st.get('dep_delay_min')}")
                except Exception as e:
                    print("   failed:", e)

asyncio.run(main())
