# status_card 到达日期合理性校验：长航线到发间隔<2h → 源日期疑似滞后一天 → +24h 修正+告警
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
cp = Path(r"D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/service/app/core/cards.py")
t = cp.read_text(encoding="utf-8")

anchor = '''def status_card(out: dict) -> None:
    """flight_status → status。"""
    f = ((out.get("data") or {}).get("flights") or [{}])[0]
    if not f:
        return
    st = f.get("status") or {}
    times = f.get("times") or {}'''

new = '''def status_card(out: dict) -> None:
    """flight_status → status。"""
    f = ((out.get("data") or {}).get("flights") or [{}])[0]
    if not f:
        return
    st = f.get("status") or {}
    times = f.get("times") or {}
    warn_notes: list[dict] = []

    # ── 到达日期合理性：到发间隔 <2h 的班次 → 源日期疑似滞后一天 → +24h 修正
    # （透明：卡面打 warn 告警，不静默改数）
    from datetime import datetime, timedelta, timezone as _tzm

    def _p_iso(v):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            return None

    def _first_iso(d):
        for k in ("actual", "estimated", "scheduled_utc"):
            v = (d or {}).get(k)
            if v:
                return v
        return None

    d0 = _p_iso(_first_iso(times.get("dep")))
    a0 = _p_iso(_first_iso(times.get("arr")))
    if d0 and a0:
        gap_min = (a0 - d0).total_seconds() / 60
        if 0 < gap_min < 120:
            arr_t = times.get("arr") or {}
            for k, v in list(arr_t.items()):
                a1 = _p_iso(v)
                if a1:
                    arr_t[k] = (a1 + timedelta(hours=24)).strftime(
                        "%Y-%m-%dT%H:%M:%SZ")
            duration_min = f.get("duration_min")
            if not duration_min or duration_min < 120:
                duration_min = int(gap_min + 1440)
            f["duration_min"] = duration_min
            warn_notes.append({
                "level": "warn", "icon": "redeye",
                "text": f"源到达日期疑似滞后一天（到发间隔仅 {gap_min:.0f} 分钟），"
                        f"已按 +24h 修正展示，请以航司为准"})'''

assert anchor in t, "status_card anchor missing"
t = t.replace(anchor, new)

# _envelope 调用带上告警
old_env = '''    card = _envelope("status", f"{f.get('flight_no')} {payload['route']}", payload,
                     actions=[{"id": "verify", "label": "双源核验",
                               "instruction": "flight_verify 计划层×ADS-B 交叉"}],'''
new_env = '''    card = _envelope("status", f"{f.get('flight_no')} {payload['route']}", payload,
                     notices=warn_notes,
                     actions=[{"id": "verify", "label": "双源核验",
                               "instruction": "flight_verify 计划层×ADS-B 交叉"}],'''
assert old_env in t, "envelope anchor missing"
t = t.replace(old_env, new_env)
cp.write_text(t, encoding="utf-8")
print("sanity check installed")
