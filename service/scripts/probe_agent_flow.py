"""修复后的 agent 配合全链验证：weather / itinerary(纯市内多日) / recommend。"""
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
MK = KEYS["mcp_api_key"]


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MK}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()

            res = await s.call_tool("weather_context",
                                    {"location": "成都", "date": "2026-10-02"})
            t = json.loads(res.content[0].text)
            c = (t.get("meta") or {}).get("card") or {}
            if t.get("error"):
                print("weather FAIL:", t["error"].get("hint"))
            else:
                p = c.get("payload") or {}
                print(f"weather OK: {p.get('weather')} {p.get('t_range')}"
                      f" id={c.get('id')}")

            res = await s.call_tool("itinerary_plan", {"legs": [
                {"mode": "drive", "from": "酒店",
                 "to": "成都大熊猫繁育研究基地",
                 "depart": "2026-10-02T07:00:00+08:00",
                 "arrive": "2026-10-02T07:40:00+08:00"},
                {"mode": "drive", "from": "成都大熊猫繁育研究基地",
                 "to": "武侯祠",
                 "depart": "2026-10-02T11:30:00+08:00",
                 "arrive": "2026-10-02T12:40:00+08:00"},
                {"mode": "drive", "from": "武侯祠", "to": "杜甫草堂",
                 "depart": "2026-10-02T15:45:00+08:00",
                 "arrive": "2026-10-02T16:05:00+08:00"},
                {"mode": "drive", "from": "酒店", "to": "都江堰景区",
                 "depart": "2026-10-03T08:00:00+08:00",
                 "arrive": "2026-10-03T09:10:00+08:00"},
                {"mode": "drive", "from": "都江堰景区", "to": "酒店",
                 "depart": "2026-10-03T16:00:00+08:00",
                 "arrive": "2026-10-03T17:10:00+08:00"}]})
            t = json.loads(res.content[0].text)
            c = (t.get("meta") or {}).get("card") or {}
            if t.get("error"):
                print("itinerary FAIL:", t["error"].get("hint"))
            else:
                n = len((c.get("payload") or {}).get("legs") or [])
                print(f"itinerary OK: id={c.get('id')} legs={n}")

            res = await s.call_tool("trip_recommend", {"summary": {
                "scenario": "成都三日两夜 · 熊猫+人文+都江堰",
                "picks": [
                    {"title": "D1 熊猫基地(早)+武侯祠+杜甫草堂",
                     "reason": "熊猫早上去最活跃；武侯祠-锦里-草堂动线顺路",
                     "tags": ["人文", "亲子"]},
                    {"title": "D2 都江堰一日",
                     "reason": "世界水利奇观，半天游览+半天慢慢逛古城",
                     "tags": ["世界遗产"]},
                    {"title": "D3 市区慢节奏+返程",
                     "reason": "人民公园喝茶+春熙路收尾，不赶路",
                     "tags": ["休闲"]}],
                "notes": ["熊猫基地务必7:30开门就进",
                          "10-02 成都 28°C 多云，适宜出行"],
                "total_cost_text": "门票合计 约¥200/人"}})
            t = json.loads(res.content[0].text)
            c = (t.get("meta") or {}).get("card") or {}
            if t.get("error"):
                print("recommend FAIL:", t["error"].get("hint"))
            else:
                n = len((c.get("payload") or {}).get("picks") or [])
                print(f"recommend OK: id={c.get('id')} picks={n}")


asyncio.run(main())
