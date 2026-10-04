# 开发文档关键信息（Tabbit 实测抓取，2026-09-29）

> 方法：本机 Tabbit 实例 `AE717A7E28FDDD79`，真实 Chromium 渲染。
> 解决的是 search-fusion 静态抓取拿不到的页面：**JS 渲染的定价页**、**登录墙后的文档**。
> 入口脚本：`D:\WorkSpace\Tools\tabbit\tabbit-run.mjs`（⚠️ 当前 CLI 已不支持 `--read-only`，勿传）

---

## 1. Aviation Edge —— 免费档已死，价格全部拿到

### `/free-api-key/` 一手原文（决定性）

> "Due to abuse of our Free API keys, **we have decided to no longer offer this feature**. […]
> To use our API keys, we offer a **15$, 29$ or 79$ version** of the API system **for the first month**."

⚠️ **定价页底部仍写着** "you could register for our Free API Key with limited data and API calls"
——**这是过期文案**（页面 footer 仍是 `© 2010-2024`）。以 `/free-api-key/` 为准：**无免费档**。

### 定价（`/premium-api/` 完整表格）

| 档位 | 标准价 | 首月 | 月调用量 | 商业用途 |
|---|---|---|---|---|
| Developer | **$299** | **$7** | 30,000 | ❌ 无 |
| Business | $599 | $15 | 100,000 | ❌ 无 |
| Business Gold | $1499 | $39 | 500,000 | ❌ 无 |
| Unlimited | 询价 | — | 无限 | ❌ 无 |

- 首月是折扣测试期，**次月自动按 $299/$599/$1499 续费**
- 取消：续费前 7 天发邮件，或 dashboard "Invoices" 立即取消
- 所有档位 API 覆盖面相同，仅调用量不同
- ⚠️ 价格口径矛盾：定价页写首月 `$7/$15/$39`，`/free-api-key/` 写 `$15/$29/$79`。**采购前须向厂商核实**

### ⭐ 两个此前未发现的关键能力

**1. Flight Delay API** —— `/v2/public/flightsHistory`
返回完整延误/取消数据，**含延误分钟数**：

```json
{
  "type": "arrival", "status": "landed",
  "departure": {
    "iataCode": "ewr", "icaoCode": "kewr",
    "terminal": "c", "gate": "74",
    "delay": 44,                              // ← 延误分钟
    "scheduledTime": "2024-05-03t17:05:00.000",
    "estimatedTime": "2024-05-03t17:52:00.000",
    "actualTime":    "2024-05-03t17:48:00.000",
    "estimatedRunway": "...", "actualRunway": "..."
  },
  "arrival": { "...", "baggage": "a2", "delay": 17 },
  "airline": { "name": "air canada", "iataCode": "ac", "icaoCode": "aca" },
  "flight":  { "number": "3696", "iataNumber": "ac3696", "icaoNumber": "aca3696" },
  "codeshared": { "airline": {...}, "flight": {...} }
}
```

参数：`code`(机场IATA) `type`(departure/arrival) `date_from`(仅单日) `date_to` `status` `flight_number` `airline_iata`
示例：`/v2/public/flightsHistory?key=KEY&code=JFK&type=departure&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD&status=cancelled`

**2. NOTAM API** —— 实时航行警告，**延误预测的黄金信息源**：

```json
{ "location": "lfpo", "number": "a0142/26", "class": "international",
  "startdateutc": "2026-01-07t13:26:00", "enddateutc": "2026-01-07t23:00:00",
  "condition": "...due to strong weather phenomenons, significant disruptions are observed for flights to and from paris-orly..." }
```

实测样本里直接读到：跑道维护停用、恶劣天气导致中断。
**插件可用它把"为什么延误"变成可解释输出**——这是其他免费源都给不了的。

### ⚠️ 性能陷阱（官方明写）

> "Using the translations function in the API with `&lang=` **will slow down the API calls** when it
> involves a lot of translations of airports, cities and countries."

→ **默认不要传 `&lang=`**，中文机场名在本地映射，不要在 API 层翻译。

---

## 2. ⭐ AirLabs —— 有免费档（此前判定为"未取证"，现证实）

