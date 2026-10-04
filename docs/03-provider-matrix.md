# 航班数据源完整能力矩阵

> 核验日：2026-09-28　｜　配套：`01-source-research.md`（甄别日志）、`02-architecture.md`（架构）
> 证据级别：**A**=厂商官方页原文　**B**=第三方横评转述定价页　**C**=官方文档/开源实现反推

---

## 0. 结论速览

**免费额度梯队差距是 300 倍，不是量级相近。** 选错主力源，插件的可用性直接归零。

| 梯队 | 服务 | 免费额度 | 可用性 |
|---|---|---|---|
| **主力** | **Aviation Edge** | **30,000 calls/月** | ✅ 首选 |
| **主力** | **OpenSky**（注册） | **4,000 credits/日** | ✅ 首选（观测类） |
| **主力** | **AeroDataBox** | **贡献 ADS-B 数据 → 永不过期 credits** | ✅ 但需自建馈电 |
| 够用 | SkyLink | 1,000 req/月（需申请，非自助） | 🟡 评估期额度 |
| 紧张 | Aviationstack | 100 req/月，**1 req/60s** | 🟡 只能省着用 |
| 紧张 | FlightAPI.io | **20 calls** | 🔴 形同没有 |
| **已死** | Amadeus Self-Service | 2026-07-17 关停 | ❌ |
| **已死** | Kiwi Tequila | 邀请制，自助注册关闭 | ❌ |

---

## 1. 主力候选（详细）

### 1.1 Aviation Edge — 免费额度断层第一　【A/C】

| 项 | 值 | 来源 |
|---|---|---|
| 免费额度 | **Developer 30,000 calls/月** | 官方页 `aviation-edge.com/premium-api/`，两个引擎独立抓取到同一表述 |
| 认证 | API key（`x-apikey` header） | ⏳ 需从文档页确认 |
| 端点 | Flight Tracker API、Schedules API、IATA/ICAO 数据库、机场/航司/航线 | 官方页 |
| 覆盖 | ⏳ 中国国内覆盖**未取证** | — |

**⭐ 关键计费规则（官方 FAQ 原文）**：
> "each action of pulling data counts as 1 API call. **If the API returns an error whether because the endpoint is incorrectly used or the data you request is unavailable, this does not count as an API call and does not consume your call limit.**"

→ **失败请求不计费**。配额账本必须在插件侧自行记账（官方不返回剩余量），但错误可安全重试。

**覆盖广度**：军方/政府/私人/货运航班，只要公开广播都能跟踪；私人飞机若无公开时刻表则只能走 Tracker 拿实时位置。

⚠️ **生态风险**：GitHub 全站搜索 `aviation-edge.com` 仅 3 处命中，SDK/教程生态极薄。
30,000/月 的额度与极薄的生态形成反差，**接入前必须小流量实测稳定性**。

### 1.2 OpenSky Network — 额度第二，唯一的免费"观测"源　【A】

**官方文档一手原文**（`openskynetwork/opensky-api` → `docs/free/rest.rst`）

- Base：`https://opensky-network.org/api`
- 认证：**仅 OAuth2 client_credentials**，token 30 分钟过期
  - `https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token`

**三个独立额度桶**：`/states/*` · `/tracks/*` · `/flights/*`，互不消耗

| 层级 | Credits | 周期 |
|---|---|---|
| 匿名（按 IP） | 400 | 日 |
| **注册用户（免费）** | **4,000** | **日** |
| Active feeder（≥30% 在线率） | 8,000 | 日 |
| Licensed | 14,400 | **小时** |

`/states/all` 按包围盒面积计价（sq° = 纬差 × 经差）：

| 面积 | Credits |
|---|---|
| ≤25 sq° 或仅 serial | 1 |
| 25–100 | 2 |
| 100–400 | 3 |
| >400 或 global | 4 |

`/flights/*`、`/tracks/*` 按跨越的日历天分区数 N 计价：实时/<24h = 4；1–2 天 = 30；
3–10 = 60×N；11–15 = 120×N；16–20 = 240×N；21–25 = 480×N；>25 = 960×N。

**响应头**：`X-Rate-Limit-Remaining` 剩余量；耗尽返回 `429` + `X-Rate-Limit-Retry-After-Seconds`。
→ **本插件里唯一能直接读到官方剩余额度的源**，账本可与之对账。

**致命限制**：
- `/flights/aircraft`、`/flights/arrival`、`/flights/departure` 是**夜间批处理**，
  **只有前一天及更早的航班** → **不能用于当日实时判断**
- 机场参数是 **ICAO**（`EDDF`/`ZBAA`），不是 IATA
- 匿名只有最新状态且 `time` 参数被忽略，10 秒分辨率；认证可回溯 1 小时、5 秒分辨率

### 1.3 AeroDataBox — 免费路径是"贡献数据"而非"领配额"　【A】

**这是本轮最重要的发现，也纠正了通行认知。**

