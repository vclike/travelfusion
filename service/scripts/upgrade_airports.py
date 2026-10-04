# 机场库升级为 {name, cc} 结构 + cards.py 跨国短间隔告警判据。幂等。
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent

# iata: (中文名, 国家码)
AIRPORTS = {
    "PEK": ("北京首都", "CN"), "PKX": ("北京大兴", "CN"), "SHA": ("上海虹桥", "CN"),
    "PVG": ("上海浦东", "CN"), "CAN": ("广州白云", "CN"), "SZX": ("深圳宝安", "CN"),
    "CTU": ("成都双流", "CN"), "TFU": ("成都天府", "CN"), "KMG": ("昆明长水", "CN"),
    "HGH": ("杭州萧山", "CN"), "XIY": ("西安咸阳", "CN"), "WUH": ("武汉天河", "CN"),
    "NKG": ("南京禄口", "CN"), "XMN": ("厦门高崎", "CN"), "TAO": ("青岛胶东", "CN"),
    "CKG": ("重庆江北", "CN"), "CSX": ("长沙黄花", "CN"), "SYX": ("三亚凤凰", "CN"),
    "HRB": ("哈尔滨太平", "CN"), "URC": ("乌鲁木齐地窝堡", "CN"),
    "HKG": ("香港国际", "HK"), "MFM": ("澳门", "MO"), "TPE": ("台北桃园", "TW"),
    "NRT": ("东京成田", "JP"), "HND": ("东京羽田", "JP"), "KIX": ("大阪关西", "JP"),
    "ICN": ("首尔仁川", "KR"), "BKK": ("曼谷素万那普", "TH"), "DMK": ("曼谷廊曼", "TH"),
    "SIN": ("新加坡樟宜", "SG"), "KUL": ("吉隆坡", "MY"), "DPS": ("巴厘岛登巴萨", "ID"),
    "SGN": ("胡志明市", "VN"), "MNL": ("马尼拉", "PH"),
    "JFK": ("纽约肯尼迪", "US"), "EWR": ("纽约纽瓦克", "US"), "LAX": ("洛杉矶", "US"),
    "SFO": ("旧金山", "US"), "ORD": ("芝加哥奥黑尔", "US"),
    "YYZ": ("多伦多皮尔逊", "CA"), "YVR": ("温哥华", "CA"),
    "SYD": ("悉尼", "AU"), "MEL": ("墨尔本", "AU"), "AKL": ("奥克兰", "NZ"),
    "CDG": ("巴黎戴高乐", "FR"), "LHR": ("伦敦希思罗", "GB"), "FRA": ("法兰克福", "DE"),
    "MUC": ("慕尼黑", "DE"), "FCO": ("罗马菲乌米奇诺", "IT"),
    "AMS": ("阿姆斯特丹", "NL"), "MAD": ("马德里", "ES"),
    "SVO": ("莫斯科谢列梅捷沃", "RU"), "IST": ("伊斯坦布尔", "TR"),
    "DXB": ("迪拜", "AE"), "DOH": ("多哈", "QA"), "CAI": ("开罗", "EG"),
}
APT_TZ = {
    "PEK": "Asia/Shanghai", "PKX": "Asia/Shanghai", "SHA": "Asia/Shanghai",
    "PVG": "Asia/Shanghai", "CAN": "Asia/Shanghai", "SZX": "Asia/Shanghai",
    "CTU": "Asia/Shanghai", "TFU": "Asia/Shanghai", "KMG": "Asia/Kunming",
    "HGH": "Asia/Shanghai", "XIY": "Asia/Shanghai", "WUH": "Asia/Shanghai",
    "NKG": "Asia/Shanghai", "XMN": "Asia/Shanghai", "TAO": "Asia/Shanghai",
    "CKG": "Asia/Shanghai", "CSX": "Asia/Shanghai", "SYX": "Asia/Shanghai",
    "HRB": "Asia/Shanghai", "URC": "Asia/Urumqi",
    "HKG": "Asia/Hong_Kong", "MFM": "Asia/Macau", "TPE": "Asia/Taipei",
    "NRT": "Asia/Tokyo", "HND": "Asia/Tokyo", "KIX": "Asia/Tokyo",
    "ICN": "Asia/Seoul", "BKK": "Asia/Bangkok", "DMK": "Asia/Bangkok",
    "SIN": "Asia/Singapore", "KUL": "Asia/Kuala_Lumpur",
    "DPS": "Asia/Makassar", "SGN": "Asia/Ho_Chi_Minh", "MNL": "Asia/Manila",
    "JFK": "America/New_York", "EWR": "America/New_York",
    "LAX": "America/Los_Angeles", "SFO": "America/Los_Angeles",
    "ORD": "America/Chicago", "YYZ": "America/Toronto",
    "YVR": "America/Vancouver",
    "SYD": "Australia/Sydney", "MEL": "Australia/Melbourne",
    "AKL": "Pacific/Auckland",
    "CDG": "Europe/Paris", "LHR": "Europe/London", "FRA": "Europe/Berlin",
    "MUC": "Europe/Berlin", "FCO": "Europe/Rome", "AMS": "Europe/Amsterdam",
    "MAD": "Europe/Madrid", "SVO": "Europe/Moscow",
    "IST": "Europe/Istanbul", "DXB": "Asia/Dubai", "DOH": "Asia/Qatar",
    "CAI": "Africa/Cairo",
}

