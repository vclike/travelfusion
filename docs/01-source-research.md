# 数据源甄别与调研记录

> 目标：为 `dsh-flight-aggregator` 插件确定可聚合的数据源。
> 本文件只记录**证据**，不含设计决策。设计见 `02-architecture.md`。

## 证据分级约定

| 级别 | 含义 |
|---|---|
| **A** | 官方文档一手原文（厂商官方仓库 / 官方文档页） |
| **B** | 本地工作区已核验研究资产（`plans/quality-rnd/`，核验日 2026-09-24） |
| **C** | 第三方开源实现反推（SDK / MCP server 源码） |
| **D** | 二手博客或聚合站，**本轮不可用**（取证通道降级） |

> ⚠️ **本轮取证通道降级**：search-fusion MCP `server is disconnected`、pwsh 直连外网 TLS 被拦截、Tabbit 未安装。
> 唯一可用通道是 **GitHub API** 与 **本地工作区资产**。因此**所有 D 级证据本轮全部缺失**，标注 `未取证` 的项不可当作"不存在"，只是"没查成"。

---

## 1. 已定结论（有一手或 B 级证据）

### 1.1 OpenSky Network — ✅ 主力源

**证据级别：A**（`openskynetwork/opensky-api` 官方仓库 `docs/free/rest.rst`）

- Base：`https://opensky-network.org/api`
- 认证：**仅 OAuth2 client_credentials**（Basic auth 已被移除）
  - Token 端点 `https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token`
  - Token **30 分钟过期**，`401` 即过期
- 额度按**三个独立桶**：`/states/*`、`/tracks/*`、`/flights/*` 互不消耗

| 层级 | Credits | 周期 |
|---|---|---|
| 匿名（按 IP 分桶） | 400 | 每日 |
| **注册用户（免费）** | **4,000** | **每日** |
| Active feeder（≥30% 月在线率） | 8,000 | 每日 |
| Licensed | 14,400 | 每小时 |

- `/states/all` 计价（按包围盒面积 sq° = 纬度差 × 经度差）：

| 面积 | Credits |
|---|---|
| ≤25 sq° 或仅按 serial 查询 | 1 |
| 25–100 | 2 |
| 100–400 | 3 |
| >400 或 global | 4 |

- `/flights/*` 与 `/tracks/*` 计价（按跨越的日历天分区数 N）：

| 分区 | Credits |
|---|---|
| 实时 / <24h | 4 |
| 1–2 天 | 30 |
| 3–10 天 | 60 × N |
| 11–15 天 | 120 × N |
| 16–20 天 | 240 × N |
| 21–25 天 | 480 × N |
| >25 天 | 960 × N |

- **关键约束**：
  - 匿名用户只有最新 state vector，`time` 参数被忽略，时间分辨率 10 秒
  - 认证用户可回溯 1 小时，分辨率 5 秒
  - `/states/own` 不消耗 credits，但需认证且只能取自己的接收站
  - **响应头 `X-Rate-Limit-Remaining`** 给出剩余额度；耗尽返回 `429` + `X-Rate-Limit-Retry-After-Seconds`
- **端点**：`/states/all`、`/states/own`、`/flights/all`、`/flights/aircraft`、`/flights/arrival`、`/flights/departure`、`/tracks`
- **⚠️ 致命限制**：`/flights/aircraft`、`/flights/arrival`、`/flights/departure` 由**夜间批处理**更新，
  **"只有前一天及更早"的航班可用**。→ OpenSky **不是实时航班状态源**。
- 机场参数用 **ICAO**（如 `EDDF`），不是 IATA（`FRA`）。中国境内对应 `ZBAA` 而非 `PEK`。
- 文档疑似笔误：`/flights/departure` 处写 "must cover more than two days"，与 `/flights/arrival` 的
  "must not be larger than two days" 矛盾，按 arrival 的写法理解更合理（**接入时实测确认**）。

### 1.2 Aviationstack — ⚠️ 可用但额度极紧张

**证据级别：C**（`Pradumnasaraf/aviationstack-mcp`，2026-09-19 仍在提交，活跃项目）
**额度级别：B**（本地 `plans/quality-rnd/reward-travel-methodology-v21-assessment.md:68`）

- 认证：单一 API Key（`AVIATION_STACK_API_KEY`），无 OAuth
- 端点（经 MCP 实现反推）：flight_status、flights（按航司）、historical_flights_by_date、
  schedule（arrival/departure）、future_flights（明天起约 12 个月）、airports、airlines、routes、taxes、
  countries、cities、airplanes、aircraft_types
- 单次 `limit` 上限 **100 条**
- **免费额度：100 次/月，1 次/60 秒**（B 级证据）
  > 与用户初始认知的「500 次/月」相差 5 倍。**待官方 pricing 页复核**。
