# dsh-flight-aggregator 架构设计

> 依赖：`01-source-research.md`（数据源证据与分级）。
> 本文件记录**决策与结构**。其中标注 `⏳待填` 的字段依赖尚未取证的额度数据。

---

## -1. 整合理由清单（立项依据 · 2026-09-29）

**为什么把十几个服务做成一个插件，而不是各自挂 MCP。**

### 用户原始三条（配调研实据）

| # | 理由 | 调研实据 |
|---|---|---|
| 1 | **配额池化**：单一 API key 月度额度怕不够 | 同类查询的实际池子：状态类 AirLabs 1,000/月 + Aviationstack 100/月；观测类 OpenSky 4,000/日。单一源几天打穿；聚合后同类查询多池轮转 + 明确降级顺序（贵的计划源省着用，便宜的观测源放开用） |
| 2 | **交叉验证**：历史参照类预估怕不准 | 实证：ADS-B 类源"只给位置不给航班"；AE `/flightsFuture` 是算法按历史外推；Travelpayouts 票价是缓存价带 `expires_at`。单一源=单一偏见。插件做**观测校验计划**（计划 ETA 时飞机实际在哪）+ 置信度带依据输出 |
| 3 | **统一工具面**：散装 MCP 重复查询、慢、提示词开销大 | DSH 里每个 MCP 的工具描述**常驻每个会话上下文**——6 个旅行 MCP（合计 60+ 工具）= 数千 token 常驻；跨源查询每跳一次 MCP 多一轮工具调用往返。一个插件 = 6 个精描述工具 + 内部调度器 |

### 补充理由（本轮调研实证）

| # | 理由 | 实证 |
|---|---|---|
| 4 | **归一化吸收字段战争** | 同一家 Aviation Edge 就有三种参数风格（`iataCode`/`depIata`/`flight_num`）；IATA（PEK）/ICAO（ZBAA）/12306 telecode（VNP）三套码表；GCJ-02 vs WGS-84 坐标差数百米；时间字段"当地/UNIX/UTC"三件套 vs 纯本地。agent 裸调每次都要重新对齐——插件在 provider 边界一次性收敛 |
| 5 | **计费与错误语义只能有一处裁判** | 失败计费各家**相反**（SkyLink 认证即扣含 404；AE/VariFlight 失败不扣）；配额可见性三档（OpenSky 头=真剩余；SkyLink 头=防滥用上限；其余需自记）；错误形态四种（200+success:false / 401·403·422 / 429 / body.error.code）。这些规则进提示词既烧 token 又易错，进账本一次写对 |
| 6 | **共享缓存 + 静态库一次抓取** | AE 机场库"单次调用拉全库仅计 1 call"——插件抓一次落盘，此后全部本地命中零消耗；同一航班在"查状态"与"复核"间共享缓存，不重复扣额度 |
| 7 | **换源韧性** | 本轮调研即坟场：Amadeus 2026-07-17 关停、Kiwi 关门、AE 砍免费档、ADSB Exchange 免费 API 消失。adapter 隔离下换源=改一个文件；散装 MCP 换源=重学工具+改全部提示词 |
| 8 | **token 经济** | 原始响应动辄 50 字段（AirLabs 三套时间 × 起降两侧）；插件投影成模型需要的 5–8 字段 canonical 输出 |
| 9 | **派生语义是真增值** | 没有任何单源直接给"延误多久、可信吗"：需要 flight↔icao24 映射（ADS-B 只给 hex）、位置对计划偏差推算、跨源分歧置信度+依据。这些计算住插件里，模型拿判断而非原料 |
| 10 | **认证治理** | OpenSky OAuth token 30 分钟过期自动刷新；AirLabs 签名 3 分钟现算；所有 key 不进 prompt/日志 |
| 11 | **速率合规前置** | Aviationstack 1 次/60s 滑动窗、AirLabs 分钟/小时/月三层、OpenSky 三桶——admission control 在调用**前**算成本与间隔，而不是打了再吃 429 |
| 12 | **跨域 join 只有插件能做** | 门到门 = 航班→落地机场→坐标（正确坐标系）→驾车/公交/火车。需要一张统一机场/车站注册表把三域接起来；散装 MCP 之间没有 join，只能靠 agent 在上下文里人肉粘合 |

### 典型场景走查：三个月后 中国→伦敦，追求经济性（能力边界 · 2026-09-29）

用户问题："哪个机场出发 + 哪天出发 + 怎样中转最划算"。拆成三个子问题，能力不同：

