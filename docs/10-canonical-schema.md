# 10 · Canonical 数据模型与维度审计（开发前定稿 · 2026-09-29）

> Schema 后改 = 全部 provider 重映射 + 缓存/基线迁移。本文件一次定到位。
> 三原则：**开放枚举 + provider 原值透传 + unknown 显式**（永不装确定）。
> 本文件是 canon 层的实现规格与验收合同。

---

## 1. TripQuery —— 所有工具的输入归一

```json
{
  "trip_type": "oneway|roundtrip",              // 默认 oneway
  "origin": "成都", "destination": "乐山",        // 任意片段，服务内部解析
  "depart_date": "2026-10-02",                  // 相对日期由 agent 解析为具体日
  "return_date": null,
  "pax": { "adults": 1 },                        // 儿童/婴儿 → 显式 unsupported
  "cabin_pref": "any",                           // any|economy|business|…；any=全舱位返回
  "mode_pref": "auto",                           // auto|rail|drive|air；auto=资格引擎决定
  "policy": { "paid_calibrate": false, "weather": true, "currency": "CNY",
              "confirm_spend": false, "trip_budget_cny": null, "force": false,
              "detail": false }
}
```

## 2. Place —— 地点（五码 + 粒度）

```json
{ "name": "成都", "granularity": "city|airport|station",
  "iata": "CTU", "icao": "ZUUU", "city_code": "CTU",
  "station_telecode": null, "coord_wgs84": [30.57, 103.95],
  "country": "CN", "tz": "Asia/Shanghai",
  "coord_gcj02": [30.573, 103.952] }             // 高德原值保留，内部转换用
```
- 城市级查询 → 结果**必须落到具体机场/车站**，粒度降级可追溯
- ⚠️ 城市码与机场码可能同串（CTU 既是成都城市码也是双流机场码）→ 两字段分立，不混用

## 3. Times —— 时刻三件套（强制）

```json
{ "scheduled_utc": "2026-10-02T08:30Z", "scheduled_local": "2026-10-02T16:30+08", "tz": "Asia/Shanghai",
  "estimated_utc": null, "actual_utc": null,
  "day_offset": 0 }
```
- **红眼/跨天航班必须显式 `day_offset`**（到达日偏移），不许只给时刻不給日
- AirLabs 三件套（local/ts/utc）原样归一到此结构

## 4. CabinClass —— 舱位/席别（mode 作用域开放枚举）

| mode | canonical | 中文标签 | 来源原值 |
|---|---|---|---|
| air | economy | 经济舱 | 飞常准 `economy` |
| air | premium_economy | 超级经济舱 | `premium_economy` |
| air | business | 公务舱 | `business` |
| air | first | 头等舱 | `first` |
| rail | business | 商务座 | 12306 商务座 |
| rail | preferred_first | 优选一等座 | 12306 优选一等座（实测存在） |
| rail | first | 一等座 | 12306 一等座 |
| rail | second | 二等座 | 12306 二等座 |
| rail | soft_sleeper | 软卧 | 12306 软卧 |
| rail | hard_sleeper | 硬卧 | 12306 硬卧 |
| rail | hard_seat | 硬座 | 12306 硬座 |
| rail | no_seat | 无座 | 12306 无座 |
| ground | — | 票价语义见 §5 | taxi_cost 为参考值，打车档次无数据 |

规则：provider 返回未知枚举值 → **原值透传不丢弃**（`cabin_class: "raw:xxx"`）；
`cabin_pref=any` → 返回全舱位数组，绝不静默只给一个舱。

### 4.1 各模式价格语义差异（最易踩坑处）

| 模式 | 价格载体 | 必须携带 |
|---|---|---|
| air | 每舱位一价 | `tax_included`（飞常准 `adult_total` 已含税，Travelpayouts 缓存价口径需标注） |
| rail | **每席别一价 + 余票数同层** | `availability{status, count}`（实测：二等座余 8 张 626 元——价格与余票是一对，不可拆） |
| drive | 能耗估算 | `energy_cost` + assumptions（油耗×油价配置 或 EV 折扣模型） |
| taxi | 参考价 | 仅 `taxi_cost` 一个数，无档次数据 |

## 5. PricePoint —— 全模式统一价格对象

```json
{ "mode": "rail", "cabin_class": "second", "cabin_label_cn": "二等座",
  "amount": 626, "currency": "CNY", "per_person": true,
  "tax_included": true,
  "price_type": "bookable|cached|baseline|forecast|composed",
  "availability": { "status": "few", "count": 8 },        // air 免费层无余票 → null
  "conditions": { "refundable": "unknown", "changeable": "unknown" },
  "fx": null,                                              // 币种转换时: {rate, date, from}
  "composed": false,
  "provenance": { "provider": "12306-mcp", "collected_at": "2026-09-29T14:02Z", "expires_at": null } }
```

- **价格语义四态**（老朋友，价格梯队的数据载体）：`bookable` 可成交 / `cached` 缓存参考
  / `baseline` 历史基线 / `forecast` 预测 / `composed` 拼接