`https://airlabs.co/` 定价表一手原文：

| 档位 | 价格 | 查询量 | 单价 | 商业用途 |
|---|---|---|---|---|
| **FREE PLAN** | **$0** | **1,000 /月** | — | ❌ **仅个人使用** |
| Developer | $49/月 | 25,000 | 0.2¢ | ✅ |
| Business | $99/月 | 100,000 | 0.1¢ | ✅ |

**免费档包含**：
- Airlines & Airports DB
- **Real-Time Flights**
- **Live Schedules** ← 这一项很关键
- Suggestion API、NearBy Geo API + 4 个额外 API
- 标注 "Limited Data" 与 "Limited Support"

**免费档拿不到**：Fleets DB、Routes DB、商业授权。

- Base：`https://airlabs.co/api/v9/`
- 认证：`api_key` 查询参数（v9 **不需要** `api_host`）
- 错误码暴露三层限流：`minute_limit_exceeded` / `hour_limit_exceeded` / `month_limit_exceeded`

> **这条修正了一个重要判断**：免费层并非"时刻表全无"。Aviationstack 锁时刻表，
> 但 **AirLabs 免费档有 Live Schedules**。

---

## 3. 航班管家 DAST MCP —— 完整定价表

**MCP 网关：`https://fly.huoli.com/mcp/dast_mcp`**　认证：Bearer API Key

| 能力 | 工具名 | 单价 |
|---|---|---|
| 航班动态-航班号查询 | `dast_flight_dynamic` | **¥0.50** |
| 航班动态-机场对查询 | `dast_flight_route` | ¥0.50 |
| 航班舒适度 | `dast_flight_happy` | ¥0.20 |
| **未来延误概率** | `dast_delay_rate` | **¥0.50** |
| **机场未来天气** | `dast_future_weather` | **¥0.10** |
| **飞行轨迹** | `dast_flight_path` | **¥0.10** |
| 全国民航每日总览 | `dast_flight_overview_daily` | ¥6.00 |
| 国内机场运行统计 | `dast_airport_operation_statistics` | ¥6.00 |
| 国内航司运行统计 | `dast_airline_operation_statistics` | ¥12.00 |

计费：预付费余额，**成功调用按次扣减，失败不扣费**，余额不足即失败。

**9 个工具入参速查**：

| 工具 | 入参 |
|---|---|
| `dast_flight_dynamic` | 航班号 + 航班日期 |
| `dast_flight_route` | 出发机场 + 到达机场 + 航班日期 |
| `dast_flight_happy` | 航班号/机场对 + 航班日期 + 舱等(可选) |
| `dast_delay_rate` | 航班号 + 出发机场 + 到达机场 + 航班日期 |
| `dast_future_weather` | 机场三字码 |
| `dast_flight_path` | 航班号 + 出发机场 + 到达机场 + 航班日期 |
| `dast_flight_overview_daily` | 统计日期 |
| `dast_airport_operation_statistics` | 机场三字码 + start_time + end_time + route_type |
| `dast_airline_operation_statistics` | 航司二字码 + start_time + end_time + passenger |

> 后三个报表类工具**单人自用几乎无价值**（¥6–12/次，是航班动态的 12–24 倍）。

---

## 4. 飞常准 VariFlight 三个入口（价格与能力分层）

| 入口 | 工具 | 定价 | 认证 |
|---|---|---|---|
| **飞友 AI** `ai.variflight.com/servers/aviation/mcp` | 9 | ✅ **¥0.50/次**（1 credit=¥0.01） | `X-API-Key` |
| **飞常准** `c-gw.variflight.com/chat_message/mcp/api` | **36** | ⚠️ 未公开 | Bearer |
| **DataWorks** `dataworks.variflight.com` | REST | ⚠️ 询价 | — |

飞友版完整单价见 `05-resource-index.md`。要点补充：
- **充值赠 4x credits（30 天有效）** → 短期密集使用可摊到 ¥0.25/次
- 支持 Streamable HTTP（无状态）+ stdio（npm `@variflight-ai/variflight-mcp`）+ OAuth 2.1 PKCE
- `?profile=compact` 让列表类工具默认返回前 20 条 summary，**省 token**
- 单次调用上限约 30 秒
- 99.99% 国内 / ~97% 国际覆盖

