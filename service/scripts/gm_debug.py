"""容器内 googlemaps adapter 直调诊断。"""
import json
import traceback

from app.config import data_dir
from app.core.keys import load_keys
from app.providers.googlemaps.adapter import Adapter

d = data_dir()
k = (load_keys(d).get("googlemaps") or {}).get("key")
print("key head:", (k or "")[:10])
a = Adapter(api_key=k)
try:
    out = a.fetch("ground.route.intl",
                  {"origin_wgs": [135.5023, 34.6937],
                   "destination_wgs": [139.6503, 35.6762],
                   "mode": "driving", "policy": {}})
    print(json.dumps(out, ensure_ascii=False)[:600])
except Exception:                                        # noqa: BLE001
    traceback.print_exc()
