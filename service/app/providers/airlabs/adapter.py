"""AirLabs adapter —— 免费层主力（双端点合并）。

免费档实测结论（2026-09-29 真机）：
  /schedules：10h 窗口内，含 scheduled 时间戳(dep_time_ts) + 延误分钟(dep_delayed/arr_delayed)
  /flights：当日实测，含 actual/estimated/gates/baggage；**在飞航班时间字段为空**（付费墙切口）
  ⇒ 两者合并才是完整三件套；2 次调用/查询（月额度 1,000 下完全可承受）

状态映射：en-route→active；未知值 raw: 前缀透传（诚实不变量）。
"""
from __future__ import annotations

from app.core.errors import ProviderError

import time
from datetime import datetime, timedelta, timezone

import httpx

from app.core.canon import (E_AUTH_REQUIRED, E_DATA_UNAVAILABLE, E_NO_MATCH,
                            E_NOT_VERIFIABLE_FREE, E_QUOTA_LIMIT,
                            E_UPSTREAM_FAILURE)

BASE = "https://airlabs.co/api/v9"

_STATUS_MAP = {
    "en-route": "active", "landed": "landed", "scheduled": "scheduled",
    "cancelled": "cancelled", "incident": "incident", "diverted": "diverted",
}




def _iso(ts) -> str | None:
    """unix 秒 → ISO UTC；兼容已为 ISO 的字符串；无效一律 None（诚实）。"""
    if not ts:
        return None
    if isinstance(ts, str) and "T" in ts:
        return ts.replace(" ", "T") + ("Z" if not ts.endswith("Z") else "")
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, OSError):
        return None


def _pick(row: dict | None, *names):
    """按优先级取第一个非空值。"""
    for n in names:
        v = (row or {}).get(n)
        if v is not None:
            return v
    return None