---

## 5. 免费层能力总表（更新后）

| 能力 | OpenSky | Aviationstack | **AirLabs** | SkyLink |
|---|---|---|---|---|
| 月/日额度 | **4,000/日** | 100/月 | **1,000/月** | 1,000/月 |
| 实时状态 | ❌ 仅位置 | ✅ | ✅ | ✅ |
| **时刻表** | ❌ | ❌ 锁付费 | ✅ **Live Schedules** | ⏳ |
| **未来航班** | ❌ | ❌ 锁付费 | ⏳ | ⏳ |
| 历史 | T-1 批处理 | ❌ 锁付费 | ⏳ | ⏳ |
| 延误分钟 | ❌ | ✅ | ⏳ | ⏳ |
| 机场/航司库 | ❌ | ✅ | ✅ | ✅ |
| 商用授权 | 研究用途 | ❌ | ❌ 免费仅个人 | ⏳ |

---

## 6. 对架构的三条修正

1. **免费方案比之前评估的更完整** —— AirLabs 免费档补上了时刻表缺口。
   原判断「L2 时刻表免费不可行」需要修正为「部分可行，取决于 AirLabs 免费档的实际覆盖」。

2. **NOTAM 是延误解释的新维度** —— 即便不买 Aviation Edge，
   也能考虑把"为什么延误"作为插件的输出维度预留字段。

3. **Aviation Edge 若买，Flight Delay API 是核心价值** —— 不是 Flight Tracker。
   前者给延误分钟+计划vs实际，正是 verifier 需要的；
   后者的位置数据 OpenSky 免费就能替代。

---

## 7. 待补（Tabbit 下一轮）

- [ ] AirLabs 免费档的**实际覆盖**（中国国内航班？）需注册后实测
- [ ] SkyLink 1,000/月 申请流程与到账
- [ ] `cmcp.variflight.com` 36 工具的完整参数与定价（登录墙）
- [ ] OpenSky 对 `ZBAA`/`ZSPD`/`ZGGG` 的实际覆盖（真机实测，最高优先级）

---

# 第二轮：用户指定 5 个文档 URL 的抓取结果

## 8. SkyLink API —— 完整定价与限流　<https://skylinkapi.com/docs/>

**Base**：`https://data.skylinkapi.com/v3.1`
**分发**：RapidAPI gateway（订阅在 RapidAPI 完成），另支持 Direct API
**版本**：v3.1（无前缀，最新）/ v3（`/v3`）/ v2（旧）

### 完整定价（`/docs/rate-limits/` 一手）

| 计划 | 价格 | 请求/月 | 超额单价 | Webhooks | Historical ADS-B 窗口 |
|---|---|---|---|---|---|
| **FREE Trial** | Free | **1,000** | $0.007/req | — | — |
| Basic | $18.59/月 | 5,000 | $0.007/req | — | — |
| Pro | $45.35/月 | 20,000 | $0.001/req | 1 | ≤90 天 |
| Ultra | $105.59/月 | 70,000 | $0.001/req | 3 | 90 或 365 天 |
| Mega | $205.39/月 | 200,000 | $0.001/req | 10 | 90 或 365 天 |

- **免费试用非自助注册**，须在 `skylinkapi.com/apply` 申请
- 额度用尽返回 `429 {"message":"Too many requests"}`，指数退避重试
- 升级/取消/查用量在 **Polar 客户门户**

### ⚠️ 三个必须知道的计费陷阱

1. **`X-RateLimit-Requests-Limit/Remaining/Reset` 不是月度配额。**
   官方原文：*"These headers report the anti-abuse ceiling, not your monthly plan quota. […] Do not use these headers to work out remaining paid quota or your bill."*
   → 它们是防滥用硬上限，查配额要去 Polar 门户。

2. **认证成功即计费，含错误。**
   *"Requests that reach the API and authenticate count toward your allowance, including ones that error […] (for example 404 or 422). Requests rejected for a missing or invalid key are not counted."*
   → 与 Aviation Edge"报错不计费"**完全相反**。写客户端时必须区别对待。