> 官方 pricing 页 "Free" 档原文：**"subject to data contribution — Contribute data to
> AeroDataBox and convert it into non-expiring API credits — then call the API without
> a paid subscription."**

即：**没有固定免费额度，跑一个 ADS-B 馈电（feed）换永不过期的 credits**。
"Basic 600 units/月"是 RapidAPI 旧免费层，已不是最优路径。

**直接订阅（自营，非市场）**：

| 档 | 月费 | units/月 | 速率 | 历史数据 | 未来时刻 | 缓存 |
|---|---|---|---|---|---|---|
| Starter | $19 | 40,000† | 5 req/s | 180 天 | 180 天 | **标准 7 天** |
| Growth | $99 | 400,000† | 10 req/s | 365 天 | 365 天 | 扩展（订阅期内任意时长） |
| Scale | $499 | 4,000,000† | 20 req/s | 365 天 | 365 天 | 扩展 + 取消后 1 年 |

端点按复杂度分 Tier：Tier 1 = 1 unit，Tier 2 = 2 units，Tier 3 = 6 units。

**⚠️ 商业条款（对插件设计有硬约束）**：
- **不可转售**：任何档位（含免费）都**不能**把 API 或数据再分发给第三方。
  包括"转格式/改字段名后再发布"也算原始数据分发。
- 商业用途：Starter/Growth 允许一般商业使用；**B2B 衍生作品再授权仅 Scale 允许**
- 署名：所列全部档位**均不要求署名**
- RapidAPI / API.Market 订阅享受祖父条款，厂商改价不影响存量订阅
- 数据覆盖**不保证全球完整**（官方原话 "coverage is extensive but not worldwide"）

**覆盖实测参考（B 级）**：美国时刻表 100% / 实时状态 86%；法国 92% / 79%。
登机口/行李转盘数据标注为 "sometimes" 而非保证。

**中国段可行替代**：极速数据 `api.jisuapi.com/flight/query`、聚合数据 `juhe.cn/docs/api/id/498`、
京东万象 `wx.jdcloud.com/api_4_104` —— ⏳ 额度与覆盖未取证。

---

## 2. 次级候选

### 2.1 Aviationstack — 免费额度比普遍认知少 5 倍　【A/B/C】

- 免费：**100 requests/月**，个人授权，HTTPS
- **1 request / 60 秒**（官方 documentation 页），单次结果上限 100 条
- 付费：Basic $49.99/月（10,000）· Professional $149.99/月（50,000）· Business $499.99/月（250,000）
- **历史数据、航司航线、自动补全、航班时刻、未来航班全部锁在付费档**
  → 免费层只有实时状态 + 机场/航司基础数据
- 端点与认证（开源 MCP 实现反推）：`AVIATION_STACK_API_KEY` 单 key，
  flight_status / flights / historical / schedule / future_flights / airports / airlines / routes / taxes / countries / cities

### 2.2 SkyLink API — 厂商自建对比内容丰富，需打折看　【C】

⚠️ **该站发布大量"竞品对比"文章，均为自家营销内容，其对比结论带利益倾向**。

- 免费：**1,000 requests/月**，但**需提交申请**，非自助注册
- 能力：ADS-B + METAR/TAF + NOTAMs + 74,000+ 机场 + 航行图 + ML 预测

### 2.3 FlightAPI.io — 20 次免费，纯试玩　【A】

- 官方原文："Start with **20 free API calls**"（另有页面写 100 req/30 天，**官方自相矛盾**）
- Lite $49/月 30,000 credits · Standard $99/月 100,000 · Plus $199/月 500,000
- credit 计价：单程 2 · 往返 2 · 多程 5 · **航班跟踪 1** · 机场时刻 2
- 700+ 航司，自称 8,000+ 开发者，声称 99.9% uptime
- 机场时刻覆盖：前 2 天 至 后 3 天
- **不能预订**

### 2.4 AirLabs — 端点与错误码已确认，额度待定　【A】

- Base：`https://airlabs.co/api/v9/`，认证为 `api_key` 查询参数（**v9 已不需要 `api_host`**）
- 端点：`ping` `flights` `schedules` `airports` `airlines` `fleets` `routes` `cities`
  `countries` `timezones` `taxes` `suggest` `nearby`
- **错误码直接暴露了限流维度**：`minute_limit_exceeded` / `hour_limit_exceeded` /
  `month_limit_exceeded` → 配额账本需同时建模「分钟/小时/月」三种窗口
- 付费起价 $19/月 Basic（共 4 档）⏳ 免费档是否存在未取证

---

## 3. 国内源

### 3.1 飞常准 VariFlight MCP — 已自带 MCP，这是最大的变量　【A】

官方 MCP 平台（`cmcp.variflight.com`）已可直接接入 Agent：