| 子问题 | 免费能力 | 依据 |
|---|---|---|
| **哪个机场出发** | ✅ 可做 | Travelpayouts 城市码聚合（`BJS`含两场、`LON`含四场）。8 个出发城市各查 1 次最低价 → 排序；再用高德 `/v3/distance` 批量算家到各机场地面成本（时间+过路费），**票价+地面成本才是真经济性**——这个 join 只有插件能做 |
| **哪天出发** | ✅ 可做，强项 | `/v1/prices/calendar` 一次返回整月逐日最低价；90 天在 330 天订票窗内，缓存价通常有覆盖（需标注稀疏度） |
| **怎样中转最划算** | ⚠️ **真实边界** | 免费只给**捆绑最低总价**，不能分解中转组合（PEK-IST-LHR vs PEK-HEL-LHR 无法比较）；过境签/行李直挂/MCT 无数据源；手工拼段价 ≠ 联程价。分解比较**只有付费路径**（飞常准 `getRouteFlightTickets`，国际最多 6 程 legs） |

**两层策略（本插件的核心查询模式）**：

```
第一层 免费·宽撒网（Travelpayouts）：8 城市最低价 + top3 价格日历 ≈ 11 calls = ¥0
  → 收敛出"最优出发城市 + 最优日期窗口"
第二层 付费·窄验证（飞常准 MCP）：top1/2 × 3-5 日期 × 2-3 中转方案 ≈ 10 calls = ¥5
  → 可成交价 + 具体中转组合 + 舱位
```

即方法论文档"免费完成方案可行性，付费完成资源确认"的实例化。全量付费扫一遍需 ¥50-100，两层策略 **¥5**。

**「最佳」的诚实输出形态**：

> "可获得的缓存价数据中，上海出发、X 月 Y 日前后、中转一次为最低参考区间 ¥3,200-3,500
> （置信度：中，缓存价，采集于 Z 日）。建议出行前 6 周用实时源复核。"

不承诺保证最佳——票价动态，任何引擎都做不到。可加通用经验（提示词注入，非工具数据）：国际票通常提前 6-10 周处于价格洼地。

**对设计的推论：查询即采集（sweep 即基线）**

此场景正是 L3 价格基线的采集器：每次 sweep 产生的 机场×日期×价格 矩阵自动落盘。
规划越多 → 基线越厚 → 免费推荐越准。`flight_price` 必须设计为
"先命中本地基线，再补增量查询"，且 sweep 结果无条件沉淀。

---

### 同类项目调研（GitHub · 2026-09-29）

| 项目 | ⭐ | 定位 | 结论 |
|---|---|---|---|
| **jimmytbc/flight-info-mcp** | 0 | **Aviationstack+OpenSky 双源**，与本项目一期组合完全同构 | **最重要的对照样本**，见下 |
| GongRzhe/TRAVEL-PLANNER-MCP-Server | 99（已归档） | Google Maps 薄封装（4 工具） | 反面教材：单源薄包装，无聚合/复核/配额——正是要避免的形态；99⭐ 证明需求存在 |
| alexlmoney83-oss/travel-planning-agent | 51 | LangChain+12306+高德+航班 MCP 的编排 demo | 借鉴 4 个模式（见下）；无治理层 |
| Cooosin/AiClient | 148 | 小红书搜索+高德+和风天气 MCP 组合 | 「小红书攻略作为目的地研究源」可作远期扩展（用户已有 zxkol 生态） |
| vog01r/skyfly-mcp | 1 | OpenSky + FAA 机型库 join | 印证 icao24→机型注册表 join 模式 |
| afjalk09/Trip-Planner-Agent 等 LangGraph 系 | 0–2 | 多 Agent 编排既有 MCP | 即用户否决的「散装 MCP」模型，无治理 |

**从 flight-info-mcp 借鉴（3 项）**：

1. **ICAO-24 目录模式**：其 `get_current_location(flight_iata)` 用 **Aviationstack 的航班记录作为 ICAO-24 目录**反查 OpenSky——航班↔icao24 映射不用自建表，计划源的响应本身就带注册号。采纳。
2. **AD-5 错误分类学**：`NO_MATCH / DATA_UNAVAILABLE / QUOTA_LIMIT / UPSTREAM_FAILURE` + **标注责任 provider**。`QUOTA_LIMIT` 作为一等错误码印证配额感知设计。采纳进错误信封。
3. **工程不变量清单**（never fabricate / never echo keys / typed errors）——采纳；但它刻意 *"surfaces upstream results **without cleaning or reconciling them**"*、*"never caches"*——**这是与本项目相反的立场**：它是无状态公共服务所以选择哑管道，我们是配额经济的私人工具，**归一化+对账+缓存恰恰是核心价值**。

**从 travel-planning-agent 借鉴（4 项）**：

