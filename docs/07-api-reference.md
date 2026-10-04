# dsh-flight-aggregator · 外部服务开发参考手册（Tabbit 实测 · 2026-09-29）

> 这是开发时**照着写 provider adapter** 的操作手册。每条都有一手出处（官方文档原文）。
> 证据分级：**A**=官方页原文　**B**=官方文档源文件（GitHub）　**C**=第三方/厂商自撰（打折看）
> 采集方式：Tabbit 真实 Chromium 渲染（实例 `AE717A7E28FDDD79`），search-fusion 静态抓取只拿到
> meta description 的 JS 页一律用 Tabbit 二次确认。

**工具定位（2026-09-29 扩展）**：覆盖**海内外航班 + 国内导航 + 火车**的门到门旅行信息工具。
- 航班（国际）：AirLabs ✅ / Aviationstack ✅ / OpenSky ✅ / Travelpayouts ✅（全免费）
- 航班（国内）：VariFlight MCP / 航班管家 MCP（付费，现成 MCP）
- 火车：12306 MCP（**免费，已连通，已实测**）
- 国内导航：高德路径规划（免费 15 万次/月）+ 高德 MCP（现成）

---

## 0. 一页速查：做什么用哪家

| 我要做的事 | 用谁 | 端点/工具 | 免费？ |
|---|---|---|---|
| **火车余票/经停/中转** | **12306 MCP（已连通）** | `get-tickets` 等 8 工具 | ✅ **已实测** |
| **自驾去机场**（限行/过路费/路况） | **高德** v5 驾车规划 | `/v5/direction/driving` + `plate` | ✅ 个人 15万/月 |
| **多机场驾车距离比选** | **高德** 距离测量 | `/v3/distance` type=1（100起点批量） | ✅ |
| 酒店→机场公共交通 | **高德** v5 公交规划 | `/v5/direction/transit/integrated` | ✅ 个人 30/月 |
| 查航班实时状态（计划/预计/实际时间、延误分钟） | **Aviationstack** | `/flight_status` | ✅ 100/月 |
| …或更全（含取消、登机口、行李、历史延误） | **Aviation Edge** Flight Delay | `/v2/public/flightsHistory` | ❌ $299/月 |
| **用观测校验计划**（计划 ETA 时飞机在哪） | **Aviation Edge** Historical Tracker | `/v2/public/flight_track_history` | ❌ 同上 |
| 查实时位置（高度/速度/航向） | **OpenSky** | `/api/states/all` | ✅ 4000/日(注册) |
| …或带注册号/机型/航司富化 | **SkyLink** ADS-B | v3.1 实时追踪 | ❌ 申请制1000/月 |
| 查时刻表（**窗口仅 ~10h**，非未来班次） | **AirLabs** | `/api/v9/schedules` | ✅ 1000/月 |
| **查"我那班机延误了几分钟"（免费）** | **AirLabs** `/schedules` | `dep_delayed` / `arr_delayed` | ✅ |
| **查"某机场今天哪些航班延误>N分钟"** | **AirLabs** `/delays` | `delay=60&type=departures` | ✅（Free limit=50） |
| 查未来航班时刻 + 每周班次（`weekday`） | **Aviation Edge** Future | `/v2/public/flightsFuture` | ❌ 同上 |
| 查历史时刻（回溯1年，含延误/取消） | **Aviation Edge** Historical | `/v2/public/flightsHistory` | ❌ 同上 |
| 查"每周几班"（未来时刻表带 weekday） | **Aviation Edge** Future | `flightsFuture` 的 `weekday` 字段 | ❌ 同上 |
| **状态变更 Webhook（免轮询）** | **AirLabs** `/listen` · **SkyLink** webhooks | — | ❌ 均需付费 |
| 查机场大屏（进出港全量） | **Aviation Edge** / **VariFlight** | `/timetable` / `getAirportFlightBoard` | ❌ / ✅试用 |
| 查机场/航司基础库（IATA/ICAO/时区/坐标） | **AirLabs** DB（免费）/ MyAirports CSV（免费） | `/api/v9/airports` · 静态CSV | ✅ |
| 查飞机（按尾号/ICAO24 反查） | **Aviation Edge** | `/airplaneDatabase` `RegNum`/`aircraftIcao24` | ❌ 同上 |
| 查实时航班动态（国内，含延误分析） | **VariFlight** 飞常准MCP | `getFlightStatus`·`flightAnalyze`·`getAircraftRotation` | ❌ 试用 |
| 查延误概率（国内） | **VariFlight** 飞常准MCP | `flightAnalyze` | ❌ 试用 |
| 查前序航班传导（国内） | **VariFlight** 飞常准MCP | `getAircraftRotation` | ❌ 试用 |
| 查航线最低价日历（国内） | **VariFlight** 飞常准MCP / **Travelpayouts** | `getFlightTicketPrice` / `/v1/prices/calendar` | ❌ / ✅ |
| 查实时票价+分舱位（国内+国际） | **VariFlight** 飞常准MCP | `getRouteFlightTickets`（DuckDB SQL） | ❌ 试用 |
| 查机票价格趋势（国际，参考价） | **Travelpayouts** Data API | `/v1/prices/monthly`·`calendar` | ✅ 免费 |
| 查机场天气（影响判断） | **VariFlight** / **SkyLink** | `getAirportWeatherBriefing` / `/weather/metar/{iata}` | ❌ / ✅申请 |
| 查"为什么延误"（航行警告） | **Aviation Edge** NOTAM | `/v2/public/notams` | ❌ 同上 |
| 查"每周几班"（未来时刻表带 weekday） | **Aviation Edge** Future | `flightsFuture` 的 `weekday` 字段 | ❌ 同上 |
| **用观测校验计划**（计划 ETA 时飞机在哪） | **Aviation Edge** Historical Tracker | `/v2/public/flight_track_history` | ❌ 同上 |
| 查空铁中转方案 | **VariFlight** 飞常准MCP | `intermodalTransferSearch` | ❌ 试用 |
| **国内机场坐标/地址/周边** | **高德** 地理编码·关键字搜索 | `restapi.amap.com/v3` | ✅ 个人 5,000/月 |
| **家到机场怎么走**（境内） | **高德** 路径规划 | 驾车/步行/公交/骑行 | ✅ 个人 **15 万/月** |
| 国内天气（**合规出口**） | **高德** 天气预报 | `restapi.amap.com/v3/weather` | ✅ 个人 5,000/月 |
| 国内地理能力（Agent 直连） | **高德官方 MCP** | `https://mcp.amap.com/mcp?key=…` | ✅ |
| **零订阅费用白嫖**（需自建 ADS-B 馈电） | **AeroDataBox** Free | 贡献位置 → 换永不过期 credits | ✅ 但需 RTL-SDR |
| 查某航班是否可被合法追踪（FAA LADD） | **AeroDataBox** | LADD API | ❌ |
| 查火车票（顺带） | 12306 社区MCP（已有） | — | ✅ |

---

## 1. 共同约定（所有 REST 源）

- **Base URL**：Aviation Edge `https://aviation-edge.com/v2/public`；
  OpenSky `https://opensky-network.org/api`；AirLabs `https://airlabs.co/api/v9/`；
  Aviationstack `https://aviationstack.com/api`（+ `/v1/…`）。
