# 机场名库：追加 airports 段到 airline_names.yaml（双副本）+ cards.py 回退链。幂等。
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent

AIRPORTS = {
    "PEK": "北京首都", "PKX": "北京大兴", "SHA": "上海虹桥", "PVG": "上海浦东",
    "CAN": "广州白云", "SZX": "深圳宝安", "CTU": "成都双流", "TFU": "成都天府",
    "KMG": "昆明长水", "HGH": "杭州萧山", "XIY": "西安咸阳", "WUH": "武汉天河",
    "NKG": "南京禄口", "XMN": "厦门高崎", "TAO": "青岛胶东", "CKG": "重庆江北",
    "CSX": "长沙黄花", "SYX": "三亚凤凰", "HRB": "哈尔滨太平",
    "HKG": "香港国际", "MFM": "澳门", "TPE": "台北桃园",
    "NRT": "东京成田", "HND": "东京羽田", "KIX": "大阪关西",
    "ICN": "首尔仁川", "BKK": "曼谷素万那普", "DMK": "曼谷廊曼",
    "SIN": "新加坡樟宜", "KUL": "吉隆坡", "DPS": "巴厘岛登巴萨",
    "SGN": "胡志明市", "MNL": "马尼拉",
    "JFK": "纽约肯尼迪", "EWR": "纽约纽瓦克", "LAX": "洛杉矶",
    "SFO": "旧金山", "ORD": "芝加哥奥黑尔", "YYZ": "多伦多", "YVR": "温哥华",
    "SYD": "悉尼", "MEL": "墨尔本", "AKL": "奥克兰",
    "CDG": "巴黎戴高乐", "LHR": "伦敦希思罗", "FRA": "法兰克福",
    "MUC": "慕尼黑", "FCO": "罗马菲乌米奇诺", "AMS": "阿姆斯特丹",
    "MAD": "马德里", "SVO": "莫斯科谢列梅捷沃", "IST": "伊斯坦布尔",
    "DXB": "迪拜", "DOH": "多哈", "CAI": "开罗",
}

for rel in ("app/data/airline_names.yaml", "data/airline_names.yaml"):
    p = ROOT / rel
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    ap = raw.get("airports") or {}
    before = len(ap)
    ap.update(AIRPORTS)
    raw["airports"] = ap
    p.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False,
                                default_flow_style=False), encoding="utf-8")
    print(f"{rel}: airports {before} -> {len(ap)}")

# cards.py：city_name 回退链加机场段
cp = ROOT / "app" / "core" / "cards.py"
t = cp.read_text(encoding="utf-8")
anchor = '''def city_name(iata: str | None) -> str:
    return (_city_by_iata().get(iata or "") or {}).get("name") or (iata or "")'''
new = '''def city_name(iata: str | None) -> str:
    hit = _city_by_iata().get(iata or "")
    if hit:
        return hit.get("name") or (iata or "")
    return _airline_names().get("airports", {}).get(iata or "") or (iata or "")'''
assert anchor in t, "city_name anchor missing"
if "airports" not in t:
    t = t.replace(anchor, new)
    cp.write_text(t, encoding="utf-8")
    print("cards.py fallback chain patched")
else:
    print("cards.py already patched")