4. **距离触发模式切换**：">800km 自动触发航班查询"的启发式路由。
5. **复杂度分级推理**：多目的地/预算紧张才走重模型，简单场景轻处理——对应本插件 travel_plan 的场景分级 schema。
6. **交通方案对比输出格式**：火车 vs 自驾（含过路费）并排对比——与场景矩阵 §2 一致。
7. **按工具差异化超时**：12306 单独 90s 超时（IP 风控慢响应）——印证慢 provider 需要独立超时策略；另其 MCP 健康检查脚本模式可借鉴。

**战略结论**：GitHub 上**不存在**「配额池化 + 跨源复核 + 价格梯队 + 国内国际 + 门到门 join」的现成实现。最接近的 flight-info-mcp 明确声明**不做**归一化/对账/缓存——恰好是本项目 §-1 整合理由 #5/#6/#9 占据的空地。市场空白假设成立。

---

### 典型场景走查：电车自驾长途（充电规划 + 高速费预估 · 2026-09-29）

用户问题："掌握电车续航的情况下，能否规划在什么服务区充电？能否预估高速费用？"

**高速费用预估 —— ✅ 直接支持（无需额外开发）**

v5 驾车规划 `show_fields=cost` 原文返回：`tolls`（过路费，元）· `toll_distance`（收费里程）·
`toll_road`（主要收费道路）· `traffic_lights`；`strategy=36`（少收费）/`35`（不走高速）/
`43`（躲避拥堵+少收费+不走高速）可按费用偏好换策略；v3 `extensions=all` 可到每段 step 的 tolls。
另有限行判断（`plate` 参数 → `restriction`）。

**充电规划 —— ⚠️ 静态可行，能力边界清晰**

数据基础（全部一手取证）：
- 路线折线：v5 driving `show_fields=polyline`（分路段坐标串）
- 充电站 POI：`/v3/place/around?types=011100`（**官方文档示例原样给出的充电站类型码**），
  `radius` 最大 50km，`sortrule=distance`；POI 返回 name/address/location/tel/distance
- 走廊搜索备选：`/v3/place/polygon`（路线外扩多边形一次查）

**三层算法（插件自建，纯计算可单测）**：

```
① 能耗模型：标称续航 × 高速折扣系数(可配置，默认~0.75；冬季/空调另调)
             × SoC 窗口(充到90%用到15%) → 单段可用里程
② 折线累计：沿 polyline 累计里程，在"预计低电量点"投影出候选服务区位置
③ 候选搜索：低电量点 → place/around(types=011100, r=5-10km) 选最优
   → 把选中的充电站作为 waypoints 重新算路 → 每段精确 距离/耗时/过路费
```

一次 1,200km 跨省行程的配额消耗：驾车规划 2-3 次（150,000/月组）+ 周边搜索 4-6 次
（5,000/月组）≈ **搜索组月配额的 0.1-0.2%**，可忽略。可叠加高德天气（出发城市低温→加大折扣系数）。

**能力边界（必须诚实输出给用户）**：

| 能力 | 有无 | 说明 |
|---|---|---|
| 高速过路费预估 | ✅ | API 原生返回 |
| "在哪个服务区充"的静态规划 | ✅ | POI 位置 + 续航模型 |
| 该服务区**有没有桩/几个桩/什么功率** | ❌ | POI 字段表无此数据；名称含"充电站"仅是间接信号 |
| **实时空闲桩 / 电价** | ❌ | 高德 App 的实时充电状态来自合作接入，未开放 Web API |
| 出发前核验 | — | 输出必须附"出发前用高德App/充电App确认桩状态"提示 |

→ 插件输出的是**充电停靠点推荐（静态）**，不是**充电保障承诺（实时）**。
能耗模型参数必须可配置（车辆画像：标称续航/折扣系数/SoC 窗口），并在输出中标注假设。

---

### 诚实的边界：什么**不**整合

- **12306 保持外部 MCP**：火车是单源领域（无多源竞争），聚合无收益；且已连通已实测。插件不重复造。
- **整合判据**：某领域存在**多个可互换数据源**（航班 5+ 家）才值得聚合进插件；单源领域直接用现成 MCP。
- **高德走 REST 进插件**：有 REST 且门到门需要坐标 join（航班→机场→驾车），进插件参与配额账本；其官方 MCP 保留给插件外临时地理查询。
- **飞常准/航班管家保持外部 MCP**：付费现成 MCP，不重复封装；插件以工具描述指引模型何时调用它们。

---

## 0. 设计立场

用户诉求是「聚合多家免费服务、充分利用额度、必要时多家比对」。调研后必须修正两点：

1. **"多家投票"不可行**。免费额度普遍太小（Aviationstack 100 次/月、1 次/60 秒），
   同一个航班问两家就没额度了。
2. **"额度充分利用"的真正杠杆是成本感知调度**，不是"尽量多问"。

