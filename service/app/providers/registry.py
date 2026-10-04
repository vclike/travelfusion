"""adapter 注册表：provider_id → Adapter 类。新源接入在此登记一行。"""
from __future__ import annotations

from app.providers.airlabs.adapter import Adapter as AirLabsAdapter
from app.providers.amap.adapter import Adapter as AmapAdapter
from app.providers.aviationstack.adapter import Adapter as AviationstackAdapter
from app.providers.googlemaps.adapter import Adapter as GoogleMapsAdapter
from app.providers.openmeteo.adapter import Adapter as OpenMeteoAdapter
from app.providers.opensky.adapter import Adapter as OpenSkyAdapter
from app.providers.travelpayouts.adapter import Adapter as TravelpayoutsAdapter
from app.providers.variflight.adapter import Adapter as VariflightAdapter

_REGISTRY: dict[str, type] = {
    AirLabsAdapter.id: AirLabsAdapter,
    AviationstackAdapter.id: AviationstackAdapter,
    OpenSkyAdapter.id: OpenSkyAdapter,
    TravelpayoutsAdapter.id: TravelpayoutsAdapter,
    AmapAdapter.id: AmapAdapter,
    OpenMeteoAdapter.id: OpenMeteoAdapter,
    VariflightAdapter.id: VariflightAdapter,
    GoogleMapsAdapter.id: GoogleMapsAdapter,
}


def get_adapter(provider_id: str):
    return _REGISTRY.get(provider_id)
