"""服务配置：环境变量 > data/settings.yaml > 内置默认。

Phase 0 只承载治理参数与车辆画像；key 管理属 Phase 1（api_keys 表 + 面板）。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SERVICE_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = SERVICE_ROOT / "app"
SEED_DATA_DIR = APP_DIR / "data"          # 随镜像分发的种子数据


def data_dir() -> Path:
    """运行时可写数据目录（iStoreOS 部署时挂卷到 /app/data）。"""
    env = os.environ.get("TF_DATA_DIR")
    path = Path(env) if env else SERVICE_ROOT / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_settings_file() -> dict:
    p = data_dir() / "settings.yaml"
    if p.exists():
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return {}


@dataclass
class Settings:
    # 支出治理
    monthly_paid_budget_cny: float = 20.0
    confirm_threshold_cny: float = 3.0
    # 资格引擎距离带（km）
    band_short: int = 300
    band_mid: int = 1000
    band_long: int = 3000
    # 车辆画像（电车默认）
    ev_rated_range_km: int = 600
    ev_consumption_factor: float = 0.75
    ev_soc_charge_to: float = 0.90
    ev_soc_floor: float = 0.15
    extra: dict = field(default_factory=dict)


def load_settings() -> Settings:
    s = Settings()
    f = _load_settings_file()
    for k in (
        "monthly_paid_budget_cny", "confirm_threshold_cny",
        "band_short", "band_mid", "band_long",
        "ev_rated_range_km", "ev_consumption_factor", "ev_soc_charge_to", "ev_soc_floor",
    ):
        if k in f:
            setattr(s, k, type(getattr(s, k))(f[k]))
    s.monthly_paid_budget_cny = float(
        os.environ.get("TF_MONTHLY_PAID_BUDGET_CNY", s.monthly_paid_budget_cny))
    s.confirm_threshold_cny = float(
        os.environ.get("TF_CONFIRM_THRESHOLD_CNY", s.confirm_threshold_cny))
    return s
