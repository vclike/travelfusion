"""MCP 工具面 —— 9 个工具（契约见 docs/09-tool-contracts.md）。

Phase 0 可用：quota_status / provider_admin / airline_kb / resolve_place
              + flight_status / flight_price 的资格护栏（先判 NOT_APPLICABLE 再报数据源未接入）
Phase 1/2 替换内部实现：flight_price sweep / flight_verify / route_ground / weather_context
——工具签名即契约，替换内部不改 agent 侧。
"""
from __future__ import annotations

from pathlib import Path
import json

import yaml
from mcp.server.fastmcp import FastMCP

from app.config import data_dir, load_settings
from app.core import airline_kb as kb_store
from app.core import attribution, canon, cards, chinatravel, dispatch, eligibility, ledger
from app.core import negmark, registry
from app.core import profile as _profile_mod
from app.core.chinatravel import get_store as _china_get_store
from app.core.tzcn import today_cn  # B3 修复：缺省日期一律按北京时间

china_store = _china_get_store(data_dir())

# streamable_http_path="/" —— 内部路由设为根，外层 FastAPI 统一挂载到 /mcp
# （1.x 默认内部路径也是 /mcp，双重挂载会 404）
# transport_security：关闭 DNS-rebinding 防护——部署决策（2026-09-30）：
#   LAN-only（iStoreOS 防火墙默认拒 WAN 入站）+ 调用方是 DSH 服务端（无 Origin/浏览器），
#   且校验器仅支持前缀白名单、LAN 设备 IP 动态无法枚举。若未来暴露公网，必须改回
#   enable_dns_rebinding_protection=True 并配鉴权。
from mcp.server.transport_security import TransportSecuritySettings  # noqa: E402
mcp = FastMCP("travelfusion", streamable_http_path="/",
              transport_security=TransportSecuritySettings(
                  enable_dns_rebinding_protection=False,
                  allowed_hosts=["*"], allowed_origins=["*"]))


def _p() -> dict[str, Path]:
    d = data_dir()
    return {
        "manifests": d / "manifests.json",
        "kb": d / "airlines_kb.yaml",
        "cache_db": d / "cache.db",
        "norms": d / "norms.yaml",
        "city": d / "city_coords.yaml",
        "ledger_db": d / "ledger.db",
        "negmark_db": d / "negmark.db",
    }


_ADMIN_MUTATING = {"enable", "disable", "set_quota", "reorder", "set_budget"}


def _require_admin(provided: str) -> dict | None:
    """管理操作密码门：admin_key 未配置=开放；配置后变更类 action 必须匹配。"""
    from app.core.keys import auth_config
    expected = auth_config(data_dir()).get("admin_key")
    if not expected:
        return None
    if provided != expected:
        return canon.error(canon.E_AUTH_REQUIRED,
                           hint="admin_key 缺失或不匹配（管理操作需密码）")
    return None


def _cities() -> dict:
    p = _p()["city"]
    if not p.exists():
        return {}
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("cities", {})


_POI_CACHE_TTL = 30 * 86400


def _poi_cache_load() -> dict:
    try:
        return json.loads((data_dir() / "poi_cache.json").read_text(
            encoding="utf-8")) or {}
    except Exception:
        return {}


