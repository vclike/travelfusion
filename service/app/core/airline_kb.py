"""航司知识库存储 —— airlines_kb.yaml + norms.yaml，MCP 可编辑（append-only 修订）。

服务部署在极空间/iStoreOS，agent 无文件系统访问 → 编辑必须经 airline_kb 工具落到本模块。
每请求重读（同 manifest 哲学）：agent 改完下一响应即生效。
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import yaml

_LOCK = threading.Lock()
HINT_TAGS = ("行李", "餐食", "选座", "座椅", "收费", "其他")


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _save(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False,
                                   width=100), encoding="utf-8")


def _now() -> str:
    return time.strftime("%Y-%m")


def load_kb(path: Path) -> list[dict]:
    return _load(path).get("airlines", [])


def get_airline(path: Path, iata: str) -> dict | None:
    return next((a for a in load_kb(path) if a.get("iata") == iata.upper()), None)


def find_by_alias(path: Path, name: str) -> dict | None:
    """别名归一（§6c）：大小写不敏感的精确匹配；返回 None 表示未命中（调用方走模糊/🌐）。"""
    n = name.strip().lower()
    for a in load_kb(path):
        names = {str(a.get(k, "")).lower() for k in ("iata", "icao", "name_cn", "name_en")}
        names |= {str(x).lower() for x in a.get("aliases", [])}
        if n in names - {""}:
            return a
    return None


def set_airline(path: Path, patch: dict, by: str, reason: str) -> dict:
    """新增/更新条目；追加 append-only revisions。返回修订后的条目。"""
    if not reason:
        raise ValueError("set 必须带 reason（修订台账要求）")
    if by not in ("agent", "user"):
        raise ValueError("by 必须是 agent|user")
    iata = str(patch.get("iata", "")).upper()
    if not iata:
        raise ValueError("patch.iata 必填")
    with _LOCK:
        data = _load(path)
        airlines = data.setdefault("airlines", [])
        entry = next((a for a in airlines if a.get("iata") == iata), None)
        if entry is None:
            entry = {"iata": iata}
            airlines.append(entry)
        for k, v in patch.items():
            if k in ("iata", "revisions"):
                continue
            entry[k] = v
        entry.setdefault("revisions", []).append(
            {"at": _now(), "by": by, "reason": reason})
        _save(path, data)
        return entry


def unset_hint(path: Path, iata: str, tag: str, by: str, reason: str) -> dict | None:
    entry = get_airline(path, iata)
    if entry is None:
        return None
    hints = [h for h in entry.get("hints", []) if h.get("tag") != tag]
    return set_airline(path, {**entry, "hints": hints, "iata": iata},
                       by=by, reason=f"unset_hint[{tag}]: {reason}")


def add_alias(path: Path, iata: str, alias: str, by: str, reason: str) -> dict | None:
    entry = get_airline(path, iata)
    if entry is None:
        return None
    aliases = list(entry.get("aliases", []))
    if alias not in aliases:
        aliases.append(alias)
    return set_airline(path, {**entry, "aliases": aliases, "iata": iata},
                       by=by, reason=f"add_alias[{alias}]: {reason}")


def load_norms(path: Path) -> dict:
    return _load(path).get("norms", {})


def set_norm(norms_path: Path, key: str, value: Any, by: str, reason: str) -> dict:
    if not reason:
        raise ValueError("set_norm 必须带 reason")
    if by not in ("agent", "user"):
        raise ValueError("by 必须是 agent|user")
    with _LOCK:
        data = _load(norms_path)
        norms = data.setdefault("norms", {})
        norms[key] = value
        rev = data.setdefault("revisions", [])
        rev.append({"at": _now(), "by": by, "key": key, "reason": reason})
        _save(norms_path, data)
        return norms
