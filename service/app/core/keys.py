"""key 存储（data/keys.yaml）—— key 与 manifest 分离的不变量载体。"""
from __future__ import annotations

from pathlib import Path

import yaml


def load_keys(data_dir: Path) -> dict:
    p = Path(data_dir) / "keys.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def provider_key(data_dir: Path, provider: str) -> str | None:
    k = load_keys(data_dir).get(provider) or {}
    if isinstance(k, dict):
        return k.get("api_key") or k.get("access_key") or k.get("token") or k.get("key")
    return None


def auth_config(data_dir: Path) -> dict:
    """服务鉴权配置：env 优先，其次 keys.yaml。未配置 = 开放模式。"""
    import os
    k = load_keys(data_dir)
    return {
        "mcp_api_key": os.getenv("TF_MCP_API_KEY") or k.get("mcp_api_key"),
        "admin_key": os.getenv("TF_ADMIN_KEY") or k.get("admin_key"),
    }