- **认证**：AirLabs & Aviation Edge & Aviationstack 用 **query 参数 `access_key` / `key`**；
  OpenSky 用 **OAuth2 client_credentials**（唯一例外，见 §4）。
- **格式**：AirLabs 默认 JSON，`?format=json`；Aviation Edge/Aviationstack JSON。
- **时区**：Aviation Edge 返回机场当地时间（`local_*`字段 UTC）；OpenSky state vector 用 UTC。

---

## 2. Aviation Edge（付费主力 · 契约最完整）　【A】

**认证**：`?key=[API_KEY]`　**无请求头、无额外必填全局参数**
**错误**：缺 key 返回 **HTTP 200** + `{"success":false,"message":"Missing API Key"}`（不是401）；
缺必填参数返 **HTTP 400** `{"message":"Missing param: type (str)"}`。两种都要处理。

### ⭐ 全部 18 个端点路径（官方 developers 页一手，2026-09-29 抓取）

Server 统一为 `https://aviation-edge.com/v2/public/`

**动态数据（12）**

| # | 端点 | Schema | 用途 |
|---|---|---|---|
| 1 | `/flights` | `FlightTrackingResponse` | 实时位置与状态 |
| 2 | **`/flight_track_history`** | `FlightTrackHistoryResponse` | **历史飞行轨迹**（逐点经纬/高度/速度） |
| 3 | `/timetable` | `ScheduleResponse` | 机场实时时刻表（±6h） |
| 4 | `/flightsHistory` | `HistoricalSchedulesResponse` | 历史时刻表 **= Flight Delay API** |
| 5 | `/flightsFuture` | `FutureSchedulesResponse` | 未来时刻表（≤1年） |
| 6 | `/routes` | `AirlineRoutesResponse` | 航线 |
| 7 | **`/notams`** | `Notam` | **航行警告**（此前待补，路径已确认） |
| 8 | `/nearby` | `NearbyAirportsResponse` | 按位置查附近机场/城市 |
| 9 | `/autocomplete` | `AutocompleteResponse` | 城市/机场/铁路/汽车站模糊查询 |
| 10 | `/satelliteDetails` | `SatelliteTrackerResponse` | 卫星追踪 |
| 11 | `/planeTypeDatabase` | — | 机型库 |
| 12 | `/airplaneDatabase` | `AirplaneResponse` | 飞机库（注册号/ICAO24 反查） |

**静态数据库（6）**
`/airportDatabase`（`AirportsResponse`）· `/airlineDatabase`（`AirlineResponse`）·
`/cityDatabase`（`CityResponse`）· `/countryDatabase`（`CountryResponse`）·
`/taxDatabase`（`TaxCodesResponse`）· `/planeTypeDatabase`

> ✅ **上轮标记为"待补"的 NOTAM 路径已确认：`GET /v2/public/notams`**，
> 官方描述"provides active and historical NOTAMs for airports worldwide by ICAO or IATA codes,
> optionally filtered by date range"。

### `/flight_track_history` 完整契约（新）　【A 实测样本】

可用三种标识符任一查历史轨迹 —— **飞行号 / 飞机 ICAO24 / 注册号**：

```
/v2/public/flight_track_history?key=KEY&depIata=LHR&flightIata=BA203&depDate=2025-10-21
/v2/public/flight_track_history?key=KEY&depIata=LHR&aircraftIcao24=AC82EC&depDate=2025-10-21
/v2/public/flight_track_history?key=KEY&depIata=LHR&RegNum=N923SW&depDate=2025-10-21
```
也可按到达日定位，或精确到计划时刻：
```
&arrDate=2025-10-21   |   &dep_schTime=2025-10-21T13:40:00   |   &arr_schTime=2025-10-21T20:10:00
```

响应结构：
```json
[{ "aircraft": { "icao24":"406A9C","icaoCode":"B788","regNumber":"G-ZBJE" },
   "airline":  { "iataCode":"BA","icaoCode":"BAW" },
   "arrival":  { "iataNumber":"BOS","icaoNumber":"KBOS","scheduledTime":"2025-10-21T20:10:00.000" },
   "departure":{ "iataNumber":"LHR","icaoNumber":"EGLL","scheduledTime":"2025-10-21T17:35:00.000" },
   "flight":   { "iataNumber":"BA203","icaoNumber":"BAW50G" },
   "flightPositions": [ { "altitude":"0.00","direction":"90.00","horizontal_speed":"1.85",
                          "isGround":1,"latitude":"51.468500","longitude":"-0.482000" } ] }]
```
> **意义**：这是全网唯一给出"计划时间 + 逐点实际位置"对齐结构的端点。
> verifier 可以直接算：**预计落地时刻时飞机在哪** → 延误量级，且不依赖第二个数据源。
> 注意参数是**驼峰**（`depIata`/`flightIata`/`RegNum`），与 `/timetable` 的下划线风格再次不同。

### `/flightsFuture` 完整契约（新）　【A 实测样本】

```
/v2/public/flightsFuture?key=KEY&type=arrival&iataCode=AGP&date=YYYY-MM-DD
/v2/public/flightsFuture?key=KEY&type=departure&iataCode=BER&date=YYYY-MM-DD&flight_num=AF1135
/v2/public/flightsFuture?key=KEY&type=departure&iataCode=AGP&arr_iataCode=ORY&date=YYYY-MM-DD
/v2/public/flightsFuture?key=KEY&type=arrival&iataCode=AGP&dep_iataCode=ORY&date=YYYY-MM-DD
```
响应：
```json
[{ "weekday":"1",
   "departure":{ "iataCode":"agp","icaoCode":"lemg","terminal":"2","gate":"d61","scheduledTime":"06:50" },
   "arrival":  { "iataCode":"ory","icaoCode":"lfpo","terminal":"3","gate":"A","scheduledTime":"09:20" },
   "aircraft": { "modelCode":"a320","modelText":"airbus a320-232" },
   "airline":  { "name":"vueling","iataCode":"vy","icaoCode":"vlg" },
   "flight":   { "number":"8172","iataNumber":"vy8172","icaoNumber":"vlg8172" } }]
```
> **`weekday` 字段是新增价值**：直接回答"这条航线每周几班"。
> ⚠️ 官方明确未来时刻表是**算法按历史外推**，班次变更不会及时反映 → 需自建定期刷新。
> ⚠️ 参数是 `flight_num`（历史端点用 `flight_number`），又一处不一致。

### 各端点关键限制

| 端点 | 限制 |
|---|---|
| `/flights` | 约5分钟更新；`limit`≤30000；**一次调用计1 call**；不含起飞前未升空航班 |
| `/timetable` | **窗口仅当前 ±6h**；约15分钟更新；机场基座非航司基座 |
| `/flightsHistory` | 回溯**1年**（5年需邮件申请）；**单次区间≤30天** |
| `/flightsFuture` | **最多1年ahead，但查不了「今天到+7天」**；算法外推 |
| `/notams` | 按 ICAO 或 IATA 查，可按日期范围过滤；**响应结构已知，参数未取到** |
| `/satelliteDetails` | 可全量或按发射年份/名称过滤 |
| 7 个静态库 | 不带过滤的单次调用即可取回整库，**仅计 1 call** → 首次集成直接全量落库 |

### 参数命名坑（同一 provider 三种风格）

