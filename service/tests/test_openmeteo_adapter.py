import json

import httpx
import pytest

from app.providers.openmeteo.adapter import Adapter, _wmo_desc

FORECAST = {"daily": {
    "time": ["2026-09-30", "2026-10-01"],
    "weather_code": [61, 3],
    "temperature_2m_max": [22.1, 19.4],
    "temperature_2m_min": [15.0, 13.2],
    "precipitation_sum": [3.2, 0.0],
    "wind_speed_10m_max": [12.5, 8.1],
}}
CLIMATE = {"daily": {
    "time": [f"2035-12-{d:02d}" for d in range(1, 29)],
    "temperature_2m_max": [5.0] * 28,
    "temperature_2m_min": [-2.0] * 28,
    "precipitation_sum": [0.5] * 28,
}}


def _adapter_with(routes: dict) -> Adapter:
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        for frag, body in routes.items():
            if frag in url:
                return httpx.Response(200, content=json.dumps(body).encode())
        return httpx.Response(404, content=b"{}")
    return Adapter(http=httpx.Client(transport=httpx.MockTransport(handler)))


def test_wmo_desc():
    assert _wmo_desc(0) == "晴"
    assert _wmo_desc(65) == "大雨"
    assert _wmo_desc(None) == "晴" or "代码" in _wmo_desc(None)


def test_forecast_layer_for_near_date():
    out = _adapter_with({"api.open-meteo.com/v1/forecast": FORECAST}).fetch(
        "weather.context", {"lat": 39.9, "lon": 116.4,
                            "date": "2026-09-30", "policy": {}})
    d = out["data"]
    assert d["layer"] == "forecast"
    assert d["target"]["weather"] == "小雨"
    assert d["target"]["t_max_c"] == 22.1


def test_climate_layer_for_far_date():
    out = _adapter_with({"climate-api.open-meteo.com": CLIMATE}).fetch(
        "weather.context", {"lat": 39.9, "lon": 116.4,
                            "date": "2026-12-25", "policy": {}})
    d = out["data"]
    assert d["layer"] == "climate"
    assert "气候常态" in d["labels"]
    assert d["summary"]["t_max_avg_c"] == 5.0
    assert d["summary"]["sample_days"] == 28
