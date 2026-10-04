import json

import httpx
import pytest

from app.providers.travelpayouts.adapter import Adapter, ProviderError

SAMPLE = {"success": True, "currency": "rub",
          "data": {"BKK": {"0": {"airline": "SU", "departure_at": "2026-09-30T22:25:00+03:00",
                                 "price": 43491, "flight_number": 272,
                                 "expires_at": "2026-09-29T20:05:13Z"}}}}


def _adapter_with(body: dict, status: int = 200) -> Adapter:
    transport = httpx.MockTransport(lambda req: httpx.Response(status, content=json.dumps(body).encode()))
    return Adapter(api_key="test", http=httpx.Client(transport=transport))


def test_cheap_normalizes_cached_semantics():
    out = _adapter_with(SAMPLE).fetch(
        "flight.price",
        {"origin_code": "MOW", "destination_code": "BKK", "currency": "CNY",
         "date": None, "policy": {}})
    p = out["data"]["prices"][0]
    assert p["amount"] == 43491
    assert p["price_type"] == "cached"
    assert p["cabin_class"] == "economy"
    assert p["expires_at"] == "2026-09-29T20:05:13Z"


def test_empty_data_is_no_match():
    with pytest.raises(ProviderError) as ei:
        _adapter_with({"success": True, "data": {}}).fetch(
            "flight.price", {"origin_code": "MOW", "destination_code": "XXX",
                             "policy": {}})
    assert ei.value.code == "NO_MATCH"


def test_failure_flag_raises_upstream():
    with pytest.raises(ProviderError) as ei:
        _adapter_with({"success": False, "error": "boom"}).fetch(
            "flight.price", {"origin_code": "MOW", "destination_code": "BKK", "policy": {}})
    assert ei.value.code == "UPSTREAM_FAILURE"
