"""amap v3 driving 结构取证：polyline / road / taxi_cost。"""
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
    "extensions": "all",
})
url = f"https://restapi.amap.com/v3/direction/driving?{params}"
j = json.load(urllib.request.urlopen(urllib.request.Request(url), timeout=25))
route = j.get("route") or {}
paths = route.get("paths") or []
print("status:", j.get("status"), "| taxi_cost:", route.get("taxi_cost"))
if paths:
    p = paths[0]
    steps = p.get("steps") or []
    print(f"dist={p.get('distance')} dur={p.get('duration')} tolls={p.get('tolls')} steps={len(steps)}")
    s0 = steps[0]
    print("step0 keys:", sorted(s0.keys()))
    print("step0 road:", s0.get("road"))
    pl = s0.get("polyline") or ""
    print("step0 polyline:", (pl[:70] + "...") if pl else repr(pl), f"({len(pl.split(';'))} pts)")
    total_pts = sum(len((x.get('polyline') or '').split(';')) for x in steps)
    print(f"total polyline pts: {total_pts}")