| 风格 | 端点 | 示例 |
|---|---|---|
| 下划线 | `/timetable` `/flightsHistory` | `iataCode` `airline_iata` `flight_iata` `flight_number` `arr_iataCode` |
| 驼峰 | `/flights` `/flight_track_history` | `depIata` `flightIata` `aircraftIcao24` `RegNum` |
| 混合 | `/flightsFuture` | `iataCode` + `flight_num`（历史端点却是 `flight_number`） |

→ **混用直接报错**，必须按端点分别映射。

### 参数命名坑（同一 provider 三种风格，见上表）

- `/timetable` 用 `iataCode`、`airline_iata`（**下划线**）、`flight_iata`、`date`、`arr_iataCode`、`dep_iataCode`
- `/flightsHistory` 用 `code`（非 iataCode）、`type`、`date_from`(仅单日)、`date_to`、`flight_number`、`airline_iata`、`status`
- `/flights` 用 `flightIata`、`airlineIata`、`depIata`（**驼峰**）
- `/flight_track_history` 用 `depIata`、`flightIata`、`aircraftIcao24`、`RegNum`、`depDate`（**驼峰**）
- `/flightsFuture` 混用：`iataCode` + `flight_num`（历史端点是 `flight_number`）
→ **同一 provider 内三种风格，混用直接报错。**

### Flight Delay API 响应（verifier 的数据源）　【A 实测样本】

```json
{
  "type": "arrival", "status": "landed",
  "departure": { "iataCode":"ewr","icaoCode":"kewr","terminal":"c","gate":"74",
                 "delay":44,
                 "scheduledTime":"2024-05-03t17:05:00.000",
                 "estimatedTime":"2024-05-03t17:52:00.000",
                 "actualTime":"2024-05-03t17:48:00.000",
                 "estimatedRunway":"...","actualRunway":"..." },
  "arrival":   { "iataCode":"ber","icaoCode":"eddb","terminal":"1","baggage":"a2","gate":"y17","delay":17, "scheduledTime":…,"actualTime":… },
  "airline": { "name":"air canada","iataCode":"ac","icaoCode":"aca" },
  "flight":  { "number":"3696","iataNumber":"ac3696","icaoNumber":"aca3696" },
  "codeshared": { "airline":{…},"flight":{…} }
}
```
→ **有 `delay`（延误分钟）+ 计划/预计/实际/跑道时刻 + 登机口/行李 + 共享代码**，
这是全网免费/低价源里最完整的"计划 vs 实际"结构，直接喂给 verifier。

### NOTAM API（"为什么延误"）　【A 实测样本】

端点未在页面明示路径（登录墙），但响应结构实测拿到：
```json
[{ "location":"lfpo","number":"a0142/26","class":"international",
   "startdateutc":"2026-01-07t13:26:00","enddateutc":"2026-01-07t23:00:00",
   "condition":"…due to strong weather phenomenons, significant disruptions are observed…" },
 { "location":"lfpo","number":"a0009/26","class":"international",
   "condition":"…rwy 06 u/s due to maintenance: do not use…" }]
```
→ **跑道维护停用、恶劣天气中断**等可直接解析进"延误原因"字段。⚠️ 端点路径待定（见 §9 待补）。

### 定价与计费　【A 一手】
Developer **$299/月**（首月$7，30,000 calls）· Business $599/100k · Gold $1499/500k。
- 首月折扣测试期，**次月按标准价自动续费**
- **失败不计费**（官方：报错的取数不消耗 call limit）
- ⚠️ 无免费档（`/free-api-key/` 明写已停用）
- ⚠️ `&lang=` 翻译参数会**显著拖慢**调用（官方警告）→ 别用
- ⚠️ 机场码在响应里有**大小写不一致历史痕迹**（`"icaoCode":"keyw"`）→ 解析大小写不敏感

---

## 2.5 AeroDataBox —— 三层数据模型（架构必读）　【A 实测原文】

文档入口 <https://aerodatabox.com/doc>（JS 渲染，需 Tabbit）。关联页：`/feed`、`/data-coverage`。

### ⭐ 三层数据模型（决定字段为何会自相矛盾）

每个航班由**最多 3 层**叠加合并而成。**这是本项目最关键的一条认知**：