因此插件的核心不是「并发问 N 家然后投票」，而是：

> **把宝贵的"计划类"额度（Aviationstack）和廉价的"观测类"额度（OpenSky 4000/日）
> 组合成一次有信息增益的双源印证。**

这也正好对上 DSH 插件契约里的「可替换能力三层接缝」——
Provider 是可替换的，调度与复核策略是插件的核心资产。

---

## 1. 分层结构

```
┌─────────────────────────────────────────────┐
│ Consumer 层：defineTool                      │
│   flight_status / flight_verify / flight_quota │
├─────────────────────────────────────────────┤
│ Orchestration 层：planner + verifier          │
│   Planner  决定「花哪家的额度、查几个源」      │
│   Verifier 用观测校验计划，产出置信度          │
├─────────────────────────────────────────────┤
│ Quota 层：ledger + admission control          │
│   周期感知记账、成本预估、超额降级             │
├─────────────────────────────────────────────┤
│ Provider 层（可替换，插件内注册）             │
│   opensky · aviationstack · ⏳ domestic-paid  │
│   ⏳ aviation-edge · ⏳ airlabs                │
└─────────────────────────────────────────────┘
```

## 2. Provider 接口（三层接缝的 Provider 层）

每个 provider 是一个独立模块，导出统一形状：

```ts
interface FlightProvider {
  id: string
  /** 本 provider 能回答哪类问题 */
  provides: ('planned' | 'observed' | 'static')[]
  /** 该查询的预估额度成本。OpenSky 是 query-dependent，不能按 provider 取常量 */
  estimateCost(query: FlightQuery): CostEstimate
  /** 当前是否可用：凭据在否、额度是否够、时间窗是否合法 */
  checkAvailability(query: FlightQuery, now: Date): Availability
  /** 实际拉取。返回 normalized 记录或带 reason 的失败 */
  fetch(query: FlightQuery, signal: AbortSignal): Promise<ProviderResult>
  /** 该源典型的新鲜度，用于置信度加权 */
  freshness: 'live' | 'delayed' | 'batch'
}
```

**为什么 `estimateCost` 挂在 query 上**：OpenSky 的 `/states/all` 按包围盒面积计价（1–4 credits），
`/flights/*` 按跨越天数计价（4 → 960×N）。这是**同一个 provider 内成本差 240 倍**的结构，
必须在查询前算清楚，否则配额账本失去意义。

**归一化输出**（canonical record）——各源字段名完全不同，必须在 provider 边界内收敛：

```ts
interface FlightRecord {
  flightIata?: string        // CCA150
  icao24?: string            // OpenSky 侧主键
  callsign?: string
  airlineIata?: string
  departure?: { iata?: string; icao?: string; scheduled?: string; estimated?: string; actual?: string }
  arrival:   { 同上 }
  position?: { lat: number; lon: number; altMeters: number; onGround: boolean; observedAt: string }
  status?: 'scheduled' | 'active' | 'landed' | 'cancelled' | 'diverted' | 'incident' | 'unknown'
  providerId: string
  fetchedAt: string
  raw?: unknown              // 保留原始，供追溯争议
}
```

## 3. Quota 层（本插件的真正资产）

### 3.1 记账模型

额度是 `(provider, bucket, period)` 三元组上的计数器，不是单一数字：

- OpenSky：`states` / `flights` / `tracks` **三个独立桶**，各自每日或每分补货
- Aviationstack：单桶，按月补货，且有 **1 次/60 秒**的滑动窗口约束

```ts
interface QuotaBucket {
  providerId: string
  bucket: string          // 'states' | 'flights' | 'tracks' | 'default'
  period: 'hour' | 'day' | 'month'
  limit: number           // ⏳待填：来自 01 文档
  used: number
  resetAt: number
  /** 滑动窗口约束（如 Aviationstack 1/60s），与计数配额是两套机制 */
  minIntervalMs?: number
  lastCallAt?: number
}
```

### 3.2 三个必须处理的工程问题

1. **周期边界**：日/时/月各自的 resetAt 计算，跨周期惰性清零（读时判断 `now > resetAt`）。
2. **滑动窗口**：`minIntervalMs` 与计数配额是两回事。Aviationstack 同时受两者约束，
   只记次数会在 1 分钟内第二次调用时撞 429。
3. **跨会话持久化**：DSH 会话重启后不知道上次花了多少。
   需要写入 profile storage，否则每次新会话都误以为额度是满的。
   ⏳ 待确认：写 `<DSH_HOME>/storages/` 还是插件自有目录。

### 3.3 超额降级策略

额度耗尽**不能直接失败**——那正是插件存在的意义（替用户管额度）。降级顺序：

