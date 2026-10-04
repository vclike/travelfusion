# PROVIDERS-PLAYBOOK —— agent 维护手册（v0.2）

> 维护者 = agent。本手册写给任何会话里的 agent：照清单操作，不需要重新读代码。
> 生效模型：manifest / KB / norms 每请求重读，改完下一响应即生效，**无需重启**。

## 0. 鉴权（2026-09-30 起）

- **MCP 端点**：所有 /mcp 调用需带 `X-API-Key: <mcp_api_key>`（或 URL `?key=`）；
  key 存 `data/keys.yaml` 的 `mcp_api_key`，也可用环境变量 `TF_MCP_API_KEY` 覆盖
- **管理操作密码门**：provider_admin 与 airline_kb 的**变更类 action**
  （enable/disable/set_quota/reorder/set_budget/set/unset_hint/add_alias）
  必须带 `admin_key` 参数；key 存 `data/keys.yaml` 的 `admin_key`
  （env `TF_ADMIN_KEY` 可覆盖）。key 不匹配 → AUTH_REQUIRED
- list / get / quota_status 只读动作不需要钥匙
- 修改钥匙：编辑 data/keys.yaml 后重启容器（docker-compose up -d --force-recreate）
- **红线**：钥匙绝不进 git；路由器上文件在 /mnt/sata1-4/travelfusion/data/keys.yaml

### 接入地址（2026-09-30 双通道）

| 场景 | URL |
|---|---|
| 内网 | `http://192.168.100.1:8900/mcp` |
| 外网（ddnsto 隧道） | `https://wotu6dcl.gd.ddnsto.com/mcp/` |

- **外网必须带尾斜杠 `/mcp/`**：`/mcp`→`/mcp/` 的 307 Location 在 TLS 终结隧道后是
  http://（死链）；`/mcp/` 直连零重定向（外网实测：401/会话/真数据全通过）
- 外网暴露的安全模型 = **API key 是唯一门**（16 字节 hex）；管理操作还有 admin_key 第二层。
  key 泄露处置：换 data/keys.yaml 的 mcp_api_key + 重启容器

## 1. 看现状

调用 `quota_status`，读懂三段：
- `providers[].quota.remaining_free` —— 该源该桶剩余（自记口径）
- `providers[].cooling_capabilities` —— 负标冷却中的能力（1h→24h 升级冷却，成功自动解封）
- `paid.remaining_cny` —— 本月付费预算余量（默认 ¥20，≥80% 响应会带警告）

## 2. 某源改了免费额度 → `provider_admin set_quota`

```
provider_admin(action="set_quota", provider="airlabs", period="month",
               limit=500, mode="monthly", reason="AirLabs 免费档下调至500")
```
清单：确认新额度数字（让用户给来源）→ set_quota → `quota_status` 复核 remaining。

## 3. 某源收费化 / 死亡 / 故障 → `provider_admin disable`

```
provider_admin(action="disable", provider="airlabs", reason="免费档取消")
```
- 降级链自动收敛到下一源（同 capability 的 order 里剩下的）
- 该源历史数据（基线）不删——它们是资产
- 若是**付费源** disable：先向用户确认
- 之后想删除条目：手编 `data/manifests.json`（或留给下个版本的管理动作）

## 4. 上新免费源（L2 热插拔，半天）

1. 读 `docs/07-api-reference.md` 对应节；无则先补调研（Tabbit/搜索，证据入档）
2. 复制 `app/providers/_template/` → `app/providers/<id>/`，实现 `probe()` + `fetch()`
   ——薄 adapter：认证+端点+字段映射，**禁止业务逻辑**；未知枚举 `raw:` 透传
3. `provider_admin` 挂 manifest（quota/billing/errorMap 按 07 文档填）
4. 冒烟：免费探针一击，成功写 `verified_at`
5. `reorder` 排进降级链合适位置 → `quota_status` 对账

## 5. 新工具需求 → 判定树

- 能用既有 capability 组合？→ 编排层加（`mcp_server.py` 注册新 @mcp.tool）
- 需要新数据？→ 先走 §4 上源，再组合
- 工具描述 ≤140 tokens；必填项全为意图（换弱模型测试）；模糊名内部解析（零轮次）

## 6. 任何改动后的回归三件套

1. `python -m pytest tests -q` —— 31 用例全绿
2. 真机一击：改动涉及的工具调一次（免费源冒烟）
3. `quota_status` 对账：账本增量与预期一致

## 7. 航司知识库维护（airline_kb）

- 用户报错知识 → `airline_kb(action="set", iata=…, patch={…}, by="agent", reason="用户实测:…")`
- 发现新别名 → `add_alias(iata, alias, by="agent", reason="平台X返回的新写法")`
- norms 基线变更 → `set_norm(key, value, reason)`（如行业手提额度整体变化）
- **红线**：安全评级类知识拒收；一切修订 append-only，理由必填

## 附录 A · key 获取清单

| 源 | 注册 | 免费额度 | key 形态 |
|---|---|---|---|
| AirLabs | airlabs.co 注册 | 1,000 查询/月 | api_key |
| Aviationstack | aviationstack.com | 100 请求/月（1次/60s） | access_key |
| OpenSky | opensky-network.org（注册+OAuth） | 4,000 credits/日 | client_id + secret |
| Travelpayouts | travelpayouts.com（联盟注册） | 免费（200/h 未取证） | token |
| 高德 | lbs.amap.com（个人认证必做） | 驾车 15万/月；搜索 5,000/月；天气 5,000/月 | key |
| 12306 | 无需 key（社区 MCP） | 免费低频 | —（Phase 1 子进程托管） |
| 飞常准 | 商务开通（校准位） | — | DSH MCP 侧 |

## 附录 B · 已知坑（来自调研实录）

- **Travelpayouts 新账号被 Drive 引导流占位**（app.travelpayouts.com 只给 Squarespace 变现引导，
  /profile /account /settings 全 404；引导向导为全屏态，无头像菜单、无可跳过按钮）。
  API token 正式路径（官方文档+截图确认）：登录 → 头像下拉 → **Profile** → 左栏 **API tokens**
  → Copy（⚠ Update token 会立即使旧 token 失效，绝不误点）。
  Data API 权限是否对新号开放**未验证**（"200次/小时"存信息冲突）→ 不在关键路径
- 航司参数命名风格不统一（AE 三种并存）→ adapter 按端点映射，勿统一转换
- 失败计费语义相反（SkyLink 扣 / AE·VariFlight 不扣）→ manifest.billing 声明制
- SkyLink 式"认证即扣含 404" → ledger 的 attempts/billed 分开记
- unknown/覆盖缺口必须原样透传（AeroDataBox departed 卡住 ≠ 延误）
- 坐标系：高德 GCJ-02，其他全 WGS-84 —— amap adapter 出口统一转 WGS-84
