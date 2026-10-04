"""ChinaTravel restaurants/accommodations 质量取证。"""
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = ("https://hf-mirror.com/datasets/LAMDA-NeSy/ChinaTravel-Sandbox/"
        "resolve/main/data/zh/")

for name in ("restaurants", "accommodations"):
    raw = urllib.request.urlopen(
        urllib.request.Request(BASE + name + ".parquet",
                               headers={"User-Agent": "curl/8"}),
        timeout=90).read()
    fn = f"data/chinatravel_{name}_raw.parquet"
    open(fn, "wb").write(raw)

import pyarrow.parquet as pq  # noqa: E402

for name in ("restaurants", "accommodations"):
    tbl = pq.read_table(f"data/chinatravel_{name}_raw.parquet")
    df = tbl.to_pydict()
    cols = tbl.column_names
    print(f"== {name}: {tbl.num_rows} rows | cols: {cols}")
    cities = {}
    for c in df.get("city") or []:
        cities[c] = cities.get(c, 0) + 1
    print("  cities:", sorted(cities.items(), key=lambda x: -x[1])[:6])
    # 样本：前 3 行全字段
    for i in range(min(3, tbl.num_rows)):
        row = {k: df[k][i] for k in cols}
        print("  sample:", {k: (str(v)[:24]) for k, v in row.items()})
    # 找知名实体（成都餐厅 / 上海酒店）
    target_city, hits = ("成都", []) if name == "restaurants" else ("上海", [])
    kw = ["火锅", "串串", "龙抄手", "陈麻婆"] if name == "restaurants" \
        else ["和平饭店", "半岛", "波特曼", "希尔顿"]
    for i in range(tbl.num_rows):
        if (df.get("city") or [None] * tbl.num_rows)[i] == target_city:
            nm = str(df["name"][i])
            if any(k in nm for k in kw):
                row = {k: df[k][i] for k in cols}
                hits.append(row)
    for h in hits[:3]:
        print("  known:", {k: (str(v)[:28]) for k, v in h.items()})
    print()
