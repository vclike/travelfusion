import json

import pytest

from app.core import registry
from app.core.negmark import record_failure

BASE = {
    "id": "airlabs",
    "status": "active",
    "tier": "free",
    "costPerCall": 1,
    "capabilities": ["flight.status"],
    "quota": {"group": "search", "period": "month", "limit": 1000},
}


def _write(tmp_path, providers, order=None):
    p = tmp_path / "manifests.json"
    p.write_text(json.dumps({"providers": providers, "order": order or {}},
                            ensure_ascii=False), encoding="utf-8")
    return p


def test_validate_rejects_missing_keys(tmp_path):
    p = _write(tmp_path, [{"id": "x"}])
    with pytest.raises(registry.ManifestError):
        registry.load(p)


def test_enable_disable_roundtrip(tmp_path):
    p = _write(tmp_path, [dict(BASE)])
    assert registry.disable(p, "airlabs", "该源收费化")
    data = registry.load(p)
    assert data["providers"][0]["status"] == "disabled"
    assert "收费" in data["providers"][0]["deprecated_reason"]
    assert registry.enable(p, "airlabs")
    assert registry.load(p)["providers"][0]["status"] == "active"


def test_set_quota_three_modes(tmp_path):
    p = _write(tmp_path, [dict(BASE)])
    assert registry.set_quota(p, "airlabs", "total", 5000, mode="total")
    e = registry.by_id(registry.load(p), "airlabs")
    assert e["quota"]["mode"] == "total"
    assert e["quota"]["period"] == "total"


def test_active_chain_orders_by_cost(tmp_path):
    cheap = dict(BASE, id="cheap", costPerCall=1)
    dear = dict(BASE, id="dear", costPerCall=5)
    p = _write(tmp_path, [dear, cheap])
    chain = registry.active_chain(registry.load(p), "flight.status")
    assert [e["id"] for e in chain] == ["cheap", "dear"]


def test_active_chain_excludes_disabled_and_cooling(tmp_path):
    cheap = dict(BASE, id="cheap", costPerCall=1)
    dear = dict(BASE, id="dear", costPerCall=5)
    p = _write(tmp_path, [cheap, dear])
    nm = tmp_path / "neg.db"
    record_failure(nm, "cheap", "flight.status")   # cheap 进入冷却
    chain = registry.active_chain(registry.load(p), "flight.status", negmark_db=nm)
    assert [e["id"] for e in chain] == ["dear"]


def test_declared_order_beats_cost(tmp_path):
    a = dict(BASE, id="a", costPerCall=9)
    b = dict(BASE, id="b", costPerCall=1)
    p = _write(tmp_path, [a, b], order={"flight.status": ["a", "b"]})
    chain = registry.active_chain(registry.load(p), "flight.status")
    assert [e["id"] for e in chain] == ["a", "b"]