- **拼接价纪律**：往返或中转由两段相加得到时 `composed: true` 必带
  note「拼接估算，实际联程/往返价可能更低」——联程价 ≠ 两段之和
- **条件规则（退改签）免费源一律 `unknown`**，永不假设"可退"
- 币种转换必带 `fx{rate, date, from}`；原始币种金额保留在 `amount_original`

## 6. Status —— 状态（含覆盖层意识）

```json
{ "value": "scheduled|active|landed|cancelled|diverted|incident|unknown",
  "dep_delay_min": 137, "arr_delay_min": 137,     // 出发/到达延误并存分开标
  "coverage": { "dep_layers": 3, "arr_layers": 2 },
  "gate": { "dep": "E4", "arr": null },
  "baggage": "1" }
```
- 到达端无实时层 → 状态可能永久停在 `departed`：**输出必带 coverage 说明**（AeroDataBox 铁律）
- `unknown` 透传，不折叠成正常

## 6b. AirlineInfo —— 航司知识层（本地精选 KB · 自动附载 · MCP 可编辑）

```json
{ "iata": "9C", "icao": "CQH", "name_cn": "春秋航空",
  "carrier_type": "low_cost",              // full_service|low_cost|ultra_low_cost|regional|charter|unknown
  "alliance": null,                        // star|skyteam|oneworld|null
  "hub": ["SHA"],
  "hints": [                               // ⭐ 短句知识：只记"偏离行业基线"的特殊之处
    { "tag": "行李", "text": "手提仅7kg，低于常见额度" },
    { "tag": "餐食", "text": "无免费餐食" },
    { "tag": "选座", "text": "选座需付费" } ],
  "notes": [],                             // 自由评注（主观，标注编辑评注）
  "source": "curated-v1", "as_of": "2026-09",
  "revisions": [ { "at": "2026-09", "by": "agent", "reason": "初版调研提炼" } ] }
```

### 短句提炼规则（调研产出的蒸馏标准）

- **只记偏离，不记常态**：行业基线存 `data/norms.yaml`（一份：手提/托运常见额度、FSC 默认含餐、
  选座默认免费……由调研子问题 6 定基线）；航司条目只写**与基线的偏差**
- **短句格式**：`{tag, text}` 结构化——tag ∈ 行李/餐食/选座/座椅/收费/其他；text ≤ 30 字、
  自含结论（"手提仅7kg，低于常见额度"而非"行李是7kg"）
- 航班结果自动附载时 hints 逐条进 `airline_info.hints`，agent 零加工转述
- 常态航司（无偏离）hints 为空数组——空也是信息（"无已知特殊规定"）

### MCP 编辑闭环（agent 修正知识）

工具 `airline_kb`（服务在极空间，agent 无文件系统访问 → 必须经 MCP）：

| 动作 | 说明 |
|---|---|
| `list` / `get` | 查条目（含 hints、来源、修订史） |
| `set` | 新增/更新条目或字段，**必带 `{by: "agent"|"user", reason}`**，追加 revisions |
| `unset_hint` | 删除某条短句（发现错误时） |
| `set_norm` | 修订行业基线（同样记 provenance） |

- **修正闭环**：结果与知识矛盾（用户实测/新证据）→ agent 调 `set` 修正 → 下一次响应即正确
- 每次 `set` 追加 revisions（append-only），不覆盖历史——与 decktag 修订台账同哲学
- 对用户的表现形式："这条标记已更新：春秋手提 7kg（你说的 20kg 是尊享飞产品线）"——
  知识被谁改、为何改，可追溯

### 既有规则（不变）

- **数据来源 = 本地精选知识库 `data/airlines_kb.yaml`（非 API）**：免费结构化源无体验口碑类字段
  （AirLabs/Aviationstack airlines 库仅骨架字段）；精选 50–100 家覆盖中国出行者 99% 场景，
  `unknown` → 🌐 网页兜底
- **自动附载**：flight_price / flight_status / itinerary 的每个航班按航司码挂 AirlineInfo；
  `low_cost|ultra_low_cost` 自动加注「廉航：票价通常不含托运/选座/餐食，按总出行成本口径比较」
  ——**只标注口径，不编造修正价**（无行李费数据源）
- **刻意不做**：安全评级类主观/时效敏感知识不进精选库，需要时 🌐 并标注来源
- v1 种子分组：国内廉航（春秋/九元/西部/中联航/乌鲁木齐）· 东南亚廉航（亚航/越捷/酷航/捷星/宿务/泰狮子）·
  欧美廉航（瑞安/威兹/易捷/精神/边疆）· 全服务主力打联盟标签（CA/MU/CZ/HU/3U + JL/NH/KE/SQ/CX/TG + UA/DL/AA + LH/AF/BA）
- PLAYBOOK 章节：新增/修订航司条目三步

---

## 6c. AirlineNameIndex —— 航司名称归一（别名索引）

**问题**：海外平台返回英文名/码（"Air China"/CA/CCA/callsign"AIR CHINA"），用户说中文（"国航"），
KB 按 IATA 码组织 → 需要别名索引把一切归一。**canonical key = IATA 二字码**。

