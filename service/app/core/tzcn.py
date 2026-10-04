"""中国时区日期助手 —— 默认日期一律按 Asia/Shanghai（UTC+8）取"今天"。

2026-10-04 修复（B3）：此前各工具缺省日期用 date.today()，容器无 TZ 时按
UTC 计算——北京时间 00:00–08:00 之间会把"今天"算成昨天，导致状态/核验/
比价默认查错一天、付费校准 args 回显错日期。中国无夏令时，固定 +8 偏移
即可，避免 tzdata 依赖。
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

CN_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")


def now_cn() -> datetime:
    """当前中国时区 aware datetime。"""
    return datetime.now(CN_TZ)


def today_cn() -> str:
    """中国时区的今天，YYYY-MM-DD。所有工具缺省日期的唯一入口。"""
    return now_cn().strftime("%Y-%m-%d")
