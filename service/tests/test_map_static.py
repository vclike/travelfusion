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
    assert "size=400*170" in url  # 加高画幅：路线垂直占框 ~75%，不贴边
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


def test_fit_zoom_covers_full_route():
    """成都绕城实例：实拍校准后的 fit zoom 必须完整容纳路线（z10 实证）。"""
    shape = [[30.5467, 104.0884], [30.6158, 104.2363]]  # 军安卫士→东安湖包围盒
    z = cards._fit_zoom([s[0] for s in shape], [s[1] for s in shape])
    assert z == 10  # 2026-10-04 实拍校准：z11 裁起点、z10 完整


def test_static_urls_three_levels():
    shape = [[30.5467, 104.0884], [30.6158, 104.2363]]
    z = cards._fit_zoom([s[0] for s in shape], [s[1] for s in shape])
    u_fit = cards._amap_static_url(shape, "k")
    u_out = cards._amap_static_url(shape, "k", zoom_fixed=max(4, z - 1))
    u_in = cards._amap_static_url(shape, "k", zoom_fixed=min(17, z + 1))
    assert f"zoom={z}" in u_fit
    assert f"zoom={z - 1}" in u_out
    assert f"zoom={z + 1}" in u_in