```
计划类源(Aviationstack)额度耗尽
  → 退回仅观测类：OpenSky 仍可回答"飞机在哪、是否已着陆"
  → 明确告知用户：本次结论仅基于位置观测，无法给出计划时间对比

OpenSky states 额度耗尽
  → 429 的 X-Rate-Limit-Retry-After-Seconds 直接进等待队列
  → 不静默重试

两者都耗尽
  → 显式失败，附各源剩余额度和恢复时间
```

## 4. Verifier 层（差异化核心）

### 4.1 为什么不是投票

`planned` 类源和 `observed` 类源回答的是**不同问题**，不存在"谁对谁错"：

- planned 说：这班机**应该** 14:35 落地
- observed 说：14:35 时它**还在** 400 海里外的航路上

这不是数据冲突，是**可用推理**：计划落地但尚未抵达 → 延误，且量级可从剩余距离/地速估算。

### 4.2 判定逻辑（草案）

```
输入：FlightRecord[]（至少 1 个 planned + 1 个 observed）
      now, 目标机场 icao

1. 时间对齐
   - observed.observedAt 与 planned.estimated 的时差 Δt
   - Δt 超过观测源延迟阈值 → 结论不可靠，标 needs-more-data

2. 地理验证
   - 目标机场 40km 半径内是否有观测？
   - 是 → landed（落地点与记录时刻一致则 confirmed）
   - 否 → 仍在途中

3. 延误量级
   - 以观测位置 → 目的地方向，结合最后已知地速
   - 输出区间而非点估计（ETA 的诚实形式是区间）

4. 置信度
   - 参与验证的源数量
   - 各源 freshness 权重（live > delayed > batch）
   - 是否跨越了源的批处理边界（OpenSky /flights/* 只有 T-1 以后）
   - 输出 low / medium / high，并在 output.render 写明**为什么**是这个等级
```

**关键**：第 4 步的「为什么」必须进模型可见输出。用户要求的是"准确时能多家比对"，
那置信度的**依据**和结论同等重要，否则用户无法判断该不该信。

### 4.3 已知的准确性陷阱（来自 01 文档）

- OpenSky `/flights/*` 是夜间批处理，只覆盖 T-1 及更早 → **绝不能用于当日实时判断**
- 机场必须用 ICAO（`ZBAA`）不能用 IATA（`PEK`）→ 归一化层必须处理
- OpenSky 匿名模式只有最新状态且 10 秒分辨率，`time` 参数被忽略
- 中国境内空域 ADS-B 覆盖**未取证，必须实测**——若不可用，OpenSky 对国内航班完全失效

## 5. Tool 表面（Consumer 层）

三个工具，边界清晰：

| Tool | 职责 | 是否耗额度 |
|---|---|---|
| `flight_status` | 查一个航班的事实（航班号/机场/日期） | 是，按 planner 决策 |
| `flight_verify` | 显式双源交叉复核 + 置信度 | 是，1 planned + 1 observed |
| `flight_quota` | 只读：各源各桶剩余额度与重置时间 | 否 |

**工具契约要求**（DSH 插件红线）：
- `execute` 只返回 `output.schema` 声明的规范 JSON 值
- 人类可读内容放 `output.render`
- 尊重 `exec.signal`
- **模型可见的每一次查询都必须能从会话日志重建** → 需新增 `SessionEventMap` 会话事件，
  记录「问了哪个航班、动了哪些源、花了多少额度、得到什么结论」

**为什么不合并成一个工具**：`flight_verify` 是这个插件存在的理由，
它的输出结构（置信度 + 分歧明细 + 依据）与 `flight_status` 显著不同，
合并会让 schema 变成一堆 optional 字段。

## 6. ⏳ 依赖调研补齐才能定的事项

| 事项 | 阻塞于 |
|---|---|
| 桶 limit 数值与周期 | 01 文档 §2 的 D 级取证 |
| Aviation Edge / AirLabs 是否纳入 | 其额度与覆盖 |
| 国内付费源选择与成本 | 供应商报价 |
| OpenSky 中国境内可用性 | **必须真机实测** |
| 额度账本持久化位置 | DSH storage 约定确认 |
| Aviationstack 免费额度 100 还是 500 | 官方 pricing 页 |

---

## 7. 已定死的不变量（供后续实现自检）

1. 所有可调参数走 Schemastery `Schema<Config>`，**不得硬编码**——判定标准是 cordis.yml 能否改。
2. 一切贡献用 `ctx.effect()` / `ctx.on()`，不做手动 removeListener/clearInterval。
3. provider 的失败必须**带 reason 返回**，不得抛穿——用户需要知道是「额度用完」还是「该源不支持此查询」。
4. 置信度输出必须携带依据，不允许只给等级。
5. 观测类与计划类源**不可混为一谈**做投票。

---