| 层 | 性质 | 覆盖窗口 | 补充字段 |
|---|---|---|---|
| **Layer 1 · Schedules 静态** | 静态，无状态更新 | 未来 **≤365 天**¹ / 过去 **≤365 天**² | 航班号、航司、计划起降时间、起降地（必有）；机型（常有）；航站楼（偶有） |
| **Layer 2 · Live 动态** | 覆盖 Layer 1 | 几小时～**通常到明天**¹ / 过去 ≤365 天² | 修订计划时间、实际/预计起降、**航班状态**（必有）；修订机型/共享代码（常有）；航站楼/值机柜台/行李转盘/**登机口**/机尾号/**ICAO24**（偶有）；ATC 呼号、跑道时间（罕见） |
| **Layer 3 · ADS-B** | **实验性** | **仅实时，无前瞻** | ATC 呼号、机尾号、ICAO24、修订机型（必有）；跑道时间/跑道号（偶有） |

¹ 取决于你的定价档位　² 因航班/机场/区域而异，取决于数据源质量及**航司发布时刻表的深度**　³ 更多历史需联系厂商

### ⚠️ 不对称覆盖（官方明写，设计插件时必须内建）

> "A flight departing from an airport in the area with all 3 data layers operational and arriving into
> an airport with only the schedule data layer active, will have live status updates for the origin airport
> […], and only scheduled time available for the destination (**consequently, this flight may not go past
> the 'departed' status**)… **sometimes, a flight or part of the flight may have no coverage at all!**"

**这直接推翻了"状态=Unknown 就是没数据"或"状态=landed 就是准点"的朴素假设。**
一个航班可能有：计划时刻 + 实际起飞 + 计划降落，但**永远拿不到实际降落**——
状态会卡在 `departed` 而非 `landed`。

→ **verifier 必须区分「无数据」与「未发生」，不能把卡在 departed 当成异常。**

### ⚠️ Layer 1 的状态语义陷阱

> "As flight schedules do not provide live status updates, **the status for a scheduled flight will stay
> 'Unknown'**, and planned times will stay the same as revised times, until the flight is updated by the
> other data layers"

→ **拿到 `status: Unknown` 不代表航班异常，只代表该机场没有 Layer 2 覆盖。**

### 免费路径：贡献 ADS-B 换永不过期 credits　【A 实测原文 · 2026-09-14 更新】

官方原文：*"This would potentially allow you to use AeroDataBox API **for free**."*

**credits 与 API units 的两个关键区别**：
1. **永不过期**（Once earned, they stay on your account until you use them）
2. **无订阅也能用** —— 没有活跃订阅时，纯 credits 就能按标准费率调 API；
   有订阅时，月度 units 用完后才自动扣 credits

**⚠️ 但有一条硬限制**：
> "receiving API credits in return is **ONLY possible when you create an account on this web-site and
> subscribe to the API directly with us**. This option is **NOT available** for our subscribers through
> 3rd-party marketplaces (RapidAPI or API.Market)."

→ **必须是官网直订用户**，走 RapidAPI / API.Market 的拿不到 credits。

**硬件要求**：树莓派（或任意单板机）+ **1090 MHz SDR USB 加密狗**（RTL-SDR）+ 1090 MHz 天线。
官方明说 *"the hardware is inexpensive, and the software is free and well documented"*。

**软件**：推荐 Ultrafeeder（`ghcr.io/sdr-enthusiasts/docker-adsb-ultrafeeder`）。
关键连接串（**必须用 `beast_reduce_plus_out`**，否则 UUID 不会上报）：

```yaml
services:
  ultrafeeder:
    image: ghcr.io/sdr-enthusiasts/docker-adsb-ultrafeeder
    environment:
      - UUID=1b4e28ba-2fa1-11d2-883f-0016d3cca427   # 生成一次，别改
      - ULTRAFEEDER_CONFIG=
          adsb,feed.aerodatabox.com,30004,beast_reduce_plus_out;
          mlat,feed.aerodatabox.com,31090;           # 可选，参与 MLAT
      - READSB_LAT=40.6399                           # 可选但影响汇率
      - READSB_LON=-73.7787
      - READSB_ALT=5m
```

**领取流程**：首次喂数据后自动注册 → 控制台 My Receivers → Assign receiver → 填 UUID
（**刚启动需等 ≤15 分钟**才可领取）→ 状态页显示 online/offline、上报位置总数。

**换 credits**：My Receivers → Convert to API credits → **最低 500 credits 起兑**，只兑整数，
零头保留累计。汇率按"多少位置 = 1 credit"固定（**未来可能调整**）；
**参与 MLAT 或邻近接收站也参与 MLAT 时汇率更优惠**。

> 💡 **对个人自用**：一台接收站持续喂数据，理论上可支撑完全免费的 API 调用。
> 这是目前唯一"零订阅费用"的路径，但门槛是**需要一块 SDR 硬件 + 部署 Docker**。
> 复用已有 ADS-B 馈电（若已在喂 adsb.lol / airplanes.live）时，UUID 可直接复用。

### 覆盖实况　【B/C】

官方举例：美国时刻表覆盖 100%，实时状态/时间 86%；法国 92% / 79%。
⚠️ 官方反复声明"coverage is extensive but **not worldwide**"，且**未公开中国境内机场覆盖清单**。

### 定价（补充 · 见 §11）

| 档 | 月费 | units/月 | 速率 | 缓存 | 商业衍生再授权 |
|---|---|---|---|---|---|
| **Free（贡献ADS-B）** | $0 | credits | 标准费率 | — | ❌ |
| Starter | $19 | 40,000 | 5 req/s | 标准 7 天 | ❌ |
| Growth | $99 | 400,000 | 10 req/s | 扩展（订阅期内任意时长） | ❌ |
| Scale | $499 | 4,000,000 | 20 req/s | 扩展 + 取消后 1 年 | ✅ |

端点按复杂度分 Tier：**Tier 1 = 1 unit，Tier 2 = 2 units，Tier 3 = 6 units**。
历史可用天数：Pro 180 天 / Growth 与 Scale **365 天**；未来时刻表同。
FIDS（进出港大屏）单次时间跨度上限：12h / 24h / 48h（对应 Starter/Growth/Scale）。

⚠️ **任何档位（含免费）禁止转售 API 或数据**，"转格式/改字段名再发布"也算原始数据分发。
自用旅行规划属 End Use 不受限。

### 其他文档里值得注意的条目

- **Beware of Scam**：官方专页警告有假冒 AeroDataBox 的 API 在收集密钥 → 只认官方入口
- **FAA LADD API & Compliance FAQ**：查询飞机是否在 FAA LADD 计划内（含合规 FAQ），
  对"能否合法追踪特定航班"这个问题有直接参考价值
- **Flight Alert API 正在迁移到 credit 计费制**
- **Flight Time API 已用 ML 增强**，考虑航路绕飞（如战区空域关闭）
- **Flight Plans 附加项**：仅 Starter 档、且仅限 2026-01 起美国境内航班，
  命中时 "Flight status" 请求**按 2 倍 units 计费**

---


- Base：`https://aviationstack.com/api`，认证 `?access_key=[KEY]`
- 免费：**100 请求/月**，**1 请求/60 秒**，单次上限 100 条
- **免费层只有实时状态 + 机场/航司基础库**；历史/时刻/未来航班/航线全锁付费
- 端点：`/flight_status`（航班号查状态）、`/flights`（按航司/机场查实时）、
  `/airports`、`/airlines`、`/countries`、`/cities`、`/schedule`(付费)、`/future_flights`(付费)、`/historical`(付费)
- 状态值：`scheduled`/`active`/`landed`/`cancelled`/`incident`/`diverted`

⚠️ **本档是"免费里唯一能给延误状态+取消"的口子，但只有 100 次/月。**
插件必须把它当**稀缺计划源**，与免费的 OpenSky（位置）配对用。

---

---

## 2.6 高德地图 AMap —— 境内地理底座（不是航班源）　【A 官方定价页 + gettingstarted】

文档：<https://lbs.amap.com/api> · MCP 接入 <https://lbs.amap.com/api/mcp-server/gettingstarted>
定价 <https://lbs.amap.com/pages/base_service_price> · 流量限制 <https://lbs.amap.com/api/webservice/guide/tools/flowlevel>

### 定位澄清（重要）

**高德没有航班 API。** 不提供航班动态、时刻表、延误或价格。
在本项目里它**不是数据源，而是境内地理/出行底座**——补的是"怎么去机场""机场在哪"这一层，
与 VariFlight（国内航班动态）互补而非重叠。

### ⭐ 官方 MCP Server（可直接挂 DSH）

**端点：`https://mcp.amap.com/mcp?key=<你的高德Key>`**（Streamable HTTP，官方推荐）

官方原文：*"支持任意 MCP 协议的客户端（如：Cursor、Claude、Cline）… 目前支持 Streamable HTTP
和 Node.js I/O 两种接入方式（推荐用户使用 Streamable HTTP）。"*

```json
{ "mcpServers": { "amap-maps-streamableHTTP": {
    "url": "https://mcp.amap.com/mcp?key=您在高德官网上申请的key" } } }
```
另有 SSE 形态 `https://mcp.amap.com/sse?key=…` 与 Node.js I/O（stdio）形态。
⚠️ `lbs.amap.com/mcp-server` 路径**不存在**（404），正确路径是 `/api/mcp-server/gettingstarted`。

> 💡 与 VariFlight 一样是**现成 MCP** → 国内段两个源都不需要自己写 provider adapter。

### Base URL 与认证

- Web 服务：`https://restapi.amap.com/v3/…`（v4/v5 用于猎鹰与部分新接口）
- 认证：`key=<KEY>` **查询参数**（不是 header）
- 返回：JSON / XML

### ⭐ 搜索 API（POI · 充电站搜索的基础）　【A 一手 · 2026-07-15 更新版文档】

文档 <https://lbs.amap.com/api/webservice/guide/api/search>

| 端点 | 用途 | 关键参数 |
|---|---|---|
| `/v3/place/text` | 关键字搜索 | `keywords` 或 `types` 二选一必填；`city`+`citylimit`；`offset`≤25/页 |
| **`/v3/place/around`** | **周边搜索（沿线找充电站用这个）** | `location*` `radius`(0–50000m，默认5000) `types` `sortrule=distance` |
| `/v3/place/polygon` | 多边形搜索（路线走廊搜索可用） | `polygon` 坐标对串（矩形可传左上右下两顶点） |
| `/v3/place/detail` | POI 详情 | `id` |

**⭐ 充电站类型码 `types=011100`** —— 官方周边搜索文档的服务示例**原文就是**：
`https://restapi.amap.com/v3/place/around?key=KEY&location=116.473168,39.993015&radius=10000&types=011100`
（01=汽车服务大类；010100=加油站中类。011100 即汽车充电站。）
POI 分类码表下载：<https://lbs.amap.com/api/webservice/download>

**翻页上限**：官方明写 *"同请求参数翻页查询最多支持获取 **200 条**数据"*，每页 `offset` ≤25。

**返回字段**：`name` `type` `typecode` `address` `location` `tel` `distance`（周边搜索返回）等。
**⚠️ 字段表里没有**：充电桩数量、功率、电价、实时空闲状态——开放平台只给**静态 POI 层**。
高德 App 里的实时充电状态来自合作数据接入，未在 Web 服务 API 开放。

### 官方月配额与 QPS（个人认证 / 企业认证）　【A 定价页一手 · ⚠️ 合并单元格更正版】

> ⚠️ 更正：官方定价页是合并单元格表格，文本化后同组服务只渲染一次配额数字、
> 后续行只剩 QPS。**同组服务共享该组月配额**（以控制台"流量分析-配额管理"为准）。

| 服务组 | 个人认证 月配额 | 个人 QPS | 企业认证 月配额 | 企业 QPS |
|---|---|---|---|---|
| **基础 LBS 服务组**（驾车/骑行/步行/公交路径规划、距离测量、地理/逆地理编码、坐标转换、行政区划、IP 定位、静态地图） | **150,000**（组内共享） | 3 | 3,000,000 | 30 |
| **基础搜索服务组**（关键字/周边/多边形/ID 查询/输入提示） | **5,000**（组内共享） | 3 | 500,000 | 100 |
| **天气预报** | **5,000** | 3 | 9,000,000 | 100 |
| JS 地图初始化 | 1,500,000 | 10 | 30,000,000 | 100 |
| 智能硬件定位 | **0** | 0 | 5,000 | 3 |

⚠️ **未认证开发者全部为 0** —— 必须先完成个人认证（支付宝）。
超额阶梯价：0–30 万 30 元/万次 → 30–100 万 24 元 → >100 万 18 元；
月配额超限后依次扣流量包 → 账户余额，每月 1 号结算。

### 对本项目的三个用途

| 用途 | 接口 | 说明 |
|---|---|---|
| **机场 → 坐标/地址** | 地理编码 v3 / 关键字搜索 v5 | 解决"PEK/ZBAA 对应哪个机场、离市区多远" |
| **家 → 机场怎么走** | 驾车/步行/公交/骑行路径规划 | 旅行场景刚需，个人额度 **15 万/月严重过剩** |
| **国内天气** | 天气预报 | ⚠️ 只覆盖中国境内，国际段仍需 Open-Meteo |

> **与 Open-Meteo 的分工**：本地 `plans/quality-rnd/reward-travel-methodology-v21-assessment.md:60`
> 已标注 Open-Meteo **非商业免费、商用需订阅**的条款风险，并写明
> "**中国境内段可叠加高德天气（额度内）**" —— **高德正是那个合规出口**。

### ⚠️ 坐标系冲突（实现必读）

| 源 | 坐标系 |
|---|---|
| **高德** | **GCJ-02**（中国大陆标准，含加密偏移） |
| **OpenSky** | **WGS-84** |
| **Aviation Edge / AirLabs / Aviationstack** | **WGS-84** |

→ **境内机场位置对齐时，高德坐标与 ADS-B 位置直接相距数百米。**
verifier 判断"飞机是否已到机场附近"之前**必须做坐标转换**，否则低空段会产生假阳性。

### ⭐ 路径规划 API（v5 推荐 · 2026-02/06 更新版文档）　【A 一手】

**v5 是新版**（v3 仍可用但策略编号不同）。5 种出行方式 + 距离测量：

| 端点 | 用途 | 关键参数 |
|---|---|---|
| `/v5/direction/driving` | **驾车（自驾去机场的主接口）** | `origin*` `destination*` `strategy`(默认32高德推荐，33躲避拥堵/34高速优先/35不走高速/36少收费/43躲避拥堵+少收费+不走高速) `waypoints`(≤16途经点) `plate`(车牌，**自动判断限行**) `cartype`(0油/1纯电/2插混) `avoidpolygons`(避让区≤32个,单个≤81km²) `show_fields`(cost/navi/tmcs/cities/polyline) |
| `/v5/direction/walking` | 步行（≤100km） | `alternative_route`(1-3条备选) `isindoor`(室内算路) |
| `/v5/direction/bicycling` | 骑行（≤500km） | `alternative_route` |
| `/v5/direction/electrobike` | 电动车（考虑限行） | 同骑行 |
| `/v5/direction/transit/integrated` | **公交（含火车/地铁/跨城）** | `city1*` `city2*`(citycode，不同=跨城) `strategy`(0推荐/1最经济/2最少换乘/3最少步行/5不乘地铁/8时间短) `AlternativeRoute`(1-10) `date`+`time`(按出发时刻筛班次) `nightflag` |
| `/v3/distance` | **距离测量（批量）** | `origins` **支持100个起点批量** `type`(0直线/1驾车含路况/3步行≤5km) |

**驾车响应**（`show_fields` 控制）：
```
route.paths[].distance(米) · restriction(0限行已规避/1有限行)
cost: duration(秒) · tolls(过路费元) · toll_distance · traffic_lights(红绿灯数)
tmcs: tmc_status(畅通/缓行/拥堵/严重拥堵) + tmc_polyline 路况分段
navi: action / assistant_action 转向指令
route.taxi_cost 打车费预估（元）
```

**公交响应**含 `railway` 火车段（车次/上下车站/时刻/仓位价格，仓位码 2011=G高铁 2012=D动车 2013=C城际 21=商务座 16=硬卧下铺…）→ **高德公交规划自己就能返回火车换乘段**，与 12306 MCP 互补但粒度更粗。

**对旅行规划的意义**：
- **家→机场自驾**：v5 driving + `plate`（自动规避限行）+ `show_fields=cost,tmcs` → 出发时间、过路费、实时路况、限行判断一次拿全
- **多机场比选**：`/v3/distance` type=1 一次算家到周边 100 个机场的驾车距离
- **酒店→机场公共交通**：v5 transit 带 date/time 能按实际出发时刻筛可用班次
- **配额**：驾车规划个人认证 **150,000 次/月**，本场景用不完

---


## 4. OpenSky Network（免费观测主力 · 只给位置）　【B 官方源文件】

认证唯一特殊，**OAuth2 client_credentials**：
```
POST https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token
grant_type=client_credentials & client_id=… & client_secret=…
→ Bearer token，30 分钟过期
```

### 三桶额度（互不消耗）
| 层级 | `/states/*` | `/tracks/*` | `/flights/*` |
|---|---|---|---|
| 匿名(按IP) 400/日 | 400 | 400 | 400 |
| **注册(免费) 4000/日** | 4000 | 4000 | 4000 |
| feeder(≥30%在线) 8000 | 8000 | 8000 | 8000 |
| Licensed 14400/**时** | 14400 | 14400 | 14400 |

### 成本模型
- `/states/all` 按包围盒面积：≤25sq° 或 serial-only = **1**；25-100=2；100-400=3；>400/global=4
- `/flights/*`&`/tracks/*` 按天数分区：实时/<24h=4；1-2天=30；3-10=60×N；…；>25=960×N
- `X-Rate-Limit-Remaining` 头=**真实**剩余（唯一可信的配额来源）；耗尽→429+`X-Rate-Limit-Retry-After-Seconds`

### 致命限制
- **机场用 ICAO**（`ZBAA`/`EDDF`），不是 IATA
- `/flights/aircraft|arrival|departure` = **夜间批处理，只有 T-1 及更早** → 实时判断只能用 `/states/*`
- **ADS-B 只给位置**（icao24/lat/lon/alt/velo/heading/on_ground），不含航司/机型/目的地——
  那些必须靠 registry join + 计划源
- ⚠️ 中国境内空域覆盖**未验证**（见 §9，最高优先级）

---

## 5. AirLabs（免费主力 · 唯一免费给延误分钟的源）　【A】

Base：`https://airlabs.co/api/v9/`，认证 `?api_key=[KEY]`（v9 **不要** api_host）

### ⭐ 修正：Schedules API 只有 10 小时窗口，不是"时刻表"

> 官方原文：*"At the moment, the Schedules API returns results **up to 10 hours ahead at most**."*

→ 我上一轮说 AirLabs 补上了 L2 时刻表缺口，**这个判断需要收回**。
10 小时窗口 ≈ Aviation Edge `/timetable` 的 ±6h，本质同源，**都不是未来时刻表**。
免费层仍无"未来班次"能力（那需要 Aviation Edge `/flightsFuture`）。

### `/schedules` 完整契约　【A 实测】

```
https://airlabs.co/api/v9/schedules?dep_iata=MIA&api_key=YOUR-API-KEY
```

请求参数：

| 参数 | 必填 | 说明 |
|---|---|---|
| `api_key` | ✅ | |
| `dep_iata` / `dep_icao` | 条件 | 出发机场 IATA / ICAO |
| `arr_iata` / `arr_icao` | 条件 | 到达机场 IATA / ICAO |
| `airline_iata` / `airline_icao` | 条件 | 按航司查（可多值） |
| `flight_iata` / `flight_icao` | 条件 | 按航班号查 |
| `_fields` | | 逗号分隔字段裁剪，**省额度用** |
| `limit` | | 按机场查 max 1000；按航司 200；**Free key 仅 50** |
| `offset` | | 分页，至 `has_more` 为止 |

响应（实测样本）：
```json
[{ "airline_iata":"BA","airline_icao":"BAW","flight_iata":"BA6984","flight_icao":"BAW6984",
   "cs_airline_iata":"AA","cs_flight_iata":"AA2421","cs_flight_number":"2421",
   "dep_iata":"MIA","dep_icao":"KMIA","dep_terminal":"C","dep_gate":"E4",
   "dep_time":"2021-07-14 19:53","dep_time_ts":1626306780,"dep_time_utc":"2021-07-14 23:53",
   "dep_estimated":"2021-07-14 22:10","dep_estimated_ts":1626315000,
   "dep_actual":"2021-07-14 22:10","dep_actual_ts":1626315000,
   "arr_iata":"SFO","arr_terminal":"1","arr_gate":"B24","arr_baggage":"1",
   "arr_time":"...","arr_estimated":"...","arr_actual":"...",
   "status":"scheduled","duration":359,
   "delayed":137,"dep_delayed":137,"arr_delayed":137 }]
```

**时间字段三件套**（每个时刻都有）：`X_time`（机场当地）· `X_time_ts`（UNIX）· `X_time_utc`（UTC）
**延误字段**：`dep_delayed`（出发延误分钟）· `arr_delayed`（到达延误分钟）· `delayed`（已废弃）
**状态枚举**：`scheduled` / `cancelled` / `active` / `landed`

> ⭐ **这是免费层里唯一同时给出「计划/预计/实际三组时间 + 出发延误分钟 + 到达延误分钟」的源。**
> 结构与 Aviation Edge Flight Delay 同构，可直接喂给 verifier 做交叉复核。
> **Free plan 明确包含这些字段**（官方在字段表里标注 "Available in the Free plan"）。

### `/delays` —— 按延误阈值筛机场全体　【A 实测】★

```
https://airlabs.co/api/v9/delays?delay=60&type=departures&api_key=YOUR-API-KEY
```

| 参数 | 必填 | 说明 |
|---|---|---|
| `delay` | ✅ | **最小延误分钟数（>30 min）** |
| `type` | ✅ | `departures` 或 `arrivals` |
| `dep_iata`/`arr_iata`/`airline_iata`/`flight_iata` 等 | | 同 schedules 的过滤组 |
| `limit` | | 默认 500，**Free key 仅 50** |
| `_fields` | | 字段裁剪 |

> ⭐ **用途完全不同**：这不是"查某班机"，而是"**查哪些航班延误超过 N 分钟**"。
> 官方定位：*"monitor all delays in the world, at all airports simultaneously… designed primarily for
> services such as airport transfers or insurance and flight delay compensation services."*
> → **对"我这个机场今天大面积延误吗"这类问题是直接答案。**
> → 插件可据此做机场级预警，而非只盯单个航班。

### `/alert` Webhook 订阅　【A 实测】⚠️ 付费限定

> 官方原文：*"**Early access to the beta is only available for paid plans.**"*

| 动作 | 端点 |
|---|---|
| 订阅 | `/api/v9/listen?...&webhook_url=<你的服务器>` |
| 取消 | `/api/v9/unlisten?...` |

可监听的变更字段：`dep_terminal` `dep_gate` `dep_estimated` `arr_terminal` `arr_gate`
`arr_baggage` `arr_estimated` `status` `duration` `dep_delayed` `arr_delayed` …

> **架构意义**：有 webhook 就不用轮询。
> ⚠️ 但 **Beta 仅付费** → 免费层只能轮询，插件的 quota planner 必须按"轮询成本"设计。

### 端点真实 slug（Tabbit 抓导航实测，勿猜）

```
/docs/ → /docs/airports  /docs/cities    /docs/airlines  /docs/fleets
       → /docs/routes    /docs/countries /docs/taxes     /docs/timezones
       → /docs/flights   /docs/schedules /docs/flight   /docs/alert
       → /docs/nearby    /docs/suggest  /docs/delays
```
> ⚠️ 是 `/docs/flight`（非 `/flight-info`）、`/docs/alert`（非 `/flight-alert`）、
> `/docs/delays`（非 `/flight-delays`）——猜 slug 会 404。

### 签名认证（不暴露 key 给前端）

```
signature = api_id : timestamp : md5(timestamp + ":" + api_key)
示例：?signature=144:1790677807:5eb29bccdac6a5062eac5d2672ce8e7c
```
- `api_id` 取自任意响应的 `request.key.id`
- timestamp 为当前 unix 秒，**签名有效期 3 分钟**

### 三层限流（错误码直接暴露）

`minute_limit_exceeded` · `hour_limit_exceeded` · `month_limit_exceeded`
另有 `unknown_api_key` · `expired_api_key` · `unknown_method` · `wrong_params` · `not_found`

### 免费档

$0 / **1,000 查询/月** / **仅个人用途**
含 Real-Time Flights · **Airport Schedules** · **Flight Delays** · Airlines/Airports/Cities DB
+ Suggestion + NearBy + 4 个额外 API
**不含** Fleets DB、Routes DB、**Alert API(beta)**、商用授权

付费：Developer $49/月(25k, 0.2¢) · Business $99/月(100k, 0.1¢)

---

## 6. VariFlight 飞常准 MCP（国内段主力 · 36工具）　【A 实测】

接入（个人微信/手机号登录拿 key）：
- 飞常准：`https://c-gw.variflight.com/chat_message/mcp/api`，Bearer，**36工具**，微信/手机号登录，试用
- 飞友：`https://ai.variflight.com/servers/aviation/mcp`，`X-API-Key`，**9工具**，¥50赠金，充值赠4x

### 36 工具入参速查（Tabbit 实测全量，Verified 2026-09-24）

**航班动态与分析（11）**——几乎全部要求"航班四要素"：
| 工具 | 入参 |
|---|---|
| `getFlightList` | dep*, arr*, date* |
| `getFlightStatus` | date*; fnum 或(dep+arr) |
| **`flightAnalyze`** | fnum*, date*, dep*, arr*（延误/取消风险/预计起飞区间） |
| `getFlightByAircraftNumber` | aircraftNumber*（B-1234）; date? |
| `getFlightByPaintName` | flightDesc*（彩绘机关键词）; date? |
| **`getAircraftRotation`** | fnum*, date*, dep*, arr*（实际执飞机+前序航班链+衔接间隔） |
| `getFlightServiceProfile` | fnum*, date*, dep*, arr* |
| `getRouteOperationSummary` | dep*, arr*; date? |
| `getFlightTrackLine` | flightStr*（`航班_出_到_日期_0`） |
| `flightMarketData` | type*(whole/country/city/airport/airline), code?, span?, tranmode? |
| `flightMarketRouteData` | orgCtry*, dstCtry*, span?, tranmode? |

**用户行程与关注（7）**：`queryUserFutureTrip`(identityType?)·`queryUserHistoryTrip`(year?,identityType?)·
`queryUserTripStats`(yearStart?,yearEnd?)·`queryUserTripDetailStats`(statType*=area/airline/aircraft, year?, tripType?)·
`queryUserTripDelayStats`(statType*=airline/airport/flight, year?)·`followFlight`(四要素+orderstyle* 0/1/2/99)·`unfollowFlight`(四要素)

**机场与航司（8）**：`searchAirport`(name*, region? CN/INT)·`getAirportStrategy`(country* ISO2, 入境卡)·
`getAirportByLatLng`(lat*,lng*)·`getAirportInfoByCode`(code* 机场IATA)·`getAirlineInfoByCode`(code* 航司2字)·
`getAirportFlightBoard`(local* 机场/城市, out? 0出/1进)·`getAirportOperationOverview`(local*, out? 0/1/2)·
`getAirportWeatherBriefing`(airportCode*, date?)（实况+METAR/TAF+特殊天气+台风→保守影响判断）

**票价与低价（10）**：
| 工具 | 入参 |
|---|---|
| `getFlightTicketPrice` | dep*, arr*, type*(1单/2往), depDateBegin?, depDateEnd?, arrDate? |
| **`getRouteFlightTickets`** | sql*（只读DuckDB SQL，`flights(market:=,legs:=[…],cabin:=)`表函数；返回 option_id/adult_total 含税） |
| `domesticPriceForecast` | dep*, arr*, date*, flightNo?（价格预测） |
| `internationalNearbySuggest` | depCityCode*, arrCityCode*, depDate*, returnDate? |
| `monitorFlightPrice` | depCity*, arrCity*, date*, flightNo*, thresholdPrice*（降价提醒，仅未来） |
| `flightPriceMonitorList` | 无参 |
| `domesticDirectTrainSearch` | depDate*, depCityName*, arrCityName*, depStationNames?, arrStationNames? |
| `trainDetail` | trainNumber*, depDate*, depStationCode*, arrStationCode*, transferContext? |
| `intermodalTransferSearch` | depCityCode*, arrCityCode*, earliestDepTime*, latestArrTime*, latestDepTime?, transferType?, sort?, limit? |
| `getAirportLowPriceRoutes` | dep*, depDateBegin*, depDateEnd* |

### 实现铁律
1. **多机场逗号分隔、不含空格**：`"PEK,PKX"`
2. **大量工具要"四要素"**（fnum+date+dep+arr），不是只给航班号 → 插件先做机场码推断
3. **`unknown`/`null` 必须原样透传**：
   - `getAircraftRotation`：*"衔接风险不代表本班已经或一定会延误；缺少有效时间数据时风险为 unknown"*
   - `getFlightServiceProfile`：*"缺失值不能当成无服务"*
   - `getAirportWeatherBriefing`：*"天气风险不等于具体航班已延误；缺失数据不代表天气正常"*
   → verifier 不能把 unknown 折叠成"无延误/正常"

---

## 7. 航班管家 DAST MCP（国内段备选 · 有延误概率）　【A 实测】

网关 `https://fly.huoli.com/mcp/dast_mcp`，Bearer API Key，stdio 包 `@flightmaster/aviation-dast-mcp`。

| 能力 | 工具 | 单价 |
|---|---|---|
| 航班动态-航班号 | `dast_flight_dynamic` | ¥0.50 |
| 航班动态-机场对 | `dast_flight_route` | ¥0.50 |
| 航班舒适度 | `dast_flight_happy` | ¥0.20 |
| **未来延误概率** | `dast_delay_rate` | ¥0.50 |
| 机场未来天气 | `dast_future_weather` | ¥0.10 |
| 飞行轨迹 | `dast_flight_path` | ¥0.10 |
| 全国民航每日总览 | `dast_flight_overview_daily` | ¥6.00 |
| 机场运行统计 | `dast_airport_operation_statistics` | ¥6.00 |
| 航司运行统计 | `dast_airline_operation_statistics` | ¥12.00 |

计费：预付费余额，**失败不扣费**。报销类 3 个工具对个人自用价值低（¥6-12，是航班动态的 12-24 倍）。

**与飞常准对比**：航班管家有 `dast_delay_rate`（延误概率）但无前序航班传导；
飞常准有 `getAircraftRotation`（前序传导）+ `flightAnalyze` 但无独立延误概率端点。**两者互补。**

---

## 8. Travelpayouts / Aviasales Data API（国际价格基线 · 免费）　【A 一手】

Base `https://api.travelpayouts.com`，`X-Access-Token` 或 `?token=`。
**两层 API 必须分清**——之前"需 5 万 MAU"的结论混淆了它们：

**✅ 免费层（注册联盟即得 token）——我们只要这层：**

| 端点 | 用途 |
|---|---|
| `/v1/prices/calendar` | 某航线**某月每一天**最低价（1 call=30 数据点）⭐ |
| `/v1/prices/monthly` | **按月分组**最低价 ⭐⭐ 直接答"一年后参考价" |
| `/v1/prices/cheap` · `/v1/prices/direct` | 最便宜 / 仅直飞最便宜 |
| `/v1/data/{countries,cities,airports,airlines,alliances,airplanes,routes}` | 静态库 |

特性：`currency` 支持 USD/EUR（默认 RUB）；响应含 `expires_at`（缓存价时效）；
**预订跳转链接仅 15 分钟有效**，但**价格数值可长期存储**（做基线只存价格+时间戳）。
数据性质：**缓存价/参考价，非可成交实时价**。

**❌ 付费/申请层**：Flights Search API（实时多城市）需提交工单。
**⚠️ 未取证**：官方 rate limits（`support.travelpayouts.com` 被 Cloudflare 挡，只有"200 req/hr"搜索摘要）→ **按未知上限设计自适应退避**。

---

## 8.5 12306 MCP（火车段 · 已在 DSH 连通 · 本项目唯一已实测源）　【A 实测】

> ✅ **2026-09-29 真机实测通过**。本 DSH profile 已挂 `train12306` MCP server，
> 无需注册、无需 key、社区开源自部署（本地文档记录：Joooook/12306-mcp 等，MIT，仅查询不购票）。

**实测记录**：
- `get-current-date` → `2026-09-29` ✅
- `get-tickets` 北京南→上海虹桥 2026-09-30 G 字头上午 → 返回真实余票与票价：
  G1 二等座余 2 张 661 元、G531 二等座余 8 张 626 元、G547 商务座余 19 张 2315 元 ✅

### 工具面（8 个）

| 工具 | 用途 | 关键参数 |
|---|---|---|
| `get-current-date` | 当前日期（上海时区，解析"明天/下周三"用） | — |
| `get-station-code-by-names` | 站名→`station_code` | `stationNames`（多站用 `\|` 分隔） |
| `get-station-code-of-citys` | 城市名→代表站 code | `citys` |
| `get-stations-code-in-city` | 城市**全部**车站及 code | `city` |
| `get-station-by-telecode` | telecode→车站详情 | `stationTelecode`（3位字母，如 VNP=北京南） |
| **`get-tickets`** | 余票查询 | `date*`(yyyy-MM-dd) `fromStation*` `toStation*`(中文名或code) `trainFilterFlags`(GDZTKOFS) `earliestStartTime`/`latestStartTime`(0-24) `sortFlag`(startTime/arriveTime/duration) `limitedNum` |
| `get-interline-tickets` | **中转**余票（尚只支持前10条） | 同上 + `middleStation` `showWZ` |
| `get-train-route-stations` | 某车次经停站/到发时刻/停留 | `trainCode*` `departDate*` |

### 约束与角色

- **只查询不购票**（本地方法论文档明确纪律）
- **无官方 API，存在 IP 风控**（社区方案带会话池/UA 轮换对策）→ 插件侧应做**本地缓存与低频查询**，别当高频源用
- telecode 与 IATA 无关：北京南=VNP、上海虹桥=AOH，**独立命名空间**，与航班的三字码体系不互通
- **与 VariFlight 的火车工具重叠**：cmcp.variflight 有 `domesticDirectTrainSearch`/`trainDetail`，
  但 12306 MCP 是免费且已连通的 → **火车查询以 12306 MCP 为主**，VariFlight 的火车工具只在空铁联程场景用

---


## 9. 待补 / 需用户提供

| 事项 | 类型 | 障碍 |
|---|---|---|
| **OpenSky 对 ZBAA/ZSPD/ZGGG 覆盖** | **真机实测（最高优先）** | 需 OAuth client_id/secret |
| **AeroDataBox 中国境内覆盖** | 实测 | 官方未公开中国机场覆盖清单 |
| AeroDataBox 完整端点路径与参数字段 | 文档 | `/doc` 下的 OpenAPI spec 页（需逐端点展开） |
| **Aviation Edge `/notams` 的具体参数名** | 文档 | 路径已确认，参数表未公开（响应结构已知） |
| SkyLink 1,000/月 申请 | 实操 | `skylinkapi.com/apply` 需人工审 |
| cmcp.variflight.com 36 工具定价 | 商务 | 登录墙 |
| Aviationstack Playground 完整参数表 | 文档 | 内容在登录后 Playground，已用开源 MCP 反推补齐 |
| AirLabs 各端点逐字段 | 文档 | 单端点页 innerText 取不到，需 tabbit.observe 逐页 |
| **AeroDataBox position→credit 汇率** | 实测 | 官方只说"固定汇率，可能调整"，未公布具体数字 |
| 各源**实测调用**（拿真实 key 打真接口） | 实测 | 需各平台注册 key |

> ✅ 已解决：Aviation Edge NOTAM 路径 → `GET /v2/public/notams`；全部 18 个端点路径；
> `/flight_track_history`、`/flightsFuture` 完整契约；AeroDataBox 三层数据模型与 ADS-B 换 credits 全流程



---

## 10. 实现层三条硬结论（写进架构）

1. **失败计费各家相反**：
   - Aviation Edge / VariFlight / 航班管家：**失败不扣费**
   - **SkyLink：认证成功即扣，含 404/422**
   → 配额账本**不能有统一"失败回滚"假设**，必须按 provider 声明。

2. **配额可见性三档**：
   - OpenSky `X-Rate-Limit-Remaining` = **真实**剩余
   - SkyLink 同名字段 = **防滥用上限，不是配额**（真配额在 Polar 门户）
   - Aviation Edge / 航班管家 / VariFlight = **需自行记账**（VariFlight 余额制天然可记）
   → `flight_quota` 工具需按 provider 分别渲染。

3. **HTTP 错误语义不统一**：
   - Aviation Edge：缺key=**200**+success:false；缺参=400
   - SkyLink 选错 plan 前缀=401/403/422
   - OpenSky 耗尽=429
   - AirLabs 错误在 body 的 `error.code`
   → 客户端按 provider 分派错误处理，不能统一按 status code 判。

4. **unknown 透传**：VariFlight 系工具明确要求"缺失≠无"。verifier 的置信度
   必须区分「确认为无延误」「数据缺失/未知」，不能把 unknown 算作正常。

5. **⭐ 覆盖率必须内建到数据模型（来自 AeroDataBox 三层模型）**：
   一个航班字段的"缺失"可能不是**没这班航班**，而是**那个机场没有对应数据层**。
   具体到 AeroDataBox：出发机场有实时层、到达机场只有时刻表层 →
   能拿到实际起飞时间，但**永远拿不到实际降落时间**，状态会永久卡在 `departed`。
   → **provider 适配层不能只返回"有没有值"，必须返回"这个机场有几层覆盖"。**
   → verifier 判定"未落地"之前，必须先确认目的地方确实有实时层，否则会误报延误。

6. **⭐ 坐标系必须统一（来自高德引入的新坑）**：
   高德用 **GCJ-02**，OpenSky 与 Aviation Edge / AirLabs / Aviationstack 用 **WGS-84**，
   两者在境内**相差数百米**。verifier 做"飞机是否已抵近机场"判断时，
   若直接比较高德机场坐标与 ADS-B 位置，**低空段必然产生假阳性**。
   → provider 归一化层应统一输出 **WGS-84**，高德坐标在适配层内转换，不外泄。

7. **Web 服务 vs MCP 的分层**：
   高德与 VariFlight 都已提供**官方 MCP**，直接配进 DSH 即可，
   **不要为它们再写 provider adapter**。真正需要自建 adapter 的是
   Aviationstack / AirLabs / OpenSky / Travelpayouts 这类 REST 源——
   它们的共同点是**认证方式、限流窗口、字段命名各不相同**。
