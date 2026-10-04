# Provider Adapter 模板 —— 新源接入就是复制本目录改名 + 填两个函数（L2 热插拔）

## 接入一个新免费源的五步（PLAYBOOK §4）

1. **复制本目录** → `providers/<新源id>/`，改写 `adapter.py`
2. **manifest 登记**：`provider_admin` 或手编 `data/manifests.json` 加一条（含 quota/billing/errorMap）
3. **冒烟**：用测试 key 打一次真接口（免费探针），成功即写 `verified_at`
4. **挂账本**：ledger 侧无需代码——manifest.quota 声明即被治理层读取
5. **降级链**：`provider_admin reorder` 把新源排进对应 capability 的合适位置

## adapter.py 必须实现的接口（薄！认证+端点+字段映射，禁止业务逻辑）

```python
class Adapter:
    id = "<新源id>"
    capabilities = ["…"]          # 与 manifest.capabilities 一致

    def __init__(self, api_key: str | None, http):   # http: 注入的 httpx 客户端
        ...

    def probe(self) -> dict:      # 免费探针（面板"一键验证"用）
        ...

    def fetch(self, capability: str, query: dict) -> dict:
        """返回 canonical 字段（见 docs/10-canonical-schema.md）。
        - 失败抛 ProviderError(code, hint)——code 取 7 种错误码之一
        - 字段缺失置 null，绝不编造
        - provider 原值放 raw 子对象，不静默丢弃"""
```

## 字段映射红线（来自调研实录）

- 同一 provider 内参数命名风格可能不一致（AE 三种风格并存）→ 按端点分别映射，禁止统一转换器
- 未知枚举值 `raw:` 前缀透传，不静默映射
- 失败计费语义按 manifest.billing.chargeOnFailure 声明，代码不假设