- **⚠️ 历史数据不在免费层**：MCP 实现的工具说明将 `historical_flights_by_date` 标注为
  **"Get historical flights for a date (Basic plan+)"** → 免费层拿不到历史航班。
  这直接坐实了用户担心的「拿历史数据当重要参考」问题。

### 1.3 Amadeus Self-Service — ❌ 已关停

**证据级别：B**（`plans/quality-rnd/reward-travel-methodology-v21-assessment.md:54`，核验日 2026-09-24）

- **2026-07-17 关停**（PhocusWire 2026-02-09 预告，Tragento 证实同日 keys 失效，Thunderbit 2026-08 复核）
- 残留路径仅 Amadeus Enterprise（需 IATA/ARC 资质，商务定价）
- 影响：原设想的「免费航班时刻表 + 价格」主力源消失
- 文档给出的替代：Duffel Test 模式（免费沙箱/假数据）、Travelpayouts Data API（免费注册，
  真搜索 API 需 5 万 MAU）、OTA 网页半自动 → **三者本轮均未取证**

### 1.4 飞常准 / VariFlight — ❌ 非免费

**证据级别：B**（同文档 `:68`）：飞常准 API **商业收费**。
→ 用户已选择「接入一个付费国内源」，具体供应商待定（见 §4）。

### 1.5 已排除（非 API 提供方）

| 平台 | 排除依据 | 级别 |
|---|---|---|
| **MyAirports** | 只提供 CSV/JSON 静态数据文件下载（`airports.csv` / `countries.csv`），无按 IATA 查询的 HTTP 接口。所谓"实时航班到达/出发"说法存疑 | D（**待证伪**） |
| **AirHelp** | 理赔服务，非数据 API（其 Claims API 面向航空公司接入）。是否另有面向第三方的状态 API 未取证 | D（**待证伪**） |
| **NextFly** | iOS App，无 API。名称真实性未取证 | D（**待证伪**） |
| **Flight Route Data API** | 未能定位真实指向。"无需 key / 60 次每分钟"无任何证据 | D（**待证伪**） |

---

## 2. 未取证候选（通道修复后必须补）

| 候选 | 待核实 | 优先级 |
|---|---|---|
| **Aviation Edge** | 每月 20,000 次免费额度**未证实也未证伪**；覆盖是否只限欧洲；中国国内覆盖 | **高**（若额度属实，是第二大主力源） |
| **AirLabs** | 免费额度、端点（`/v9/*`）、认证（`api_key` + `api_host` 是否仍必填）、中国覆盖 | **高** |
| **AeroDataBox** | B 级证据称 Basic 600 units/月、1 req/s；需确认是否仍 active（RapidAPI 免费层是**平台共享池**，可能被他人耗尽） | 中 |
| **FlightAware AeroAPI** | B 级证据"$5/月免费额度"表述含糊；是否已停止自助注册 | 中 |
| **adsb.fi / ADSB.lol / ADS-B Exchange** | 自建/替代 OpenSky 的可能性与免费额度 | 中 |
| **国内付费源** | 飞常准/变飞开放平台的实际报价、接口形态、覆盖 | **高**（用户已选定此路径） |
| **Duffel / Travelpayouts** | 作为 Amadeus 替代的免费层现状 | 低 |

> **Aviation Edge 生态信号**：GitHub 全站代码搜索 `aviation-edge.com` 仅 **3 处命中**，
> 其中 2 处是同一作者的个人项目。SDK/文档生态极薄，接入前需确认服务稳定性。

---

## 3. 关键洞察：OpenSky 与 Aviationstack 互补而非冗余

用户设想的「多源投票复核」在免费额度下**不可行**——因为多数源额度太小，问不起两次。

正确的交叉复核形态是 **用观测校验计划**：

```
Aviationstack (1 次宝贵调用)  →  计划/预计时间、航班状态
OpenSky      (N 次廉价调用)   →  实际观测位置
                                    ↓
                          计划 ETA 已到但飞机仍在航路上
                          → 确认延误，且能算出量级
```

**成本**：1 次 Aviationstack + 1 次 OpenSky（小包围盒 1 credit）→ 产出一个双源印证结论。
这绕开了「免费额度太小无法比对」的死结。

**OpenSky 的位置类数据不含延误分钟数**，因此延误量级需要由插件自己从位置/时间推算——
这是插件必须自建的计算逻辑，不能指望数据源直接给。

---

## 4. 待用户决策

- [ ] 国内付费源具体选哪家（飞常准/变飞？报价与接口形态待核）
- [ ] 是否需要「时刻表 + 价格」能力（Amadeus 已死，是否值得为付费源买单）
- [ ] OpenSky 对中国境内空域（`ZBAA`/`ZSPD` 等）ADS-B 覆盖是否可用——**必须实测**，文档未说明
