"""Open-Meteo adapter —— 天气上下文（docs/09 §5 分层铁律）。

  date ≤ 今天+16 天 → forecast 层（免费无 key）
  date > 今天+16 天 → climate 层（模型月度投影，标签永不与预报混用）
WMO weathercode → 中文描述映射（子集）。
"""
from __future__ import annotations

from app.core.errors import ProviderError

import datetime as _dt

import httpx

from app.core.canon import E_NO_MATCH, E_UPSTREAM_FAILURE

FORECAST = "https://api.open-meteo.com/v1/forecast"
CLIMATE = "https://climate-api.open-meteo.com/v1/climate"

_WMO = {0: "晴", 1: "基本晴", 2: "多云", 3: "阴", 45: "雾", 48: "雾凇",
        51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨", 61: "小雨", 63: "中雨",
        65: "大雨", 66: "冻雨", 67: "冻雨", 71: "小雪", 73: "中雪", 75: "大雪",
        77: "雪粒", 80: "阵雨", 81: "阵雨", 82: "强阵雨", 85: "阵雪",
        86: "阵雪", 95: "雷暴", 96: "雷暴伴冰雹", 99: "雷暴伴冰雹"}


def _wmo_desc(code) -> str:
    try:
        return _WMO.get(int(code or 0), f"代码{code}")
    except (TypeError, ValueError):
        return "未知"




class Adapter:
    id = "openmeteo"
    capabilities = ["weather.context"]

    def __init__(self, api_key: str | None = None, http: httpx.Client | None = None):
        self.http = http or httpx.Client(timeout=20)

    def probe(self) -> dict:
        r = self.http.get(FORECAST, params={"latitude": 39.9, "longitude": 116.4,
                                            "forecast_days": 1})
        return {"status": r.status_code, "ok": r.status_code == 200}

    def fetch(self, capability: str, query: dict) -> dict:
        if capability == "weather.context":
            return self._context(query)
        raise ProviderError(E_DATA_UNAVAILABLE, f"openmeteo 未实现 {capability}", self.id)

    def _context(self, q: dict) -> dict:
        lat, lon = q.get("lat"), q.get("lon")
        if lat is None or lon is None:
            raise ProviderError(E_NO_MATCH, "缺少 lat/lon", self.id)
        target = str(q.get("date") or _dt.date.today().isoformat())
        try:
            tdate = _dt.date.fromisoformat(target)
        except ValueError:
            raise ProviderError(E_NO_MATCH, f"date 格式应为 YYYY-MM-DD：{target}", self.id)
        horizon = _dt.date.today() + _dt.timedelta(days=16)
        if tdate <= horizon:
            return self._forecast(lat, lon, tdate)
        return self._climate(lat, lon, tdate)

    # ---------------- 预报层（≤16 天） ----------------
    def _forecast(self, lat, lon, tdate: _dt.date) -> dict:
        start = max(tdate - _dt.timedelta(days=2), _dt.date.today())
        end = min(tdate + _dt.timedelta(days=2), tdate)
        r = self.http.get(FORECAST, params={
            "latitude": lat, "longitude": lon,
            "daily": ("weather_code,temperature_2m_max,temperature_2m_min,"
                      "precipitation_sum,wind_speed_10m_max"),
            "timezone": "auto", "start_date": start.isoformat(),
            "end_date": max(start, end).isoformat()})
        j = r.json() if r.status_code == 200 else {}
        daily = j.get("daily") or {}
        dates = daily.get("time") or []
        if not dates:
            raise ProviderError(E_UPSTREAM_FAILURE, f"openmeteo 无预报 {r.status_code}", self.id)
        rows = [{"date": d, "weather_code": wc, "weather": _wmo_desc(wc),
                 "t_max_c": tmax, "t_min_c": tmin,
                 "precip_mm": pr, "wind_max_kmh": ws}
                for d, wc, tmax, tmin, pr, ws in zip(
                    dates, daily.get("weather_code") or [],
                    daily.get("temperature_2m_max") or [],
                    daily.get("temperature_2m_min") or [],
                    daily.get("precipitation_sum") or [],
                    daily.get("wind_speed_10m_max") or [])]
        target_rows = [x for x in rows if x["date"] == tdate.isoformat()] or rows
        return {"data": {
            "layer": "forecast", "labels": "预报（≤16 天）",
            "target_date": tdate.isoformat(),
            "target": target_rows[0],
            "window": rows,
            "tz": j.get("timezone"),
        }, "cost_calls": 1}

    # ---------------- 气候层（>16 天：模型月度投影） ----------------
    def _climate(self, lat, lon, tdate: _dt.date) -> dict:
        import calendar as _cal
        year = 2035                                   # 模型投影代表年
        start = _dt.date(year, tdate.month, 1)
        end = _dt.date(year, tdate.month, _cal.monthrange(year, tdate.month)[1])
        r = self.http.get(CLIMATE, params={
            "latitude": lat, "longitude": lon,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "models": "MRI_AGCM3_2_S",
            "daily": ("temperature_2m_max,temperature_2m_min,precipitation_sum")})
        j = r.json() if r.status_code == 200 else {}
        daily = j.get("daily") or {}
        dates = daily.get("time") or []
        if not dates:
            raise ProviderError(E_UPSTREAM_FAILURE,
                                "气候层无数据（模型投影不可用）", self.id)
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        pr = daily.get("precipitation_sum") or []
        valid_tmax = [t for t in tmax if t is not None]
        valid_tmin = [t for t in tmin if t is not None]
        valid_pr = [p for p in pr if p is not None]
        summary = {
            "t_max_avg_c": round(sum(valid_tmax) / len(valid_tmax), 1) if valid_tmax else None,
            "t_min_avg_c": round(sum(valid_tmin) / len(valid_tmin), 1) if valid_tmin else None,
            "precip_total_mm": round(sum(valid_pr), 1) if valid_pr else None,
            "sample_days": len(dates),
        }
        return {"data": {
            "layer": "climate", "labels": ("气候常态（模型月度投影，"
                                           f"{tdate.month} 月参考，非预报）"),
            "target_date": tdate.isoformat(),
            "summary": summary,
            "note": "超出 16 天预报窗：仅给月度气候常态，拒给伪精确逐日值",
        }, "cost_calls": 1}
