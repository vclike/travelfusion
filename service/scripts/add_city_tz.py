# 给 city_coords.yaml 每座城市补 IANA 时区（客户端 Intl 换算用）。幂等。.agent-maintainable
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TZ = {
    # 中国（含港台）
    "北京": "Asia/Shanghai", "上海": "Asia/Shanghai", "广州": "Asia/Shanghai",
    "深圳": "Asia/Shanghai", "成都": "Asia/Shanghai", "重庆": "Asia/Shanghai",
    "杭州": "Asia/Shanghai", "西安": "Asia/Shanghai", "武汉": "Asia/Shanghai",
    "南京": "Asia/Shanghai", "厦门": "Asia/Shanghai", "青岛": "Asia/Shanghai",
    "昆明": "Asia/Shanghai", "三亚": "Asia/Shanghai", "哈尔滨": "Asia/Shanghai",
    "郑州": "Asia/Shanghai", "长沙": "Asia/Shanghai", "天津": "Asia/Shanghai",
    "合肥": "Asia/Shanghai", "福州": "Asia/Shanghai", "贵阳": "Asia/Shanghai",
    "南宁": "Asia/Shanghai", "兰州": "Asia/Shanghai", "乌鲁木齐": "Asia/Urumqi",
    "香港": "Asia/Hong_Kong", "台北": "Asia/Taipei", "高雄": "Asia/Taipei",
    "澳门": "Asia/Macau",
    # 日韩
    "东京": "Asia/Tokyo", "大阪": "Asia/Tokyo", "京都": "Asia/Tokyo",
    "名古屋": "Asia/Tokyo", "札幌": "Asia/Tokyo", "冲绳": "Asia/Tokyo",
    "首尔": "Asia/Seoul", "济州岛": "Asia/Seoul", "釜山": "Asia/Seoul",
    # 东南亚
    "曼谷": "Asia/Bangkok", "清迈": "Asia/Bangkok", "普吉": "Asia/Bangkok",
    "芭提雅": "Asia/Bangkok", "芭堤雅": "Asia/Bangkok",
    "新加坡": "Asia/Singapore", "吉隆坡": "Asia/Kuala_Lumpur", "槟城": "Asia/Kuala_Lumpur",
    "巴厘岛": "Asia/Makassar", "河内": "Asia/Ho_Chi_Minh", "岘港": "Asia/Ho_Chi_Minh",
    "胡志明市": "Asia/Ho_Chi_Minh", "马尼拉": "Asia/Manila", "金边": "Asia/Phnom_Penh",
    "暹粒": "Asia/Phnom_Penh", "仰光": "Asia/Yangon",
    # 南亚/中东
    "马尔代夫": "Indian/Maldives", "马累": "Indian/Maldives",
    "迪拜": "Asia/Dubai", "阿布扎比": "Asia/Dubai", "多哈": "Asia/Qatar",
    "伊斯坦布尔": "Europe/Istanbul", "孟买": "Asia/Kolkata", "新德里": "Asia/Kolkata",
    # 大洋洲
    "墨尔本": "Australia/Melbourne", "悉尼": "Australia/Sydney",
    "布里斯班": "Australia/Brisbane", "奥克兰": "Pacific/Auckland",
    "珀斯": "Australia/Perth", "斐济": "Pacific/Fiji",
    "塞班岛": "Pacific/Guam", "关岛": "Pacific/Guam",
    # 欧洲
    "伦敦": "Europe/London", "巴黎": "Europe/Paris", "法兰克福": "Europe/Berlin",
    "慕尼黑": "Europe/Berlin", "罗马": "Europe/Rome", "米兰": "Europe/Rome",
    "苏黎世": "Europe/Zurich", "阿姆斯特丹": "Europe/Amsterdam",
    "马德里": "Europe/Madrid", "巴塞罗那": "Europe/Madrid", "里斯本": "Europe/Lisbon",
    "维也纳": "Europe/Vienna", "布拉格": "Europe/Prague", "布达佩斯": "Europe/Budapest",
    "雅典": "Europe/Athens", "莫斯科": "Europe/Moscow", "圣彼得堡": "Europe/Moscow",
    "哥本哈根": "Europe/Copenhagen", "斯德哥尔摩": "Europe/Stockholm", "奥斯陆": "Europe/Oslo",
    "赫尔辛基": "Europe/Helsinki", "华沙": "Europe/Warsaw", "都柏林": "Europe/Dublin",
    # 北美
    "纽约": "America/New_York", "华盛顿": "America/New_York", "波士顿": "America/New_York",
    "洛杉矶": "America/Los_Angeles", "旧金山": "America/Los_Angeles",
    "拉斯维加斯": "America/Los_Angeles", "西雅图": "America/Los_Angeles",
    "芝加哥": "America/Chicago", "多伦多": "America/Toronto", "温哥华": "America/Vancouver",
    "墨西哥城": "America/Mexico_City",
    # 南美/非洲
    "圣保罗": "America/Sao_Paulo", "里约热内卢": "America/Sao_Paulo",
    "布宜诺斯艾利斯": "America/Argentina/Buenos_Aires", "利马": "America/Lima",
    "开罗": "Africa/Cairo", "内罗毕": "Africa/Nairobi", "约翰内斯堡": "Africa/Johannesburg",
    "卡萨布兰卡": "Africa/Casablanca",
}


def patch(path: Path) -> int:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cities = raw.get("cities") or {}
    added = 0
    for name, meta in cities.items():
        tz = TZ.get(name)
        if tz and isinstance(meta, dict) and not meta.get("tz"):
            meta["tz"] = tz
            added += 1
    path.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False,
                                   default_flow_style=False), encoding="utf-8")
    return added


for p in (Path(__file__).resolve().parent.parent / "app" / "data" / "city_coords.yaml",
          Path(__file__).resolve().parent.parent / "data" / "city_coords.yaml"):
    n = patch(p)
    print(f"{p}: +{n} tz")