def _merge(sched: dict | None, fl: dict | None, want: str) -> dict:
    s, f = sched or {}, fl or {}
    dep_sched_ts = _pick(s, "dep_time_ts") or _pick(f, "dep_time")
    arr_sched_ts = _pick(s, "arr_time_ts") or _pick(f, "arr_time")
    dep_actual = _pick(f, "dep_actual")
    arr_actual = _pick(f, "arr_actual")
    day_offset = 0
    if dep_sched_ts and arr_sched_ts:
        day_offset = max(0, (int(arr_sched_ts) - int(dep_sched_ts)) // 86400)
    status_raw = (_pick(f, "status") or _pick(s, "status") or "").lower()
    return {
        "flight_no": f.get("flight_iata") or s.get("flight_iata") or want,
        "flight_icao": f.get("flight_icao") or s.get("flight_icao"),
        "airline_iata": f.get("airline_iata") or s.get("airline_iata"),
        "dep_iata": f.get("dep_iata") or s.get("dep_iata"),
        "arr_iata": f.get("arr_iata") or s.get("arr_iata"),
        "dep_terminal": _pick(f, "dep_terminal") or _pick(s, "dep_terminal"),
        "arr_terminal": _pick(f, "arr_terminal") or _pick(s, "arr_terminal"),
        "times": {
            "dep": {"scheduled_utc": _iso(dep_sched_ts),
                    "estimated_utc": _iso(_pick(f, "dep_estimated")),
                    "actual_utc": _iso(dep_actual)},
            "arr": {"scheduled_utc": _iso(arr_sched_ts),
                    "estimated_utc": _iso(_pick(f, "arr_estimated")),
                    "actual_utc": _iso(arr_actual),
                    "day_offset": day_offset},
        },
        "duration_min": _pick(f, "duration") or _pick(s, "duration"),
        "status": {
            "value": _STATUS_MAP.get(status_raw, f"raw:{status_raw}" if status_raw else "unknown"),
            "dep_delay_min": _pick(f, "dep_delayed") or _pick(s, "dep_delayed"),
            "arr_delay_min": _pick(f, "arr_delayed") or _pick(s, "arr_delayed"),
            "gate": {"dep": _pick(f, "dep_gate"), "arr": _pick(f, "arr_gate")},
            "baggage": _pick(f, "baggage"),
        },
    }


class Adapter:
    id = "airlabs"
    capabilities = ["flight.status", "flight.schedule", "flight.delay", "airport.db", "airline.db"]

    def __init__(self, api_key: str | None, http: httpx.Client | None = None):
        self.k = api_key
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        r = self.http.get(f"{BASE}/ping", params={"api_key": self.k})
        return {"status": r.status_code, "ok": r.status_code == 200}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability in ("flight.status", "flight.schedule"):
            return self._flight_status(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"airlabs 未实现 {capability}", self.id)

    def _params(self, q: dict) -> dict:
        params: dict = {}
        if q.get("flight_no"):
            params["flight_iata"] = str(q["flight_no"]).strip().upper().replace(" ", "")
        else:
            if q.get("airline_iata"):
                params["airline_iata"] = q["airline_iata"]
            if q.get("origin"):
                params["dep_iata"] = q["origin"]
            if q.get("destination"):
                params["arr_iata"] = q["destination"]
        return params

    def _get_rows(self, endpoint: str, params: dict) -> list[dict]:
        p = {**params, "api_key": self.k}
        r = self.http.get(f"{BASE}/{endpoint}", params=p)
        if r.status_code in (401, 403):
            raise ProviderError(E_AUTH_REQUIRED, f"airlabs 鉴权失败 {r.status_code}", self.id)
        if r.status_code == 429:
            raise ProviderError(E_QUOTA_LIMIT, "airlabs 限流", self.id)
        try:
            j = r.json()
        except ValueError:
            raise ProviderError(E_UPSTREAM_FAILURE, f"airlabs 非 JSON {r.status_code}", self.id)
        err = j.get("error")
        if err:
            code = str(err.get("code", "")).lower()
            hint = str(err.get("message", ""))[:120]
            if "limit" in code or "quota" in code:
                raise ProviderError(E_QUOTA_LIMIT, hint, self.id)
            raise ProviderError(E_UPSTREAM_FAILURE, hint or code, self.id)
        return j.get("response") or []

    @staticmethod
    def _row_dep_local_date(row: dict) -> str | None:
        """行计划起飞的机场当地日期（YYYY-MM-DD）；无时间戳/无效返回 None。

        2026-10-02 修复：此前仅按班号取首行、不验日期——查明日可拿到今天
        同名班次。当地日期 = dep_time_ts(UTC) + 机场时区偏移，偏移由
        dep_time(当地 HH:MM) 与 dep_time_utc(UTC HH:MM) 之差推导。
        """
        ts = row.get("dep_time_ts")
        if not ts:
            return None
        try:
            dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
        off_min = 0
        loc, utc = row.get("dep_time"), row.get("dep_time_utc")
        if isinstance(loc, str) and isinstance(utc, str) \
                and len(loc) >= 5 and len(utc) >= 5:
            try:
                off_min = (int(loc[:2]) * 60 + int(loc[3:5])
                           - int(utc[:2]) * 60 - int(utc[3:5])) % 1440
            except ValueError:
                off_min = 0
        return (dt + timedelta(minutes=off_min)).date().isoformat()

    def _match(self, rows: list[dict], q: dict, *, check_date: bool = False) -> dict | None:
        """按班号+航线选行；check_date=True 时再验行当地日期。

        日期过滤只用于 /flights（当日实测端点不辨日期，同名班次会跨日串行）；
        /schedules 的 ±10h 服务端窗口本身就是日期护栏——2026-10-04 修复：
        此前两端点都过滤，明日查询反被日期过滤误杀（schedules 行日期≠明天）。
        """
        want = str(q.get("flight_no") or "").strip().upper().replace(" ", "")
        dep = str(q.get("dep_iata") or "").strip().upper()
        arr = str(q.get("arr_iata") or "").strip().upper()
        qdate = str(q.get("date") or "").strip()
        for f in rows:
            if want and (f.get("flight_iata") or "").upper() != want:
                continue
            if dep and (f.get("dep_iata") or "").upper() != dep:
                continue
            if arr and (f.get("arr_iata") or "").upper() != arr:
                continue
            if check_date and qdate and self._row_dep_local_date(f) not in (None, qdate):
                continue
            return f
        return None

    def _flight_status(self, q: dict) -> dict:
        if not self.k:
            raise ProviderError(E_AUTH_REQUIRED, "airlabs key 未配置", self.id)
        qdate = str(q.get("date") or "").strip()
        today = time.strftime("%Y-%m-%d")
        tomorrow = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))
        if qdate and qdate not in (today, tomorrow):
            # 2026-10-01 实测校准：免费核验窗 = 当日 + 明日（schedules 未来 ≤10h 计划窗）
            raise ProviderError(
                E_NOT_VERIFIABLE_FREE,
                f"免费层核验窗=当日+明日10h计划窗；请求日期 {qdate} 超出窗口——"
                "T-24h 内再核，或 paid_calibrate=true 走付费层", self.id)
        params = self._params(q)
        if not params.get("flight_iata") and not params.get("dep_iata"):
            raise ProviderError(E_NO_MATCH, "缺少航班号或航线参数", self.id)

        calls = 0
        sched_row, fl_row = None, None
        errors: list[str] = []

        # /schedules：10h 窗口内——计划时间戳 + 延误分钟
        try:
            rows = self._get_rows("schedules", params)
            calls += 1
            sched_row = self._match(rows, q)
        except ProviderError as e:
            calls += 1
            errors.append(f"schedules: {e.code} {e.hint}")
            if e.code in (E_AUTH_REQUIRED, E_QUOTA_LIMIT):
                raise                                    # 鉴权/限流立刻上抛，负标接管

        # /flights：当日实测——actual/gates/baggage/实时 status
        # （明日起飞查询跳过：flights 端点不辨日期，会拿今天的同名班次冒充——防错位）
        fl_row = None
        if qdate != tomorrow:
            try:
                rows = self._get_rows("flights", params)
                calls += 1
                fl_row = self._match(rows, q, check_date=True)
            except ProviderError as e:
                calls += 1
                errors.append(f"flights: {e.code} {e.hint}")
                if e.code in (E_AUTH_REQUIRED, E_QUOTA_LIMIT):
                    raise

        if not sched_row and not fl_row:
            if qdate == tomorrow:
                # 2026-10-02 修复：明日班次尚未进入免费 10h 计划窗 ≠ 无此航班
                raise ProviderError(
                    E_NOT_VERIFIABLE_FREE,
                    f"免费层暂无 {params.get('flight_iata') or '该班次'} 在 {qdate} 的"
                    "计划记录（10h 计划窗未覆盖该时刻或当日不执飞）——"
                    "起飞前 ≤10h 内再核，或 paid_calibrate=true 走付费校准", self.id)
            detail = "; ".join(errors)
            raise ProviderError(
                E_NO_MATCH,
                "airlabs 免费窗内无此班次（schedules≤10h 计划窗；flights 当日实测）"
                + (f"；{detail}" if detail else ""),
                self.id)

        merged = _merge(sched_row, fl_row, params.get("flight_iata", ""))
        coverage = ("schedules+flights 双端点合并" if (sched_row and fl_row)
                    else ("仅 schedules" if sched_row else "仅 flights（时间字段可能缺失）"))
        if errors:
            merged["status"]["partial"] = errors
        return {"data": {"flights": [merged], "coverage_note": coverage},
                "cost_calls": max(1, calls)}