3. **Historical ADS-B 的窗口由 URL 路径前缀决定，不是 plan 名。**
   `/ultra/history/...` ≤90 天（Pro/Ultra/Mega）；`/mega/history/...` ≤365 天（Ultra/Mega）。
   选错前缀返回 **401/403/422，不是 429** —— 不能当成额度问题去退避重试。

### 能力清单

天气（METAR/TAF/航路 advisories/US 高空风）· 机场档案与**多模式搜索 74,000+ 机场** ·
实时航班状态与进出港时刻 · 距离与方位 · **AI 飞行前简报** ·
ADS-B 实时位置（含注册号/机型/航司富化）· **历史 ADS-B 归档位置** ·
**615,000+ 飞机档案**（按尾号或 ICAO24 hex 查）·
**航图 PDF 覆盖 91 国** · **NOTAM 与 FAA NAS 延误计划** ·
ML（飞行时间估算、CO₂、AI 简报）· **callsign 航线解析与事件 Webhook 推送(v3.1)** ·
**自带 MCP Server** · Python SDK + TypeScript SDK

⚠️ 站点有整套竞品对比页（vs AviationStack / FlightRadar24 / FlightAware / AirLabs / Aviation Edge / Amadeus / Cirium）
——**厂商自撰营销内容，其对比结论不可采信**。

---

## 9. AirLabs —— 接口全清单与签名认证　<https://airlabs.co/docs/>

**Base**：`https://airlabs.co/api/v9/ENDPOINT`　认证：`?api_key=YOUR-API-KEY`
**版本**：v9（最新）。响应格式默认 JSON，加 `.xml` / `.csv` 后缀切换。

### 端点全清单

| 端点 | 分类 |
|---|---|
| Real-Time Flights | 运行数据 |
| **Airport Schedules** | 运行数据 |
| **Flight Delays** ★ | 运行数据 |
| Flight Info | 运行数据 |
| Flight Alert ✔ | 运行数据 |
| NearBy Airports · Name Suggestion | 地理/搜索 |
| Airlines DB · Airports DB · Cities DB | 静态库 |
| **Fleets DB** · **Routes DB** · Countries DB | 静态库 |
| Timezones List · Taxes List | 静态库 |

★ = 文档标注的热门端点　✔ = 已支持

### ⭐ 签名认证（此前未发现）

不在前端暴露 api_key 的方案：

```
signature = api_id : timestamp : md5(timestamp + ":" + api_key)
示例：?signature=144:1790677807:5eb29bccdac6a5062eac5d2672ce8e7c
```
- `api_id` 取自任意响应的 `request.key.id`
- timestamp 为当前 unix 秒，**签名有效期 3 分钟**
- → 插件若要把 AirLabs 接到前端/公开工具，必须走签名而非裸 key

### 三层限流（错误码直接暴露）

`minute_limit_exceeded` · `hour_limit_exceeded` · `month_limit_exceeded`
另有 `unknown_api_key` · `expired_api_key` · `unknown_method` · `wrong_params` · `not_found`

### 免费档再确认

FREE PLAN **$0 / 1,000 查询/月 / 仅个人用途**，含 Real-Time Flights + Airport Schedules + Flight Delays
+ Airlines/Airports/Cities DB + Suggestion + NearBy + 4 个额外 API。
不含 Fleets DB、Routes DB，不含商用授权。

---

## 10. 飞常准 MCP —— 36 个工具完整参数　<https://cmcp.variflight.com/tools/>

工具文档标注 **"Verified 2026-09-24"**，"名称、参数类型和必填项已核对服务端工具列表"。

### 四类分组

