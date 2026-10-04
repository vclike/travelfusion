"""Canonical 数据模型与统一响应信封（规格见 docs/10-canonical-schema.md）。

Phase 0 用 dataclass + to_dict（stdlib 优先，MCP 层做 JSON 序列化）；
pydantic 校验在 Phase 1 接入真实 provider 时再收紧。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# 错误码 7 种（AD-5 扩展 + 责任 provider）
E_NO_MATCH = "NO_MATCH"
E_DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
E_QUOTA_LIMIT = "QUOTA_LIMIT"
E_BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
E_NOT_APPLICABLE = "NOT_APPLICABLE"
E_UPSTREAM_FAILURE = "UPSTREAM_FAILURE"
E_AUTH_REQUIRED = "AUTH_REQUIRED"
E_NOT_VERIFIABLE_FREE = "NOT_VERIFIABLE_FREE"   # 免费核验窗外：诚实拒 + 复检点提示


@dataclass
class Place:
    name: str
    granularity: str = "city"            # city|airport|station
    iata: str | None = None
    icao: str | None = None
    city_code: str | None = None
    station_telecode: str | None = None
    lat: float | None = None
    lon: float | None = None
    country: str | None = None
    tz: str | None = None
    coord_gcj02: tuple[float, float] | None = None


@dataclass
class Times:
    scheduled_utc: str | None = None
    scheduled_local: str | None = None
    tz: str | None = None
    estimated_utc: str | None = None
    actual_utc: str | None = None
    day_offset: int = 0                  # 红眼跨天显式偏移


@dataclass
class PricePoint:
    mode: str                            # air|rail|ground
    cabin_class: str | None = None       # mode 作用域开放枚举；未知值 raw: 前缀透传
    cabin_label_cn: str | None = None
    amount: float | None = None
    currency: str = "CNY"
    per_person: bool = True
    tax_included: bool | None = None
    price_type: str | None = None        # bookable|cached|baseline|forecast|composed
    availability: dict | None = None     # rail: {status, count}
    conditions: dict = field(default_factory=lambda: {
        "refundable": "unknown", "changeable": "unknown"})
    composed: bool = False
    fx: dict | None = None
    provenance: dict = field(default_factory=dict)


@dataclass
class AirlineInfo:
    iata: str
    icao: str | None = None
    name_cn: str | None = None
    name_en: str | None = None
    carrier_type: str = "unknown"        # full_service|low_cost|ultra_low_cost|regional|charter|unknown
    alliance: str | None = None
    hub: list = field(default_factory=list)
    aliases: list = field(default_factory=list)
    parent_iata: str | None = None
    status: str = "active"               # active|ceased_operations
    hints: list = field(default_factory=list)   # [{tag, text}] 只记偏离基线的特殊之处
    notes: list = field(default_factory=list)
    source: str | None = None
    as_of: str | None = None
    revisions: list = field(default_factory=list)


def ok(data: Any, meta: dict | None = None) -> dict:
    return {"data": data, "meta": meta or {}, "error": None}


def error(code: str, provider: str | None = None, hint: str = "",
          meta: dict | None = None) -> dict:
    return {"data": None,
            "meta": meta or {},
            "error": {"code": code, "provider": provider, "hint": hint}}


def to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    return obj
