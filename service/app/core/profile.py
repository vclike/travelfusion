"""出行档案（data/profile.yaml）—— 常用地址簿（别名→地址）。

管理面板（/admin）与 route_ground 别名解析共用；原子写 + 修订审计字段。
车牌 / EV 续航不在此处——它们属车辆画像，归 settings.yaml（config.Settings）。
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml

MAX_ADDRESSES = 8


def _path(data_dir: Path) -> Path:
    return Path(data_dir) / "profile.yaml"


def load_profile(data_dir: Path) -> dict:
    """读档案；缺文件/坏结构 → 空档案（fail-soft：档案缺失不该拖垮查询）。"""
    p = _path(data_dir)
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        raw = {}
    addrs = raw.get("addresses") or []
    return {
        "version": raw.get("version", 1),
        "updated_at": raw.get("updated_at", ""),
        "updated_by": raw.get("updated_by", ""),
        "addresses": [a for a in addrs
                      if isinstance(a, dict) and a.get("alias") and a.get("text")],
    }


def save_profile(data_dir: Path, profile: dict, by: str = "admin-panel") -> dict:
    """校验 + 原子写。非法输入抛 ValueError（面板负责把错误转成人话）。"""
    addrs = profile.get("addresses") or []
    if len(addrs) > MAX_ADDRESSES:
        raise ValueError(f"地址最多 {MAX_ADDRESSES} 条")
    seen: set[str] = set()
    clean: list[dict] = []
    for a in addrs:
        alias = str(a.get("alias") or "").strip()
        text = str(a.get("text") or "").strip()
        if not alias or not text:
            raise ValueError("地址行存在空的别名或内容")
        if alias in seen:
            raise ValueError(f"别名重复：{alias}")
        if len(alias) > 16 or len(text) > 120:
            raise ValueError("别名 ≤16 字，地址 ≤120 字")
        seen.add(alias)
        clean.append({"alias": alias, "text": text})
    import time as _t
    doc = {"version": 1, "updated_at": _t.strftime("%Y-%m-%dT%H:%M:%S"),
           "updated_by": by, "addresses": clean}
    p = _path(data_dir)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return doc


def resolve_alias(data_dir: Path, text: str) -> tuple[str, str] | None:
    """查询词精确命中别名 → (地址文本, 别名)。无大小写/去空格宽容。"""
    q = text.strip()
    if not q:
        return None
    for a in load_profile(data_dir)["addresses"]:
        if a["alias"] == q:
            return a["text"], a["alias"]
    return None