- **36 个 Travel Tools**（页面实数，非摘要所称 19）
- 端点：`https://c-gw.variflight.com/chat_message/mcp/api`（WorkBuddy 用 `/legacy`）
- 认证：登录后生成 MCP Key，`Authorization: Bearer`
- 登录：微信扫码 / 手机号验证码，**区分个人账号与企业账号**
- 官方文档称 Flight Status Data 提供 **14 天免费试用**

**工具能力远超"查航班"**：

| 工具 | 能力 |
|---|---|
| `getFlightStatus` / `getFlightList` | 航班动态、候选比较 |
| `flightAnalyze` | **延误可能性分析** |
| `getAircraftRotation` | **前序航班追踪**（判断前序延误是否传导） |
| `getAirportOperationOverview` | 机场整体运行状况 |
| `getAirportWeatherBriefing` | 机场天气简报 |
| `getFlightServiceProfile` | 餐食 / Wi-Fi 等舱位服务 |
| `queryUserTripDelayStats` | 个人行程延误统计 |
| `getAirportLowPriceRoutes` / `monitorFlightPrice` | 低价目的地 / 降价监控 |
| `getRouteFlightTickets` | 航线票价 |
| `queryUserTripDetailStats` | 行程足迹 |
| `domesticDirectTrainSearch` / `intermodalTransferSearch` | 火车 / 空铁中转 |

**这对本插件的影响**：国内段如果直接挂 VariFlight MCP，`flightAnalyze` 和 `getAircraftRotation`
已经实现了我们原计划自建的"复核引擎"。插件应考虑**分工**而非重复造轮子——
自建价值在**跨源交叉复核与配额治理**，不在单源查询能力。

### 3.2 飞常准付费 API（非 MCP 通道）

⏳ 企业资质认证，第三方称 **0.03–0.1 元/次**（B/C 级，需官方报价确认）。
数据延迟通常 1–3 分钟。另有 `dataworks.variflight.com` 商业 DataWorks 产品线。

---

## 4. 已排除

| 平台 | 排除理由 |
|---|---|
| **Amadeus Self-Service** | 2026-07-17 关停，新开发者无任何路径；Enterprise 需 IATA/ARC 资质 |
| **Kiwi Tequila** | 自助注册关闭，转邀请制；经 Travelpayouts 需 50,000 MAU |
| **Skyscanner 官方** | 无公开免费层，需商务审批（约 100K MAU） |
| **MyAirports** | 仅 CSV/JSON 静态下载，无 HTTP 查询接口 |
| **AirHelp** | 理赔服务，非数据源 |
| **NextFly** | iOS App，无 API |
| **"Flight Route Data API"** | 无法定位真实指向，"无需 key / 60 次每分钟"无任何证据 |
| **Duffel** | 仅测试模式免费，且是沙箱假数据，无真实航班数据 |
| **Travelpayouts** | 免费注册，但真搜索 API 需 50,000 MAU |

---

## 5. 决定性洞察：ADS-B 类源只给位置，不给航班数据

SkyLink 博客（2026-09-16）这段话是本项目的地基：

> "**You get positions, not flight data.** Everything above hands you an ICAO24 hex address and
> coordinates. **None of them tells you the registration, the aircraft type, the operator, or where
> the flight is going, because none of that is broadcast by the aircraft.** Turning `40621d` into
> 'British Airways 777 from Heathrow' is a **registry join, a schedule correlation, and ongoing
> maintenance** as aircraft change hands."

**三个推论**：

1. **OpenSky / adsb.lol / airplanes.live 无法独立回答航班状态**。
   必须先有一个计划源把「航班号」映射成「icao24」，观测源才有意义。
   → 这决定了插件内部必须维护 **flight ↔ icao24 映射层**。

2. **覆盖跟随志愿者**："Western Europe is very well covered, much of the US is excellent,
   and parts of Africa, central Asia and the open ocean are thin to absent."
   → **中国境内空域 ADS-B 覆盖必须实测**，文档未说明。这是最大的未知项。

3. **社区源无 SLA**："Terms change. Free services get acquired, restructured, or run out of funding."
   → 社区源只能做增强，不能做唯一依赖源。

---

## 6. 仍需实测/取证（下一轮）

| 事项 | 类型 | 阻塞影响 |
|---|---|---|
| **OpenSky 对 ZBAA/ZSPD/ZGGG 等境内机场的覆盖** | **真机实测** | 若不可用，国际段方案需换主力 |
| Aviation Edge 中国国内航班覆盖质量 | 实测 + 文档 | 决定它能否当全球主力还是只做国际段 |
| Aviation Edge 免费层认证方式与端点清单 | 文档页抓取 | 接入实现 |
| AirLabs 是否有免费档 | 官方页 | 备选源 |
| SkyLink 1,000/月 申请通道与到账 | 实操 | 备选源 |
| VariFlight MCP 免费试用额度与限流 | 实操 | 国内段方案 |
| 国内聚合 API（极速/聚合/京东）额度与覆盖 | 官方页 | 国内段降级方案 |
