"""key 真机探针 —— 每个 provider 发一次最小免费调用，验证凭据有效性。

用法: python scripts/probe_keys.py
结果只打印判定，不回显完整 key。规则：
  - AirLabs /ping        官方健康检查端点
  - Aviationstack /flights?limit=1  消耗 1/100 月额度（http，免费档无 https）
  - OpenSky OAuth token  取 token 免费；随后 ZBAA 包围盒 states 一击（1 credit）
    —— 直接回答「OpenSky 境内覆盖」这一最高优先验证项
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import yaml

KEYS = Path(__file__).resolve().parent.parent / "data" / "keys.yaml"
TIMEOUT = 20


def main() -> int:
    keys = (yaml.safe_load(KEYS.read_text(encoding="utf-8")) or {})
    results: dict[str, str] = {}

    # ---- AirLabs ----
    k = (keys.get("airlabs") or {}).get("api_key")
    if k:
        try:
            r = httpx.get("https://airlabs.co/api/v9/ping", params={"api_key": k},
                          timeout=TIMEOUT)
            ok = r.status_code == 200 and "error" not in r.json()
            results["airlabs"] = f"OK /ping {r.status_code}" if ok else \
                f"FAIL {r.status_code} {r.text[:120]}"
        except Exception as e:
            results["airlabs"] = f"FAIL {type(e).__name__}: {e}"
    else:
        results["airlabs"] = "SKIP no key"

    # ---- Aviationstack（免费档 http-only）----
    k = (keys.get("aviationstack") or {}).get("access_key")
    if k:
        try:
            r = httpx.get("http://api.aviationstack.com/v1/flights",
                          params={"access_key": k, "limit": 1}, timeout=TIMEOUT)
            j = r.json()
            ok = r.status_code == 200 and "data" in j
            results["aviationstack"] = f"OK flights n={len(j.get('data', []))}" if ok else \
                f"FAIL {r.status_code} {json.dumps(j)[:160]}"
        except Exception as e:
            results["aviationstack"] = f"FAIL {type(e).__name__}: {e}"
    else:
        results["aviationstack"] = "SKIP no key"

    # ---- OpenSky：OAuth token + ZBAA 包围盒 states（境内覆盖实测）----
    osk = keys.get("opensky") or {}
    if osk.get("client_id") and osk.get("client_secret"):
        try:
            r = httpx.post(
                "https://auth.opensky-network.org/auth/realms/opensky-network/"
                "protocol/openid-connect/token",
                data={"grant_type": "client_credentials",
                      "client_id": osk["client_id"],
                      "client_secret": osk["client_secret"]},
                timeout=TIMEOUT)
            if r.status_code != 200:
                results["opensky"] = f"FAIL token {r.status_code} {r.text[:120]}"
            else:
                token = r.json()["access_token"]
                # 北京首都机场周边包围盒 —— 1 credit 级
                s = httpx.get("https://opensky-network.org/api/states/all",
                              params={"lamin": 39.0, "lomin": 115.5,
                                      "lamax": 41.2, "lomax": 117.5},
                              headers={"Authorization": f"Bearer {token}"},
                              timeout=TIMEOUT)
                if s.status_code != 200:
                    results["opensky"] = f"FAIL states {s.status_code} {s.text[:120]}"
                else:
                    states = (s.json() or {}).get("states") or []
                    results["opensky"] = (
                        f"OK token + ZBAA 包围盒 states = {len(states)} 架 "
                        f"—— 境内覆盖{'有数据' if states else '该时段无观测（需多时段复测）'}")
        except Exception as e:
            results["opensky"] = f"FAIL {type(e).__name__}: {e}"
    else:
        results["opensky"] = "SKIP no key"

    # ---- Travelpayouts / 高德 / 飞常准 ----
    results["travelpayouts"] = "SKIP token 未取得（控制台 → API Tokens）"
    results["amap"] = "SKIP 待 Phase 2"
    results["variflight"] = "SKIP Phase 3 校准位（key 已存）"

    for k, v in results.items():
        print(f"{k:14s} {v}")
    return 0 if all("FAIL" not in v for v in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
