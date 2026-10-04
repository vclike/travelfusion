import json
import os
import sys

for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)

import httpx
import yaml

k = yaml.safe_load(open(Path_ := "data/keys.yaml", encoding="utf-8"))["airlabs"]["api_key"]
r = httpx.get("https://airlabs.co/api/v9/schedules",
              params={"flight_iata": "TG615", "api_key": k}, timeout=20)
j = r.json()
rows = j.get("response") or []
if not rows:
    print("empty response")
    sys.exit(0)
f = rows[0]
interesting = {kk: vv for kk, vv in f.items()
               if ("time" in kk or "delay" in kk or kk == "status"
                   or kk in ("flight_iata", "dep_iata", "arr_iata"))}
print(json.dumps(interesting, ensure_ascii=False, indent=1))
