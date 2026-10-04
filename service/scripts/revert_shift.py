# 撤销 +24h 自动修正（猜测式改数违反不编造铁律）→ 改为 warn 标记 + 原样展示。幂等。
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
cp = Path(r"D:/WorkSpace/【Plugin-development】/dsh-flight-aggregator/service/app/core/cards.py")
t = cp.read_text(encoding="utf-8")

old_block = '''    if d0 and a0:
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

new_block = '''    if d0 and a0:
        gap_min = abs((a0 - d0).total_seconds()) / 60
        if gap_min < 120 or gap_min > 24 * 60:
            warn_notes.append({
                "level": "warn", "icon": "redeye",
                "text": f"源数据到发间隔异常（{gap_min / 60:.1f} 小时），"
                        f"时间字段可信度低——以上为源原样数据，请以航司官网为准"})'''

assert old_block in t, "auto-shift block not found"
t = t.replace(old_block, new_block)
cp.write_text(t, encoding="utf-8")
print("auto-shift removed; warn-only installed")
