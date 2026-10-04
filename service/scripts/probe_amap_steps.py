"""amap v5 原始 steps 结构取证：polys 字段到底有没有。"""
import json
import os
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
          "ALL_PROXY", "all_proxy"):
    os.environ.pop(v, None)
import yaml

KEYS = yaml.safe_load(open("data/keys.yaml", encoding="utf-8"))
_ap = (KEYS.get("providers") or {}).get("amap") or KEYS.get("amap")
AMAP_KEY = _ap.get("key") if isinstance(_ap, dict) else _ap

params = urllib.parse.urlencode({
    "key": AMAP_KEY,
    "origin": "104.0668,30.5728",
    "destination": "108.9398,34.3416",
    "strategy": "0",
    "show_fields": "cost,steps",
})
url = f"https://restapi.amap.com/v5/direction/driving?{params}"
j = json.load(urllib.request.urlopen(urllib.request.Request(url), timeout=25))
paths = (j.get("route") or {}).get("paths") or []
if not paths:
    print("no paths:", json.dumps(j, ensure_ascii=False)[:200])
else:
    steps = paths[0].get("steps") or []
    print(f"steps: {len(steps)}")
    s0 = steps[0]
    print("step0 keys:", sorted(s0.keys()))
    print("step0 road:", s0.get("road_name"), "| dist:", s0.get("distance"))
    polys = s0.get("polys")
    print("step0 polys:", (polys[:80] + "...") if polys else repr(polys))
    has_poly = sum(1 for x in steps if x.get("polys"))
    print(f"steps with polys: {has_poly}/{len(steps)}")
