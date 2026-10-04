import json

import httpx
import pytest

from app.providers.googlemaps.adapter import Adapter, ProviderError

OK = {"routes": [{
    "distanceMeters": 514000, "duration": "9000s",
    "legs": [{"steps": [
        {"travel_mode": "WALK", "staticDuration": "300s"},
        {"travel_mode": "TRANSIT", "transitDetails": {"transitLine": {
            "name": "Tokaido Shinkansen", "vehicle": {"name": "Train"}}}},
        {"travel_mode": "TRANSIT", "transitDetails": {"transitLine": {
            "short_name": "83", "vehicle": {"name": "Bus"}}}},
    ]}]}]}


def _adapter_with(body: dict, status: int = 200) -> Adapter:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(status, content=json.dumps(body).encode())

    return Adapter(api_key="test", http=httpx.Client(transport=httpx.MockTransport(handler)))


def test_v2_transit_normalize():
    out = _adapter_with(OK).fetch(
        "ground.route.intl",
        {"origin_wgs": [135.7681, 35.0116], "destination_wgs": [135.5023, 34.6937],
         "mode": "transit", "policy": {}})
    d = out["data"]
    assert d["distance_km"] == 514.0
    assert d["duration_min"] == 150
    assert "Tokaido Shinkansen" in d["transit_lines"][0]
    assert "83" in d["transit_lines"][1]
    assert d["walk_min_total"] == 5


def test_no_routes_is_no_match():
    with pytest.raises(ProviderError) as ei:
        _adapter_with({"routes": []}).fetch(
            "ground.route.intl",
            {"origin_wgs": [135.7, 35.0], "destination_wgs": [135.5, 34.7],
             "mode": "transit", "policy": {}})
    assert ei.value.code == "NO_MATCH"


def test_permission_denied_is_auth():
    with pytest.raises(ProviderError) as ei:
        _adapter_with({"error": {"code": 403, "status": "PERMISSION_DENIED",
                                 "message": "API key not valid"}}, status=403).fetch(
            "ground.route.intl",
            {"origin_wgs": [135.7, 35.0], "destination_wgs": [135.5, 34.7],
             "mode": "transit", "policy": {}})
    assert ei.value.code == "AUTH_REQUIRED"
