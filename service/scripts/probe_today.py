"""时间精度阶梯演示：当日航班（AirLabs 10h 窗口内）三组时刻+延误+双源核验。"""
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

# 今日 9/30 的 CTU→CAN 班次（AirLabs 10h 窗口覆盖当日已飞/待飞）
SAMPLES = ["3U6701", "CZ3414", "3U8735"]


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for flight_no in SAMPLES:
                print(f"== {flight_no}（今日 9/30）")
                try:
                    res = await s.call_tool("flight_status",
                                            {"flight_no": flight_no})
                    t = json.loads(res.content[0].text)
                    if t.get("error"):
                        print(f"   {t['error'].get('code')}: "
                              f"{t['error'].get('hint', '')[:70]}")
                        continue
                    f = (t.get("data") or {}).get("flights") or [{}]
                    f = f[0]
                    times = f.get("times") or {}
                    st = f.get("status") or {}
                    print(f"   sources: {json.dumps(t.get('meta', {}).get('sources'), ensure_ascii=False)}")
                    print(f"   dep: {json.dumps(times.get('dep'), ensure_ascii=False)}")
                    print(f"   arr: {json.dumps(times.get('arr'), ensure_ascii=False)}")
                    print(f"   status={st.get('value')} delay={st.get('dep_delay_min')}min "
                          f"gate={json.dumps(st.get('gate'), ensure_ascii=False)}")
                except Exception as e:
                    print("   failed:", e)

asyncio.run(main())
