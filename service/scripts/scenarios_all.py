"""三场景全链模拟：所有 meta.card 以完整 JSON 打进 stdout（渲染器直取）。"""
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


def dump_cards(tag, t):
    m = t.get("meta") or {}
    cards = []
    if m.get("card"):
        cards.append(m["card"])
    cards.extend(m.get("cards") or [])
    for c in cards:
        print(f"===CARD[{tag}:{c.get('type')}]=== " + json.dumps(c, ensure_ascii=False))


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()

            # ── 场景①：今日 SH→CA N 下午候选，批量核验 ──
            print("### 场景① 单程推荐：flight_status_batch")
            res = await s.call_tool("flight_status_batch", {
                "flight_nos": ["HO1869", "9C6719", "MU5319", "CA8347"],
                "date": ""})
            t1 = json.loads(res.content[0].text)
            b = t1.get("meta") or {}
            print(f"matched={b.get('cards') and len(b['cards'])} "
                  f"skipped={json.dumps(t1.get('data', {}).get('skipped'), ensure_ascii=False)}")
            dump_cards("S1", t1)

            # ── 场景②：成都→广州 往返 + 市区衔接 + 全程卡 ──
            print("### 场景② 往返行程：itinerary_plan（腿数据=班期知识+估算衔接）")
            legs2 = [
                {"mode": "drive", "from": "成都", "to": "成都天府国际机场",
                 "depart": "2026-10-02T06:30:00+08:00",
                 "arrive": "2026-10-02T07:30:00+08:00"},
                {"mode": "flight", "from": "成都天府国际机场", "to": "广州白云国际机场",
                 "depart": "2026-10-02T08:30:00+08:00",
                 "arrive": "2026-10-02T11:00:00+08:00"},
                {"mode": "drive", "from": "广州白云国际机场", "to": "广州",
                 "depart": "2026-10-02T11:30:00+08:00",
                 "arrive": "2026-10-02T12:30:00+08:00"},
                {"mode": "drive", "from": "广州", "to": "广州白云国际机场",
                 "depart": "2026-10-04T18:30:00+08:00",
                 "arrive": "2026-10-04T19:30:00+08:00"},
                {"mode": "flight", "from": "广州白云国际机场", "to": "成都天府国际机场",
                 "depart": "2026-10-04T20:30:00+08:00",
                 "arrive": "2026-10-04T23:10:00+08:00"},
                {"mode": "drive", "from": "成都天府国际机场", "to": "成都",
                 "depart": "2026-10-04T23:40:00+08:00",
                 "arrive": "2026-10-05T00:40:00+08:00"},
            ]
            res = await s.call_tool("itinerary_plan", {"legs": legs2})
            t2 = json.loads(res.content[0].text)
            dump_cards("S2", t2)
            print("S2 notices:", json.dumps(
                (t2.get("meta", {}).get("card", {}).get("notices")),
                ensure_ascii=False))

            # ── 场景③：成都→西安 三天两夜自驾 ──
            print("### 场景③ 自驾西安：route_ground（v2 路线形状+路段）")
            res = await s.call_tool("route_ground",
                                    {"origin": "成都", "destination": "西安"})
            t3 = json.loads(res.content[0].text)
            dump_cards("S3-route", t3)
            d3 = t3.get("data") or {}
            print(f"roads={len(d3.get('roads') or [])} "
                  f"shape={len(d3.get('shape') or [])}pts "
                  f"{d3.get('distance_km')}km/{d3.get('duration_min')}min")

            print("### 场景③ 天气：weather_context 西安")
            res = await s.call_tool("weather_context",
                                    {"location": "西安", "date": "2026-10-02"})
            try:
                t3w = json.loads(res.content[0].text)
                dump_cards("S3-weather", t3w)
            except Exception as e:
                print("weather raw content:",
                      repr([c.text[:200] if hasattr(c, 'text') else str(c)
                            for c in res.content]))

            print("### 场景③ 全程：itinerary_plan 三天两夜")
            legs3 = [
                {"mode": "drive", "from": "成都", "to": "西安",
                 "depart": "2026-10-02T07:30:00+08:00",
                 "arrive": "2026-10-02T16:30:00+08:00"},
                {"mode": "drive", "from": "西安", "to": "西安",
                 "depart": "2026-10-03T09:00:00+08:00",
                 "arrive": "2026-10-03T18:00:00+08:00"},
                {"mode": "drive", "from": "西安", "to": "成都",
                 "depart": "2026-10-04T09:00:00+08:00",
                 "arrive": "2026-10-04T18:00:00+08:00"},
            ]
            res = await s.call_tool("itinerary_plan", {"legs": legs3})
            t3i = json.loads(res.content[0].text)
            dump_cards("S3-itin", t3i)

asyncio.run(main())
