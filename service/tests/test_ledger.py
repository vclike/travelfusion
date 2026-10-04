import pytest

from app.core.ledger import QuotaLedger


class FakeClock:
    def __init__(self, ts: float):
        self.ts = ts

    def __call__(self) -> float:
        return self.ts

    def advance_days(self, n: int):
        self.ts += n * 86400


# 2026-09-29 12:00 UTC
SEPT = 1789977600.0


def test_monthly_lazy_reset(tmp_path):
    clock = FakeClock(SEPT)
    led = QuotaLedger(tmp_path / "l.db", now_fn=clock)
    # 9 月消耗 3 次，上限 1000
    for _ in range(3):
        used = led.consume_free("airlabs", "month")
    assert used == 3
    assert led.remaining("airlabs", "month", 1000) == 997
    # 跨到 10 月：惰性重置 → 余额回满
    clock.advance_days(32)
    assert led.remaining("airlabs", "month", 1000) == 1000
    used = led.consume_free("airlabs", "month")
    assert used == 1


def test_day_period_independent(tmp_path):
    clock = FakeClock(SEPT)
    led = QuotaLedger(tmp_path / "l.db", now_fn=clock)
    led.consume_free("opensky", "day")
    clock.advance_days(1)
    assert led.remaining("opensky", "day", 4000) == 4000


def test_total_never_resets(tmp_path):
    clock = FakeClock(SEPT)
    led = QuotaLedger(tmp_path / "l.db", now_fn=clock)
    led.consume_paid("variflight", 0.5)
    clock.advance_days(60)
    led.consume_paid("variflight", 0.5)
    assert led.paid_month_cny() >= 1.0   # total 制累计不因跨月清零


def test_paid_accumulates(tmp_path):
    led = QuotaLedger(tmp_path / "l.db", now_fn=FakeClock(SEPT))
    led.consume_paid("variflight", 0.5)
    led.consume_paid("variflight", 0.5)
    assert led.paid_month_cny() == pytest.approx(1.0)


def test_status_shape(tmp_path):
    led = QuotaLedger(tmp_path / "l.db", now_fn=FakeClock(SEPT))
    led.consume_free("airlabs", "month", 2)
    rows = led.status()
    assert rows[0]["provider"] == "airlabs"
    assert rows[0]["free_used"] == 2
    assert rows[0]["period_key"].startswith("2026-09")
