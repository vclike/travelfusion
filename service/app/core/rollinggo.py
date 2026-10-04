"""RollingGo 酒店检索客户端（服务端实现）——归因链接在服务端代码层保证。

关键代码自 rollinggo-hotel-booking skill 迁入：
  POST https://mcp.rollinggo.cn/mcp/hotelsearch （Bearer access_token）
  bookingUrl 输出前强制 utm_source=0A0OIB（有则换值/无则追加）——不依赖调用方自觉。

边界：本模块只做只读检索与链接归因；锁价/下单（资金操作）保留在
rollinggo-hotel-booking skill 的人工确认闸门内，服务端不碰钱。

Token：RGH_TOKEN_PATH（默认 /app/data/.hotel-cli/token.json，NAS 端 rgh login 产生）。
推广码：keys.yaml 的 rgh_promo_code（缺省 0A0OIB），管理面板可改。
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import time
from pathlib import Path

import httpx

MCP_BASE_URL = "https://mcp.rollinggo.cn/mcp"
OAUTH_SERVER = "https://rollinggo.store"
AUTHORIZE_URL = "https://api.rollinggo.cn/oauth2/authorize"
CLIENT_ID = "rollinggoskill"
OAUTH_SCOPE = "profile phone email hotel:order:read hotel:order:book hotel:order:cancel"
DEFAULT_PROMO_CODE = "0A0OIB"
DEFAULT_TOKEN_PATH = "/app/data/.hotel-cli/token.json"

_PLACE_TYPES = ("城市", "机场", "景点", "火车站", "地铁站", "酒店", "区/县", "详细地址")


class RghError(Exception):
    """RollingGo 检索失败（网络/鉴权/业务）。"""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _token_path() -> Path:
    import os
    return Path(os.environ.get("RGH_TOKEN_PATH", DEFAULT_TOKEN_PATH))


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _login_session_path(data_dir: Path) -> Path:
    return _token_path().parent / "login-session.json"


def logged_in(data_dir: Path) -> bool:
    p = _token_path()
    if not p.exists():
        return False
    try:
        return bool((json.loads(p.read_text(encoding="utf-8")) or {}).get("access_token"))
    except Exception:
        return False


def logout(data_dir: Path) -> bool:
    p = _token_path()
    existed = p.exists()
    if existed:
        p.unlink()
    return existed


def start_login(data_dir: Path) -> dict:
    """发起 OAuth（PKCE + state 中转）——复刻官方 CLI login 编排。

    返回 {auth_url, short_url}；轮询凭证（poll_key）落盘 login-session.json，
    由 login_status() 逐次轮询，成功后写入 token 文件。
    """
    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    session_id = secrets.token_hex(16)
    try:
        with httpx.Client(timeout=15) as client:
            r = client.post(f"{OAUTH_SERVER}/skill/oauth/init",
                            json={"session_id": session_id,
                                  "code_verifier": verifier,
                                  "client_id": CLIENT_ID})
    except Exception as e:
        raise RghError("UPSTREAM", f"授权服务不可达: {e}")
    if r.status_code != 200:
        raise RghError("UPSTREAM", f"获取授权 state 失败: HTTP {r.status_code}")
    doc = r.json() or {}
    state, poll_key = doc.get("state"), doc.get("session_id") or session_id
    redirect_uri = f"{OAUTH_SERVER}/skill/oauth/callback"
    auth_url = (f"{AUTHORIZE_URL}?response_type=code&client_id={CLIENT_ID}"
                f"&redirect_uri={redirect_uri}"
                f"&state={state}&code_challenge={challenge}"
                f"&code_challenge_method=S256&scope={OAUTH_SCOPE}"
                f"&resource={MCP_BASE_URL}&prompt=consent")
    short_url = auth_url
    try:
        with httpx.Client(timeout=10) as client:
            sh = client.post(f"{OAUTH_SERVER}/s/shorten", json={"url": auth_url})
        if sh.status_code == 200:
            short_url = (sh.json() or {}).get("shortUrl") or short_url
    except Exception:
        pass  # 短链服务不可用就用长链接
    sess = {"session_id": session_id, "poll_key": poll_key,
            "code_verifier": verifier, "created": time.time()}
    sp = _login_session_path(data_dir)
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(sess), encoding="utf-8")
    return {"auth_url": auth_url, "short_url": short_url}


def login_status(data_dir: Path) -> dict:
    """面板轮询端点：每次调用向上游查一次授权结果。

    success → 写 token 文件并清除会话；expired → 清会话；其余 pending。
    """
    if logged_in(data_dir):
        return {"status": "logged_in"}
    sp = _login_session_path(data_dir)
    if not sp.exists():
        return {"status": "not_started"}
    try:
        sess = json.loads(sp.read_text(encoding="utf-8"))
    except Exception:
        sp.unlink(missing_ok=True)
        return {"status": "not_started"}
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(f"{OAUTH_SERVER}/skill/oauth/token",
                           params={"session_id": sess["poll_key"]})
        if r.status_code != 200:
            return {"status": "pending"}
        j = r.json() or {}
    except Exception:
        return {"status": "pending"}   # 网络波动，前端继续轮询
    if j.get("status") == "success" and j.get("token"):
        tp = _token_path()
        tp.parent.mkdir(parents=True, exist_ok=True)
        tp.write_text(json.dumps(j["token"], ensure_ascii=False, indent=2),
                      encoding="utf-8")
        sp.unlink(missing_ok=True)
        return {"status": "success"}
    if j.get("status") == "expired":
        sp.unlink(missing_ok=True)
        return {"status": "expired"}
    return {"status": "pending"}


def load_access_token(data_dir: Path) -> str:
    """NAS 端 rgh login 产出的 token.json → access_token。"""
    p = _token_path()
    if not p.exists():
        raise RghError("NO_TOKEN", "服务端尚未登录 RollingGo（缺 token 文件）")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
        token = (doc or {}).get("access_token") or ""
    except Exception as e:  # 坏 token 文件
        raise RghError("NO_TOKEN", f"token 文件损坏: {e}")
    if not token:
        raise RghError("NO_TOKEN", "token 文件缺少 access_token")
    return token


def promo_code(data_dir: Path) -> str:
    """推广码：keys.yaml rgh_promo_code 优先（面板可改），缺省 0A0OIB。"""
    try:
        from app.core.keys import load_keys
        code = (load_keys(data_dir) or {}).get("rgh_promo_code")
        if isinstance(code, str) and code.strip():
            return code.strip()
    except Exception:
        pass
    return DEFAULT_PROMO_CODE


def apply_promo(text: str, code: str = DEFAULT_PROMO_CODE) -> str:
    """归因改写（服务端强制版）：rollinggo.cn 链接 utm_source 统一为推广码。

    - utm_source=rollinggo_cus → utm_source=<code>（换值）
    - rollinggo.cn 链接缺 utm_source → 追加 &utm_source=<code>
    """
    out = text.replace("utm_source=rollinggo_cus", f"utm_source={code}")
    out = re.sub(
        r"https://rollinggo\.cn/[^\s\"'<>{}]*",
        lambda m: m.group(0) if "utm_source=" in m.group(0)
        else f"{m.group(0)}&utm_source={code}",
        out,
    )
    return out


def build_search_payload(origin_query: str, place: str, place_type: str = "城市",
                         check_in_date: str = "", stay_nights: int = 1,
                         adult_count: int = 2, size: int = 5,
                         star_ratings: str = "", max_price: float = 0) -> dict:
    """按 CLI 同构 payload 组装（字段名对齐 RollingGo 服务端）。"""
    if place_type not in _PLACE_TYPES:
        raise ValueError(f"place_type 必须是 {'/'.join(_PLACE_TYPES)}")
    params: dict = {"originQuery": origin_query, "place": place,
                    "placeType": place_type, "size": max(1, min(20, size))}
    if check_in_date or stay_nights or adult_count:
        params["checkInParam"] = {}
        if check_in_date:
            params["checkInParam"]["checkInDate"] = check_in_date
        if stay_nights:
            params["checkInParam"]["stayNights"] = int(stay_nights)
        if adult_count:
            params["checkInParam"]["adultCount"] = int(adult_count)
    if star_ratings or max_price:
        params["filterOptions"] = {}
        if star_ratings:
            params["filterOptions"]["starRatings"] = star_ratings
        if max_price:
            params["filterOptions"]["maxPricePerNight"] = float(max_price)
    return params


def _pc_booking_url(hotel_id, hotel_name: str, check_in: str,
                    nights: int, adults: int, code: str) -> str | None:
    """PC 单酒店预订页深链——跳过会丢 utm_source 的移动详情页 302。"""
    if not hotel_id or not check_in:
        return None
    from datetime import date as _d, timedelta
    from urllib.parse import quote
    try:
        y, m, dd = (int(x) for x in check_in.split("-"))
        check_out = (_d(y, m, dd) + timedelta(days=int(nights or 1))).isoformat()
    except Exception:
        return None
    q = "&".join(
        f"{k}={quote(str(v))}" for k, v in {
            "hotelId": hotel_id, "hotelType": "hotel",
            "checkIndate": check_in, "checkOutDate": check_out,
            "room": 1, "adults": adults, "children": 0,
            "hotelName": hotel_name or "", "utm_source": code,
        }.items())
    return f"https://rollinggo.cn/pc/#/hotel/single?{q}"


def search_hotels(data_dir: Path, origin_query: str, place: str,
                  place_type: str = "城市", check_in_date: str = "",
                  stay_nights: int = 1, adult_count: int = 2, size: int = 5,
                  star_ratings: str = "", max_price: float = 0,
                  timeout: float = 30.0) -> list[dict]:
    """检索酒店；bookingUrl 服务端强制归因后返回。抛 RghError。"""
    token = load_access_token(data_dir)
    code = promo_code(data_dir)
    payload = build_search_payload(origin_query, place, place_type,
                                   check_in_date, stay_nights, adult_count,
                                   size, star_ratings, max_price)
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(f"{MCP_BASE_URL}/hotelsearch", json=payload,
                            headers={"Authorization": f"Bearer {token}",
                                     "Accept": "application/json"})
    except Exception as e:
        raise RghError("UPSTREAM", f"RollingGo 接口不可达: {e}")
    if r.status_code == 401:
        raise RghError("TOKEN_EXPIRED", "token 失效——在 NAS 重新执行 rgh login")
    if r.status_code != 200:
        raise RghError("UPSTREAM", f"HTTP {r.status_code}: {r.text[:120]}")
    body = r.json() or {}
    hotels = body.get("hotelInformationList") or []
    out = []
    for h in hotels:
        price = h.get("price") or {}
        mobile_url = apply_promo(h.get("bookingUrl") or "", code)
        # 主链接用 PC 预订页深链（utm_source 全程保留）；移动详情页作备用字段
        pc = (_pc_booking_url(h.get("hotelId"), h.get("name"), check_in_date,
                              stay_nights, adult_count, code)
              or mobile_url)
        out.append({
            "name": h.get("name"),
            "star": h.get("starRating"),
            "address": h.get("address"),
            "price_lowest": price.get("lowestPrice"),
            "price_note": price.get("message") or "",
            "booking_url": pc,
            "mobile_url": mobile_url,
            "tags": (h.get("tags") or [])[:6],
        })
    return out
