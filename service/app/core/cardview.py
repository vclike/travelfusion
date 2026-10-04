"""卡片 → 人读 HTML 详情页（/cards/{id}/view）。

服务端负责可读性：侧栏 iframe 直接展示排版好的中文详情，替代原始 JSON。
设计约束：零依赖（内联 CSS）、深浅色自适应（prefers-color-scheme）、按卡型分模板。
"""
import html as _html
from datetime import datetime

_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  margin: 0; padding: 20px; line-height: 1.55; font-size: 14px;
  background: #fff; color: #1f2328; }
@media (prefers-color-scheme: dark) {
  body { background: #14161a; color: #e6e6e6; }
  .sec, table { border-color: #33373d; }
  .k { color: #9aa0a6; } .muted { color: #9aa0a6; }
}
h1 { font-size: 18px; margin: 0 0 4px; }
.sub { color: #888; font-size: 12px; margin-bottom: 16px; }
.sec { border: 1px solid #e1e4e8; border-radius: 10px; padding: 12px 14px;
  margin-bottom: 12px; }
.sec h2 { font-size: 13px; margin: 0 0 8px; color: #57606a;
  text-transform: none; }
.kv { display: grid; grid-template-columns: 96px 1fr; gap: 4px 10px; }
.k { color: #888; }
table { width: 100%; border-collapse: collapse; margin-top: 6px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid #e1e4e8;
  font-size: 13px; vertical-align: top; }
th { color: #888; font-weight: 500; }
.pill { display: inline-block; padding: 1px 8px; border-radius: 10px;
  font-size: 12px; border: 1px solid #d0d7de; margin-left: 6px; }
.pill.warn { border-color: #d4a72c66; color: #9a6700; }
.pill.ok { border-color: #2da44e66; color: #1a7f37; }
.notice { border-left: 3px solid #d4a72c; padding: 6px 10px; margin: 8px 0;
  font-size: 13px; }
.rank { font-size: 16px; font-weight: 700; color: #0969da; }
.top { color: #0969da; font-weight: 600; }
.muted { color: #888; font-size: 12px; }
"""


def _e(v) -> str:
    return _html.escape(str(v)) if v is not None else "—"


def _fmt_iso(v: str) -> str:
    try:
        dt = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return dt.strftime("%m-%d %H:%M") + (
            f" ({dt.strftime('%z')[:3]}时区)" if dt.tzinfo else "")
    except Exception:
        return _e(v)


def _notices(card) -> str:
    out = []
    for n in card.get("notices") or []:
        icon = "⚠️" if n.get("level") == "warn" else "ℹ️"
        out.append(f'<div class="notice">{icon} {_e(n.get("text"))}</div>')
    return "".join(out)


def _actions(card) -> str:
    acts = card.get("actions") or []
    if not acts:
        return ""
    rows = "".join(
        f'<div class="muted">可执行动作：{_e(a.get("label"))}'
        f'{(" — " + _e(a.get("instruction"))) if a.get("instruction") else ""}</div>'
        for a in acts)
    return f'<div class="sec"><h2>下一步</h2>{rows}</div>'


def _generic(payload: dict) -> str:
    rows = "".join(
        f'<div class="kv"><div class="k">{_e(k)}</div><div>{_e(v)}</div></div>'
        for k, v in payload.items() if not isinstance(v, (dict, list)))
    tables = ""
    for k, v in payload.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            head = list(v[0].keys())
            trs = "".join("<tr>" + "".join(
                f"<td>{_e(r.get(h))}</td>" for h in head) + "</tr>" for r in v)
            tables += (f"<h2>{_e(k)}</h2><table><tr>" + "".join(
                f"<th>{_e(h)}</th>" for h in head) + f"</tr>{trs}</table>")
    return f'<div class="sec">{rows}</div>{tables}'


def _status(card) -> str:
    p = card.get("payload") or {}
    tl = p.get("timeline") or {}
    rows = ""
    for side, label in (("dep", "起飞"), ("arr", "到达")):
        t = tl.get(side) or {}
        tz = p.get("dep_tz" if side == "dep" else "arr_tz") or ""
        for grp, tag in (("actual", "实际"), ("estimated", "预计"),
                         ("scheduled_utc", "计划")):
            v = t.get(grp)
            if v:
                rows += (f"<tr><td>{label} · {tag}</td><td>{_fmt_iso(v)}"
                         f"{'（' + _e(tz) + '）' if tz else ''}</td></tr>")
    delay = p.get("dep_delay_min")
    pill = (f'<span class="pill warn">延误 +{_e(delay)}min</span>'
            if isinstance(delay, (int, float)) and delay > 0
            else '<span class="pill ok">准点</span>'
            if delay is not None else "")
    bits = " ｜ ".join(x for x in (
        f"航站楼 {p.get('dep_terminal')}→{p.get('arr_terminal')}"
        if p.get("dep_terminal") and p.get("arr_terminal") else "",
        f"行李转盘 {p.get('baggage')}" if p.get("baggage") else "",
        f"登机口 {p.get('gate', {}).get('dep')}"
        if (p.get("gate") or {}).get("dep") else "") if x)
    total = (f'<div class="kv"><div class="k">总飞行时长</div><div>'
             f'{p.get("duration_min", 0) // 60}h{p.get("duration_min", 0) % 60:02d}m'
             f"</div></div>" if p.get("duration_min") else "")
    return (f'<div class="sec"><h2>时间 {pill}</h2>'
            f"<table>{rows}</table></div>"
            f"{total}"
            + (f'<div class="sec"><div>{_e(bits)}</div></div>' if bits else ""))


def _price(card) -> str:
    p = card.get("payload") or {}
    rows = "".join(
        f"<tr><td>{r.get('rank')}"
        f"{' ⭐' if r.get('recommended') else ''}</td>"
        f"<td>{_e(r.get('airline_name') or r.get('airline_iata'))}"
        f" {_e(r.get('flight_no'))}</td>"
        f"<td>{_fmt_iso(r.get('dep_local'))}</td>"
        f"<td>{'¥' if r.get('currency') == 'CNY' else ''}{r.get('amount', '')}"
        f"{'（需付费校准）' if not r.get('amount') else ''}</td></tr>"
        for r in p.get("prices") or [])
    base = p.get("baseline")
    base_html = (f'<div class="muted">90 天低位 ¥{_e(base.get("low"))} / '
                 f'常态 ¥{_e(base.get("mid"))} / 高位 ¥{_e(base.get("high"))}'
                 f"</div>" if base else "")
    return (f'<div class="sec"><table><tr><th>#</th><th>航班</th>'
            f"<th>起飞（当地）</th><th>价格</th></tr>{rows}</table>"
            f"{base_html}</div>")


def _route(card) -> str:
    p = card.get("payload") or {}
    segs = "".join(
        f"<tr><td>{_e(s.get('name'))}</td><td>{s.get('km')} km</td>"
        f"<td>{s.get('pct')}%</td></tr>"
        for s in p.get("segments") or p.get("roads") or [])
    dur_txt = (_e(p.get("duration_text"))
               or f"{p.get('duration_min')} min")
    attr = "".join(f"<li>{_e(a.get('name'))}"
                   f"{(' — ' + _e(a.get('address')[:30])) if a.get('address') else ''}</li>"
                   for a in p.get("attractions") or [])
    return (f'<div class="sec"><div class="kv">'
            f'<div class="k">里程</div><div>{p.get("distance_km")} km</div>'
            f'<div class="k">用时</div><div>{dur_txt}</div>'
            f'<div class="k">过路费</div><div>{_e(p.get("tolls_cny"))}</div>'
            f'<div class="k">打车估价</div><div>{_e(p.get("taxi_estimate_cny"))}'
            f"（{_e(p.get('taxi_estimate_basis'))}）</div></div></div>"
            + (f'<div class="sec"><h2>主要路段</h2><table><tr><th>路段</th>'
               f"<th>里程</th><th>占比</th></tr>{segs}</table></div>" if segs else "")
            + (f'<div class="sec"><h2>沿途/目的地景点</h2><ul>{attr}</ul></div>'
               if attr else ""))


def _itinerary(card) -> str:
    p = card.get("payload") or {}
    icon = {"flight": "✈️", "rail": "🚄", "drive": "🚗"}
    rows = ""
    for leg in p.get("legs") or []:
        fixed = "（固定）" if leg.get("fixed") else ""
        rows += (f"<tr><td>{icon.get(leg.get('mode'), '🚗')}</td>"
                 f"<td>{_e(leg.get('from'))} → {_e(leg.get('to'))}{fixed}</td>"
                 f"<td>{_fmt_iso(leg.get('depart'))}<br>"
                 f"{_fmt_iso(leg.get('arrive'))}</td>"
                 f"<td>{leg.get('duration_min')} min</td></tr>")
    anchors = "".join(
        f'<div class="notice">⏰ {_e(n.get("text"))}</div>'
        for n in p.get("notices") or [])
    span = (f'<div class="muted">全程 {p.get("span_min", 0) // 60}h'
            f'{p.get("span_min", 0) % 60:02d}m</div>' if p.get("span_min") else "")
    return (f'<div class="sec"><table><tr><th></th><th>段</th>'
            f"<th>时刻</th><th>时长</th></tr>{rows}</table>{span}</div>"
            f"{anchors}")


def _weather(card) -> str:
    p = card.get("payload") or {}
    return (f'<div class="sec"><div class="kv">'
            f'<div class="k">天气</div><div>{_e(p.get("weather"))}</div>'
            f'<div class="k">气温</div><div>{_e(p.get("t_range", ["", ""])[0])}'
            f" ~ {_e(p.get('t_range', ['', ''])[1])} °C</div>"
            f'<div class="k">降水</div><div>{_e(p.get("precip_mm"))} mm</div>'
            f"</div></div>")


def _recommend(card) -> str:
    p = card.get("payload") or {}
    rows = ""
    for i, pk in enumerate(p.get("picks") or []):
        tags = " ".join(f'<span class="pill">{_e(t)}</span>'
                        for t in pk.get("tags") or [])
        top = '<span class="top"> ⭐ 首推</span>' if i == 0 else ""
        rows += (f'<div class="sec"><span class="rank">{i + 1}</span>'
                 f"{top} <b>{_e(pk.get('title') or pk.get('label'))}</b><br>"
                 f"{_e(pk.get('reason'))}<br>{tags}</div>")
    return rows


_RENDERERS = {"status": _status, "price": _price, "route": _route,
              "itinerary": _itinerary, "weather": _weather,
              "recommend": _recommend}


# ─────────────────────────── 纯文本分享摘要（复制给他人用） ───────────────────────────
def _local_str(v: str, tz: str | None) -> str:
    """ISO → 当地时区 "MM-DD HH:MM"（无 tz 回退 UTC 标注）。"""
    try:
        from datetime import datetime as _dtc
        dt = _dtc.fromisoformat(str(v).replace("Z", "+00:00"))
        if tz:
            try:
                from zoneinfo import ZoneInfo
                dt = dt.astimezone(ZoneInfo(tz))
                return dt.strftime("%m-%d %H:%M")
            except Exception:
                pass
        return dt.strftime("%m-%d %H:%M") + " UTC"
    except Exception:
        return str(v)


def _t_status(card) -> str:
    p = card.get("payload") or {}
    tl = p.get("timeline") or {}
    lines = [f"✈️ {card.get('title')}（{p.get('airline_name') or p.get('airline_iata')}）"]
    for side, label in (("dep", "起飞"), ("arr", "到达")):
        t = tl.get(side) or {}
        v = t.get("actual") or t.get("estimated") or t.get("scheduled_utc")
        tag = "实际" if t.get("actual") else ("预计" if t.get("estimated") else "计划")
        if v:
            tz = p.get("dep_tz" if side == "dep" else "arr_tz")
            lines.append(f"{label}·{tag} {_local_str(v, tz)}（{label}地）")
    d = p.get("dep_delay_min")
    if isinstance(d, (int, float)) and d != 0:
        lines.append(f"{'延误 +' if d > 0 else '提前 '}{abs(int(d))}min")
    if p.get("dep_terminal") and p.get("arr_terminal"):
        lines.append(f"航站楼 {p.get('dep_terminal')}→{p.get('arr_terminal')}")
    if p.get("baggage"):
        lines.append(f"行李转盘 {p.get('baggage')}")
    if p.get("duration_min"):
        m = p["duration_min"]
        lines.append(f"总飞行时长 {m // 60}h{m % 60:02d}m")
    src = " · ".join(s.get("provider", "") for s in
                     (card.get("meta") or {}).get("sources") or [])
    if src:
        lines.append(f"数据源: {src}")
    return "\n".join(lines)


def _t_price(card) -> str:
    p = card.get("payload") or {}
    lines = [f"🎫 {card.get('title')}"]
    for r in p.get("prices") or []:
        cur = "¥" if r.get("currency") == "CNY" else (r.get("currency") or "")
        amt = f"{cur}{r.get('amount')}" if r.get("amount") else "价格需付费校准"
        dep = (r.get("dep_local") or "")[5:16].replace("T", " ")
        lines.append(f"{r.get('rank')}. {r.get('airline_name') or r.get('airline_iata')}"
                     f" {r.get('flight_no')} {dep} {amt}")
    b = p.get("baseline")
    if b:
        lines.append(f"90天参考：低位¥{b.get('low')} 常态¥{b.get('mid')}")
    return "\n".join(lines)


def _t_route(card) -> str:
    p = card.get("payload") or {}
    lines = [f"🚗 {card.get('title')}"]
    lines.append(f"{p.get('distance_km')} km · "
                 f"{p.get('duration_text') or str(p.get('duration_min')) + 'min'}"
                 + (f" · 过路费 ¥{p.get('tolls_cny')}"
                    if p.get("tolls_cny") is not None else ""))
    segs = p.get("segments") or p.get("roads") or []
    if segs:
        seg_str = "、".join(f"{s.get('name')} {s.get('km')}km" for s in segs[:5])
        lines.append(f"主要路段：{seg_str}")
    attrs = p.get("attractions") or []
    if attrs:
        lines.append("沿途景点：" + "、".join(a.get("name") for a in attrs[:5]))
    src = " · ".join(s.get("provider", "") for s in
                     (card.get("meta") or {}).get("sources") or [])
    if src:
        lines.append(f"数据源: {src}")
    return "\n".join(lines)


def _t_itinerary(card) -> str:
    p = card.get("payload") or {}
    icon = {"flight": "✈️", "rail": "🚄", "drive": "🚗"}
    lines = [f"🗺️ {card.get('title')}"]
    for leg in p.get("legs") or []:
        dep = (leg.get("depart") or "")[5:16].replace("T", " ")
        arr = (leg.get("arrive") or "")[5:16].replace("T", " ")
        m = leg.get("duration_min")
        dur = f"（{m // 60}h{m % 60:02d}m）" if m else ""
        lines.append(f"{icon.get(leg.get('mode'), '🚗')} {leg.get('from')}→"
                     f"{leg.get('to')} {dep}–{arr}{dur}")
    for n in p.get("notices") or []:
        lines.append(f"⏰ {n.get('text')}")
    if p.get("span_min"):
        m = p["span_min"]
        lines.append(f"全程 {m // 60}h{m % 60:02d}m")
    return "\n".join(lines)


def _t_weather(card) -> str:
    p = card.get("payload") or {}
    tr = p.get("t_range") or ["", ""]
    return (f"🌦️ {card.get('title')}\n{p.get('weather')} "
            f"{tr[0]}~{tr[1]}°C"
            + (f" 降水 {p.get('precip_mm')}mm" if p.get("precip_mm") else "")
            + f"\n（{p.get('labels')}）")


def _t_recommend(card) -> str:
    p = card.get("payload") or {}
    lines = [f"🧭 {card.get('title')}"]
    for i, pk in enumerate(p.get("picks") or []):
        lines.append(f"{i + 1}. {pk.get('title') or pk.get('label')}"
                     + (" ⭐首推" if i == 0 else ""))
        if pk.get("reason"):
            lines.append(f"   {pk.get('reason')}")
    for n in card.get("notices") or []:
        lines.append(f"· {n.get('text')}")
    if p.get("total_cost_text"):
        lines.append(f"成本：{p.get('total_cost_text')}")
    return "\n".join(lines)


def _t_generic(card) -> str:
    p = card.get("payload") or {}
    lines = [str(card.get("title"))]
    for k, v in p.items():
        if not isinstance(v, (dict, list)):
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


_TEXT_RENDERERS = {"status": _t_status, "price": _t_price, "route": _t_route,
                   "itinerary": _t_itinerary, "weather": _t_weather,
                   "recommend": _t_recommend}


def render_text(card: dict) -> str:
    ctype = card.get("type") or ""
    fn = next((v for k, v in _TEXT_RENDERERS.items() if ctype.startswith(k)),
              _t_generic)
    head = "".join(f"⚠️ {n.get('text')}\n"
                   for n in card.get("notices") or []
                   if n.get("level") == "warn")
    return head + fn(card) + "\n（via travelfusion）"


def render_html(card: dict) -> str:
    ctype = card.get("type") or ""
    fn = next((v for k, v in _RENDERERS.items() if ctype.startswith(k)), None)
    body = fn(card) if fn else _generic(card.get("payload") or {})
    sources = " · ".join(
        s.get("provider", "") for s in (card.get("meta") or {}).get("sources")
        or [])
    return ("<!doctype html><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<style>{_CSS}</style>"
            f"<h1>{_e(card.get('title'))}</h1>"
            f"<div class='sub'>{_e(ctype)}"
            f"{' · 数据源: ' + _e(sources) if sources else ''}</div>"
            f"{_notices(card)}{body}{_actions(card)}"
            f"<div class='muted' style='margin-top:14px'>由 travelfusion "
            f"服务端生成 · 点击卡片即可回到对话</div>")