> **统一原则**：目标是**身份唯一**，不是语言偏好。别名集合是**语言无关的开放集合**——
> 中文/英文/ICAO/callsign/历史曾用名都是平等的别名形态，各数据源贡献各自有的部分；
> agent 遇到新形态解析成功后可经 `airline_kb add_alias` 登记，索引越用越全（自改进闭环）。

### 来源（全免费，启动时一次构建 → `data/airlines_index.json`，月更同 places 注册表）

| 源 | 提供 |
|---|---|
| AirLabs `/airlines` DB（免费档含，1 call 拉全库） | iata / icao / 英文名 |
| OpenFlights airlines.dat（免费 CSV） | name / alias / icao / callsign |
| Aviationstack `/airlines`（免费） | name / iata / icao |
| **airlines_kb.yaml（精选）** | **中文简称**（国航/东航/南航/川航…英文库没有中文，只能精选） |

### 解析顺序（确定性，flight 工具内部自动，agent 可给任意形态）

```
1. 航班号前缀        CA1501 → CA        ← 最常见场景免费自带
2. 精确 IATA(2字) / ICAO(3字)
3. callsign 精确      "AIR CHINA" → CA
4. 别名/名称精确      "国航"/"中国国航"/"Air China" → CA（大小写不敏感）
5. 子串模糊           → 歧义列候选，不自动选
全部失败             → unknown + 🌐 指引
```

### 子公司继承

KB 条目可选 `parent_iata`（深航 ZH←国航 CA · 山航 SC←CA · 上航 FM←MU）：
子航司缺条目时按 parent 补基线规则，输出标注「继承自母公司基线」；hints 以子航司自有为准。

### 使用位置

flight 工具输入解析（"国航"也收）· 跨 provider 结果 join（各家均以 IATA 为主键）· KB 命中。
`resolve_place` 保持仅地点，不混航司。

---

## 7. Itinerary —— 多模式行程组合

```json
{ "legs": [ { "mode": "rail", "…Times/Place…", "prices": [PricePoint…], "weather": {…} } ],
  "totals": { "price_cny": { "sum": 752, "missing_legs": ["机场大巴段: 无数据"] },
              "duration_min": 340 },
  "labels": ["价格含拼接段，非联程"] }
```
- 缺价格的 leg 显式列入 `missing_legs`，**不算 0、不省略**

## 8. VehicleProfile —— 车辆画像（config 默认 + 调用覆盖）

```json
{ "type": "ev", "rated_range_km": 600, "consumption_factor_highway": 0.75,
  "soc_charge_to": 0.9, "soc_floor": 0.15,
  "fuel_l_per_100km": null, "fuel_price_cny": null,
  "plate": null }
```

## 9. 维度审计总表（逐维 × 免费源能力 × 诚实默认）

| 维度 | 航空（免费） | 铁路 | 地面 | 诚实默认 |
|---|---|---|---|---|
| **分舱/席别价格** | ⚠️ 仅经济向参考价（Travelpayouts 缓存）；**分舱精确价=付费校准** | ✅ 全席别价+余票（已实测） | — | `cabin_pref=any` 全返回；航空分舱走校准 |
| 税费口径 | ⚠️ 各源不一 | ✅ 含 | — | `tax_included` 必填 |
| 余票/座位可得 | ❌ | ✅ | — | air 置 null |
| 儿童婴儿票 | ❌ | ❌ | — | **unsupported 显式返回** |
| 退改签规则 | ❌ | ❌ | — | `unknown` |
| 往返联程价 | 💰 飞常准 `type=2` | —（12306 往返=两段） | — | 拼接价 + `composed` 标签 |
| 中转组合价 | 💰 DuckDB legs | ✅ 中转查询 | — | 免费只给捆绑参考 |
| 币种 | ✅ 参数 | ✅ CNY | ✅ CNY | 转换带 `fx{rate,date}` |
| 多乘客总价 | 每人价 | 每人价 | — | `per_person: true`，总价 ×n 由 agent 算 |
| 红眼跨天 | ✅ | ✅ | — | `day_offset` 显式 |
| 时段偏好 | ✅ 时间参 | ✅ 早晚筛选 | ✅ depart_time | — |
| 直飞/经停/中转次数 | ✅ | ✅ | — | — |
| 选座/行李额/值机 | ❌ | ❌ | — | 🌐 航司/12306 指引 |

## 10. 显式不支持清单（防 scope creep）

儿童/婴儿票 · 退改签规则 · 选座 · 行李额/超重费 · 常旅客里程 · 机酒套餐 ·
舱位子级（Y/B/M/H 运价舱位）· 团体票

> 全部走"unsupported/unknown 显式 + 官网指引"输出，不假装支持。

---

## 11. 验收（canon 层）

- [ ] 每个 provider 映射表覆盖本文件全部字段，未知枚举走 `raw:` 透传
- [ ] 价格对象五态（bookable/cached/baseline/forecast/composed）各有单测
- [ ] 余票与价格同对象（rail 快照含 8 席别 × 价×余票）
- [ ] `day_offset`、`composed`、`conditions: unknown`、`coverage` 均有样例 fixture
- [ ] 显式不支持清单在对应工具输出中有专属错误/标注文案
