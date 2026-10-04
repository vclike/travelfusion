"""虚拟规划任务 E2E：个人（曼谷自由行）× 奖励旅游（团建），走真 MCP。"""
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


def _j(res) -> dict:
    return json.loads(res.content[0].text)


def _brief_price(j, tag: str) -> None:
    if j.get("error"):
        print(f"  [{tag}] err={j['error']['code']} {j['error']['hint'][:60]}")
        return
    prices = j["data"].get("prices") or []
    tt = j.get("meta", {}).get("trip_type", "personal")
    print(f"  [{tag}] trip_type={tt} 共{len(prices)}条：")
    for p in prices[:4]:
        flags = ("LCC" if p.get("lcc") else "") + \
                ("·红眼" if p.get("red_eye") else "")
        print(f"    {p.get('airline_iata')} CNY{p.get('amount')} "
              f"{(p.get('departure_at') or '')[:16]} {flags or '正班'}")
    b = j.get("meta", {}).get("baseline_90d")
    if b:
        print(f"    基线90d: min CNY{b['min_cny']} avg CNY{b['avg_cny']} "
              f"当前 vs_min {b.get('vs_min')}%")


async def main() -> None:
    async with streamablehttp_client(
            "http://192.168.100.1:8900/mcp",
            headers={"X-API-Key": MCP_KEY}) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()

            print("== 场景 A · 个人 · 曼谷自由行 5 天（预算优先）==")
            _brief_price(_j(await s.call_tool(
                "flight_price",
                {"origin": "成都", "destination": "曼谷",
                 "trip_type": "personal"})), "A1 机票")
            j = _j(await s.call_tool("weather_context",
                                     {"location": "曼谷", "date": "2026-10-03"}))
            if j.get("data"):
                t = j["data"].get("target") or {}
                print(f"  [A2 天气] {j['data'].get('layer')}: {t.get('weather')} "
                      f"{t.get('t_min_c')}–{t.get('t_max_c')}°C 降水{t.get('precip_mm')}mm")
            j = _j(await s.call_tool("route_ground",
                                     {"origin": "曼谷", "destination": "芭提雅",
                                      "mode": "driving"}))
            d = j.get("data") or {}
            print(f"  [A3 延伸自驾] {d.get('distance_km')}km {d.get('duration_min')}min")

            print("== 场景 B · 奖励旅游 · 曼谷团建（质量优先，廉航/红眼压后）==")
            _brief_price(_j(await s.call_tool(
                "flight_price",
                {"origin": "成都", "destination": "曼谷",
                 "trip_type": "incentive"})), "B1 机票")
            j = _j(await s.call_tool("route_ground",
                                     {"origin": "成都", "destination": "乐山"}))
            d = j.get("data") or {}
            print(f"  [B2 短途替代·高德] {d.get('distance_km')}km "
                  f"{d.get('duration_min')}min 打车≈CNY{d.get('taxi_estimate_cny')} "
                  f"过路CNY{d.get('tolls_cny')}")
            j = _j(await s.call_tool("flight_status", {"flight_no": "CA165"}))
            if j.get("data", {}).get("flights"):
                f = j["data"]["flights"][0]
                print(f"  [B3 接机信息] {f['flight_no']} {f['dep_iata']}→{f['arr_iata']} "
                      f"到达T{f.get('arr_terminal')} 行李 {f['status'].get('baggage')}")
                hints = json.dumps(j["meta"].get("airline_hints", {}),
                                   ensure_ascii=False)[:100]
                print(f"      航司知识: {hints}")

            print("== 成本审计 ==")
            j = _j(await s.call_tool("quota_status", {}))
            for p in j["data"]["providers"]:
                if p.get("quota", {}).get("remaining_free") is not None or p["tier"] == "paid":
                    q = p.get("quota") or {}
                    print(f"  {p['provider']:14s} used={q.get('used') or '-'} "
                          f"remaining={q.get('remaining_free')} paid_cny={p.get('paid', {}).get('month_cny', '-')}"
                          if isinstance(p.get("paid"), dict) else
                          f"  {p['provider']:14s} {q}")


asyncio.run(main())