# v2 定稿（2026-09-29 · 范围确认后）

## v2-0. 范围收口与三条定稿原则

**范围：专注交通规划。** 航班（国内+国际）、火车（经既有 12306 MCP）、地面交通（高德）。
酒店/景点内容/签证明确不做（`08-scenario-coverage.md` 的 🌐/❌ 行）。

| # | 定稿原则 | 落地机制 |
|---|---|---|
| 1 | **免费优先，付费 = 确定性校准**（飞常准角色：免费链路已确定"哪天/哪到哪"后，补价格/精确性） | 校准梯队 + **支出闸门**（付费月预算默认 ¥20，超阈值动作需确认） |
| 2 | **配额池化自动轮转**，月度额度自动恢复 | 同能力组按 costPerCall 升序轮转，`QUOTA_LIMIT` 自动降级；账本**惰性周期重置**（读时判 resetAt）+ 持久化（profile storage，重启不丢） |
| 3 | **热插拔且 agent 可维护**——加/删/改工具是日常维护，不是重新开发 | manifest 驱动 + `provider_admin` 维护工具 + 面向 agent 的维护手册 |

## v2-1. 两级热插拔

**L1 · 对话级（分钟，不动代码）**——维护工具 `provider_admin`：

| 动作 | 效果 |
|---|---|
| `list` | 各源状态/额度余量/降级顺序/上次校验日期 |
| `enable` / `disable` | 热下线某源（收费化/死亡/故障） |
| `set_quota` | 改额度/周期（服务商调免费额度时） |
| `reorder` | 调同能力组降级顺序 |
| `set_budget` | 调付费月预算闸门 |

实现：provider **manifest 存运行时可写目录**（`<DSH_HOME>/storages/flight-aggregator/providers.json`），
**每次请求重读 manifest**（本地小 JSON 开销可忽略）→ 改完下一次调用即生效，无需重启。
**key 等机密不进 manifest**，留在 Schemastery 设置界面管理。

**L2 · 适配器级（半天，一个文件）**——新服务出现：
按 `providers/_template/`（逐行注释 adapter 模板 + README）写一个 adapter，
manifest 加一条声明，真机冒烟一次，完成。适配器保持**薄**（认证+端点+字段映射），
智能全部住在编排层——所以模板足够小、足够稳定。

## v2-2. Provider Manifest（声明式契约）

```json
{
  "id": "airlabs",
  "status": "active",
  "tier": "free",
  "costPerCall": 1,
  "capabilities": ["flight.status", "flight.delay", "airport.db"],
  "auth": "query_param:api_key",
  "quota": { "group": "search", "period": "month", "limit": 1000 },
  "billing": { "chargeOnFailure": false },
  "rateLimit": { "minute": null, "hour": null, "month": 1000 },
  "errorMap": { "minute_limit_exceeded": "QUOTA_LIMIT", "not_found": "NO_MATCH" },
  "docs": "docs/07-api-reference.md#airlabs",
  "verifiedAt": "2026-09-29",
  "notes": "免费 key 单查 limit=50；签名认证备选"
}
```

## v2-3. 仓库结构（实现蓝图）

```
dsh-flight-aggregator/
├── src/
│   ├── index.ts              # 契约入口 apply(ctx, config)
│   ├── config.ts             # Schemastery：keys / 付费预算闸门 / 车辆画像
│   ├── core/
│   │   ├── registry.ts       # manifest 加载+schema 校验（每请求重读）
│   │   ├── ledger.ts         # 配额账本：持久化+惰性重置+组内轮转
│   │   ├── canon.ts          # canonical schema + 字段归一
│   │   ├── places.ts         # 机场/城市/车站五码注册表（启动抓库+本地命中）
│   │   ├── energy.ts         # 电车能耗模型（纯函数）
│   │   └── verify.ts         # 跨源复核引擎（观测校验计划+置信度）
│   ├── providers/
│   │   ├── _template/        # adapter 模板 + 注释 README（L2 载体）
│   │   ├── airlabs/{manifest.json, adapter.ts}
│   │   ├── aviationstack/… opensky/… travelpayouts/… amap/…
│   │   └── external.json     # 飞常准/12306 等 external-mcp 指引声明
│   └── tools/                # 7 个 defineTool
├── PROVIDERS-PLAYBOOK.md     # ⭐ 面向 agent 的维护手册（清单式）
└── tests/
```

**工具面（7 个，定稿）**：`flight_status` / `flight_price`（内置两层策略：免费 sweep →
付费校准，付费前查预算闸门）/ `flight_verify` / `resolve_place` / `route_ground`(含 EV) /
`quota_status` / **`provider_admin`**。

## v2-4. PROVIDERS-PLAYBOOK.md 章节（agent 维护手册）

