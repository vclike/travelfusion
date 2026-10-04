"""Provider manifest 注册表 —— 每请求重读（对话级热插拔的载体）。

manifest 文件: data/manifests.json
  { "providers": [ {id,status,tier,costPerCall,capabilities,quota{group,period,limit},
                    billing{chargeOnFailure}, rateLimit{}, errorMap{}, docs, notes} ],
    "order": { "<capability>": ["idA","idB", …按优先级] },
    "external": [ {"id":"variflight","kind":"external-mcp","hint":"…"} ] }
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

REQUIRED_KEYS = ("id", "status", "tier", "costPerCall", "capabilities")
PERIODS = ("month", "day", "total")
_LOCK = threading.Lock()


class ManifestError(ValueError):
    pass


def _validate(entry: dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in entry]
    if missing:
        raise ManifestError(f"provider {entry.get('id','?')} 缺少字段: {missing}")
    if entry["status"] not in ("active", "disabled", "deprecated"):
        raise ManifestError(f"{entry['id']}: 非法 status={entry['status']}")
    if entry["tier"] not in ("free", "paid"):
        raise ManifestError(f"{entry['id']}: 非法 tier={entry['tier']}")
    q = entry.get("quota") or {}
    if q.get("period") not in PERIODS:
        raise ManifestError(f"{entry['id']}: quota.period 必须是 {PERIODS}")


def load(path: Path) -> dict:
    """每请求调用：小 JSON，读盘开销可忽略。损坏即抛错（fail-fast，不静默用旧值）。"""
    with _LOCK:
        data = json.loads(path.read_text(encoding="utf-8"))
    providers = data.get("providers", [])
    for e in providers:
        _validate(e)
    return data


def save(path: Path, data: dict) -> None:
    for e in data.get("providers", []):
        _validate(e)
    with _LOCK:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def by_id(data: dict, provider_id: str) -> dict | None:
    return next((e for e in data.get("providers", []) if e["id"] == provider_id), None)


def active_chain(data: dict, capability: str, negmark_db: Path | None = None) -> list[dict]:
    """某能力下的可用降级链：启用 ∧ 具备能力 ∧ 非 deprecated ∧ 非负标冷却。
    排序：manifest order 声明优先，否则 costPerCall 升序。"""
    banned: set[str] = set()
    if negmark_db is not None:
        from app.core.negmark import banned_providers
        try:
            banned = banned_providers(negmark_db, capability)
        except Exception:
            banned = set()   # 负标库不可用不阻断降级链构建
    chain = [e for e in data.get("providers", [])
             if e["status"] == "active" and capability in (e.get("capabilities") or [])
             and e["id"] not in banned]
    declared = data.get("order", {}).get(capability)
    if declared:
        rank = {pid: i for i, pid in enumerate(declared)}
        chain.sort(key=lambda e: rank.get(e["id"], 10_000))
    else:
        chain.sort(key=lambda e: float(e.get("costPerCall", 0)))
    return chain


def enable(path: Path, provider_id: str) -> bool:
    return _set_status(path, provider_id, "active")


def disable(path: Path, provider_id: str, reason: str = "") -> bool:
    ok = _set_status(path, provider_id, "disabled")
    if ok and reason:
        data = load(path)
        e = by_id(data, provider_id)
        if e is not None:
            e["deprecated_reason"] = reason
            save(path, data)
    return ok


def _set_status(path: Path, provider_id: str, status: str) -> bool:
    data = load(path)
    e = by_id(data, provider_id)
    if e is None:
        return False
    e["status"] = status
    save(path, data)
    return True


def set_quota(path: Path, provider_id: str, period: str, limit: int,
              mode: str = "monthly") -> bool:
    """mode: monthly 月度刷新 / total 总量制 / unlimited 充值制（searchfusion 三分类）。"""
    data = load(path)
    e = by_id(data, provider_id)
    if e is None:
        return False
    e["quota"] = {"group": (e.get("quota") or {}).get("group", "default"),
                  "period": period, "limit": limit, "mode": mode}
    save(path, data)
    return True


def reorder(path: Path, capability: str, order: list[str]) -> bool:
    data = load(path)
    data.setdefault("order", {})[capability] = order
    save(path, data)
    return True


def add_provider(path: Path, entry: dict, order: dict[str, Any] | None = None) -> None:
    _validate(entry)
    data = load(path)
    if by_id(data, entry["id"]) is not None:
        raise ManifestError(f"{entry['id']} 已存在")
    data["providers"].append(entry)
    for cap, ids in (order or {}).items():
        data.setdefault("order", {}).setdefault(cap, []).extend(ids)
    save(path, data)