for rel in ("app/data/airline_names.yaml", "data/airline_names.yaml"):
    p = ROOT / rel
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    raw["airports"] = {k: {"name": n, "cc": cc}
                       for k, (n, cc) in AIRPORTS.items()}
    raw["airport_tz"] = APT_TZ
    p.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False,
                                default_flow_style=False), encoding="utf-8")
    print(f"{rel}: airports(dict)+airport_tz ok")

cp = ROOT / "app" / "core" / "cards.py"
t = cp.read_text(encoding="utf-8")

# names 回退链适配 dict 结构
t = t.replace(
    'return _airline_names().get("airports", {}).get(iata or "") or (iata or "")',
    'return (_airline_names().get("airports", {}).get(iata or "")'
    ' or {}).get("name") or (iata or "")')

# city meta 补 cc
t = t.replace(
    '_CITY_BY_IATA = {v.get("iata"): {"name": k, "tz": v.get("tz")}',
    '_CITY_BY_IATA = {v.get("iata"): {"name": k, "tz": v.get("tz"),'
    ' "cc": v.get("country")}')

# 告警判据：跨国 + 到发间隔 <4h（或 >26h）
old_cond = '''    if d0 and a0:
        gap_min = abs((a0 - d0).total_seconds()) / 60
        if gap_min < 120 or gap_min > 24 * 60:'''
new_cond = '''    cc_dep = (_city_by_iata().get(f.get("dep_iata") or "")
              or {}).get("cc")
    apt_dep = (_airline_names().get("airports", {})
               .get(f.get("dep_iata") or "") or {}).get("cc")
    cc_arr = (_city_by_iata().get(f.get("arr_iata") or "")
              or {}).get("cc")
    apt_arr = (_airline_names().get("airports", {})
               .get(f.get("arr_iata") or "") or {}).get("cc")
    cross_border = bool(cc_dep and cc_arr and apt_dep and apt_arr
                        and (cc_dep != cc_arr))
    if d0 and a0:
        gap_min = abs((a0 - d0).total_seconds()) / 60
        if cross_border and (gap_min < 240 or gap_min > 26 * 60):'''
assert old_cond in t, "condition anchor missing"
t = t.replace(old_cond, new_cond)
t = t.replace(
    '"text": f"源数据到发间隔异常（{gap_min / 60:.1f} 小时），"',
    '"text": f"跨国航线到发间隔仅 {gap_min / 60:.1f} 小时，源数据异常"，')
cp.write_text(t, encoding="utf-8")
print("cards.py patched (dict airports + cross-border heuristic)")
