"""coords（GCJ-02 转换）+ 静态地图 URL 构造单测。"""
from app.core import cards
from app.core.coords import wgs2gcj


def test_wgs2gcj_offsets_are_small_and_positive_direction():
    """北京天安门 WGS(39.9042,116.4074) → GCJ 偏移 0.001~0.01 量级。"""
    g_lat, g_lng = wgs2gcj(39.9042, 116.4074)
    assert 0.001 < g_lat - 39.9042 < 0.01
    assert 0.001 < g_lng - 116.4074 < 0.01


def test_wgs2gcj_foreign_passthrough():
    """境外（东京）原样返回——Google 系保持 WGS。"""
    assert wgs2gcj(35.6812, 139.7671) == (35.6812, 139.7671)


def test_wgs2gcj_deterministic():
    assert wgs2gcj(31.2304, 121.4737) == wgs2gcj(31.2304, 121.4737)


def test_amap_static_url_structure():
    shape = [[39.90, 116.40], [39.92, 116.45], [39.94, 116.50]]
    url = cards._amap_static_url(shape, "test-key")
    assert url and url.startswith("https://restapi.amap.com/v3/staticmap")
    assert "key=test-key" in url
    assert "size=400*130" in url
    assert "paths=6,0x2E7CF6,1,," in url


def test_amap_static_url_downsamples_long_shape():
    shape = [[30.0 + i * 0.001, 104.0 + i * 0.001] for i in range(500)]
    url = cards._amap_static_url(shape, "k")
    coords_part = url.split("1,,:", 1)[1]
    n = len(coords_part.split(";"))
    assert n <= 60
    assert len(url) < 1800  # URL 长度安全线


def test_amap_static_url_rejects_degenerate_shape():
    assert cards._amap_static_url([[30.0, 104.0]], "k") is None