1. 看现状：`provider_admin list` 输出怎么读
2. 某源改免费额度 → `set_quota` 五分钟清单
3. 某源收费化/死亡 → `disable` + 降级链自动收敛清单
4. 上新免费源 → L2 模板五步清单（adapter → manifest → 冒烟 → ledger 挂账 → 更新 verifiedAt）
5. 新工具需求 → 编排层组合既有 capability 的判定树
6. 任何改动后的回归三件套：单测 → 真机一击 → `quota_status` 对账

## v2-5. 维护场景 → 操作路径（验收表）

| 场景 | 谁做 | 路径 | 耗时 |
|---|---|---|---|
| 某源调免费额度 | agent | `provider_admin set_quota` | 分钟 |
| 某源收费化/关停 | agent | `provider_admin disable` | 分钟 |
| key 轮换 | 用户 | DSH 设置界面 | 分钟 |
| 新免费源出现 | agent | L2 模板写 adapter + manifest | 半天 |
| 新工具需求 | agent | 编排层组合既有 capability | 视范围 |
| 付费预算调整 | 用户/agent | `provider_admin set_budget` 或设置 | 分钟 |

## v2-6. 实施路线（文件级）

| Phase | 交付 | 依赖 |
|---|---|---|
| **0** | 契约入口 + config + registry + ledger + canon + `_template` + **12306 走查模式验证管道**（唯一已实测源）+ 单测 + PLAYBOOK 初稿 | **无任何 key** |
| 1 | airlabs / aviationstack / opensky / travelpayouts 四 adapter + flight_status / flight_verify / flight_price(免费层) + 注册表启动抓库 | 4 个免费 key |
| 2 | amap adapter + route_ground(含 EV) + resolve_place 增强 | 高德 key |
| 3 | 校准梯队接飞常准 MCP 指引 + 支出闸门实战 | 飞常准开通决策 |

## v2-7. 同源模式对照：searchfusion 是本模式的第一次实例化（2026-09-29）

用户指出本插件与自研 searchfusion（`D:\WorkSpace\Github\searchfusion`，FastAPI+SQLite，生产运行中，
README 原文："多源搜索聚合 + 多爬虫容错回退的 Web 中间件…自带管理面板、MCP Server、**额度治理与档位调度系统**"）
高度同构。对照源码（`negmark.py` / `tier_governor.py` / `quality.py` / README）后的结论：

### 独立收敛（相互验证，无需改动）

| searchfusion 机制 | 本设计对应物 |
|---|---|
| 配额感知调度：免费余额比例排序、耗尽熔断、**月初自动复活** | ledger 组内轮转 + 惰性重置 |
| 场景化引擎池（六场景各自回退链） | capability groups |
| 五角色 fallback 链 | 降级链 |
| 引擎分档 A每月免费/B一次性/C收费 | manifest tier: free/paid |
| 管理面板额度页（熔断阈值/上限/计费模式） | `provider_admin` + `quota_status`（对话级） |
| `docs/research/` 新增引擎/爬虫指南 | `_template` + `PROVIDERS-PLAYBOOK` |

### 移植项（本轮采纳，改动 v2 设计）

1. **负标系统**（源 `negmark.py`）：`(provider, capability)` 组合负标——失败计数升级冷却时长
   （如连续 3 次 QUOTA_LIMIT → 冷却至次日）、**成功一次自动解封**、候选分 fresh/stale。
   manifest 管静态策略，负标管运行时声誉，两层并存。进 Phase 1（ledger 同表可承载）。
2. **计费模式三分类**（README 额度参数）：`monthly 月度刷新 / total 总量制 / unlimited 充值制`
   替代 v2-2 的 `period: month/day`——OpenSky=日(total/日)、AirLabs=monthly、AeroDataBox credits=total。
3. **Provider Governor 只留地基**：tier_governor 的次数窗口径（最近 200 次/40 底线）适配为
   **近 30 天窗口**（低频 episodic 场景），本轮不建本体——ledger 已按调用记录 success/error_type，
   数据攒够再上自动治理（与 searchfusion 自身演进路径一致）。

### 类比断裂处（明确不抄）

| searchfusion | 为什么不抄 |
|---|---|
| 多源并发聚合 + BM25 重排 + 去重 | 搜索结果同质，投票合理；航班事实类型化（计划/观测/价格），跨类型投票违反 §7 不变量 #5。对应物 = canon 归一 + verify 类型化复核 |
| 全免费经济，付费爬虫只做终结者 | 付费源在此是**校准梯队**（预算闸门），经济模型不同 |
| 结果即用即弃 | 快照沉淀 L3 基线（查询即采集） |

### 是否抽象通用 fusion 框架：**暂不**

