"""variflight flight.price 直调诊断（CTU→NKG）。"""
import json
import traceback

from app.config import data_dir
from app.core.keys import load_keys
from app.providers.variflight.adapter import Adapter

d = data_dir()
k = (load_keys(d).get("variflight") or {}).get("api_key")
a = Adapter(api_key=k)
try:
    out = a.fetch("flight.price",
                  {"origin": "成都", "destination": "南京",
                   "origin_code": "CTU", "destination_code": "NKG",
                   "date": "2026-10-15", "policy": {}})
    print(json.dumps(out, ensure_ascii=False)[:900])
except Exception:                                        # noqa: BLE001
    traceback.print_exc()
