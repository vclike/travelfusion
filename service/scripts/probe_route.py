"""成都(CTU/TFU)→广州(CAN) 2026-10-02 航线时刻直查：aviationstack 原始层。"""
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import yaml

KEYS = yaml.safe_load(open("data/keys.yaml", encoding="utf-8"))
_ap = (KEYS.get("providers") or {}).get("aviationstack") or KEYS.get("aviationstack")
AS_KEY = _ap.get("access_key") if isinstance(_ap, dict) else _ap

for dep in ("TFU", "CTU"):
    params = urllib.parse.urlencode({
        "access_key": AS_KEY, "dep_iata": dep, "arr_iata": "CAN",
        "flight_date": "2026-10-02", "limit": 20})
    url = f"http://api.aviationstack.com/v1/flights?{params}"
    try:
        raw = json.load(urllib.request.urlopen(url, timeout=25))
        data = raw.get("data") or []
        print(f"== {dep}->CAN: {len(data)} 条")
        for f in data:
            airline = (f.get("airline") or {}).get("name")
            fn = f.get("flight", {}).get("iata")
            depo, arro = f.get("departure") or {}, f.get("arrival") or {}
            print(f"  {fn} {airline} | {f.get('flight_status')} | "
                  f"dep {depo.get('scheduled')} | "
                  f"arr {arro.get('scheduled')} | "
                  f"delay={depo.get('delay')}")
    except Exception as e:
        print(f"== {dep}->CAN failed: {e}")
