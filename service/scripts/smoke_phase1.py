"""Phase 1 真机冒烟：dispatch 全链路 → AirLabs + Travelpayouts 真实 API。"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

# 清理本机代理环境变量（httpx TRUST_ENV 默认跟随，死代理会掐断请求）
for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
            "ALL_PROXY", "all_proxy"):
    os.environ.pop(var, None)

SERVICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVICE))

from app.config import data_dir  # noqa: E402
from app.core import dispatch  # noqa: E402

# 播种运行时种子（如缺失）——与 app.main 的正式播种一致
rt = data_dir()
for _name in ("manifests.json", "norms.yaml", "airlines_kb.yaml", "city_coords.yaml"):
    src = SERVICE / "app" / "data" / _name
    if not (rt / _name).exists() and src.exists():
        shutil.copy(src, rt / _name)
        print(f"seeded: {_name}")

# amap adapter 已上线：运行时启用（热插拔标准动作，等价 provider_admin enable）
from app.core import registry  # noqa: E402
registry.enable(rt / "manifests.json", "amap")

print("=== 1. flight_status（AirLabs 真机 · 自喂养式） ===")
import httpx  # noqa: E402
import yaml  # noqa: E402
for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ.pop(var, None)
k = (yaml.safe_load((rt / "keys.yaml").read_text(encoding="utf-8")) or {}).get("airlabs", {}).get("api_key")
live = httpx.get("https://airlabs.co/api/v9/flights",
                 params={"dep_iata": "PEK", "api_key": k}, timeout=20).json()
rows = live.get("response") or []
if not rows:
    print("PEK 当前无可查航班（窗口空）——改用 CA1501 直查")
    target = "CA1501"
else:
    target = rows[0].get("flight_iata")
    print(f"PEK 当前航班 {len(rows)} 个，取 {target}（{rows[0].get('dep_iata')}→{rows[0].get('arr_iata')}）做端到端")
out = dispatch.call_capability(
    "flight.status", {"flight_no": target, "policy": {}},
    data_dir=rt, settings=None)
print(json.dumps(out, ensure_ascii=False)[:1500])

print()
print("=== 2. flight_price MOW->BKK（Travelpayouts 真机） ===")
out2 = dispatch.call_capability(
    "flight.price",
    {"origin_code": "MOW", "destination_code": "BKK", "date": None,
     "currency": "CNY", "policy": {}},
    data_dir=rt, settings=None)
print(json.dumps(out2, ensure_ascii=False)[:1200])

print()
print("=== 4. flight_verify TG615（AirLabs×OpenSky 复合核验） ===")
from app.mcp_server import flight_verify  # noqa: E402
out4 = flight_verify("TG615")
print(json.dumps(out4, ensure_ascii=False)[:1400])

print()
print("=== 5. aviationstack 备用源（同航班直查） ===")
from app.core import keys  # noqa: E402
from app.providers.aviationstack.adapter import Adapter as ASAdapter  # noqa: E402
ka = (keys.load_keys(rt) or {}).get("aviationstack", {}).get("access_key")
try:
    o5 = ASAdapter(api_key=ka).fetch("flight.status",
                                     {"flight_no": target, "policy": {}})
    print(json.dumps(o5, ensure_ascii=False)[:500])
except Exception as e:                                    # noqa: BLE001
    print(f"aviationstack: {type(e).__name__} {str(e)[:160]}")

print()
print("=== 6. route_ground 成都→乐山（高德真机 · 立项旗舰场景） ===")
from app.mcp_server import route_ground  # noqa: E402
out6 = route_ground("成都", "乐山", ev_rated_range_km=400)
print(json.dumps(out6, ensure_ascii=False)[:800])

print()
print("=== 3. quota_status（账本对账） ===")
from app.core import ledger, registry  # noqa: E402
led = ledger.QuotaLedger(rt / "ledger.db")
print(json.dumps(led.status(), ensure_ascii=False))
