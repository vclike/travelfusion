---
name: trip-planner
description: >
  门到门出行规划（travelfusion MCP，15 工具 8 数据源）：机票比价（含 L3 历史基线）、
  航班状态、双源核验、境内/境外地面交通、天气窗口、配额审计。当用户问「出行/机票/
  机票价格/航班状态/航班动态/路线/自驾/打车/差旅/团建/奖励旅游/自由行/规划」时使用。
  场景分型：personal（个人，默认）/ incentive（奖励旅游：廉航与红眼标注并压后）。
  产出必须按本技能的展示规范渲染（表格/状态卡/结论先行），meta.notes 与 attempted[]
  如实转述、绝不编造。Not for: 火车票实购（→12306 MCP）、纯网页资料搜索（→search-fusion）、
  酒店搜索与预订（→rollinggo-hotel-booking 技能，见路由表住宿行）。
---

# 门到门出行规划（travelfusion MCP）

## 0. 铁律（先读）

1. **付费永不自动**：`paid_calibrate` 只在用户明确要求"校准/精确/官方价"时才带；
   返回 `CONFIRM_REQUIRED` 时，向用户说明费用征得同意后才能带 `confirm_spend` 重试。
2. **不编造**：`NO_MATCH` = 该源真没有，转述为"没查到+覆盖范围说明"；
   `meta.attempted[]` 里的失败如实转述；`null` 字段保持 null（未知不填造）。
3. **缓存命中**（`meta.cache=hit`）直接用，不重复调用；同一问题短时间重问直接答。
4. 火车购票走 12306 MCP；本服务管机票/地面/天气/核验。

## 1. 场景分型（决定 trip_type）

| 信号 | trip_type |
|---|---|
| 团建/年会/奖励旅游/公司组织/客户答谢 | `incentive`（廉航、红眼标注并压后） |
| 自由行/穷游/个人/探亲（默认） | `personal`（只标注不过滤） |

用户没说且无法推断时，问一句："个人出行还是公司奖励旅游口径？"

## 2. 工具路由

| 用户意图 | 工具链 |
|---|---|
| 机票多少钱 / 比价 | `flight_price`（+`trip_type`；要精确价→征得同意后 `paid_calibrate`） |
| 航班现在什么状态 / 延误 / 登机口 | `flight_status`；需交叉确认→`flight_verify` |
| 多候选航班推荐 | `flight_status_batch`（一次 N 班、每班一张卡）；传 `dep_iata/arr_iata` 过滤航线（免费源按班号匹配会张冠李戴）；诊断性单查加 `silent=true` 不出卡 |
| 境内两地开车/打车 | `route_ground`（自动走高德：限行/EV/官方打车价） |
| 境外落地交通（机场↔市区/城际） | `route_ground`（自动走 Google；transit 默认） |
| 出行日天气 | `weather_context`（≤16 天预报 / >16 天只给气候常态） |
| **多日行程排程** | 先 `attraction_search`(city, keyword) 查建议游览时长/门票/开放时间（覆盖杭州/上海/苏州/重庆/广州/北京/武汉/成都/南京/深圳十城）→ 排程后必调 `plan_validate`(city, items) 可行性校验——违规必须调整，不可照发；未覆盖城市按通用规则+联网核验 |
| 全程行程（✈️🚄🚗 多段） | `itinerary_plan`（legs=[{mode,from,to,depart,arrive}] 按时间升序；✈️🚄 为固定锚点——服务端自动反推到站 deadline 与地面段最迟出发，✈️ 默认提前 60min、🚄 30min） |
| 这个航班靠谱吗 | `flight_verify`（计划层×ADS-B 观测层） |
| 历史 cheapest 到过多少 | `flight_price` 的 `meta.baseline_90d`（<5 样本不显示，如实说） |
| 额度/花了多少钱 | `quota_status`（规划收尾主动附一行成本） |
| 航司行李/餐食/收费怎么算 | `airline_kb`(action=list/get)——已沉淀廉航/全服务航司行李与收费知识；涉及廉航（9C/KN/FR 等）报价时主动带一条行李提示 |
| 境内具体地点/POI 坐标 | `poi_search`(keywords, city)——地标/车站/景点精确坐标；地名解析失败会自动降级并在卡片出 warn |
| 地点中文名转标准码/坐标 | `resolve_place`（五码注册表解析） |
| 多方案汇总推荐卡 | `trip_recommend`(summary={scenario, picks:[{label,title,reason,tags}], notes})——服务端渲染推荐汇总卡，picks 按推荐序排列 |
| 数据源运维（启用/停用/预算） | `provider_admin`（变更类 action 需 admin_key；disable 付费源、调预算先向用户确认） |
| **住宿：酒店检索** | `hotel_search`（travelfusion 原生工具，服务端已强制附加推广归因；展示价注明"参考价"）。检索不依赖 rollinggo 技能 |
| **住宿：锁价/下单/订单管理** | → 切换 `rollinggo-hotel-booking` 技能（OAuth 登录态 + 人工两步确认）；资金闸门留在技能层，服务端不碰交易 |

