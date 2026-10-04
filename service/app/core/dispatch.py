"""能力调度器 —— 引擎最后一块：降级链 × 配额账本 × 负标 × 付费闸门。

流程（每个 capability 调用）:
  1. manifest 降级链（active ∧ 有能力 ∧ 未负标冷却）
  2. 逐源：额度余量检查 → 付费闸门（paid 仅显式 paid_calibrate=true）→ adapter.fetch
  3. 成功 → 账本记账 + 负标解封；失败 → 按错误码处置（QUOTA/AUTH/UPSTREAM 记负标）→ 下一源
  4. 全链耗尽 → 返回最后一个错误信封（诚实透出，不静默）
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import load_settings
from app.core import cache, canon, keys, ledger, negmark, registry
from app.core.errors import ProviderError
from app.providers.registry import get_adapter

_NON_FATAL = {canon.E_NO_MATCH, canon.E_DATA_UNAVAILABLE, canon.E_NOT_APPLICABLE}


def call_capability(capability: str, query: dict, *, data_dir: Path,
                    settings=None, http: httpx.Client | None = None) -> dict:
    p = Path(data_dir)
    cache_db = p / "cache.db"

    # ① 缓存优先（docs/09 §3 TTL 总表；policy 不入键）
    ck = cache.cache_key(capability, query)
    ttl = cache.ttl_for(capability)
    if ttl > 0:
        hit = cache.cache_get(cache_db, ck)
        if hit is not None:
            hit.setdefault("meta", {})["cache"] = "hit"
            cost0 = hit["meta"].get("cost")
            hit["meta"]["cost"] = {"free_calls": 0, "paid_cny": 0}
            if isinstance(cost0, dict):
                hit["meta"]["cost"]["at_acquisition"] = cost0  # 原采集费用单列
            hit["meta"].setdefault("notes", []).append("缓存命中（未消耗上游额度）")
            return hit

    data = registry.load(p / "manifests.json")
    nm_db = p / "negmark.db"
    chain = registry.active_chain(data, capability, negmark_db=nm_db)
    paid_requested = bool((query.get("policy") or {}).get("paid_calibrate"))
    if not chain:
        return canon.error(canon.E_DATA_UNAVAILABLE,
                           hint=f"{capability} 无已启用数据源（provider_admin enable 或配 key）")
    if paid_requested:
        # 校准语义：用户付费买的是优先精确源——paid 提到队首，失败仍回退免费
        chain = sorted(chain, key=lambda e: 0 if e.get("tier") == "paid" else 1)
    led = ledger.QuotaLedger(p / "ledger.db")
    kstore = keys.load_keys(p)
    last_err: dict | None = None
    sources_meta = []
    attempted: list[dict] = []

    for entry in chain:
        pid = entry["id"]
        q = entry.get("quota") or {}
        period, limit = (q.get("period") or "total"), q.get("limit")
        tier = entry.get("tier", "free")

        # 付费闸门三连（docs/09 四规则）：永不自动 → 月预算 → 单次确认
        if tier == "paid" and not paid_requested:
            # 2026-10-02 修复：免费源已给出真实错误（如 NOT_VERIFIABLE_FREE）时
            # 不被付费闸门提示覆盖；链上无免费源错误时才以此兜底。
            if last_err is None:
                last_err = canon.error(canon.E_DATA_UNAVAILABLE, pid,
                                       hint="该能力只有付费源可提供——需显式 paid_calibrate=true（走预算闸门）")
            continue
        est_cost = float(entry.get("costPerCall", 0) or 0)
        if tier == "paid":
            s_obj = settings or load_settings()
            spent = led.paid_month_cny()
            if spent + est_cost > s_obj.monthly_paid_budget_cny:
                last_err = canon.error(canon.E_BUDGET_EXHAUSTED, pid,
                                       hint=f"本月付费预算不足：已用 {spent:.2f}+"
                                            f"本次≈{est_cost:.2f} > 预算 "
                                            f"{s_obj.monthly_paid_budget_cny}")
                continue
            if est_cost > s_obj.confirm_threshold_cny and not \
                    (query.get("policy") or {}).get("confirm_spend"):
                last_err = canon.error("CONFIRM_REQUIRED", pid,
                                       hint=f"单次约 ¥{est_cost} 超过确认阈值 ¥"
                                            f"{s_obj.confirm_threshold_cny}"
                                            "——需 confirm_spend=true（用户知情后放行）")
                continue

        # 额度余量（免费周期桶）
        if limit is not None and period in ("month", "day"):
            if (led.remaining(pid, period, limit) or 0) <= 0:
                negmark.record_failure(nm_db, pid, capability, "免费额度耗尽")
                last_err = canon.error(canon.E_QUOTA_LIMIT, pid,
                                       hint=f"{pid} 本{period}额度已耗尽，等重置或降级")
                continue

        adapter_cls = get_adapter(pid)
        if adapter_cls is None:
            last_err = canon.error(canon.E_DATA_UNAVAILABLE, pid, hint=f"{pid} adapter 未实现")
            continue

        ak = None
        kblock = kstore.get(pid) or {}
        ak = (kblock.get("api_key") or kblock.get("access_key")
              or kblock.get("token") or kblock.get("key"))
        if entry.get("auth", "").startswith("oauth2"):
            ak = kblock if kblock else None      # OAuth 源：adapter 拿完整凭据块
        if not ak and "key" in (entry.get("auth") or ""):
            last_err = canon.error(canon.E_AUTH_REQUIRED, pid, hint=f"{pid} key 未配置")
            negmark.record_failure(nm_db, pid, capability, "key missing")
            attempted.append({"provider": pid, "code": canon.E_AUTH_REQUIRED,
                              "hint": "key missing"})
            continue

        adapter = adapter_cls(api_key=ak, http=http)
        try:
            result = adapter.fetch(capability, query)
        except ProviderError as e:
            code, hint = e.code, str(e.hint)[:150]
            if code in (canon.E_QUOTA_LIMIT, canon.E_UPSTREAM_FAILURE,
                        canon.E_AUTH_REQUIRED):
                negmark.record_failure(nm_db, pid, capability, hint)
            attempted.append({"provider": pid, "code": code, "hint": hint})
            last_err = canon.error(code, pid, hint=hint)
            continue
        except Exception as e:                       # 任何意外都不得抛穿给 agent
            negmark.record_failure(nm_db, pid, capability, str(e)[:100])
            attempted.append({"provider": pid, "code": canon.E_UPSTREAM_FAILURE,
                              "hint": str(e)[:150]})
            last_err = canon.error(canon.E_UPSTREAM_FAILURE, pid, hint=str(e)[:150])
            continue
        # 成功
        negmark.record_success(nm_db, pid, capability)
        calls = int(result.get("cost_calls", 1))
        if tier == "paid":
            led.consume_paid(pid, est_cost)             # 付费扣费（审计四元组）
        elif limit is not None and period in ("month", "day"):
            led.consume_free(pid, period, calls)
        else:
            led.consume_free(pid, "total", calls)
        sources_meta.append({"provider": pid, "freshness": "live",
                             "calls": calls,
                             "verified_at": entry.get("verifiedAt")})
        meta = {"sources": sources_meta,
                "confidence": "medium",
                "cost": {"free_calls": calls if tier != "paid" else 0,
                         "paid_cny": est_cost if tier == "paid" else 0},
                "manifest_note": entry.get("notes", "")}
        if paid_requested and tier != "paid":
            # 2026-10-01 立项：付费请求落到免费源 = 校准回退，必须显式标注（防假精确）
            meta["calibration_fallback"] = (
                "付费校准未成功（见 attempted），已回退免费缓存口径——非精确价")
            meta["attempted"] = attempted            # 诚实不变量：回退成功也带付费源失败轨迹
        out = canon.ok(result.get("data"), meta=meta)
        if result.get("coverage_note"):
            out["meta"]["notes"] = [result["coverage_note"]]
        # 缓存写入：flight.price 按 expires_at，其余按能力 TTL
        eff = ttl
        if capability == "flight.price":
            exps = [pr.get("expires_at") for pr in
                    (result.get("data") or {}).get("prices", [])
                    if pr.get("expires_at")]
            if exps:
                try:
                    earliest = min(datetime.fromisoformat(e.replace("Z", "+00:00"))
                                   for e in exps)
                    eff = max(300, int(earliest.timestamp()) - int(time.time()))
                except ValueError:
                    pass
        if tier == "paid":
            eff = min(eff, 900)          # 付费精确价保鲜 ≤15min，防陈旧价冒充校准
        cache.cache_put(cache_db, ck, out, eff)
        return out

    final = last_err or canon.error(canon.E_UPSTREAM_FAILURE, hint="降级链耗尽")
    if attempted:
        final["meta"]["attempted"] = attempted    # 诚实透出：每个源试了什么、为什么
    return final