两实例的差异处（类型化事实/付费校准/持久基线）正是通用框架会漏抽象的地方。
手抄模式，第三个实例出现后再议（rule of three）。

---

# v3 定稿（2026-09-29 · 部署形态与智能路由）

> v2 的"DSH 插件契约 / apply(ctx,config) / Schemastery"节由本节**取代**；
> 其余（canonical schema、校准梯队、manifest 热插拔、negmark 移植、PLAYBOOK、场景矩阵）全部沿用。

## v3-0. 部署决策：极空间独立服务，MCP 接入 DSH

**决策**：不做成 DSH 插件。做成独立服务（Python/FastAPI + SQLite，searchfusion 同构骨架）
部署在**极空间**（Docker Compose），以 MCP（streamable-http）接入 DSH。

**理由**：
1. 本服务是**数据资产型**：L3 基线采集、出行日监控、NOTAM 轮询需要 7×24——DSH 插件随宿主生死，基线断采即永久缺数据点
2. searchfusion 的 Python 治理资产（negmark / tier_governor / 额度治理 / 管理面板）**逐行复用**，而非跨语言重写
3. agent 侧体验不变：7 个干净工具，治理全黑盒（第一原则与部署形态无关）
4. 多客户端可用；基线数据与 DSH 重装解耦

```
极空间（Docker，常开）
└── travelfusion/
    ├── adapters/      airlabs · aviationstack · opensky · travelpayouts · amap
    ├── governance/    quota ledger(三计费模式) · negmark · (governor 留地基)
    ├── core/          canon · verify · places(五码注册表) · energy · eligibility⭐
    ├── collectors/    L3基线定时采集 · 出行日监控 · NOTAM轮询        ← 7×24 本体
    ├── mcp/           7 个工具（streamable-http）+ provider_admin
    ├── admin/         Web 面板（复用 searchfusion 模式）
    └── data/          quota.db · baseline.db · snapshots.db
DSH（Windows）
└── cordis.patch.yml 挂 mcp → agent 只见 7 个工具
火车：Phase 1 起由服务内嵌 12306 MCP 客户端（子进程托管）统一缓存与低频纪律
```

## v3-1. ⭐ 交通方式资格引擎（mode eligibility · 智能路由）

**用户要求**：如"成都→乐山 个人游"——即便 agent 未指定交通方式倾向，也不应查任何航班。
**结论：可行，且是规则引擎不是 AI**——距离 × 码表存在性 = 确定性资格判定。

### 规则表（阈值可配置）

| 条件 | 资格 |
|---|---|
| 距离 < 300km | 高铁+自驾；**航班 BLOCKED**（理由：距离过短，高铁门到门更快） |
| 300–1000km | 高铁优先+自驾；航班低优先（仅显式要求或高铁无果） |
| 1000–3000km（国内） | 航班+高铁并查比选 |
| > 3000km（国内） | 航班优先 |
| 跨境 | 仅航班 |
| 码表无商业机场 / 无车站 | 对应方式直接关闭 |
| 同城 | 不输出城际方案 |

（300km/1000km 为默认值，进配置；先例：GitHub travel-planning-agent 的 ">800km 触发航班"启发式。）

### 三层架构

1. **判定层（advisory）**：纯规则零 API——注册表本地查机场/车站存在性 + haversine 距离
   + 距离带 → 资格矩阵，每项附一句理由
2. **执行层（enforcement，护栏）**：航班类查询过资格闸——不合格且未 `force` →
   类型化 `NOT_APPLICABLE(reason)`，**配额消耗 0**。LLM 判断可以错，守门员不会错
3. **理由透出**：资格矩阵+理由原样返回 agent（"航班已跳过：距离过短"），agent 零解释负担

### 成本与联动

`core/eligibility.py` 约 100–150 行纯函数 + 规则表，依赖的码表是注册表既有内容，单测极易。
同一引擎白送：同城检测、无车站→纯自驾、**场景属性联动付费闸门**（个人 ¥20/月默认 vs 团组按 trip 预算）。

## v3-2. 实施路线（服务化修订）

| Phase | 交付 | 依赖 |
|---|---|---|
| **0** | 服务骨架（FastAPI+SQLite+Docker）+ registry/ledger/negmark + canon + **eligibility 引擎** + places 注册表启动抓库 + `_template` + 单测 + PLAYBOOK 初稿 | **无任何 key** |
| 1 | 四免费 adapter + flight_status/flight_verify/flight_price(免费层) + 12306 MCP 子进程托管(火车工具) | 4 个免费 key |
| 2 | amap adapter + route_ground(含EV) + L3 基线采集器 + 出行日监控 | 高德 key |
| 3 | 校准梯队(飞常准 MCP 指引) + 支出闸门实战 | 飞常准开通决策 |

---
