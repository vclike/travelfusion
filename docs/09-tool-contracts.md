# 09 · 工具契约与治理规则（产品形态定稿 · 2026-09-29）

> 回答四个问题：agent 用起来的难度是多少？哪些抛给程序、哪些必须 agent 给？
> 每个工具的调用规则是什么？key 和收费怎么管？
> 本文件是 **agent 侧体验的验收合同**。

---

## 0. 信息分工总原则

- **agent 只提供"意图"**：谁、去哪、什么时候、什么偏好。
- **程序补齐一切"事实"**：码制解析、方式资格、来源路由、缓存、校准、计价、置信度。
- **程序永不要求 agent 提供**：API key、provider 名称、配额细节、降级逻辑、码制选择（IATA/ICAO/telecode）。

**设计自检（换弱模型测试）**：把调用方换成更弱的模型——只要必填项全是"意图"而非"知识"，契约即合格。
**零轮次原则**：任何查询一次调用出结果；禁止"先 resolve 再查"的两轮编排（模糊名在工具内部解析）。
**描述预算**：每工具描述 ≤140 tokens，9 工具合计 ≤1,250 tokens 常驻。

---

## 1. 统一响应信封（所有工具）

```json
{
  "data": { "…canonical 5-8 字段…" },
  "meta": {
    "sources":  [{ "provider": "airlabs", "at": "2026-09-29T14:02Z", "freshness": "live|cache" }],
    "confidence": "high|medium|low",
    "notes":    ["航班已跳过：距离过短(130km)，适用高铁/自驾"],
    "cost":     { "free_calls": 2, "paid_cny": 0 }
  },
  "error": null
}
```

- 默认紧凑输出；`detail=true` 才展开完整溯源（token 经济）
- 错误码 7 种（AD-5 扩展 + 责任 provider）：
  `NO_MATCH` · `DATA_UNAVAILABLE` · `QUOTA_LIMIT` · `BUDGET_EXHAUSTED` ·
  `NOT_APPLICABLE` · `UPSTREAM_FAILURE` · `AUTH_REQUIRED`
- `meta.notes` 承载所有"程序替 agent 做掉的决定"（资格跳过、缓存命中、降级），agent 可直接转述

---

## 2. 九工具契约

### 2.1 flight_status —— 航班状态

| 项 | 内容 |
|---|---|
| 必填（意图） | `flight_no + date` **或** `origin + destination + date` |
| 可选 | `detail` |
| 程序自动 | 航班号规范化（`ca 1501`→`CA1501`）；码表解析；provider 路由（国际 AirLabs→Aviationstack，国内→飞常准指引/校准位）；缓存；归一；置信度 |
| 护栏 | 两端距离 <300km → `NOT_APPLICABLE`；免费层查 >10h 未来时刻 → `DATA_UNAVAILABLE`+指引 |
| TTL | 当日状态 5min；时刻表 1h；历史 24h |
| 计价 | 国际免费 1 call；国内走付费闸门 |

### 2.2 flight_price —— 票价（两层策略内置）

| 项 | 内容 |
|---|---|
| 必填（意图） | `origin` `destination` `date`（具体日 / 区间 / 月份均可） |
| 可选 | `cabin` · `currency`(默认 CNY) · `paid_calibrate`(默认 **false**) · `trip_budget_cny` |
| 程序自动 | 城市码聚合（BJS→两场）；sweep 编排；**基线/缓存优先命中**；梯队降级；成本预估 |
| 护栏 | 国内免费层 → 明确"无免费参考价"（不假装）；跨境资格由 eligibility 引擎先判 |
| 付费确认流 | 校准预估花费 > `confirm_threshold_cny`(默认¥3) → 返回 estimate，要求 `confirm_spend=true` 才执行 |
| TTL | 上游缓存价按 `expires_at` 否则 24h；基线永久（带时间戳） |

### 2.3 flight_verify —— 跨源复核

| 项 | 内容 |
|---|---|
| 必填（意图） | `flight_no + date` |
| 可选 | `claim`（待核验断言，如"航司称延误 2h"）· `paid_calibrate` |
| 程序自动 | 计划源 + 观测源（OpenSky，icao24 由计划源记录反查）并行；类型化对比；置信度+依据 |
| 护栏 | 目的机场无实时覆盖层 → 置信度降级并说明（不误报"未落地"） |
| 计价 | 免费双源 2–3 calls |

