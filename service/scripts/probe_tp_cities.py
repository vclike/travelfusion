"""TravelPlanner query 集目的地城市统计（datasets-server rows API）。"""
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

cities = {}
n = 0
for split in ("validation", "test"):
    offset = 0
    while True:
        url = ("https://datasets-server.huggingface.co/rows"
               "?dataset=osunlp%2FTravelPlanner&config=default"
               f"&split={split}&offset={offset}&length=100")
        try:
            j = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "curl/8"}),
                timeout=30))
        except Exception as e:
            print("api error:", e)
            break
        rows = j.get("rows") or []
        if not rows:
            break
        for r in rows:
            q = (r.get("row") or {}).get("query") or ""
            n += 1
            m = re.search(r"to ([A-Z][a-zA-Z ]+?)(?:,| and|\.|\breturning\b"
                          r"|\bstarting\b|$)", q)
            if m:
                dest = m.group(1).strip()
                cities[dest] = cities.get(dest, 0) + 1
        offset += 100
        if offset >= (j.get("num_rows_total") or 0):
            break

print(f"queries scanned: {n}")
print("destination cities (top 30):")
for c, k in sorted(cities.items(), key=lambda x: -x[1])[:30]:
    print(f"  {c}: {k}")
