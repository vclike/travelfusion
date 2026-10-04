# 机场级 IANA 时区：airline_names.yaml 加 airport_tz 段（双副本）+ city_tz 回退链。幂等。
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent

APT_TZ = {
    "PEK": "Asia/Shanghai", "PKX": "Asia/Shanghai", "SHA": "Asia/Shanghai",
    "PVG": "Asia/Shanghai", "CAN": "Asia/Shanghai", "SZX": "Asia/Shanghai",
    "CTU": "Asia/Shanghai", "TFU": "Asia/Shanghai", "KMG": "Asia/Kunming",
    "HGH": "Asia/Shanghai", "XIY": "Asia/Shanghai", "WUH": "Asia/Shanghai",
    "NKG": "Asia/Shanghai", "XMN": "Asia/Shanghai", "TAO": "Asia/Shanghai",
    "CKG": "Asia/Shanghai", "CSX": "Asia/Shanghai", "SYX": "Asia/Shanghai",
    "HRB": "Asia/Shanghai",
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
    old = raw.get("airport_tz") or {}
    old.update(APT_TZ)
    raw["airport_tz"] = old
    p.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False,
                                default_flow_style=False), encoding="utf-8")
    print(f"{rel}: airport_tz -> {len(raw['airport_tz'])}")

# cards.py：city_tz 回退链 = 城表 tz → 机场 tz → None
cp = ROOT / "app" / "core" / "cards.py"
t = cp.read_text(encoding="utf-8")
old_fn = '''def city_tz(iata: str | None) -> str | None:
    return (_city_by_iata().get(iata or "") or {}).get("tz")'''
new_fn = '''def city_tz(iata: str | None) -> str | None:
    hit = _city_by_iata().get(iata or "")
    if hit and hit.get("tz"):
        return hit["tz"]
    return (_airline_names().get("airport_tz") or {}).get(iata or "")'''
assert old_fn in t, "city_tz anchor missing"
if "airport_tz" not in t:
    t = t.replace(old_fn, new_fn)
    cp.write_text(t, encoding="utf-8")
    print("city_tz fallback patched")
else:
    print("city_tz already patched")