### 2.4 resolve_place —— 码制解析（可选工具）

| 项 | 内容 |
|---|---|
| 必填 | `name` 任意片段（"成都"/"Chengdu"/"PEK"/"首都机场"） |
| 可选 | `region` 提示 |
| 程序 | 码表全类型匹配，歧义列选项（含坐标/国家）；无歧义直接给默认 |
| 规则 | **其余工具一律接受模糊名并内部解析**；本工具只在歧义展示（"北京：首都还是大兴？"）或组合编排时才需要 |

### 2.5 route_ground —— 地面交通（含电车）

| 项 | 内容 |
|---|---|
| 必填（意图） | `origin` `destination` |
| 可选 | `mode`(默认 auto：驾车+公交并列) · `depart_time` · `ev{rated_range_km, soc_start, soc_target}`(缺省读配置车辆画像) · `plate`(限行) · `detail` |
| 程序自动 | 地理编码（永久缓存）；能耗模型；充电候选 + waypoints 重算；taxi_cost；坐标系归一 WGS-84 输出 |
| 护栏 | 境外 → `NOT_APPLICABLE`(高德仅境内)；轨道交通需求 → 指引 12306 |
| TTL | 路线/路况不缓存；距离测量 7 天；地理编码永久 |
| 计价 | 免费（高德组） |

### 2.6 quota_status —— 额度仪表盘

无参。输出：各源各桶余额/周期/重置日、负标（冷却中）状态、本月免费已耗/付费已花、付费预算余量。

### 2.7 provider_admin —— 对话级维护

| 动作 | 参数 | 约束 |
|---|---|---|
| list | — | — |
| enable/disable | `provider` | disable 付费源需用户确认（工具描述写明） |
| set_quota | `provider, limit, period, mode` | — |
| reorder | `capability, order` | — |
| set_budget | `monthly_cny` | 不得超过 config 硬上限 |

manifest 每请求重读 → 生效无需重启。

### 2.8 weather_context —— 天气上下文（第 8 工具 + 自动附载）

| 项 | 内容 |
|---|---|
| 必填（意图） | `location`（目的地；可选第二个 location 作出发地）+ `date`（或月份） |
| 可选 | 无——地平线分层自动选择 |

**时间地平线分层**：

| 出行日期距今天 | 层 | 数据源 | 输出标签 |
|---|---|---|---|
| ≤16 天 | 预报层 | Open-Meteo forecast（全球免费无 key）；境内可回落高德天气 | "预报"（**7–16 天段必须标注可信度递减**） |
| >16 天 | 气候常态层 | Open-Meteo Historical（ERA5，1940+，免费无 key）→ 该月常年均值（均高/低温、降水日数、极端值、source_years） | **"气候参考（历史均值，非预报）"** |

**规则**：
- 预报与气候常态的标签**永不混用**（诚实输出不变量的天气版）
- **自动附载**：flight_price sweep 与行程组合响应默认附目的地+出发日天气上下文，`weather=false` 关闭
- **EV 联动**：出发日 ≤16 天自动拉气温修正电池折扣系数（假设透明标注）
- 缓存：预报 3h；月度气候常态按 `(location, month)` 永久缓存（年更）
- 计价：免费（Open-Meteo 10k/日；高德天气 5,000/月为境内合规选项）

### 2.9 airline_kb —— 航司知识库编辑（agent 修正知识的入口）

| 项 | 内容 |
|---|---|
| 动作 | `list` / `get(iata)` / `set(iata, patch, by, reason)` / `unset_hint(iata, tag)` / `add_alias(iata, alias)` / `set_norm(key, value, reason)` |
| 必带 | `set` 必带 `{by: "agent"\|"user", reason}`——修订 append-only 追加 revisions，不覆盖历史 |
| 护栏 | 安全评级类知识**拒收**（工具描述写明，主观/时效风险）；修正须注明依据（用户实测/新来源） |
| 生效 | KB 每请求重读（同 manifest），下一响应即正确 |
| 计价 | 零外部调用 |

