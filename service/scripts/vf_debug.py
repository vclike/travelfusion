"""容器内 variflight adapter 直调诊断。"""
import json
import traceback

from app.config import data_dir
from app.core import negmark
from app.core.keys import load_keys
from app.providers.variflight.adapter import Adapter

d = data_dir()
k = (load_keys(d).get("variflight") or {}).get("api_key")
print("key head:", (k or "")[:8])
print("negmark banned:",
      negmark.is_banned(d / "negmark.db", "variflight", "flight.status"))
a = Adapter(api_key=k)
try:
    out = a.fetch("flight.status",
                  {"flight_no": "CA165", "date": "2026-09-30", "policy": {}})
    print(json.dumps(out, ensure_ascii=False)[:700])
except Exception:                                        # noqa: BLE001
    traceback.print_exc()
