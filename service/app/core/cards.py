"""卡片编排器 —— meta.card 组装（travelfusion-card/v1）。

三层分工：服务端编排（判定+格式全在这）→ agent 搬运（meta.card 原样写工件+present）
→ 插件渲染（按 type 套模板）。模型零格式化。
设计稿：docs/cards-design-v2.md

数据通道（v2 定案）：客户端读不到工件内容、harness 折叠不可靠（description 实测会丢）
→ 卡片入内存暂存区（CARD_STAGING，TTL 2h），agent 用 `<id>.tf.json` 命名工件，
客户端按文件名里的 id 从 GET /cards/{id} 自取（CORS 放开，内容均为公开交通数据）。
description 仍随行作为冗余通道。
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from urllib.parse import quote

import yaml

from app.config import data_dir
from app.core.coords import wgs2gcj
from app.core.keys import provider_key

CARD_STAGING: dict[str, tuple[float, dict]] = {}
_TTL = 2 * 3600

# ── 翻译层：IATA 码 → 普通人看得懂的名字（查不到回退原码，不编造）────────
_CITY_BY_IATA: dict | None = None
_AIRLINE_NAMES: dict | None = None


def _city_by_iata() -> dict:
    global _CITY_BY_IATA
    if _CITY_BY_IATA is None:
        try:
            raw = yaml.safe_load(
                (data_dir() / "city_coords.yaml").read_text(encoding="utf-8")) or {}
            cities = raw.get("cities") or {}
            _CITY_BY_IATA = {v.get("iata"): {"name": k, "tz": v.get("tz"), "cc": v.get("country")}
                             for k, v in cities.items() if v.get("iata")}
        except Exception:
            _CITY_BY_IATA = {}
    return _CITY_BY_IATA


def _airline_names() -> dict:
    """全量名称库：{airlines: {IATA: 中文名}, airports: {IATA: 中文名}}。"""
    global _AIRLINE_NAMES
    if _AIRLINE_NAMES is None:
        try:
            _AIRLINE_NAMES = yaml.safe_load(
                (data_dir() / "airline_names.yaml").read_text(encoding="utf-8")) or {}
        except Exception:
            _AIRLINE_NAMES = {}
    return _AIRLINE_NAMES


def _airlines() -> dict:
    return _airline_names().get("airlines") or {}


def city_name(iata: str | None) -> str:
    hit = _city_by_iata().get(iata or "")
    if hit:
        return hit.get("name") or (iata or "")
    return (_airline_names().get("airports", {}).get(iata or "") or {}).get("name") or (iata or "")


def city_tz(iata: str | None) -> str | None:
    hit = _city_by_iata().get(iata or "")
    if hit and hit.get("tz"):
        return hit["tz"]
    return (_airline_names().get("airport_tz") or {}).get(iata or "")


def review_actions(flight_no: str | None, *,
                   dep_local_date: str | None = None) -> list:
    """外部人工复核直链（模板 2026-10-02 Tabbit 真浏览器实测可用）：
    Flightera 日期直达页（URL 编码 航班号+日期，当日起降状态一页可核）
    → FR24 班表页（按日期排列的复核表）→ FlightAware 航班主页（页内选日期）。
    遵循"卡片只渲染不计算"——URL 在服务端拼好，客户端遇到 url 字段渲染真按钮，
    卡片主体点击取第一个 review_* 直链。"""
    fno = (flight_no or "").strip()
    if not fno:
        return []
    acts: list = []
    if dep_local_date:
        acts.append({
            "id": "review_flightera", "label": "Flightera 当日直达↗",
            "url": f"https://www.flightera.net/en/flight/{fno}/{dep_local_date}"})
    acts += [
        {"id": "review_fr24", "label": "FR24 班表↗",
         "url": f"https://www.flightradar24.com/data/flights/{fno.lower()}"},
        {"id": "review_fa", "label": "FlightAware↗",
         "url": f"https://www.flightaware.com/live/flight/{fno}"},
    ]
    return acts


def empty_card(out: dict, *, title: str, hint: str = "",
               actions: list | None = None) -> None:
    """错误/空数据 → 空态卡（诚实告知 + 下一步动作），任何 turn 都有卡。"""
    card = _envelope("empty", title, {"hint": hint}, actions=actions)
    card["id"] = stage_card(card)
    out.setdefault("meta", {})["card"] = card


def recent_cards(since_ts: float) -> list[dict]:
    """按时间窗取暂存卡片（渲染器时间窗自取通道；旧→新排序，附 id/ts）。"""
    now = time.time()
    out = []
    for k, (ts, card) in CARD_STAGING.items():
        if ts >= since_ts and now - ts <= _TTL:
            c = dict(card)
            c["id"] = k
            c["_ts"] = int(ts)
            out.append((ts, c))
    out.sort(key=lambda x: x[0])
    return [c for _, c in out]


def airline_name(iata: str | None) -> str:
    return _airlines().get(iata or "") or (iata or "")


def stage_card(card: dict) -> str:
    """卡片入暂存区，返回 12 位 id（用于 <id>.tf.json 命名与 /cards/{id} 自取）。"""
    now = time.time()
    for k in [k for k, (ts, _) in CARD_STAGING.items() if now - ts > _TTL]:
        CARD_STAGING.pop(k, None)
    raw = json.dumps(card, ensure_ascii=False, sort_keys=True)
    cid = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    CARD_STAGING[cid] = (now, card)
    return cid


def get_card(cid: str) -> dict | None:
    hit = CARD_STAGING.get(cid)
    return hit[1] if hit else None


def _envelope(card_type: str, title: str, payload: dict,
              notices: list | None = None, actions: list | None = None,
              meta: dict | None = None) -> dict:
    return {"schema": "travelfusion-card/v1", "type": card_type, "title": title,
            "payload": payload, "notices": notices or [], "actions": actions or [],
            "meta": meta or {}}


def _lcc_notice(airlines: list[str], norms: dict) -> dict | None:
    lcc = sorted({a for a in airlines if a})
    if not lcc:
        return None
    base = ((norms or {}).get("norms") or {}).get("lcc") or {}
    bits = [base.get("carry_on"), base.get("meals"), base.get("seat_selection")]
    detail = "；".join(b for b in bits if b)
    named = "/".join(airline_name(a) for a in lcc)
    return {"level": "warn", "icon": "lcc",
            "text": f"{named} 为廉航：{detail or '行李/餐食/选座政策见航司页'}"}


def _dur_text(minutes) -> str | None:
    """93 → 「1小时33分」；不足 1 小时 → 「45分钟」。"""
    if minutes in (None, ""):
        return None
    m = int(minutes)
    if m <= 0:
        return None
    h, mm = divmod(m, 60)
    return f"{h}小时{mm:02d}分" if h else f"{mm}分钟"


def price_card(out: dict, *, od: str, trip_type: str, norms: dict,
               origin: str = "", destination: str = "", date: str = "") -> None:
    """flight_price → price.select / price.single。
    非校准结果附「付费校准」动作（confirm=True，agent 须征得用户同意后执行；
    飞常准一次返回价格+航班号/起降时刻/航站楼/机型，45 天窗内有效）。"""
    prices = (out.get("data") or {}).get("prices") or []
    m = out.setdefault("meta", {})
    notices = []
    lcc_hits = [p.get("airline_iata") for p in prices if p.get("lcc")]
    if n := _lcc_notice(lcc_hits, norms):
        notices.append(n)
    if any(p.get("red_eye") for p in prices):
        notices.append({"level": "info", "icon": "redeye",
                        "text": "含红眼航班（当地 00:00–05:59 起飞）"})
    payload = {
        "od": od,
        "trip_type": trip_type,
        "price_type": (prices[0].get("price_type") if prices else None),
        "prices": [{"rank": i + 1,
                    "recommended": trip_type == "incentive" and i == 0,
                    "airline_iata": p.get("airline_iata"),
                    "airline_name": airline_name(p.get("airline_iata")),
                    "flight_no": p.get("flight_number"),
                    "amount": p.get("amount"),
                    "currency": p.get("currency", "CNY"),
                    "dep_local": p.get("departure_at"),
                    "dep_terminal": p.get("dep_terminal"),
                    "arr_terminal": p.get("arr_terminal"),
                    "stop_city": p.get("stop_city"),
                    "cabin_class": p.get("cabin_class"),
                    "aircraft": p.get("aircraft"),
                    "lcc": p.get("lcc", False),
                    "red_eye": p.get("red_eye", False)}
                   for i, p in enumerate(prices)],
    }
    if trip_type == "incentive":
        notices.insert(0, {"level": "info", "icon": "policy",
                           "text": "奖励旅游口径：廉航/红眼已压后，① 为推荐"})
    # 付费校准动作：仅非校准结果挂（校准卡本身已是精确价，不再递归推销）
    actions = []
    if (prices and prices[0].get("price_type") != "calibrated") or not prices:
        act = {"id": "paid_calibrate", "label": "💰 付费校准（信息+价格）",
               "confirm": True,
               "instruction": "flight_price 同参数重查 + paid_calibrate=true——飞常准精确价"
                              "约¥0.5/次，一次返回价格+航班号/起降时刻/航站楼/机型/舱位"
                              "（45 天价格窗内有效）"}
        act_args = {}
        if origin:
            act_args["origin"] = origin
        if destination:
            act_args["destination"] = destination
        if date:
            act_args["date"] = date
        if act_args:
            act["args"] = {**act_args, "paid_calibrate": True}
        actions.append(act)
    card = _envelope("price.single" if len(prices) == 1 else "price.select",
                     f"{od} · 机票", payload, notices, actions=actions,
                     meta={"baseline": m.get("baseline_90d"),
                           "sources": m.get("sources"),
                           "cost": m.get("cost"), "cache": m.get("cache")})
    card["id"] = stage_card(card)
    m["card"] = card


def status_card(out: dict, *, date_given: bool = False) -> None:
    """flight_status → status。date_given：用户是否显式指定了日期（决定陈旧班次告警）。"""
    f = ((out.get("data") or {}).get("flights") or [{}])[0]
    if not f:
        return
    st = f.get("status") or {}
    times = f.get("times") or {}
    warn_notes: list[dict] = []

    # ── 时间语义工具 + 陈旧班次告警 + 到发间隔合理性（全部透明告警，不改数）
    from datetime import datetime, timedelta, timezone as _tzm

    def _p_iso(v):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            return None

    def _first_iso(d):
        for k in ("actual", "estimated", "scheduled_utc"):
            v = (d or {}).get(k)
            if v:
                return v
        return None

    d_dep0 = _p_iso(_first_iso(times.get("dep")))
    if not date_given and d_dep0:
        now_utc = datetime.now(_tzm.utc)
        if d_dep0 < now_utc - timedelta(hours=12) and (
                st.get("value") in ("landed", "cancelled", "")):
            warn_notes.append({
                "level": "warn", "icon": "redeye",
                "text": f"返回为 {d_dep0:%m-%d} 的最近已完成班次——"
                        f"当日班次可能未收录；如需今天的班次请确认日期后重查"})

    d0 = _p_iso(_first_iso(times.get("dep")))
    a0 = _p_iso(_first_iso(times.get("arr")))
    cc_dep = ((_city_by_iata().get(f.get("dep_iata") or "")
               or {}).get("cc")
              or (_airline_names().get("airports", {})
                  .get(f.get("dep_iata") or "") or {}).get("cc"))
    cc_arr = ((_city_by_iata().get(f.get("arr_iata") or "")
               or {}).get("cc")
              or (_airline_names().get("airports", {})
                  .get(f.get("arr_iata") or "") or {}).get("cc"))
    cross_border = bool(cc_dep and cc_arr and cc_dep != cc_arr)
    if d0 and a0:
        gap_min = abs((a0 - d0).total_seconds()) / 60
        if cross_border and (gap_min < 240 or gap_min > 26 * 60):
            warn_notes.append({
                "level": "warn", "icon": "redeye",
                "text": f"跨国航线到发间隔仅 {gap_min / 60:.1f} 小时，源数据异常，"
                        f"时间字段可信度低——以上为源原样数据，请以航司官网为准"})
    dep_nm = city_name(f.get("dep_iata"))
    arr_nm = city_name(f.get("arr_iata"))
    al = f.get("airline_iata")
    payload = {
        "flight_no": f.get("flight_no"), "airline_iata": al,
        "airline_name": airline_name(al),
        "route": f"{dep_nm} → {arr_nm}",
        "route_codes": f"{f.get('dep_iata')}→{f.get('arr_iata')}",
        "dep_city": dep_nm, "arr_city": arr_nm,
        "dep_tz": city_tz(f.get("dep_iata")),
        "arr_tz": city_tz(f.get("arr_iata")),
        "timeline": {k: (times.get(k) or {}) for k in ("dep", "arr")},
        "dep_delay_min": st.get("dep_delay_min"),
        "arr_delay_min": st.get("arr_delay_min"),
        "dep_terminal": f.get("dep_terminal"),
        "arr_terminal": f.get("arr_terminal"),
        "gate": st.get("gate") or {},
        "baggage": st.get("baggage"),
        "duration_min": f.get("duration_min"),
    }
    # Flightera 日期直达：用起飞机场当地日期编码 URL（UTC 换算，跨日航班不串日期）
    dep_local_date = None
    tz_dep = city_tz(f.get("dep_iata"))
    if d0 and tz_dep:
        try:
            from zoneinfo import ZoneInfo
            dep_local_date = d0.astimezone(ZoneInfo(tz_dep)).strftime("%Y-%m-%d")
        except Exception:
            dep_local_date = None
    m = out.setdefault("meta", {})
    card = _envelope("status", f"{f.get('flight_no')} {payload['route']}", payload,
                     notices=warn_notes,
                     actions=[{"id": "verify", "label": "双源核验",
                               "instruction": "flight_verify 计划层×ADS-B 交叉"}]
                              + review_actions(f.get("flight_no"),
                                               dep_local_date=dep_local_date),
                     meta={"sources": m.get("sources"), "cost": m.get("cost"),
                           "airline_hints": m.get("airline_hints"),
                           "cache": m.get("cache")})
    card["id"] = stage_card(card)
    m["card"] = card


def _downsample(shape: list, max_pts: int = 60) -> list:
    """等距抽稀 shape 到 ≤max_pts 点（静态地图 URL 长度安全线）。"""
    if len(shape) <= max_pts:
        return shape
    step = (len(shape) - 1) / (max_pts - 1)
    return [shape[round(i * step)] for i in range(max_pts)]


def _fit_zoom(lats: list, lngs: list, width_px: int = 400,
              height_px: int = 130) -> int:
    """按包围盒自适应 zoom（含高德实测校准）。

    2026-10-04 v2：纸面 Web-Mercator 公式比高德静态图实际视野深一档
    （scale=2 物理像素口径）——z11 公式值实测裁掉起点，z10 完整
    （军安卫士→东安湖实拍四档对比校准）。故公式值再减 1。
    """
    lat_span = (max(lats) - min(lats)) or 1e-4
    lng_span = (max(lngs) - min(lngs)) or 1e-4
    m = 1.15
    span = max(lng_span * m, lat_span * m * (width_px / height_px))
    zoom = math.floor(math.log2(360.0 * width_px / (256.0 * span))) - 1
    return max(4, min(17, zoom))


def _amap_static_url(shape: list, key: str, zoom_bias: int = 0,
                     zoom_fixed: int | None = None) -> str | None:
    """高德静态地图 URL：真实底图 + 路径折线 + 起终点标注。

    shape 为 WGS-84 [lat,lng] 序列——逐点转 GCJ-02 对齐高德底图；
    境外点 wgs2gcj 原样透传（境内路线不涉及）。任何异常返回 None，
    客户端回退 SVG 折线。zoom_bias/zoom_fixed 服务于比例尺切换档位。
    """
    try:
        pts = _downsample([s for s in shape
                           if isinstance(s, (list, tuple)) and len(s) == 2], 60)
        if len(pts) < 2:
            return None
        gcj = [wgs2gcj(float(a), float(b)) for a, b in pts]
        path = ";".join(f"{lng:.6f},{lat:.6f}" for lat, lng in gcj)
        lats = [p[0] for p in gcj]
        lngs = [p[1] for p in gcj]
        clat = (min(lats) + max(lats)) / 2
        clng = (min(lngs) + max(lngs)) / 2
        zoom = (_fit_zoom(lats, lngs) if zoom_fixed is None
                else max(4, min(17, zoom_fixed)))
        zoom = max(4, min(17, zoom + zoom_bias))
        o, dpt = gcj[0], gcj[-1]
        return ("https://restapi.amap.com/v3/staticmap"
                f"?location={clng:.6f},{clat:.6f}&zoom={zoom}"
                f"&size=400*130&scale=2"
                f"&markers=mid,0x2E7CF6,A:{o[1]:.6f},{o[0]:.6f}"
                f"|mid,0x00B578,B:{dpt[1]:.6f},{dpt[0]:.6f}"
                f"&paths=6,0x2E7CF6,1,,:{path}&key={key}")
    except Exception:
        return None


def _nav_actions(o: dict, d: dict, o_name: str, d_name: str,
                 intl: bool, mode: str) -> list:
    """导航深链动作：境内高德导航（wgs84 口径由 uri.amap.com 自转），
    境外 Google Maps 导航。坐标缺失返回空。"""
    if o.get("lat") is None or d.get("lat") is None:
        return []
    if intl:
        gm = {"driving": "driving", "transit": "transit", "walking": "walking",
              "bicycling": "bicycling"}.get(mode, "transit")
        url = ("https://www.google.com/maps/dir/?api=1"
               f"&origin={o['lat']},{o['lon']}&destination={d['lat']},{d['lon']}"
               f"&travelmode={gm}")
        label = "🗺️ Google 地图"
    else:
        url = ("https://uri.amap.com/navigation?"
               f"from={o['lon']},{o['lat']},{quote(o_name)}"
               f"&to={d['lon']},{d['lat']},{quote(d_name)}"
               f"&mode=car&coordinate=wgs84&src=travelfusion&callnative=0")
        label = "🗺️ 高德导航"
    return [{"id": "nav_map", "label": label, "url": url}]


def route_card(out: dict, *, o_name: str, d_name: str, o: dict, d: dict,
               intl: bool, degrade: list | None = None) -> None:
    """route_ground → route.cn / route.intl（坐标齐全时附 route.map）。
    degrade：地名解析降级说明（B5）——POI 未命中、按城市中心起算时如实告警。"""
    data = out.get("data") or {}
    if not data:
        return
    mode = data.get("mode", "driving")
    card_type = "route.intl" if intl else "route.cn"
    title = f"{o_name} → {d_name}"
    if intl:
        payload = {"mode": mode, "distance_km": data.get("distance_km"),
                   "duration_min": data.get("duration_min"),
                   "transit_lines": data.get("transit_lines") or [],
                   "walk_min_total": data.get("walk_min_total")}
    else:
        payload = {"mode": mode, "distance_km": data.get("distance_km"),
                   "duration_min": data.get("duration_min"),
                   "duration_text": _dur_text(data.get("duration_min")),
                   "tolls_cny": data.get("tolls_cny"),
                   "toll_distance_km": data.get("toll_distance_km"),
                   "highway_pct": data.get("highway_pct"),
                   "taxi_estimate_cny": data.get("taxi_estimate_cny"),
                   "taxi_estimate_basis": data.get("taxi_estimate_basis"),
                   "traffic_lights": data.get("traffic_lights"),
                   "segments": data.get("segments") or [],
                   "roads": data.get("roads") or [],
                   "shape": data.get("shape") or [],
                   "ev_plan": data.get("ev_plan"),
                   # 途经景点由 agent 侧行程上下文补入（服务端无 POI 源），渲染器有则展示
                   "attractions": data.get("attractions") or []}
    # route.map：两端坐标齐备才附（城表坐标，零网络）
    if o.get("lat") is not None and d.get("lat") is not None:
        payload["map"] = {
            "points": [{"name": o_name, "lat": o["lat"], "lng": o["lon"], "seq": 1},
                       {"name": d_name, "lat": d["lat"], "lng": d["lon"], "seq": 2}],
            "lines": [{"from": 1, "to": 2, "mode": mode,
                       "label": f"{data.get('distance_km')}km·{data.get('duration_min')}min"}],
        }
    # 静态地图（境内 + 有真实折线）：高德底图上叠路线，客户端 img 失败回退 SVG；
    # static_urls 附 out/fit/in 三档 zoom 供客户端比例尺切换
    if not intl and payload.get("shape"):
        _key = provider_key(data_dir(), "amap")
        if _key:
            payload["static_url"] = _amap_static_url(payload["shape"], _key)
            _pts = [s for s in payload["shape"]
                    if isinstance(s, (list, tuple)) and len(s) == 2]
            if len(_pts) >= 2:
                _z = _fit_zoom([s[0] for s in _pts], [s[1] for s in _pts])
                payload["static_urls"] = {
                    "out": _amap_static_url(payload["shape"], _key,
                                            zoom_fixed=max(4, _z - 1)),
                    "fit": payload["static_url"],
                    "in": _amap_static_url(payload["shape"], _key,
                                           zoom_fixed=min(17, _z + 1))}
    # 导航深链动作（route 卡渲染进 foot）
    actions = _nav_actions(o, d, o_name, d_name, intl, mode)
    # 过路费自相矛盾：收费里程长但费用为 0 → 打标（v5 cost.tolls 偶发漏报）
    # degrade（B5）：地名解析降级说明排在最前
    route_notes: list[dict] = [
        {"level": "warn", "icon": "lint", "text": t} for t in (degrade or [])]
    if data.get("tolls_cny") == 0 and (data.get("toll_distance_km") or 0) > 50:
        route_notes.append({
            "level": "warn", "icon": "redeye",
            "text": f"过路费数据可疑（收费里程 {data.get('toll_distance_km')} km"
                    f" 但费用为 0）——实际以高德 App 实时为准"})
    m = out.setdefault("meta", {})
    card = _envelope(card_type, title, payload, notices=route_notes,
                     actions=actions,
                     meta={"sources": m.get("sources"), "cost": m.get("cost"),
                           "cache": m.get("cache")})
    card["id"] = stage_card(card)
    m["card"] = card


def confirm_card(out: dict, *, od: str = "") -> None:
    """CONFIRM_REQUIRED 错误 → confirm 卡（含回灌动作）。"""
    err = out.get("error") or {}
    hint = err.get("hint") or ""
    card = _envelope(
        "confirm", "付费校准确认",
        {"od": od, "hint": hint},
        actions=[{"id": "approve", "label": "同意，执行付费校准",
                  "confirm": True, "instruction": "confirm_spend=true 重试"}])
    card["id"] = stage_card(card)
    out.setdefault("meta", {})["card"] = card


def _city_point(name: str) -> dict | None:
    """城市名/POI 名 → 坐标（城表 → poi_cache 兜底；全程卡 SVG 用）。"""
    try:
        raw = yaml.safe_load(
            (data_dir() / "city_coords.yaml").read_text(encoding="utf-8")) or {}
        meta = (raw.get("cities") or {}).get(name)
        if meta and meta.get("lat") is not None:
            return {"name": name, "lat": meta["lat"], "lng": meta["lon"]}
    except Exception:
        pass
    try:
        import json as _json
        cache = _json.loads((data_dir() / "poi_cache.json").read_text(
            encoding="utf-8")) or {}
        rec = cache.get(name)
        if rec and rec.get("lat") is not None:
            return {"name": name, "lat": rec["lat"], "lng": rec["lon"]}
    except Exception:
        pass
    return None


def itinerary_card(out: dict, *, legs: list[dict], norms: dict) -> None:
    """itinerary_plan → itinerary。

    legs: [{mode: flight|rail|drive, from, to, depart, arrive}, ...] 按时间升序。
    flight/rail 为固定锚点（不可改时刻）；drive 为地面衔接段。
    锚点反推：固定段起飞/开车前需预留 buffer（默认 ✈60min / 🚄30min，norms 可调），
    前一地面段自动标注 `must_arrive_by`（需抵达时刻）与 `latest_depart`（最迟出发）。
    """
    from datetime import datetime, timedelta

    buf = ((norms or {}).get("buffers") or {})
    buf_flight = int(buf.get("flight_min", 60))
    buf_rail = int(buf.get("rail_min", 30))

    def p_iso(v):
        try:
            return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        except Exception:
            return None

    view: list[dict] = []
    notes: list[dict] = []
    for leg in legs:
        mode = (leg.get("mode") or "drive").lower()
        d0, a0 = p_iso(leg.get("depart")), p_iso(leg.get("arrive"))
        dur = (int((a0 - d0).total_seconds() / 60)
               if d0 and a0 else leg.get("duration_min"))
        fixed = mode in ("flight", "rail")
        buf_min = buf_flight if mode == "flight" else (
            buf_rail if mode == "rail" else None)
        item = {"mode": mode, "from": leg.get("from"), "to": leg.get("to"),
                "depart": leg.get("depart"), "arrive": leg.get("arrive"),
                "duration_min": dur, "fixed": fixed, "buffer_min": buf_min}
        if fixed and d0:
            must = d0 - timedelta(minutes=buf_min)
            item["must_arrive_by"] = must.isoformat()
            if view and view[-1].get("mode") not in ("flight", "rail"):
                view[-1]["must_arrive_by"] = item["must_arrive_by"]
                prev_dur = view[-1].get("duration_min")
                if prev_dur:
                    latest = must - timedelta(minutes=int(prev_dur))
                    view[-1]["latest_depart"] = latest.isoformat()
            notes.append({"level": "info", "icon": "anchor",
                          "text": f"{leg.get('from')}：需不晚于 "
                                  f"{must.strftime('%m-%d %H:%M')} 抵达"
                                  f"（含提前 {buf_min} 分钟）"})
        view.append(item)

    span_min = None
    if legs:
        first, last = p_iso(legs[0].get("depart")), p_iso(legs[-1].get("arrive"))
        if first and last:
            span_min = int((last - first).total_seconds() / 60)

    points, seq = [], 1
    for leg in legs:
        for stop in (leg.get("from"), leg.get("to")):
            if stop and not any(x["name"] == stop for x in points):
                pt = _city_point(stop)
                if pt:
                    pt["seq"] = seq
                    points.append(pt)
                    seq += 1
    # 线只连两端都在城表里的腿（缺坐标的端点会把线索引进索引空洞）
    name_seq = {pt["name"]: pt["seq"] for pt in points}
    lines = []
    for l in view:
        a, b = l.get("from"), l.get("to")
        if a in name_seq and b in name_seq:
            lines.append({"from": name_seq[a], "to": name_seq[b],
                          "mode": (l.get("mode") or "drive"),
                          "label": f"{a}→{b}"})
    payload = {"legs": view, "span_min": span_min, "notices": notes,
               "map": {"points": points, "lines": lines}}
    card = _envelope("itinerary", "全程行程", payload, notices=notes)
    card["id"] = stage_card(card)
    out.setdefault("meta", {})["card"] = card


def recommend_card(out: dict, *, summary: dict) -> None:
    """trip_recommend → recommend（结构化结论 → 服务端排版，模型零格式化）。"""
    picks = summary.get("picks") or []
    notes = [{"level": "info", "text": n} for n in (summary.get("notes") or [])]
    payload = {"scenario": summary.get("scenario") or "",
               "picks": picks[:4],
               "total_cost_text": summary.get("total_cost_text") or ""}
    card = _envelope("recommend", summary.get("scenario") or "行程推荐",
                     payload, notices=notes)
    card["id"] = stage_card(card)
    out.setdefault("meta", {})["card"] = card


def weather_card(out: dict, *, location: str) -> None:
    """weather_context → weather（layer 标签强制，两态永不混用）。"""
    data = out.get("data") or {}
    if not data:
        return
    m = out.setdefault("meta", {})
    t = data.get("target") or {}
    payload = {"layer": data.get("layer"), "labels": data.get("labels"),
               "date": data.get("target_date"),
               "weather": t.get("weather"),
               "t_range": [t.get("t_min_c"), t.get("t_max_c")],
               "precip_mm": t.get("precip_mm"),
               "summary": data.get("summary")}
    card = _envelope("weather",
                     f"🌦️ {location} · {data.get('target_date', '')}",
                     payload,
                     meta={"sources": m.get("sources"),
                           "cost": m.get("cost")})
    card["id"] = stage_card(card)
    m["card"] = card


def quota_card(out: dict) -> None:
    """quota_status → quota 仪表卡。"""
    data = out.get("data") or {}
    rows = [{"provider": p.get("provider"), "tier": p.get("tier"),
             "remaining": (p.get("quota") or {}).get("remaining_free"),
             "limit": (p.get("quota") or {}).get("limit"),
             "used": (p.get("quota") or {}).get("used"),
             "paid_month_cny": ((p.get("paid") or {}).get("month_cny")
                                if isinstance(p.get("paid"), dict) else None)}
            for p in data.get("providers", [])]
    card = _envelope("quota", "额度仪表盘",
                     {"rows": rows, "paid": data.get("paid")}, meta={})
    card["id"] = stage_card(card)
    out.setdefault("meta", {})["card"] = card
