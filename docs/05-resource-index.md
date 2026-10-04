# 资源总表 · 开发文档索引

> 核验日 2026-09-29　｜　配套：`03-provider-matrix.md`、`04-goal-feasibility.md`
> ⚠️ 本文档含**一处对前一轮结论的重大更正**，见 §1。

---

## 1. ⚠️ 更正：Aviation Edge 没有免费档

上一轮我把「Developer 30,000 calls/月」当成免费额度，**这是错的**。

官方 `/free-api-key/` 页面原文：

> **"Due to abuse of our Free API keys, we have decided to no longer offer this feature."**

FAQ 亦确认免费试用已禁用。搜索引擎缓存里的 `Developer 30 000 calls per month`
是**最便宜的付费档**（标准月费 $299，首月促销 $7），不是免费额度。

**后果**：我上一轮说「免费额度断层第一，Aviation Edge 30,000/月 是 Aviationstack 的 300 倍」——作废。
Aviation Edge 从"免费主力"降级为"付费主力"。

这直接改变了全免费方案的可行性判断，见 §6。

---

## 2. 国际段资源

### 2.1 确认免费

| 服务 | 免费额度 | 能给什么 | 开发文档 |
|---|---|---|---|
| **OpenSky Network** | 注册 **4,000 credits/日**（匿名 400/日） | **只有位置**，无延误分钟、无计划时间 | [官方文档](https://opensky-network.org/data/api-docs) · [GitHub 源文档](https://github.com/openskynetwork/opensky-api) |
| **Aviationstack** | **100 次/月，1 次/60 秒** | 实时状态 + 机场/航司基础库。**历史/时刻/未来航班全锁付费** | [文档](https://aviationstack.com/documentation) · [FAQ](https://aviationstack.com/faq) |
| **SkyLink API** | 1,000 次/月，**需申请非自助** | ADS-B + 天气 + NOTAM | [文档](https://skylinkapi.com/docs/) · [申请](https://skylinkapi.com/apply/) |
| **FlightAPI.io** | **20 次** | 票价 + 跟踪 + 机场时刻 | [文档](https://www.flightapi.io/documentation/flight-tracking-api/) |
| **AirLabs** | 免费档存疑 | flights/schedules/airports/airlines/routes/fleets | [文档](https://airlabs.co/docs/) |
| **adsb.lol / airplanes.live** | 免费无额度声明 | 社区 ADS-B，只有位置 | [adsb.lol](https://adsb.lol) |
| **MyAirports** | 完全免费 | 机场/国家 CSV 静态数据 | [myairports.com/data](https://myairports.com/data/) |
| **Oanor**（OpenSky 网关） | 10 次/日，无需 key | OpenSky 代理 | [文档](https://www.oanor.com/api/opensky-api/get-v1-meta) |

**OpenSky 认证**（唯一必须实现的复杂认证）：
```
POST https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token
grant_type=client_credentials & client_id=... & client_secret=...
→ Bearer token，30 分钟过期
```
额度分**三个独立桶**：`/states/*`、`/tracks/*`、`/flights/*`。
`/states/all` 按包围盒面积计价 1–4 credits；`/flights/*` 按跨越天数计价 4 → 960×N。
响应头 `X-Rate-Limit-Remaining` 给出剩余量。

**OpenSky 致命限制**：`/flights/aircraft`、`/flights/arrival`、`/flights/departure`
是**夜间批处理，只有 T-1 及更早**。实时判断只能用 `/states/*`。
机场参数用 **ICAO**（`ZBAA`），不是 IATA。

### 2.2 确认付费（按性价比排序）

**AeroDataBox** — <https://aerodatabox.com/pricing>

免费路径不是领配额，而是 **"贡献 ADS-B 数据换永不过期 credits"**：
> "Contribute data to AeroDataBox and convert it into **non-expiring API credits** — then call the API without a paid subscription."

需自备 ADS-B 接收器（RTL-SDR 约 ¥150–300）。

直接订阅：Starter $19/月（40,000 units、5 req/s、180 天时刻+历史、**缓存限 7 天**）
→ Growth $99/月（400,000 units、365 天、扩展缓存）→ Scale $499/月（含 B2B 再授权）

端点按复杂度分 Tier：Tier 1 = 1 unit，Tier 2 = 2 units，Tier 3 = 6 units。

⚠️ **条款硬约束**：任何档位（含免费）**禁止转售 API 或数据**，"转格式/改字段名再发布"
也算原始数据分发。自用旅行规划属 End Use 不受限；做成对外服务则必须买 Scale 档。

**Aviation Edge** — <https://aviation-edge.com/flight-radar-and-tracker-api/>
（契约已完整取证，**若付费则性价比最高**，见 §2.3）

**FlightAware AeroAPI** — <https://www.flightaware.com/commercial/aeroapi/>
Personal 档每月 $5 免费额度（ADS-B feeder $20）；Standard 起 $200/月。

**FlightLabs** — <https://www.goflightlabs.com/>
7 天试用 / 50 次；Starter $249.99/月起。客户含 FedEx、United、dnata。**很贵**。

**OAG Airfare** — <https://www.oag.com/airfare-data>
**10+ 年历史 + 1 年前瞻**，覆盖 1500+ 订票站点。Enterprise 报价。
这是唯一"对得上你原始目标"的产品，代价是价格。

---

## 3. 国内段资源 —— 结论：航司直连这条路是死的

### 3.1 航司官方 API（你的直觉在这里不成立）

逐一核实了国航、东航、南航、海航、厦航、深航、吉祥、春秋、华夏、西藏航空。**结论：有明确证据表明三大航均不可个人获取。**

| 航司 | 开放平台 | 个人可用？ | 证据 |
|---|---|---|---|
| **国航 CA** | 无公开开发者门户 | ❌ | IATA 注册表登记 "Air China New Retailing Platform"，合作伙伴全是美团/去哪儿/同程/飞猪/中航信。采购公告显示其数据接口"单一来源采购"，反证不做市场开放 |
| **东航 MU** | `developer.ceair.com` 真实存在 | ❌ | 接入流程第二步即"注册为卖家 → 完善**公司**资料并等待审核"，个人无法通过 |
| **南航 CZ** | `open.csair.com` 有「航班动态相关信息」产品 | ❌ | 定价"面议"，标注"免费试用：敬请期待"（即尚未提供）；入驻需盖章营业执照 + 近 2 年审计财报 + 近 3 年合同发票 |
| **海航 HU** | 无 | ❌ | 官网仅"大客户合作计划"（企业差旅签约通道），非数据 API |
| **深航 ZH** | 无 | ❌ | 官网"接口"字样全在**采购公告**里（舱单推送接口等），方向是深航作为买方 |
| **吉祥 HO** | `openapi.juneyaoair.com` 域名存在但无文档 | ⚠️ 无法证实 | 需商务渠道 |
| **春秋 9C** | NDC 4 级认证（国内首家），`gds-openapi.springairlines.com` 抓取超时 | ❌ | 仅面向签约伙伴；第三方标"适用于个人&企业"是**转售商口径，非航司直供** |
| **华夏 G5 / 西藏 3U** | 无 | ❌ | 官网内容以招标采购公告为主 |
| **厦航 XM** ⭐ | `developer.xiamenair.com` | ⚠️ **唯一支持个人开发者认证** | 需证件号 + **100 字以上使用场景说明** + 人工审批 + IP 白名单（2-3 工作日）。**但公开文档目录中无实时航班动态 API**，能拿的是 NDC AirShopping 可售报价 |

> ⚠️ **重要排雷**：aviation-edge / airlabs / duffel / FlightLabs 上都有 "Air China API"、
> "China Eastern API" 等页面，**那是第三方聚合商基于自有数据封装的产品，不代表航司存在官方开放 API**。
> 极易误判。

**逆向路线也不可靠**：三大航 App 普遍使用梆梆/爱加密加固 + 自定义 SO 加密 + 动态签名，
GitHub 上无任何成熟持续维护的公开逆向项目（仅 2017 年的教学记录，且作者声明"不想违法"）。

### 3.2 国内聚合平台

| 平台 | 免费额度 | 覆盖 | 说明 |
|---|---|---|---|
| **聚合数据 juhe.cn** | **首次申请送 3 次** | 国内主流 | <https://www.juhe.cn/docs/api/id/818>。返回字段是 `ticketPrice`，官方注释为**"参考票价"，非可成交价**。单价 ¥0.16–0.22/次，查得计费。⚠️ 第三方站称"每天免费调用"**不成立**，官方页面只写"首次申请送 3 次" |
| 极速数据 jisuapi | ⏳ 额度未取证 | ⏳ | <https://m.jisuapi.com/api/flight/> |
| 京东万象 | ⏳ 未取证 | ⏳ | <https://wx.jdcloud.com/api_4_104> |
| **飞常准 VariFlight** | 14 天试用后收费 | 国内权威 | <https://cmcp.variflight.com/>，36 工具。**明确不含票价** |
| 中航信 TravelSky GDS | ❌ | 国内机票数据根上游 | 对独立开发者实质关闭 |
| 携程/去哪儿/飞猪 | ❌ | — | 开放平台是**商家接入**方向，不是开发者取数。想拿数据只能逆向 |
| 蜻蜓旅行（国内 Hopper） | ❌ | — | 有价格预测但**无 API** |

### 3.3 国内价格：方向级证伪

> **"存在可免费返回中国国内机票价格的 API" —— 不存在。**

法律框架明确不利：避开或突破验证措施（密码防护、身份认证、加密、验证码）即落入
《刑法》第 285 条"非法获取计算机信息系统数据"射程；《反不正当竞争法》已增设侵害数据权益规定。
未检索到专门针对"爬取 OTA 机票价格"的生效判例，风险敞口无法量化。

唯一技术路径是 `yangka1212/JiPiao`（Playwright 抓携程/去哪儿/同程 + httpx 逆向飞猪/途牛），
但项目极不成熟且**明确不可商用**。

---

## 4. Aviation Edge 完整契约（若决定付费，这是最完整的一份）

Base：`https://aviation-edge.com/v2/public`　认证：query 参数 `key=[API_KEY]`
官方 README：*"All plans grant access to the Airport Schedules API and other APIs with a
difference of the monthly API call limit."* → **各档只差月调用量，API 覆盖面相同。**

| 端点 | 用途 | 关键限制 |
|---|---|---|
| `/flights` | 实时位置 | 约 5 分钟更新。`limit` 上限 30000，**一次调用只计 1 call** |
| `/timetable` | 机场实时时刻表（延误分钟/登机口/行李/航站楼/共享代码） | **窗口仅 ±6 小时**（合计 12h）。约 15 分钟更新 |
| `/flightsHistory` | 历史时刻表 + 取消 + 延误 | 标准 **1 年**（5 年需邮件申请）。**单次区间 ≤30 天** |
| `/flightsFuture` | 未来时刻表 | **最多 1 年 ahead，但查不了今天到 +7 天这段！** 官方原文："The Future Schedules API does not return between today and 7 days ahead." |
| `/airlineDatabase` `/airportDatabase` `/cityDatabase` `/countryDatabase` `/airplaneDatabase` `/planeTypeDatabase` `/taxDatabase` `/routes` | 静态库 | 全库端点单次调用取回整库，仅计 1 call → **首次集成直接全量拉取落库** |

**三个必须写进架构的坑**：

1. **`/flightsFuture` 的 +7 天空洞** → 必须建"预取 + 本地落库 + 定期刷新"管道，
   否则最近一周的行程查不到。官方 FAQ 给的正解就是提前批量抓。
2. **参数命名风格不一致**：`/timetable` 用 `iataCode`、`airline_iata`（下划线）；
   `/flights` 用 `depIata`、`airlineIata`（驼峰）。用错直接报错。
3. **错误约定不一致**：多数端点缺 key 返回 **HTTP 200 + `{"success":false,"message":"Missing API Key"}`**，
   不是 401；`/flightsHistory` 缺参则返回 HTTP 400。客户端必须同时处理两种。

**计费口径**（官方 FAQ）：1 次成功取数 = 1 call，与返回数据量无关；
**报错（端点用错或数据不存在）不计费**。

**中国覆盖**：CA/MU/CZ/HU 四大航司均有官方专页确认覆盖 Live/Historical/Future 三类时刻表。
但时刻表是**机场基座**，官方未公开中国机场收录清单，部分小型/军用/私人/直升机场可能缺失。

---

## 4.5 Travelpayouts / Aviasales Data API —— 国际段价格：免费可用 ✅

文档：<https://api.travelpayouts.com/documentation>（Slate，一手）
镜像：<https://travelpayouts.github.io/slate/>

### ⚠️ 关键：两层 API 必须分清

之前"Travelpayouts 搜索 API 需 50,000 MAU"的结论，混淆了这两层：

| 层 | 内容 | 门槛 | 能不能免费用 |
|---|---|---|---|
| **Flight Data Access API v1 / v2** | **缓存价、价格日历、月份矩阵、热门航线、静态库** | 注册 travelpayouts.com 联盟拿 token | ✅ **免费** |
| **Flights Search API** | 实时多城市搜索、含代理机构实时报价与跳转链接 | 官方原文："To obtain access... **send a request**"（提交工单申请） | ❌ 大概率卡 MAU |

**我们只需要第一层**，而且它恰好包含做价格基线最需要的两个端点。

### 认证

`X-Access-Token` 请求头，或 `token` 查询参数。
Token 领取：<https://www.travelpayouts.com/programs/100/tools/api>
注册 travelpayouts.com 联盟账号即可（个人自用无需变现）。

### v1 端点（价格类）

| 端点 | 用途 | 对项目的价值 |
|---|---|---|
| `/v1/prices/calendar` | **某航线某月每一天的最低价**（价格日历） | ⭐⭐ 攒基线的核心，1 次调用拿 30 个数据点 |
| `/v1/prices/monthly` | **按月分组的最低价**（月份矩阵） | ⭐⭐ **直接回答"一年后参考价"** |
| `/v1/prices/cheap` | 某航线最便宜票（0/1/2 转机） | 即时比价 |
| `/v1/prices/direct` | 仅直飞最便宜 | 排除中转干扰 |
| `/v1/popular/airlines`、`/v1/popular/cities`、`/v1/popular/routes` | 热门航线与目的地 | 发现选项 |

### v2 端点

`/v2/prices/latest`（最新票价）、`/v2/prices/calendar`（月价格日历）、
`/v2/prices/nearest`（邻近目的地价格）、`/v2/prices/week-by-week`（按周价格日历）、
`/v2/user/ip-location`、`/v2/prices/special-offers`。

### 静态库（免费无限）

`/v1/data/countries`、`/v1/data/cities`、`/v1/data/airports`、`/v1/data/airlines`、
`/v1/data/alliances`、`/v1/data/airplanes`、`/v1/data/routes` —— 全部 JSON 格式。

### 三个必须知道的特性

1. **`currency` 参数支持 USD/EUR 等**，默认 RUB。中国用户务必显式传 USD 或 CNY。
2. **`expires_at` 字段**给出该价格的失效时间——缓存价有时效，不能当承诺价。
3. **预订跳转链接只有 15 分钟有效期**，但**价格数值本身可以长期存储**。
   → 做基线时只存价格与查询时间戳，**不要缓存跳转链接**。

### 端点已被第三方 MCP 封装验证

Pipeworx 的 `travelpayouts` pack 独立实现了 4 个工具，说明这些端点当前确实可用：
`travelpayouts_cheap_prices` / `travelpayouts_price_calendar` /
`travelpayouts_cheapest_by_month` / `travelpayouts_popular_destinations`。
（Pipeworx 自己的 free tier 是 50 calls/day，与 Travelpayouts 本身无关。）

### 未取证的项

- **官方 rate limits 数字**：`support.travelpayouts.com` 全站被 Cloudflare 挡（403/429），
  "200 requests/hour/IP" 这个数字只有搜索摘要，**没有一手页面确认**。
  ⚠️ 实现时必须按"未知上限"设计，做自适应退避而不是硬编码 200。
- **中国国内航线覆盖**：Aviasales 是俄罗斯 OTA，覆盖重心在俄语区和国际航线，
  中国国内航线质量**需实测**。这是本节唯一的实质风险。

### 数据性质

**缓存价 / 参考价，不是可成交实时价。** 这恰好就是"参考价格"这个词要的语义——
用于回答"这条航线大概多少钱""这个月份相对便宜还是贵"，而不是"现在买能成交多少"。

---

## 5. 调研过程的两条经验

1. **JS 渲染的定价页抓不到**。Aviation Edge 与 FlightLabs 的定价页 scrape 只返回 meta description。
   绕行办法：找 API Evangelist 的机器可读转录（`api-evangelist/aviation-edge` 仓库的
   plans/rate-limits YAML），并用 `/free-api-key/`、FAQ 等**非 JS 页面**交叉验证。
   → **教训：判断一家有没有免费档，要直接找它的 free trial 页面，而不是读定价页。**

2. **"某平台有 X API 页面"是个陷阱**。aviation-edge / airlabs / duffel / FlightLabs 都挂着
   "Air China API" 页面，但那是聚合商自有数据封装。**聚合商的航司专页 ≠ 航司官方开放 API。**

---

## 6. 全免费方案的最终判定

| 目标层 | 免费可行性 | 卡在哪 |
|---|---|---|
| L1 实时**位置** | ✅ 可行 | OpenSky 4,000/日，额度充足 |
| L1 实时**延误/取消** | ⚠️ 勉强 | Aviationstack 100/月且无历史；无第二个免费源可交叉验证 |
| L2 **时刻表**（330天） | ❌ **不可行** | 免费源中只有 Aviation Edge 完整覆盖，而它已取消免费档 |
| L3 **价格基线** | ❌ **国际勉强/国内不可能** | Travelpayouts 待查；国内方向已证伪 |

**结论：接受 330 天并不能让免费方案成立。** 卡点不是时间跨度，而是
**免费层里根本没有提供时刻表和价格的数据源**——Aviation Edge 取消免费档是压垮 L2 的那一下。

最小可行的付费入口有两个：

| 方案 | 成本 | 覆盖 |
|---|---|---|
| **AeroDataBox Starter** | $19/月 + RTL-SDR（可选） | 180 天时刻 + 180 天历史 + 全部静态库 |
| **Aviation Edge Developer** | $299/月（首月 $7） | 实时 + 历史 1 年 + 未来 1 年 + 全部静态库，中国四大航司有官方背书 |

若坚持零付费，可行范围收窄为：**OpenSky 查位置 + Aviationstack 每月 100 次查状态**，
放弃时刻表与价格基线，插件退化成一个"国际航班状态查询器"。
