"""tzcn（B3 修复）单测：缺省日期必须按北京时间取"今天"。"""
from datetime import datetime, timedelta, timezone

from app.core.tzcn import CN_TZ, now_cn, today_cn


def test_today_cn_matches_beijing_date():
    expected = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    assert today_cn() == expected


def test_today_cn_differs_from_utc_before_0800_cst():
    """边界语义验证：UTC 日期与北京日期在北京时间 00:00–08:00 之间必然不同。

    用固定钟构造：UTC 2026-10-03 22:00 == 北京 2026-10-04 06:00。
    """
    utc_now = datetime(2026, 10, 3, 22, 0, tzinfo=timezone.utc)
    cn = utc_now.astimezone(CN_TZ)
    assert cn.strftime("%Y-%m-%d") == "2026-10-04"
    assert utc_now.strftime("%Y-%m-%d") == "2026-10-03"


def test_now_cn_is_aware_and_plus8():
    n = now_cn()
    assert n.tzinfo is not None
    assert n.utcoffset() == timedelta(hours=8)