| 类别 | 数量 | 工具 |
|---|---|---|
| 航班动态与分析 | 11 | `getFlightList` `getFlightStatus` **`flightAnalyze`** `getFlightByAircraftNumber` `getFlightByPaintName` **`getAircraftRotation`** `getFlightServiceProfile` `getRouteOperationSummary` `getFlightTrackLine` `flightMarketData` `flightMarketRouteData` |
| 用户行程与关注 | 7 | `queryUserFutureTrip` `queryUserHistoryTrip` `queryUserTripStats` `queryUserTripDetailStats` `queryUserTripDelayStats` `followFlight` `unfollowFlight` |
| 机场与航司 | 8 | `searchAirport` `getAirportStrategy` `getAirportByLatLng` `getAirportInfoByCode` `getAirlineInfoByCode` `getAirportFlightBoard` `getAirportOperationOverview` `getAirportWeatherBriefing` |
| 票价与低价 | 10 | `getFlightTicketPrice` `getRouteFlightTickets` `domesticPriceForecast` `internationalNearbySuggest` `monitorFlightPrice` `flightPriceMonitorList` `domesticDirectTrainSearch` `trainDetail` `intermodalTransferSearch` `getAirportLowPriceRoutes` |

### 核心工具入参（实测抓取）

| 工具 | 必填参数 |
|---|---|
| `getFlightList` | `dep` `arr` `date` |
| `getFlightStatus` | `date`；`fnum` 或 (`dep`+`arr`) 二选一 |
| **`flightAnalyze`** | `fnum` `date` `dep` `arr`（**四要素全必填**） |
| **`getAircraftRotation`** | `fnum` `date` `dep` `arr`（**四要素全必填**） |
| `getFlightTrackLine` | `flightStr`：格式 `航班号_出发_到达_yyyy-MM-dd_类型`，多个用分号分隔 |
| `flightMarketData` | `type`（whole/country/city/airport/airline）`code` `span` `tranmode` |
| `flightMarketRouteData` | `orgCtry` `dstCtry` `span` `tranmode` |
| `queryUserTripStats` | `yearStart` `yearEnd` |
| `queryUserHistoryTrip` | `year` `identityType`（0乘机/1接机/2送机/3机组/99仅关注） |

### ⚠️ 三个实现要点

1. **多机场用英文逗号分隔且不含空格**：`"PEK,PKX"`、`"PVG,SHA"`。
   工具说明里专门强调了"不含空格"。

2. **大量工具要求"航班四要素"**（`fnum`+`date`+`dep`+`arr`）而非只给航班号。
   → 插件必须先做**机场码推断**，否则调用会失败。

3. **语义警告（工具自述）**：
   `getAircraftRotation` 明确写 *"衔接风险不代表本班已经或一定会延误；缺少有效时间数据时风险为 unknown"*；
   `getFlightServiceProfile` 明确写 *"缺失值不能当成无服务"*。
   → **返回的 unknown/null 必须原样透传，不能折叠成"无"或"正常"**。这条对 verifier 的置信度设计很关键。

---

## 11. 其余两个 URL

- **`https://dast.133.cn/mcp/docs`** —— 见 §3，9 工具完整定价 + 入参速查 + 网关地址。
- **`https://openskynetwork.github.io/opensky-api/`** —— 已在 `05-resource-index.md` §2.1
  收录完整契约（OAuth2 client_credentials、三桶 credits、bbox 计价、批次限制）。
  GitHub 源文件 `openskynetwork/opensky-api/docs/free/rest.rst` 是同一份的一手出处。

---

## 12. 实现层三条硬结论

1. **失败是否计费，各家相反，必须逐 provider 配置：**
   - Aviation Edge / VariFlight / 航班管家：**失败不扣费**
   - SkyLink：**认证成功即扣，含 404/422**
   → 配额账本不能有统一的"失败回滚"假设，必须按 provider 声明。

2. **配额可见性各不相同：**
   - OpenSky：`X-Rate-Limit-Remaining` = **真实**剩余额度
   - SkyLink：同名字段 = **防滥用上限，不是配额**，真配额在 Polar 门户
   - Aviation Edge / 航班管家 / VariFlight：**需自行记账**（VariFlight 是余额制，天然可记）

3. **HTTP 状态码语义不统一：**
   - Aviation Edge：缺 key 返回 **200 + success:false**，缺参才 400
   - SkyLink 选错 plan 前缀：**401/403/422**
   - OpenSky 额度耗尽：**429**（且 Aviasales 系的错误在 body 的 `error.code` 里）
   → 客户端必须按 provider 分派错误处理，不能统一按 status code 判。


