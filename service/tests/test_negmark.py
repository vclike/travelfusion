from app.core.negmark import (banned_providers, is_banned, record_failure,
                              record_success)


def test_failure_bans_then_success_clears(tmp_path):
    nm = tmp_path / "neg.db"
    assert is_banned(nm, "airlabs", "flight.status") is False
    until1 = record_failure(nm, "airlabs", "flight.status", reason="429")
    assert is_banned(nm, "airlabs", "flight.status") is True
    # 成功一次 → 解封清零
    record_success(nm, "airlabs", "flight.status")
    assert is_banned(nm, "airlabs", "flight.status") is False


def test_escalation_grows(tmp_path):
    nm = tmp_path / "neg.db"
    t = 1_000_000.0   # 固定时钟：banned_until - now 即冷却时长
    u1 = record_failure(nm, "airlabs", "flight.status", now=t)
    u2 = record_failure(nm, "airlabs", "flight.status", now=t)
    u3 = record_failure(nm, "airlabs", "flight.status", now=t)
    assert u1 - t == 3600          # 首次冷却 1h
    assert u2 - t == 7200          # 二次 2h
    assert u3 - t == 14400         # 三次 4h


def test_capability_isolation(tmp_path):
    nm = tmp_path / "neg.db"
    record_failure(nm, "airlabs", "flight.status")
    # 状态查询被限流不代表机场库也坏了
    assert is_banned(nm, "airlabs", "airport.db") is False


def test_ban_expires(tmp_path):
    nm = tmp_path / "neg.db"
    until = record_failure(nm, "airlabs", "flight.status")
    future = until + 1
    assert is_banned(nm, "airlabs", "flight.status") is True
    assert is_banned(nm, "airlabs", "flight.status", now=future) is False