**修正闭环**：结果与知识矛盾（用户实测/新证据）→ agent `set` 修正（附依据）→ 转述用户
"已更新：××（依据：…）"。知识被谁改、为何改、何时改，全程可追溯（revisions 台账）。
短句提炼标准与 norms 基线机制见 `10-canonical-schema.md` §6b。

工具总数 7→9，描述预算上限 1,250 tokens。

---

## 3. 缓存与新鲜度总表

| 数据 | TTL | 理由 |
|---|---|---|
| 当日航班状态 | 5 min | 频变 |
| 时刻表（≤10h 窗口） | 1 h | |
| 上游缓存价 | `expires_at` 或 24h | Travelpayouts 性质 |
| 价格基线 | 永久（时间戳） | 资产 |
| 机场/车站注册表 | 月更 | 静态 |
| 地理编码 | 永久 | 静态 |
| 距离测量 | 7 天 | 路网缓变 |
| 驾车路线/路况 | 不缓存 | 实时 |

---

## 4. API Key 管理（后端）

- **存储**：SQLite `api_keys(provider, key, status, added_at, verified_at, last_error)`。
  key **永不**进 manifest / 日志 / 工具输出 / 错误信封（searchfusion 不变量）。
- **面板「Key 管理」**：增删改 + **一键验证**（对每源发一次免费探针调用——AirLabs `/ping`、
  OpenSky 取 token——成功即写 `verified_at`）。
- **启动自检**：对所有 enabled 且有 key 的源跑探针 → 状态板亮灯。
- **运行时 AUTH 失效**：某源开始报鉴权错 → 标 `AUTH_REQUIRED`，**自动降级下一源**，面板告警，
  工具层无感（meta.notes 提示"AirLabs 鉴权失效，已切换 Aviationstack"）。
- **各源 key 清单**（PLAYBOOK 附录）：AirLabs（注册即得 1k/月）· Aviationstack（100/月）·
  OpenSky（client_id+secret 两字段）· Travelpayouts（token）· 高德（key，需个人认证）；
  12306 无 key；飞常准 key 在 DSH MCP 侧，本服务只发指引。

---

## 5. 收费信息使用规则（支出治理四条）

1. **永不自动**：付费源唯一入口 = 工具上的显式 `paid_calibrate=true`；**免费降级链永不含付费源**。
2. **月度预算闸门**：`monthly_paid_budget_cny`（默认 ¥20）。消耗 ≥80% → 响应带 warning 字段；
   100% → `BUDGET_EXHAUSTED` + 免费替代指引；每月 1 号惰性重置。
3. **单次确认**：预计花费 > `confirm_threshold_cny`（默认 ¥3，覆盖一次 6 调用校准 sweep）→
   返回 `{estimate_calls, estimate_cny}`，要求 `confirm_spend=true` 重发；agent 负责向用户转述。
   支持在确认时带 `trip_budget_cny` 收紧本次上限。
4. **全程审计**：`spend_log(at, tool, provider, calls, cny, reason)`；quota_status 可出月账单。

**计价基础**：价格表存各 provider manifest（飞常准各工具 ¥0.1–0.5 等），服务调用**前**即可算出
预估成本——确认流才有依据。失败计费差异（航班管家失败不扣费等）：`attempts` 与 `billed` 分开记账，
以数据成功为 billed 依据。

---

## 6. 验收清单（agent 体验）

- [ ] 换弱模型：必填项全为意图，无一项需要"知识"
- [ ] 零轮次：九个工具均一次调用出结果（模糊名内部解析）
- [ ] 护栏全类型化：NOT_APPLICABLE 场景（短途航班/境外高德/国内免费价）全部返回带理由的错误而非空结果
- [ ] 付费不可自动触发：代码审查确认免费链路无付费分支
- [ ] key 零泄漏：日志/信封/面板导出无明文 key
- [ ] 描述预算：9 工具 ≤1,250 tokens
- [ ] 预报与气候常态标签永不混用（weather_context）
- [ ] airline_kb 修订全程留痕（revisions append-only），安全类知识拒收
