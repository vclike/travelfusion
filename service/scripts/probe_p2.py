"""P2 全链实测：POI 缓存预热 → route_ground 景点 → trip_recommend 出卡。"""
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


def cards_of(t):
    m = t.get("meta") or {}
    out = []
    if m.get("card"):
        out.append(m["card"])
    out.extend(m.get("cards") or [])
    return out


async def main():
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MK}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()

            print("== 1) poi_search 天府机场（进缓存）")
            res = await s.call_tool("poi_search",
                                    {"keywords": "成都天府国际机场"})
            t = json.loads(res.content[0].text)
            pois = (t.get("data") or {}).get("pois") or []
            if pois:
                print("  top:", pois[0]["name"],
                      (pois[0]["lat"], pois[0]["lon"]))
            else:
                print("  NONE")

            print("== 2) route_ground 成都→西安 with_attractions")
            res = await s.call_tool("route_ground", {
                "origin": "成都", "destination": "西安",
                "with_attractions": True})
            t = json.loads(res.content[0].text)
            d = t.get("data") or {}
            print("  attractions:", [a.get("name")
                                     for a in (d.get("attractions") or [])][:6])
            for c in cards_of(t):
                pl = c.get("payload") or {}
                print(f"  CARD {c.get('id')} attrs="
                      f"{len(pl.get('attractions') or [])} "
                      f"shape={len(pl.get('shape') or [])}")

            print("== 3) trip_recommend 出卡")
            res = await s.call_tool("trip_recommend", {"summary": {
                "scenario": "成都→西安 三天两夜自驾",
                "picks": [
                    {"title": "D1 成都→西安（G5京昆 754km）",
                     "reason": "早出发避开绕城早高峰，傍晚抵西安逛大唐不夜城",
                     "tags": ["9h44m", "高速99%"]},
                    {"title": "D2 西安城区：兵马俑+城墙+回民街",
                     "reason": "经典一日线，夜间回民街收尾",
                     "tags": ["文化"]},
                    {"title": "D3 西安→成都",
                     "reason": "上午返程避开午后山区雨雾",
                     "tags": ["返程"]}],
                "notes": ["10-02 西安有阵雨，备伞",
                          "G5京昆高速秦岭段注意货车"],
                "total_cost_text": "油费+过路 约¥700/单程"}})
            t = json.loads(res.content[0].text)
            for c in cards_of(t):
                pl = c.get("payload") or {}
                print(f"  CARD {c.get('id')} picks="
                      f"{len(pl.get('picks') or [])}")


asyncio.run(main())
