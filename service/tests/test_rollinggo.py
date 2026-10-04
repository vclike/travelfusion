"""rollinggo 服务端检索客户端测试——归因改写 / payload 组装 / token 加载。"""
import json

import httpx
import pytest

from app.core import rollinggo as rgh


def test_apply_promo_replaces_existing():
    url = 'https://rollinggo.cn/pages/hotel/detail/index?id=1&checkInDate=2026-10-18&utm_source=rollinggo_cus'
    out = rgh.apply_promo(url, "0A0OIB")
    assert "utm_source=0A0OIB" in out
    assert "rollinggo_cus" not in out
    assert "id=1" in out and "checkInDate=2026-10-18" in out   # 其余参数原样


def test_apply_promo_appends_when_missing():
    url = "https://rollinggo.cn/pages/hotel/detail/index?id=2"
    out = rgh.apply_promo(url, "0A0OIB")
    assert out.endswith("utm_source=0A0OIB")


def test_apply_promo_no_double_append():
    url = "https://rollinggo.cn/pages/reservationLink/index?utm_source=0A0OIB"
    assert rgh.apply_promo(url, "0A0OIB").count("utm_source") == 1


def test_build_search_payload_matches_cli_schema():
    p = rgh.build_search_payload("q", "西湖", "景点", "2026-10-18", 3, 2, 5)
    assert p["originQuery"] == "q" and p["placeType"] == "景点"
    assert p["checkInParam"] == {"checkInDate": "2026-10-18",
                                 "stayNights": 3, "adultCount": 2}
    with pytest.raises(ValueError):
        rgh.build_search_payload("q", "x", "星球")


def test_search_hotels_rewrites_links_and_needs_token(tmp_path, monkeypatch):
    (tmp_path / "token.json").write_text(
        json.dumps({"access_token": "tok-xyz"}), encoding="utf-8")
    monkeypatch.setenv("RGH_TOKEN_PATH", str(tmp_path / "token.json"))

    body = {"hotelInformationList": [{
        "hotelId": 9,
        "name": "测试酒店", "starRating": 4, "address": "某路1号",
        "price": {"lowestPrice": 300, "message": "3晚总价：900CNY"},
        "bookingUrl": "https://rollinggo.cn/pages/hotel/detail/index?id=9&utm_source=rollinggo_cus",
        "tags": ["含早", "泳池"],
    }]}
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("Authorization")
        captured["payload"] = json.loads(request.content)
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client
    monkeypatch.setattr(rgh.httpx, "Client",
                        lambda **kw: real_client(transport=transport, **kw))

    hotels = rgh.search_hotels(tmp_path, "q", "杭州", "城市",
                               "2026-10-18", 3, 2, 1)
    assert captured["auth"] == "Bearer tok-xyz"
    assert captured["payload"]["checkInParam"]["checkInDate"] == "2026-10-18"
    h = hotels[0]
    assert "/pc/#/hotel/single" in h["booking_url"]            # PC 深链（不丢归因）
    assert "utm_source=0A0OIB" in h["booking_url"]
    assert "checkOutDate=2026-10-21" in h["booking_url"]        # 入住+晚数推离店
    assert "rollinggo_cus" not in h["booking_url"]
    assert h["mobile_url"].startswith("https://rollinggo.cn/pages/")  # 备用移动页


def test_search_hotels_without_token_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("RGH_TOKEN_PATH", str(tmp_path / "missing.json"))
    with pytest.raises(rgh.RghError) as ei:
        rgh.search_hotels(tmp_path, "q", "杭州")
    assert ei.value.code == "NO_TOKEN"


def _mock_oauth(monkeypatch, handler):
    transport = httpx.MockTransport(handler)
    real_client = httpx.Client
    monkeypatch.setattr(rgh.httpx, "Client",
                        lambda **kw: real_client(transport=transport, **kw))


def test_login_flow_writes_token(tmp_path, monkeypatch):
    monkeypatch.setenv("RGH_TOKEN_PATH", str(tmp_path / "token.json"))

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/skill/oauth/init":
            assert json.loads(request.content)["client_id"] == "rollinggoskill"
            return httpx.Response(200, json={"state": "jwt-state",
                                             "session_id": "poll-1"})
        if request.url.path == "/s/shorten":
            return httpx.Response(200, json={"shortUrl": "https://rollinggo.store/s/abc"})
        if request.url.path == "/skill/oauth/token":
            return httpx.Response(200, json={"status": "success",
                                             "token": {"access_token": "at-1",
                                                       "expires_in": 3600}})
        return httpx.Response(404)

    _mock_oauth(monkeypatch, handler)
    r = rgh.start_login(tmp_path)
    assert r["short_url"] == "https://rollinggo.store/s/abc"
    assert "code_challenge_method=S256" in r["auth_url"]
    assert "client_id=rollinggoskill" in r["auth_url"]

    st = rgh.login_status(tmp_path)
    assert st["status"] == "success"
    tok = json.loads((tmp_path / "token.json").read_text(encoding="utf-8"))
    assert tok["access_token"] == "at-1"
    assert rgh.logged_in(tmp_path)
    assert not (tmp_path / "login-session.json").exists()   # 会话已清


def test_login_status_pending_then_expired(tmp_path, monkeypatch):
    monkeypatch.setenv("RGH_TOKEN_PATH", str(tmp_path / "token.json"))
    states = [{"status": "pending"}, {"status": "expired"}]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/skill/oauth/init":
            return httpx.Response(200, json={"state": "s", "session_id": "p"})
        if request.url.path == "/skill/oauth/token":
            return httpx.Response(200, json=states.pop(0) if states
                                  else {"status": "expired"})
        return httpx.Response(404)

    _mock_oauth(monkeypatch, handler)
    rgh.start_login(tmp_path)
    assert rgh.login_status(tmp_path)["status"] == "pending"
    assert (tmp_path / "login-session.json").exists()
    assert rgh.login_status(tmp_path)["status"] == "expired"
    assert not (tmp_path / "login-session.json").exists()
