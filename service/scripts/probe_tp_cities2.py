"""发现 TravelPlanner HF 数据集的 config/split 结构后统计目的地城市。"""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HDR = {"User-Agent": "curl/8"}


def get(url):
    return json.load(urllib.request.urlopen(
        urllib.request.Request(url, headers=HDR), timeout=30))


try:
    splits = get("https://datasets-server.huggingface.co/splits"
                 "?dataset=osunlp%2FTravelPlanner")
    print("splits:", json.dumps(splits.get("splits"), ensure_ascii=False)[:400])
    cfg_list = [(s["config"], s["split"]) for s in splits.get("splits") or []]
except Exception as e:
    print("splits api error:", e)
    cfg_list = [("default", "test")]

cities = {}
n = 0
for cfg, split in cfg_list[:3]:
    offset = 0
    total = None
    while True:
        url = ("https://datasets-server.huggingface.co/rows"
               f"?dataset=osunlp%2FTravelPlanner&config={cfg}"
               f"&split={split}&offset={offset}&length=100")
        try:
            j = get(url)
        except Exception as e:
            print(f"rows error {cfg}/{split}@{offset}:", e)
            break
        rows = j.get("rows") or []
        if not rows:
            break
        total = j.get("num_rows_total")
        for r in rows:
            row = r.get("row") or {}
            q = row.get("query") or ""
            n += 1
            import re
            m = re.search(
                r"to ([A-Z][a-zA-Z ]+?)(?:,| and|\.|\breturning\b"
                r"|\bstarting\b|$)", q)
            if m:
                dest = m.group(1).strip()
                cities[dest] = cities.get(dest, 0) + 1
        offset += 100
        if total and offset >= total:
            break
    if n > 0:
        break

print(f"queries scanned: {n}")
for c, k in sorted(cities.items(), key=lambda x: -x[1])[:30]:
    print(f"  {c}: {k}")
