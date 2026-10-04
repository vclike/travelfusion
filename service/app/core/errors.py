"""Provider 异常契约的唯一正主（anti-entropy：一 bug 一 owner）。

历史教训（2026-09-30）：各 adapter 曾各自定义本地 ProviderError，
dispatch 只 import airlabs 的类——其它 adapter 的 NO_MATCH 掉进
`except Exception` catch-all 被误记为 UPSTREAM_FAILURE 并负标。
现在所有 adapter 与 dispatch 统一 import 本模块。
"""
from __future__ import annotations


class ProviderError(Exception):
    def __init__(self, code: str, hint: str = "", provider: str = ""):
        self.code, self.hint, self.provider = code, hint, provider
        super().__init__(f"{code}: {hint}")
