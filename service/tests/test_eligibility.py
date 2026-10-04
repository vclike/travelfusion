from app.core.eligibility import decide, haversine_km


def test_haversine_chengdu_leshan_about_130km():
    # 成都 30.5728,104.0668 → 乐山 29.5521,103.7656
    km = haversine_km(30.5728, 104.0668, 29.5521, 103.7656)
    assert 110 < km < 150


def test_chengdu_leshan_blocks_air():
    """用户验收场景：成都→乐山 不得触发任何航班查询。"""
    res = decide(130, cross_border=False)
    assert res.blocked("air")
    assert res.eligible["rail"] is True
    assert res.eligible["drive"] is True
    assert "距离" in res.reasons["air"]
    assert res.rank[0] == "rail"


def test_mid_band_rail_first():
    res = decide(500, cross_border=False)
    assert res.eligible["air"] is True          # 允许但低优先
    assert res.rank[0] == "rail"


def test_long_band_air_first():
    res = decide(1500, cross_border=False)
    assert res.rank[0] == "air"
    assert res.eligible["drive"] is True        # <2000km 仍可自驾


def test_ultra_long_blocks_drive():
    res = decide(3000, cross_border=False)
    assert res.eligible["drive"] is False


def test_cross_border_blocks_rail_and_drive():
    res = decide(8500, cross_border=True)
    assert res.eligible["air"] is True
    assert res.eligible["rail"] is False
    assert res.eligible["drive"] is False


def test_no_airport_blocks_air():
    res = decide(1200, cross_border=False, has_airport=False)
    assert res.eligible["air"] is False
    assert "机场" in res.reasons["air"]


def test_same_place_blocks_all():
    res = decide(0, cross_border=False, same_place=True)
    assert all(v is False for v in res.eligible.values())


def test_custom_bands():
    res = decide(500, cross_border=False, band_short=600)
    assert res.blocked("air")   # 500 < 600 短途带 → 航班关闭
