"""ChinaTravel attractions.parquet 取证：schema / 覆盖城市 / 西安样本。"""
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = ("https://huggingface.co/datasets/LAMDA-NeSy/ChinaTravel-Sandbox/"
       "resolve/main/data/zh/attractions.parquet")
req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
raw = urllib.request.urlopen(req, timeout=60).read()
print(f"downloaded: {len(raw) / 1024 / 1024:.1f} MB")
open("data/chinatravel_attractions_raw.parquet", "wb").write(raw)

import pyarrow.parquet as pq  # noqa: E402

tbl = pq.read_table("data/chinatravel_attractions_raw.parquet")
print("rows:", tbl.num_rows, "| cols:", tbl.column_names)
df = tbl.to_pydict()
cities = {}
for c in df.get("city") or df.get("city_name") or []:
    cities[c] = cities.get(c, 0) + 1
top = sorted(cities.items(), key=lambda x: -x[1])
print(f"cities: {len(top)} | top10: {top[:10]}")
xa = [(n, t) for n, t, c in zip(df["name"], df.get("type") or [], df["city"])
      if c == "西安"]
print(f"西安 attractions: {len(xa)} | sample: {xa[:8]}")
# 兵马俑字段全貌
for i, name in enumerate(df["name"]):
    if "兵马俑" in str(name):
        row = {k: df[k][i] for k in df.keys()}
        print("兵马俑行:", json.dumps(row, ensure_ascii=False, default=str)[:400])
        break
import json  # noqa: E402