## 2b. 场景配方（照抄链路，别重新发明）

- **单程航班推荐**：web 搜索拿候选班号 → `flight_status_batch`(带 dep_iata/arr_iata) → 逐班结论 + 首推理由
- **往返/联程规划**：两端航班/车次时刻 → `route_ground` 衔接段（市区↔机场）→ `itinerary_plan` 拼全程卡
- **自驾游（N 天）**：`route_ground`(主干往返) + `weather_context`(目的地+日期) + `itinerary_plan`(每日腿) + 沿途景点 `poi_search` 补充、多方案收尾用 `trip_recommend` 出汇总卡

## 2c. 住宿选址 SOP「以线定房」（行程含住宿时必走）

> 原则：**酒店选址由线路决定，不由城市名决定**。先有行程，后有酒店锚点。

1. **行程先定**：`attraction_search` + `plan_validate` 排出每日景点（含坐标与建议时长）
2. **锚点计算**：取各日景点的地理重心与地铁站锚点——优先选能一条地铁线串联多数锚点的站（如杭州 3 号线串灵隐/西溪方向）
3. **锚定搜索**：优先 `hotel_search`（travelfusion 原生，place_type 支持城市/景点/地铁站等，链接归因服务端保证）；结果不足再降级 rollinggo 技能搜索（此时归因靠 2d 规则改写）
4. **通勤核验**：对候选酒店集中区，用 `route_ground` 实测「锚点 → 各日头号景点」的通勤，出通勤矩阵
5. **推荐输出**：通勤矩阵 + 参考价 + 权衡说明（近 A 景点必然远离 B 景点，如实说），用户选定后回 rollinggo 走房型→锁价→两步确认下单

## 2d. RollingGo 推广归因（输出必改，一单都不能漏）

所有 rollinggo.cn 链接（bookingUrl/详情页）输出前必须做归因替换：
- `utm_source=rollinggo_cus` → **`utm_source=<YOUR_PROMO_CODE>`**（官方推广参数格式：`?id=xxx&utm_source=推广编号`）
- 若链接没有 utm_source 参数 → 追加 `&utm_source=<YOUR_PROMO_CODE>`
- 其余参数（id/checkInDate/checkOutDate/roomCount 等）一律原样保留，改参数名=佣金丢失
- 代码 <YOUR_PROMO_CODE> 为推广归因标识（非机密，公开链接可见）；自购订单是否计佣以 RollingGo 推广规则为准
- **两个固定归因入口**（分享"自己去找/自己订"的场景时用，而非具体酒店链接）：
  - 酒店搜索页：`https://rollinggo.cn/pages/reservationLink/index?utm_source=<YOUR_PROMO_CODE>`
  - AI 对话订房页：`https://rollinggo.cn/pages/ai-home/index?utm_source=<YOUR_PROMO_CODE>`
- 归因覆盖三面：具体酒店详情页（改 utm_source 值）、搜索页、AI 入口页——分享哪个环节就给哪个页

## 3. 产出交付（v3 零加工直取——模型只管结论）

**正常路径**：渲染器会**直接从本轮工具调用轨迹里提取**服务端编排的 `meta.card`
并渲染富卡片——你不需要写工件、不需要 present、不需要格式化。职责只有：

1. 正常调用工具
2. 对话里给一两句**结论摘要**（推荐哪条/延误与否/下一步动作），不复述卡片内容
3. `actions[].confirm=true` 的动作必须先征得用户同意

- 可选双保险：把 `meta.card` 写入 `<id>.tf.json` 并 present（description=单行 JSON）
  可让侧栏打开卡片原文——非必需
- 旧版 markdown 模板保留在 [references/fallback-markdown.md](references/fallback-markdown.md)，
  仅当渲染插件缺位时按需加载

- 不认识的 type 也原样搬运（插件有通用预览回退）
- `actions[].confirm=true` 的动作必须先征得用户同意

**回退路径**：交付卡片插件缺位时，按 [references/fallback-markdown.md](references/fallback-markdown.md)
的模板做 markdown 渲染（仅此场景加载该参考）。

## 4. 错误码 → 用户话术

| 错误码 | 一句话话术 |
|---|---|
| NO_MATCH | 没查到：<hint>（通常是覆盖范围或日期窗口外） |
| DATA_UNAVAILABLE | 暂无可用数据源：<hint> |
| NOT_APPLICABLE | 不适用：<hint>（如短途不建议飞行） |
| QUOTA_LIMIT | <源>免费额度已用完，本月恢复或改用其他源 |
| BUDGET_EXHAUSTED | 本月付费预算不足（已用+本次>预算），需用户决定是否调预算 |
| CONFIRM_REQUIRED | 精确查询约 ¥X——要我花这笔吗？（同意后带 confirm_spend 重试） |
| AUTH_REQUIRED | <源>密钥问题，需要维护（提醒用户，不要反复重试） |

## 5. 收尾纪律

- 规划类回答（≥3 次工具调用）末尾附一行成本（来自 quota_status 或各 meta.cost）
- 同一会话同一查询结果直接复述，不重打（服务端有 TTL 缓存，重打浪费额度）
