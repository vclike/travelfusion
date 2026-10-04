"""一次性数据迁移：城市表挂 IATA 城市码 + 补充国内/国际城市。幂等。"""
from pathlib import Path

import yaml

P = Path(__file__).resolve().parent.parent / "app" / "data" / "city_coords.yaml"
data = yaml.safe_load(P.read_text(encoding="utf-8")) or {}
cities = data.get("cities") or {}

IATA = {
    "成都": "CTU", "北京": "BJS", "上海": "SHA", "广州": "CAN", "深圳": "SZX",
    "昆明": "KMG", "西安": "SIA", "杭州": "HGH", "重庆": "CKG", "厦门": "XMN",
    "南京": "NKG", "武汉": "WUH", "长沙": "CSX", "郑州": "CGO", "青岛": "TAO",
    "哈尔滨": "HRB", "乌鲁木齐": "URC", "海口": "HAK", "三亚": "SYX",
    "伦敦": "LON", "曼谷": "BKK", "莫斯科": "MOW", "东京": "TYO", "首尔": "SEL",
    "新加坡": "SIN", "纽约": "NYC", "巴黎": "PAR", "香港": "HKG", "台北": "TPE",
    # 乐山无民航机场——刻意不给码，flight_price 走诚实提示
}

NEW_CITIES = {
    "天津": {"lat": 39.0851, "lon": 117.1994, "country": "CN", "iata": "TSN"},
    "大连": {"lat": 38.9140, "lon": 121.6147, "country": "CN", "iata": "DLC"},
    "福州": {"lat": 26.0745, "lon": 119.2965, "country": "CN", "iata": "FOC"},
    "贵阳": {"lat": 26.6470, "lon": 106.6302, "country": "CN", "iata": "KWE"},
    "南宁": {"lat": 22.8170, "lon": 108.3665, "country": "CN", "iata": "NNG"},
    "桂林": {"lat": 25.2742, "lon": 110.2902, "country": "CN", "iata": "KWL"},
    "兰州": {"lat": 36.0611, "lon": 103.8343, "country": "CN", "iata": "LHW"},
    "长春": {"lat": 43.8171, "lon": 125.3235, "country": "CN", "iata": "CGQ"},
    "合肥": {"lat": 31.8206, "lon": 117.2272, "country": "CN", "iata": "HFE"},
    "宁波": {"lat": 29.8683, "lon": 121.5440, "country": "CN", "iata": "NGB"},
    "珠海": {"lat": 22.2707, "lon": 113.5767, "country": "CN", "iata": "ZUH"},
    "西宁": {"lat": 36.6171, "lon": 101.7782, "country": "CN", "iata": "XNN"},
    "清迈": {"lat": 18.7669, "lon": 98.9626, "country": "TH", "iata": "CNX"},
    "普吉": {"lat": 7.8804, "lon": 98.3923, "country": "TH", "iata": "HKT"},
    "大阪": {"lat": 34.6937, "lon": 135.5023, "country": "JP", "iata": "OSA"},
    "悉尼": {"lat": -33.8688, "lon": 151.2093, "country": "AU", "iata": "SYD"},
    "洛杉矶": {"lat": 34.0522, "lon": -118.2437, "country": "US", "iata": "LAX"},
    "法兰克福": {"lat": 50.1109, "lon": 8.6821, "country": "DE", "iata": "FRA"},
    "芭提雅": {"lat": 12.9236, "lon": 100.8825, "country": "TH"},
    "京都": {"lat": 35.0116, "lon": 135.7681, "country": "JP"},
    "罗马": {"lat": 41.9028, "lon": 12.4964, "country": "IT"},
    "札幌": {"lat": 43.0621, "lon": 141.3543, "country": "JP", "iata": "CTS"},
}

added = 0
for name, iata in IATA.items():
    if name in cities and isinstance(cities[name], dict):
        cities[name]["iata"] = iata
for name, meta in NEW_CITIES.items():
    if name not in cities:
        cities[name] = meta
        added += 1

data["cities"] = cities
P.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
             encoding="utf-8")
print(f"iata attached: {len(IATA)} | cities added: {added} | total: {len(cities)}")
