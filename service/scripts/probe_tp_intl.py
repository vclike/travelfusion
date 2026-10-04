"""TravelPlanner 全量 query 国际目的地扫描。"""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HDR = {"User-Agent": "curl/8"}
INTL = ["Paris", "Tokyo", "London", "Rome", "Barcelona", "Bali", "Cancun",
        "Amsterdam", "Bangkok", "Singapore", "Seoul", "Beijing", "Shanghai",
        "Hong Kong", "Dubai", "Sydney", "Toronto", "Vancouver", "Mexico",
        "Jamaica", "Bahamas", "Aruba", "Paris,", "Europe", "Japan", "China",
        "Italy", "France", "Spain", "Thailand", "Canada", "Caribbean",
        "Puerto Rico", "Iceland", "Switzerland", "Germany", "Greece"]
hits = {}
n = 0
for cfg in ("validation", "test", "train"):
    offset = 0
    while True:
        try:
            j = json.load(urllib.request.urlopen(urllib.request.Request(
                "https://datasets-server.huggingface.co/rows"
                f"?dataset=osunlp%2FTravelPlanner&config={cfg}&split={cfg}"
                f"&offset={offset}&length=100", headers=HDR), timeout=30))
        except Exception as e:
            print("err:", e)
            break
        rows = j.get("rows") or []
        if not rows:
            break
        for r in rows:
            q = (r.get("row") or {}).get("query") or ""
            n += 1
            for k in INTL:
                if k in q:
                    hits.setdefault(k, []).append(q[:90])
        offset += 100
        if offset >= (j.get("num_rows_total") or 0):
            break

print(f"scanned: {n} queries")
if hits:
    for k, v in hits.items():
        print(f"[{k}] x{len(v)} e.g. {v[0]}")
else:
    print("NO international destination mentions found")