def _poi_cache_put(name: str, rec: dict) -> None:
    cache = _poi_cache_load()
    rec = dict(rec, cached_at=today_cn())  # B3：北京时间戳
    cache[name] = rec
    try:
        (data_dir() / "poi_cache.json").write_text(
            json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _poi_cache_get(name: str) -> dict | None:
    rec = _poi_cache_load().get(name)
    if not rec:
        return None
    return {"name": name, "lat": rec.get("lat"), "lon": rec.get("lon"),
            "country": "CN", "poi": True}


def _resolve_city(name: str) -> dict | None:
    cities = _cities()
    if name in cities:
        return {"name": name, **cities[name]}
    n = name.strip()
    # 2026-10-02：机场码直查（三字码 ∈ 城市表 iata 或 airports 成员，如 TFU/KHN）
    if len(n) == 3 and n.isascii() and n.isalpha() and n.isupper():
        for k, v in cities.items():
            v = v or {}
            if v.get("iata") == n:
                return {"name": k, **v}
            if n in (v.get("airports") or []):
                base = cities.get(n) or {}
                return {"name": k, "iata": n,
                        "lat": base.get("lat") if base.get("lat") is not None
                        else v.get("lat"),
                        "lon": base.get("lon") if base.get("lon") is not None
                        else v.get("lon"),
                        "country": v.get("country", "CN"), "tz": v.get("tz")}
    # POI 精确缓存优先于城市表模糊匹配（"成都天府国际机场"不得被"成都"劫持）
    cached = _poi_cache_get(n)
    if cached and cached.get("lat"):
        return cached
    # 2026-10-04 修复（B5）：POI 搜索提到子串模糊匹配之前——"北京南站"⊃"北京"
    # 曾被城市表劫持成市中心坐标且无任何告警；POI 命中后入缓存（TTL 30 天）。
    try:
        out = dispatch.call_capability(
            "poi.search", {"keywords": n, "policy": {}}, data_dir=data_dir())
        pois = (out.get("data") or {}).get("pois") or []
        if pois:
            top = pois[0]
            rec = {"lat": top["lat"], "lon": top["lon"]}
            _poi_cache_put(n, rec)
            return {"name": n, "lat": top["lat"], "lon": top["lon"],
                    "country": "CN", "poi": True}
    except Exception:
        pass
    hit = [k for k in cities if n and (n in k or k in n)]
    if len(hit) == 1:
        # 走到模糊命中 = POI 未命中、地名被降级为城市——带 fuzzy 标记，
        # 下游（route_card 等）据此出 warn，不再静默。
        return {"name": hit[0], "fuzzy": True, **cities[hit[0]]}
    return None


# ---------------------------------------------------------------- 1 quota_status
@mcp.tool()
def quota_status() -> dict:
    """额度仪表盘：各源各桶余额/周期、负标冷却状态、本月付费消耗与预算余量。"""
    p = _p()
    data = registry.load(p["manifests"])
    s = load_settings()
    led = ledger.QuotaLedger(p["ledger_db"])
    rows = []
    for e in data.get("providers", []):
        q = e.get("quota") or {}
        period, limit = (q.get("period") or "total"), q.get("limit")
        rem = (led.remaining(e["id"], period, limit)
               if (limit and period in ("month", "day", "total")) else None)
        cooling = sorted(
            c for c in e.get("capabilities", [])
            if negmark.is_banned(p["negmark_db"], e["id"], c))
        rows.append({
            "provider": e["id"], "status": e["status"], "tier": e["tier"],
            "capabilities": e.get("capabilities", []),
            "quota": {"period": period, "limit": limit,
                      "remaining_free": rem, "mode": q.get("mode", "monthly")},
            "cooling_capabilities": cooling,
        })
    paid = led.paid_month_cny()
    out = canon.ok({
        "providers": rows,
        "paid": {"month_cny": round(paid, 2), "budget_cny": s.monthly_paid_budget_cny,
                 "remaining_cny": round(max(0.0, s.monthly_paid_budget_cny - paid), 2)},
        "external": data.get("external", []),
    }, meta={"note": "账本为自记口径；OpenSky 响应头为真值，其余以各控制台为准"})
    cards.quota_card(out)
    return out


# ------------------------------------------------------------ 2 provider_admin
@mcp.tool()
def provider_admin(action: str, provider: str = "", reason: str = "",
                   period: str = "month", limit: int = 0, mode: str = "monthly",
                   capability: str = "", order: list[str] | None = None,
                   monthly_cny: float = 0, admin_key: str = "") -> dict:
    """对话级维护：list / enable / disable / set_quota / reorder / set_budget。
    变更类 action 需 admin_key（管理密码）；disable 付费源、set_budget 先向用户确认。"""
    p = _p()
    s = load_settings()
    if action == "list":
        return quota_status()
    if action in _ADMIN_MUTATING:
        gate = _require_admin(admin_key)
        if gate:
            return gate
    if action == "enable":
        return canon.ok({"enabled": registry.enable(p["manifests"], provider)},
                        meta={"note": reason})
    if action == "disable":
        return canon.ok({"disabled": registry.disable(p["manifests"], provider, reason)},
                        meta={"note": reason})
    if action == "set_quota":
        return canon.ok({"updated": registry.set_quota(
            p["manifests"], provider, period, limit, mode)})
    if action == "reorder":
        return canon.ok({"updated": registry.reorder(p["manifests"], capability,
                                                     order or [])})
    if action == "set_budget":
        hard_max = float(s.extra.get("budget_hard_max_cny",
                                     s.monthly_paid_budget_cny * 10))
        if monthly_cny > hard_max:
            return canon.error(canon.E_BUDGET_EXHAUSTED, hint=
                               f"{monthly_cny} 超过硬上限 {hard_max}，请改小或修改配置")
        f = p["manifests"].parent / "settings.yaml"
        cur = {}
        if f.exists():
            cur = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        cur["monthly_paid_budget_cny"] = monthly_cny
        f.write_text(yaml.safe_dump(cur, allow_unicode=True, sort_keys=False),
                     encoding="utf-8")
        return canon.ok({"monthly_paid_budget_cny": monthly_cny}, meta={"note": reason})
    return canon.error(canon.E_NO_MATCH, hint=f"未知 action={action}")


# ---------------------------------------------------------------- 3 airline_kb
@mcp.tool()
def airline_kb(action: str = "list", iata: str = "", patch: dict | None = None,
               alias: str = "", tag: str = "", by: str = "agent",
               reason: str = "", admin_key: str = "") -> dict:
    """航司知识库：list / get / set（必带 by+reason，append-only 修订）/
    unset_hint(tag) / add_alias。变更类 action 需 admin_key；安全评级类知识拒收。"""
    p = _p()
    if action in ("set", "unset_hint", "add_alias"):
        gate = _require_admin(admin_key)
        if gate:
            return gate
    if action == "list":
        return canon.ok({"airlines": kb_store.load_kb(p["kb"])})
    if action == "get":
        e = kb_store.get_airline(p["kb"], iata)
        return canon.ok(e) if e else canon.error(
            canon.E_NO_MATCH, hint=f"KB 无 {iata} 条目；unknown → 🌐 网页兜底")
    if action == "set":
        joined = " ".join(str(v) for v in (patch or {}).values() if isinstance(v, str))
        if "安全" in joined and "评级" in joined:
            return canon.error(canon.E_NO_MATCH,
                               hint="安全评级类知识拒收（主观/时效风险），走 🌐 现查现标来源")
        try:
            return canon.ok(kb_store.set_airline(p["kb"], patch or {}, by, reason))
        except ValueError as ve:
            return canon.error(canon.E_NO_MATCH, hint=str(ve))
    if action == "unset_hint":
        e = kb_store.unset_hint(p["kb"], iata, tag, by, reason)
        return canon.ok(e) if e else canon.error(canon.E_NO_MATCH, hint=f"KB 无 {iata}")
    if action == "add_alias":
        e = kb_store.add_alias(p["kb"], iata, alias, by, reason)
        return canon.ok(e) if e else canon.error(canon.E_NO_MATCH, hint=f"KB 无 {iata}")
    return canon.error(canon.E_NO_MATCH, hint=f"未知 action={action}")


# -------------------------------------------------------------- 4 resolve_place
@mcp.tool()
def resolve_place(name: str) -> dict:
    """地点解析：中文名→坐标/国家/码（五码注册表扩建中）。"""
    c = _resolve_city(name)
    if c:
        return canon.ok(c)
    return canon.error(canon.E_NO_MATCH, hint=f"未命中城市表: {name}")


# -------------------------------------------------------------- 5 flight_status
@mcp.tool()
def flight_status(flight_no: str = "", origin: str = "", destination: str = "",
                  date: str = "", detail: bool = False,
                  paid_calibrate: bool = False,
                  confirm_spend: bool = False,
                  dep_iata: str = "", arr_iata: str = "",
                  silent: bool = False) -> dict:
    """航班状态：计划/预计/实际三组时间+延误分钟+登机口/行李。
    填航班号（如 CA1501）即可；免费层覆盖当日（date 仅接受今天）。
    ⏱ 数据源覆盖矩阵（选通道前先看）：
      - 当日 ±10h 窗口内 → AirLabs 三组时刻+延误（免费 ★★★）
      - 当日窗口外/未来日期 → 免费源无动态，仅付费校准（飞常准）
      - 免费源按班号匹配、忽略航线 → 建议同时传 dep_iata/arr_iata 过滤
    paid_calibrate=true 走飞常准付费校准（消耗预算，>¥3 需 confirm_spend）。"""
    p = _p()
    dep_f = (dep_iata or "").strip().upper()
    arr_f = (arr_iata or "").strip().upper()
    if not date:
        date = today_cn()   # 缺省强制当日口径（北京时间——容器 UTC 时钟下 date.today 会差一天）
    if origin and destination and not flight_no:
        o, d = _resolve_city(origin), _resolve_city(destination)
        if o and d and o.get("country") == d.get("country") == "CN":
            km = eligibility.haversine_km(o["lat"], o["lon"], d["lat"], d["lon"])
            res = eligibility.decide(km, cross_border=False)
            if res.blocked("air"):
                return canon.error(
                    canon.E_NOT_APPLICABLE,
                    hint=f"航班已跳过：{res.reasons['air']}；建议 {'/'.join(res.rank)}",
                    meta={"eligibility": {"distance_km": res.distance_km,
                                          "eligible": res.eligible,
                                          "reasons": res.reasons}})
    chain = registry.active_chain(registry.load(p["manifests"]), "flight.status",
                                  negmark_db=p["negmark_db"])
    if not chain:
        return canon.error(canon.E_DATA_UNAVAILABLE,
                           hint="flight.status 无已启用数据源——配置 key 后 "
                                "provider_admin enable 即接入")
    out = dispatch.call_capability(
        "flight.status",
        {"flight_no": flight_no, "origin": origin, "destination": destination,
         "date": date, "detail": detail,
         "policy": {"paid_calibrate": paid_calibrate,
                    "confirm_spend": confirm_spend}},
        data_dir=data_dir())
    if not out.get("error"):
        flights = (out.get("data") or {}).get("flights") or []
        if dep_f or arr_f:
            matched = [x for x in flights
                       if (not dep_f
                           or (x.get("dep_iata") or "").upper() == dep_f)
                       and (not arr_f
                            or (x.get("arr_iata") or "").upper() == arr_f)]
            if not matched:
                unparseable = any(
                    not ((x.get("dep_iata") or "").strip()
                         or (x.get("arr_iata") or "").strip())
                    and x.get("parse_ok") is False for x in flights)
                out = canon.error(
                    canon.E_NO_MATCH,
                    hint=("付费源返回未能归一化，暂无法核对航线（raw 已保留）——"
                          "请稍后重试或反馈" if unparseable else
                          f"航班号 {flight_no} 存在但航线不符（免费源按班号匹配、"
                          f"忽略航线）——请核对班号或换日期重查"))
                if not silent:
                    cards.empty_card(out, title=("结果归一化失败" if unparseable else "航线不匹配"),
                                     hint=out["error"].get("hint", ""))
                return out
            out["data"]["flights"] = matched
        al = ((out.get("data") or {}).get("flights") or [{}])[0].get("airline_iata")
        if al:
            kb = kb_store.get_airline(_p()["kb"], str(al))
            if kb and kb.get("hints"):
                out["meta"]["airline_hints"] = kb["hints"]
        if not silent:
            cards.status_card(out, date_given=bool(date))
    elif out["error"].get("code") == "CONFIRM_REQUIRED":
        cards.confirm_card(out, od=flight_no)
    elif out["error"].get("code") in (canon.E_NO_MATCH, canon.E_DATA_UNAVAILABLE,
                                      canon.E_NOT_VERIFIABLE_FREE):
        if not silent:
            cards.empty_card(out, title="状态暂不可得",
                             hint=out["error"].get("hint", ""),
                             actions=[{"id": "paid_calibrate",
                                       "label": "💰 付费校准动态",
                                       "confirm": True,
                                       "instruction": "flight_status 同参数 + "
                                                      "paid_calibrate=true——飞常准"
                                                      "任意日期班次动态，约¥0.5/次",
                                       "args": {"flight_no": flight_no,
                                                "date": date,
                                                "paid_calibrate": True}}]
                                 + cards.review_actions(flight_no,
                                                        dep_local_date=date))
    return out


# --------------------------------------------------- 5b flight_status_batch
@mcp.tool()
def flight_status_batch(flight_nos: list[str], date: str = "",
                        dep_iata: str = "", arr_iata: str = "",
                        paid_calibrate: bool = False,
                        confirm_spend: bool = False) -> dict:
    """批量航班状态：一次查询 N 个班号，每个命中班次出一张状态卡。
    多候选推荐场景用它替代逐班 flight_status（调用数从 N 降到 1）。
    date 缺省=今天（免费源缺省会返回最近完成班次，服务端强制当日口径）。
    dep_iata/arr_iata 航线过滤：不符的班号按未匹配跳过（不产卡），
    结果在 meta.skipped 里如实列出。"""
    p = _p()
    dep_f = (dep_iata or "").strip().upper()
    arr_f = (arr_iata or "").strip().upper()
    if not date:
        date = today_cn()   # 缺省=北京时间今天（免费源缺省会返回最近完成班次，服务端强制当日口径）
    nos = [n.strip().upper() for n in (flight_nos or []) if str(n).strip()]
    if not nos:
        return canon.error(canon.E_NO_MATCH, hint="flight_nos 为空")
    chain = registry.active_chain(registry.load(p["manifests"]), "flight.status",
                                  negmark_db=p["negmark_db"])
    if not chain:
        return canon.error(canon.E_DATA_UNAVAILABLE,
                           hint="flight.status 无已启用数据源")
    cards_out: list[dict] = []
    _item_metas: list[dict] = []
    flights: list[dict] = []
    skipped: list[dict] = []
    for no in nos:
        try:
            out = dispatch.call_capability(
                "flight.status",
                {"flight_no": no, "origin": "", "destination": "",
                 "date": date, "detail": False,
                 "policy": {"paid_calibrate": paid_calibrate,
                            "confirm_spend": confirm_spend}},
                data_dir=data_dir())
        except Exception as e:                       # 单班失败不拖垮批次
            skipped.append({"flight_no": no, "reason": str(e)[:80]})
            continue
        if out.get("error"):
            skipped.append({"flight_no": no,
                            "reason": out["error"].get("hint")
                            or out["error"].get("code")})
            continue
        fl = (out.get("data") or {}).get("flights") or []
        matched = [x for x in fl
                   if (not dep_f or (x.get("dep_iata") or "").upper() == dep_f)
                   and (not arr_f or (x.get("arr_iata") or "").upper() == arr_f)]
        if not matched:
            unparseable = any(
                not ((x.get("dep_iata") or "").strip()
                     or (x.get("arr_iata") or "").strip())
                and x.get("parse_ok") is False for x in fl)
            skipped.append({"flight_no": no,
                            "reason": "付费源返回未能归一化，无法按航线过滤"
                            if unparseable else "航线不符（免费源按班号匹配）"})
            continue
        sub = {"data": {"flights": matched},
               "meta": out.get("meta") or {}}
        cards.status_card(sub)
        flights.extend(sub["data"]["flights"])
        if sub.get("meta", {}).get("card"):
            cards_out.append(sub["meta"]["card"])
    out = canon.ok({"flights": flights,
                    "matched": len(flights), "skipped": skipped})
    out.setdefault("meta", {})["cards"] = cards_out
    cache_hits = sum(1 for s in _item_metas if s.get("cache") == "hit")
    paid_cny = sum(float((s.get("cost") or {}).get("paid_cny") or 0)
                   for s in _item_metas)
    free_calls = sum(int((s.get("cost") or {}).get("free_calls") or 0)
                     for s in _item_metas)
    out["meta"]["sources"] = [{"provider": "batch", "freshness": "live",
                               "calls": len(nos),
                               "note": "calls=候选数；真实执行量见 meta.cost"}]
    out["meta"]["cost"] = {"free_calls": free_calls, "paid_cny": paid_cny,
                           "cache_hits": cache_hits}
    return out


def _apply_trip_rules(prices: list[dict], trip_type: str, norms: dict) -> list[dict]:
    """双场景规则（docs/10 场景分型）：incentive 压后廉航/红眼；personal 只标注。"""
    tr = (norms or {}).get("trip_rules") or {}
    lcc = set(tr.get("lcc_airlines") or [])
    lo, hi = (tr.get("red_eye_hour_range") or [0, 6])
    for pr in prices:
        dep = str(pr.get("departure_at") or "")
        hour = int(dep[11:13]) if len(dep) >= 13 and dep[11:13].isdigit() else None
        pr["lcc"] = (pr.get("airline_iata") or "") in lcc
        pr["red_eye"] = hour is not None and int(lo) <= hour < int(hi)
    if trip_type == "incentive":
        prices.sort(key=lambda p: (p["lcc"], p["red_eye"]))
    return prices


# -------------------------------------------------------------- 6 flight_price
@mcp.tool()
def flight_price(origin: str, destination: str, date: str = "",
                 cabin: str = "any", currency: str = "CNY",
                 paid_calibrate: bool = False,
                 confirm_spend: bool = False,
                 trip_type: str = "personal") -> dict:
    """机票参考价（缓存价，国际线为主）：两城市名（如 成都→曼谷）。
    trip_type=personal 只标注 / incentive（奖励旅游）廉航与红眼标注并压后。
    正式成交价需付费校准（paid_calibrate=true，超阈值需 confirm_spend）；
    国内线免费层无价源，paid_calibrate=true 走飞常准（价格窗约 45 天）。
    免费缓存价带归属 lint：命中红旗下班号/航司/时刻仅参考（attribution_trust=low）。"""
    p = _p()
    km = None                                # 资格引擎距离；o/d 未解析时 lint 不判 L3
    o, d = _resolve_city(origin), _resolve_city(destination)
    if o and d:
        cross = o.get("country") != d.get("country")
        km = eligibility.haversine_km(o["lat"], o["lon"], d["lat"], d["lon"])
        res = eligibility.decide(km, cross_border=cross)
        if res.blocked("air"):
            return canon.error(
                canon.E_NOT_APPLICABLE,
                hint=f"航班票价已跳过：{res.reasons.get('air', '资格引擎判定不可用')}",
                meta={"eligibility": {"distance_km": res.distance_km,
                                      "eligible": res.eligible, "rank": res.rank}})
        if not cross and not paid_calibrate:
            return canon.error(
                canon.E_DATA_UNAVAILABLE,
                hint="国内航线无免费价格源（已证伪）；精确价走飞常准校准——"
                     "paid_calibrate=true 触发预算闸门")
        # 国内 + paid_calibrate：放行进 dispatch（variflight 已入链，精确价可达；
        # travelpayouts 对国内线自会 NO_MATCH，不构成假数据）
    chain = registry.active_chain(registry.load(p["manifests"]), "flight.price",
                                  negmark_db=p["negmark_db"])
    if not chain:
        return canon.error(canon.E_DATA_UNAVAILABLE,
                           hint="flight.price 无已启用免费源（Travelpayouts 待 token）")
    codes = {"成都": "CTU", "成都天府": "TFU", "南昌": "KHN",
             "北京": "BJS", "上海": "SHA", "广州": "CAN", "深圳": "SZX",
             "昆明": "KMG", "西安": "SIA", "杭州": "HGH", "重庆": "CKG", "厦门": "XMN",
             "南京": "NKG", "武汉": "WUH", "长沙": "CSX", "郑州": "CGO", "青岛": "TAO",
             "哈尔滨": "HRB", "乌鲁木齐": "URC", "海口": "HAK", "三亚": "SYX",
             "伦敦": "LON", "曼谷": "BKK", "莫斯科": "MOW", "东京": "TYO", "首尔": "SEL",
             "新加坡": "SIN", "纽约": "NYC", "巴黎": "PAR", "香港": "HKG", "台北": "TPE"}
    ocode = (o or {}).get("iata") or (codes.get(o["name"]) if o else None)
    dcode = (d or {}).get("iata") or (codes.get(d["name"]) if d else None)
    if not (ocode and dcode):
        no_iata = (o or d) and (
            (o and not ocode) or (d and not dcode))
        if no_iata:
            return canon.error(canon.E_NO_MATCH,
                               hint="该城市无民航机场或码表未收录（就近机场见 "
                                    "resolve_place / 资格引擎会建议高铁）")
    out = dispatch.call_capability(
        "flight.price",
        {"origin": origin, "destination": destination,
         "origin_code": ocode, "destination_code": dcode,
         "date": date, "cabin": cabin, "currency": currency,
         "policy": {"paid_calibrate": paid_calibrate,
                    "confirm_spend": confirm_spend}},
        data_dir=data_dir())
    if not out.get("error"):
        # 双场景规则（docs/10 分型）+ L3 基线附着（攒满 5 样本起报）+ 卡片编排
        prices = (out.get("data") or {}).get("prices") or []
        norms_f = _p()["norms"]
        norms = (yaml.safe_load(norms_f.read_text(encoding="utf-8"))
                 if norms_f.exists() else {}) or {}
        _apply_trip_rules(prices, trip_type, norms)
        # 归属 lint（2026-10-01 立项）：免费缓存价归属字段结构性不可信——
        # 只降级不删数据；命中后 meta.flags + confidence 降 low，卡片附警示
        if (out.get("data") or {}).get("price_type") != "calibrated" and prices:
            fl = attribution.lint_prices(
                prices, origin_code=ocode, destination_code=dcode,
                distance_km=km,
                known_direct=attribution.load_known_direct(
                    data_dir() / "known_direct.yaml"))
            if fl:
                out["meta"]["flags"] = fl
                out["meta"]["confidence"] = "low"
                out["meta"].setdefault("notes", []).append(
                    "归属 lint 命中（" + "、".join(fl) + "）：班号/航司/时刻为缓存"
                    "口径，直飞结论需时刻表源或付费校准复核")
        if trip_type == "incentive":
            out["meta"]["trip_type"] = "incentive"
            out["meta"].setdefault("notes", []).append(
                "奖励旅游口径：廉航/红眼已逐条标注并压后（规则见 norms.yaml trip_rules，"
                "agent 可维护）")
        from app.core import baseline
        st = baseline.stats(data_dir() / "baseline.db", ocode, dcode)
        if st:
            out["meta"]["baseline_90d"] = st
        # 查询即采集：成功价格自动入 L3 基线（软路由价值核心）
        try:
            baseline.record(data_dir() / "baseline.db", ocode, dcode, prices)
        except Exception:
            pass
        cards.price_card(out, od=f"{origin}→{destination}",
                         trip_type=trip_type, norms=norms,
                         origin=origin, destination=destination, date=date)
        if out.get("meta", {}).get("flags"):
            (out["meta"].get("card") or {}).setdefault("notices", []).append(
                {"level": "warn", "icon": "lint",
                 "text": "免费缓存价归属未核验（" + "、".join(out["meta"]["flags"])
                         + "）——班次信息以订票平台/付费校准为准"})
    elif out["error"].get("code") == "CONFIRM_REQUIRED":
        cards.confirm_card(out, od=f"{origin}→{destination}")
    elif out["error"].get("code") in (canon.E_NO_MATCH, canon.E_DATA_UNAVAILABLE,
                                      canon.E_NOT_VERIFIABLE_FREE):
        # 空态卡挂付费校准动作：国内无免费价源/免费窗外——付费层恰好是补位真源
        cards.empty_card(out, title="机票价格暂不可得",
                         hint=out["error"].get("hint", ""),
                         actions=[{"id": "paid_calibrate",
                                   "label": "💰 付费校准（信息+价格）",
                                   "confirm": True,
                                   "instruction": "flight_price 同参数重查 + "
                                                  "paid_calibrate=true——飞常准精确价约"
                                                  "¥0.5/次，一次返回价格+航班号/起降时刻/"
                                                  "航站楼/机型（45 天窗内）",
                                   "args": {"origin": origin,
                                            "destination": destination,
                                            "date": date,
                                            "paid_calibrate": True}}])
    return out


# -------------------------------------------------------------- 7 flight_verify
@mcp.tool()
def flight_verify(flight_no: str, date: str = "", claim: str = "") -> dict:
    """飞行前确定性核验：计划层（AirLabs）× 观测层（OpenSky ADS-B）交叉。

    在飞航班自动追加观测复核；一致 → 高置信；未捕获 → 如实标注（覆盖缺口 ≠ 异常）。
    """
    dd = data_dir()
    st = dispatch.call_capability(
        "flight.status", {"flight_no": flight_no, "date": date, "policy": {}},
        data_dir=dd)
    if st.get("error"):
        return {"data": None, "meta": st.get("meta", {}),
                "error": {"code": "VERIFY_INCOMPLETE",
                          "provider": st["error"].get("provider"),
                          "hint": f"计划层不可得：{st['error']['hint']}"}}
    flight = (st["data"].get("flights") or [{}])[0]
    status_val = (flight.get("status") or {}).get("value")
    observe, obs_note = None, None
    if status_val == "active":
        callsign = flight.get("flight_icao") or flight.get("flight_no")
        obs = dispatch.call_capability("flight.observe",
                                       {"callsign": callsign, "policy": {}},
                                       data_dir=dd)
        if obs.get("error"):
            obs_note = f"观测层不可得：{obs['error']['hint']}"
        else:
            observe = obs["data"]
    if status_val == "active":
        if observe and observe.get("observed"):
            consistency = "一致：计划层 active ∧ 观测层捕获在飞目标 → 高置信"
        elif observe is not None:
            consistency = ("计划层 active ∧ 观测层未捕获——ADS-B 覆盖缺口 ≠ 异常，"
                           "置信降为 medium，可复测")
        else:
            consistency = f"仅计划层（观测层不可得：{obs_note}）"
    else:
        consistency = f"{status_val}：终态/未起飞，计划层即结论，观测层不适用"

    free_calls = (st.get("meta", {}).get("cost", {}).get("free_calls", 0)
                  + (1 if observe else 0))
    meta = {"sources": st.get("meta", {}).get("sources", [])
            + ([{"provider": "opensky", "freshness": "live", "calls": 1}]
               if observe is not None else []),
            "confidence": ("high" if (status_val != "active"
                                      or (observe and observe.get("observed")))
                           else "medium"),
            "cost": {"free_calls": free_calls, "paid_cny": 0}}
    return canon.ok({"flight": flight, "observe": observe, "obs_note": obs_note,
                     "consistency": consistency, "claim": claim}, meta=meta)


# -------------------------------------------------------------- 8 route_ground
@mcp.tool()
def route_ground(origin: str, destination: str, mode: str = "auto",
                 depart_time: str = "", plate: str = "",
                 ev_rated_range_km: int = 0, detail: bool = False,
                 with_attractions: bool = False) -> dict:
    """地面交通：境内走高德驾车（限行/EV/官方打车价）；境外走 Google
    （transit 默认=火车地铁巴士，支持 driving/walking）。境外段门到门覆盖。
    出行档案：origin/destination 可用管理面板配置的别名（家/公司/自定义）。"""
    _hit = _profile_mod.resolve_alias(data_dir(), origin)
    if _hit:
        origin = _hit[0]
    _hit = _profile_mod.resolve_alias(data_dir(), destination)
    if _hit:
        destination = _hit[0]
    _s = load_settings()
    plate = plate or _s.plate                       # 车辆画像默认（settings.yaml）
    ev_rated_range_km = ev_rated_range_km or _s.ev_rated_range_km
    o, d = _resolve_city(origin), _resolve_city(destination)
    if not o or not d:
        return canon.error(canon.E_NO_MATCH,
                           hint="城市码表未收录（五码注册表扩建后放开）")
    # B5：地名降级如实告警（POI 未命中 → 按城市中心起算，距离/时长有偏差）
    degrade = [f"出发地「{origin}」未解析到精确 POI，已按城市「{o['name']}」中心起算"
               if o.get("fuzzy") else None,
               f"目的地「{destination}」未解析到精确 POI，已按城市「{d['name']}」中心起算"
               if d.get("fuzzy") else None]
    degrade = [t for t in degrade if t]
    o_c, d_c = o.get("country"), d.get("country")
    if o_c != d_c:
        return canon.error(canon.E_NOT_APPLICABLE,
                           hint="跨境驾驶不存在：飞行段用 flight_price/flight_status；"
                                "境外地面段请单独查询（如 route_ground 曼谷→芭提雅）")
    if o_c == "CN":
        if mode in ("bus", "transit", "train", "bus_train"):
            return canon.error(canon.E_DATA_UNAVAILABLE,
                               hint="境内公交/火车规划属 Phase 2 后段（高德公交含车次价格；"
                                    "火车另接 12306）")
        km = eligibility.haversine_km(o["lat"], o["lon"], d["lat"], d["lon"])
        res = eligibility.decide(km, cross_border=False)
        if res.blocked("drive"):
            return canon.error(canon.E_NOT_APPLICABLE, hint=res.reasons["drive"])
        out = dispatch.call_capability(
            "ground.route",
            {"origin_wgs": [o["lon"], o["lat"]],
             "destination_wgs": [d["lon"], d["lat"]],
             "plate": plate, "ev_rated_range_km": ev_rated_range_km,
             "policy": {}},
            data_dir=data_dir())
        if with_attractions:
            try:
                po = dispatch.call_capability(
                    "poi.around",
                    {"location_wgs": [d["lon"], d["lat"]],
                     "keywords": "风景名胜", "radius_m": 25000,
                     "types": "110000", "policy": {}},
                    data_dir=data_dir())
                out.setdefault("data", {})["attractions"] = (
                    (po.get("data") or {}).get("pois") or [])[:6]
            except Exception:
                pass
        cards.route_card(out, o_name=o["name"], d_name=d["name"],
                         o=o, d=d, intl=False, degrade=degrade)
        return out
    # —— 境外段：Google Maps（transit 默认 = 火车/地铁/巴士，机场↔市区高频）——
    gmode = mode if mode in ("transit", "driving", "walking", "bicycling") else "transit"
    out = dispatch.call_capability(
        "ground.route.intl",
        {"origin_wgs": [o["lon"], o["lat"]],
         "destination_wgs": [d["lon"], d["lat"]],
         "mode": gmode, "policy": {}},
        data_dir=data_dir())
    cards.route_card(out, o_name=o["name"], d_name=d["name"],
                     o=o, d=d, intl=True, degrade=degrade)
    return out


# ------------------------------------------------------------ 9 weather_context
@mcp.tool()
def weather_context(location: str, date: str = "") -> dict:
    """天气上下文：≤16 天 → 预报层（逐日）；>16 天 → 气候常态层（月度投影）。
    分层标签永不混用；date 缺省=今天。"""
    o = _resolve_city(location)
    if not o:
        return canon.error(canon.E_NO_MATCH, hint="城市码表未收录该地点")
    out = dispatch.call_capability(
        "weather.context",
        {"lat": o["lat"], "lon": o["lon"], "date": date, "policy": {}},
        data_dir=data_dir())
    cards.weather_card(out, location=o.get("name", location))
    return out


# ---------------------------------------------------------- 10 itinerary_plan
@mcp.tool()
def itinerary_plan(legs: list[dict]) -> dict:
    """全程行程卡：多段（✈️飞机/🚄高铁/🚗自驾）拼装为一条时间线。

    legs 按时间升序，每段 {mode, from, to, depart, arrive}：
      - mode: "flight" | "rail" | "drive"（flight/rail 为固定锚点）
      - depart/arrive: ISO 时刻（含时区偏移，如 2026-10-02T11:30:00+08:00）
    固定锚点自动反推到站 deadline（✈️默认提前 60min、🚄提前 30min，
    norms.buffers 可调）与前一地面段的最迟出发时刻。 depart/arrive 亦可只给一段
    + duration_min（另一侧自动推算）。"""
    norms = {}
    try:
        nf = data_dir() / "norms.yaml"
        if nf.exists():
            norms = yaml.safe_load(nf.read_text(encoding="utf-8")) or {}
    except Exception:
        norms = {}
    if not legs or not isinstance(legs, list):
        return canon.error(canon.E_NO_MATCH,
                           hint="legs 必须为非空数组：[{mode, from, to, depart, arrive}]")
    fixed = [l for l in legs
             if (l.get("mode") or "").lower() in ("flight", "rail")]
    if not fixed:
        # 纯市内/自驾多日行程放行：跨度 >24h 视为多日游（无锚点也可出全程卡）
        def _ts(v):
            try:
                return __import__("datetime").datetime.fromisoformat(
                    str(v).replace("Z", "+00:00"))
            except Exception:
                return None
        tss = [t for t in (_ts(l.get("depart")) for l in legs) if t]
        if not (tss and (max(tss) - min(tss)).total_seconds() > 86400):
            return canon.error(
                canon.E_NO_MATCH,
                hint="至少需要一段固定锚点（flight/rail）——单日纯市内行程"
                     "请直接输出建议；多日行程（跨度>24h）可直接调用")
    out: dict = {"data": {"legs": legs}}
    cards.itinerary_card(out, legs=legs, norms=norms)
    return out


# ------------------------------------------------------------- 11 poi_search
@mcp.tool()
def poi_search(keywords: str, city: str = "") -> dict:
    """POI 搜索（高德 text）：机场/火车站/景点/酒店等非城市地名解析。
    返回 [{name, address, lat, lon(WGS), type}]；结果自动进缓存供行程/地图复用。"""
    if not keywords.strip():
        return canon.error(canon.E_NO_MATCH, hint="keywords 为空")
    out = dispatch.call_capability(
        "poi.search", {"keywords": keywords.strip(), "city": city.strip(),
                       "policy": {}},
        data_dir=data_dir())
    if not out.get("error"):
        pois = (out.get("data") or {}).get("pois") or []
        if pois:
            top = pois[0]
            _poi_cache_put(keywords.strip(),
                           {"lat": top["lat"], "lon": top["lon"]})
    return out


# -------------------------------------------------------- 12 trip_recommend
@mcp.tool()
def trip_recommend(summary: dict) -> dict:
    """行程推荐汇总卡：模型交结构化结论，服务端出卡（模型不做任何排版）。
    summary: {scenario: str, picks: [{label, title, reason, tags?: [str]}],
              notes?: [str], total_cost_text?: str}
    picks 按推荐序排列（第 1 个为首选）。"""
    if not isinstance(summary, dict) or not summary.get("picks"):
        return canon.error(canon.E_NO_MATCH,
                           hint="summary.picks 不能为空"
                                "（[{label,title,reason,tags?}] 按推荐序）")
    out: dict = {"data": summary}
    cards.recommend_card(out, summary=summary)
    return out


# -------------------------------------------------------- 13 attraction_search
@mcp.tool()
def attraction_search(city: str, keyword: str = "") -> dict:
    """景点知识库查询（ChinaTravel 沙盒数据，覆盖
    杭州/上海/苏州/重庆/广州/北京/武汉/成都/南京/深圳 十城头部景点）。
    返回 name/type/门票/开放时间/建议游览时长（min~max）。
    规划多日行程前必查——建议时长是排程可行性的硬依据。
    ⚠️ 必须带 keyword 检索经典景点（如 熊猫/博物馆/古迹/古镇/山）——
    无 keyword 时按价格降序，会偏向高价游乐项目而非经典景区。"""
    if not city.strip():
        return canon.error(canon.E_NO_MATCH, hint="city 为空")
    rows = china_store.search(city.strip(), keyword.strip())
    if not rows:
        return canon.error(
            canon.E_NO_MATCH,
            hint=f"{city} 不在知识库覆盖城市（{'/'.join(chinatravel.CITIES)}）"
                 f"或无匹配——该城市行程请按通用规则排程并用联网搜索核验开放信息")
    return canon.ok({"city": city, "count": len(rows), "attractions": rows})


# ----------------------------------------------------------- 14 plan_validate
@mcp.tool()
def plan_validate(city: str, items: list[dict],
                  day_start: str = "08:00", day_end: str = "18:00") -> dict:
    """行程可行性校验（多日行程必调）：
    items=[{name, start_time?: 'HH:MM', end_time?: 'HH:MM', minutes?: 数}]。
    校验：景点存在性 / 开闭园冲突 / 建议游览时长 vs 排入时长 /
    当日合计 vs 时间窗。只出违规清单（advisory），绝不改行程。
    知识库未覆盖的城市返回 skipped 说明——按通用规则排程。"""
    if not city.strip() or not items:
        return canon.error(canon.E_NO_MATCH,
                           hint="city 与 items 必填"
                                "（items=[{name, start_time?, end_time?, minutes?}]）")
    out = canon.ok(china_store.validate_day(city.strip(), items,
                                      day_start or "08:00",
                                      day_end or "18:00"))
    v = out.get("data") or {}
    violations = v.get("violations") or []
    notices = [{"level": "warn", "icon": "redeye", "text": x.get("text")}
               for x in violations]
    if v.get("skipped"):
        skipped = v["skipped"]
        text = (skipped if isinstance(skipped, str)
                else "、".join(map(str, skipped)))
        notices.append({"level": "info", "icon": "anchor",
                        "text": f"知识库未覆盖：{text}"})
    card = cards._envelope("validate",
                           f"行程可行性 · {city}",
                           {"city": city, "checked": v.get("checked", 0),
                            "skipped": v.get("skipped"),
                            "window": v.get("window"),
                            "violations": violations},
                           notices=notices)
    card["id"] = cards.stage_card(card)
    out.setdefault("meta", {})["card"] = card
    return out
