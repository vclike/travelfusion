# travelfusion 卡片系统设计 v1（travelfusion-card/v1）

> 状态：设计稿待评审 ｜ 上游依赖：P0 数据层（VF 价格归一化/自动基线）
> 宿主：dsh-delivery-cards 扩展渲染器（turnTail 链 priority -2，present 拦截）

## 0. 设计原则

1. **卡片只渲染，不计算**——所有判定（LCC/红眼/排序/置信/基线解读）由服务端或 agent 完成，卡片消费现成结论。
2. **schema 版本化**：`schema: travelfusion-card/v1`；不认识的 type 一律回退通用预览（永不白屏）。
3. **渐进增强**：插件缺位时，agent 按 trip-planner skill 的 markdown 模板回退（skill 保留精简版模板作 fallback）。
4. **notices 通用通道**：LCC 特殊提示/红眼提示/覆盖缺口一律走 `notices[]`（服务端从 norms.yaml 生成结构化文案），客户端只管分级渲染（warn=⚠️ / info=ℹ️）。

## 1. 场景矩阵 → 卡片类型

| # | 场景 | 数据源（真实形状已实测） | 卡片 type |
|---|---|---|---|
| S1 | 机票多选一（含单条退化） | TP cached 价 / VF calibrated 舱位 | `price.select` / `price.single` |
| S2 | 列车多选一（二期，VF tripmatch） | searchTrainTickets | `rail.select` |
| S3 | 机票 vs 高铁对比（奖励旅游高频） | S1+S2 复合 | `airrail.compare` |
| S4 | 航班状态（单航班跟踪） | AirLabs 双端点合并 | `status` |
| S5 | 双源核验 | AirLabs×OpenSky + consistency | `verify` |
| S6 | 路线导行·境内驾车 | 高德 v5（距离/时长/过路/打车价/EV） | `route.cn` |
| S7 | 路线导行·境外 | Google Routes v2（transit 线路链） | `route.intl` |
| S8 | 天气窗口 | Open-Meteo 双层 | `weather` |
| S9 | 多日行程汇总 | agent 编排复合 | `itinerary` |
| S10 | 错误/空态（含 CONFIRM_REQUIRED） | canon error | `empty` |

## 2. 信封 schema（所有卡共用）

```json
{
  "schema": "travelfusion-card/v1",
  "type": "price.select",
  "title": "成都 → 曼谷 · 机票",
  "scene": {"trip_type": "incentive", "date": "2026-11-17", "pax": 2},
  "payload": { /* 按 type 定义的强类型载荷 */ },
  "notices": [
    {"level": "warn", "icon": "lcc", "text": "FD 泰亚航为廉航：无免费行李、无餐食、选座收费"},
    {"level": "info", "icon": "redeye", "text": "02:30 起飞为红眼航班"}
  ],
  "actions": [
    {"id": "calibrate", "label": "花 ¥0.5 校准官方价", "confirm": false}
  ],
  "meta": {
    "sources": [{"provider": "travelpayouts", "freshness": "live"}],
    "attempted": [],
    "cost": {"free_calls": 1, "paid_cny": 0},
    "baseline": {"min_cny": 1153, "avg_cny": 1153, "vs_min": 0, "samples": 5},
    "cache": "miss"
  }
}
```

- `actions[].confirm: true` 表示点击需用户二次确认（付费类）。
- `meta.baseline` 存在时价格卡必渲染"历史位置条"。

## 3. 各卡片视觉规格（ASCII 线框）

### S1 `price.select` —— 航班多选一 + 票价

```
┌─ 成都 → 曼谷 ｜ 11-17 ｜ 奖励旅游口径 ────────────┐
│ ① ✓推荐  3U 川航   ¥1,200  10-03 08:00  正班      │
│ ②        FD 泰亚航 ¥800   10-03 02:30  ⚠️LCC·红眼 │
│ ③        CZ 南航   ¥1,350 10-03 12:10  正班·经停  │
│ ├ 历史位置 ▁▁▂▁█ ← 当前 vs_min 0%（90天最低位）   │
│ ⚠️ LCC 提示：FD 无免费行李·无餐·选座收费  [展开]   │
│ [花 ¥0.5 校准官方价]  来源:TP缓存·expires 2h      │
└──────────────────────────────────────────────────┘
```

- payload：`{prices:[{rank,recommended,airline,flight_no,amount,currency,dep_local,lcc,red_eye,stop}], price_type: "cached|calibrated"}`
- `price_type=calibrated` → 角标"官方价"徽章 + 来源标 VF；cached → 标"参考缓存价+expires_at"
- incentive 已由服务端排序 → `recommended=true` 渲染 ✓推荐 徽章（正班优先）
- **单条退化**：`price.single` 复用同一载荷，隐藏选择列
- LCC 脚注数据源：norms.yaml `norms.lcc`（行李/餐食/选座基线）——服务端检测选中项含 lcc 时自动生成 notices

### S2 `rail.select` —— 列车多选一（二期）

```
┌─ 成都东 → 南京南 · 高铁 ──────────────────────────┐
│ G1974  08:12→17:36 (9h24m)  二等¥703 一等¥1149    │
│         余票: 二等有 · 一等紧张                    │
│ D632   09:40→19:58 (10h18m) 二等¥620  ⚠️仅无座    │
└──────────────────────────────────────────────────┘
```

- payload：`{trains:[{no,type(G/D/C),dep,arr,duration,seats:[{class,price,status}]}]}`
- 与 S1 组合出 `airrail.compare`：左右分栏 机票最优 vs 高铁最优 + 时长/价格/准点对比行

### S4 `status` —— 航班状态卡

```
✈️ CA165 北京首都 → 墨尔本 （国航）
●计划 01:00 ──●预计 01:12 (+12min) ──○实际 ──
到达：14:25 预计 ｜ T3→T2 ｜ 行李：待定
来源 AirLabs(live) · 置信 medium
```

- 时间线三节点：scheduled→estimated→actual（有则实心）；延误 pill 着色（<15 绿 / 15-60 黄 / >60 红）
- `airline_hints` → 底部一行贴士

### S5 `verify` —— 核验判定（结论先行横幅）

```
┌─ ✅ 核验一致（高置信）──────────────────────────┐
│ 计划层 active ＋ ADS-B 捕获：曼谷上空 2,568m 下降中 │
│ 计划: AirLabs ｜ 观测: OpenSky(live)              │
└──────────────────────────────────────────────────┘
```

- 横幅三态：✅一致 / ⚠️未捕获（覆盖缺口≠异常）/ ○仅计划层

### S6 `route.cn` —— 境内驾车（高德）

```
🚗 成都 → 乐山
136.8 km · 1h33m ｜ 过路 ¥52 ｜ 红绿灯 11
官方打车 ¥445 ｜ EV(400km)：无需充电
```

### S7 `route.intl` —— 境外（Google transit 链）

```
🚄 大阪 → 东京 498.9km · 6h
[🚶5m] → 🚄东海道新干线 → 🚌83路 ｜ 步行合计 5m
```

- `transit_lines` 渲染成步进链（图标=vehicle 类型）；空 transit → 显示 NO_MATCH 说明行

### S8 `weather`

```
🌦️ 曼谷 10-03 ｜ 预报（≤16天）
25.0–30.4°C 降水 8.7mm ｜ 7–16 天段：可信度递减
```

- layer 徽章强制；climate 层不渲染逐日，只渲染月度摘要（schema 层面禁止）

### S9 `itinerary` —— 多日行程

```
🧳 成都→曼谷 5天 · 奖励旅游 ｜ 假设:2人
[D1 抵达+夜游] [D2 海岛] [D3 ...]  ← tab 切换
每日槽: 交通/安排/备注
底部: 本次查询消耗 免费5次·付费¥0.5 ｜ 风险2条(折叠)
```

### S10 `empty` —— 错误/空态（永远给下一步动作）

```
┌─ ⚠️ 该日期暂无价格数据 ──────────────────────────┐
│ 飞常准价格窗口约 45 天；11-17 超出窗口             │
│ [临近 30 天内提醒我校准]  [改查 10-15]            │
└──────────────────────────────────────────────────┘
```

- 每个 canon 错误码 → 图标 + 人话 + 至少一个 action（对照 skill §4 话术表）

## 4. 服务端配套改造（卡片燃料）

1. **VF 价格归一化**（P0-3）：`raw_text` → `cabins:[{class,code,price,discount,seatnum}]` + `flight_no/dep/arr/stop/meal`——S1 舱位明细的燃料
2. **flight_price 成功自动入基线**（P0-2）：`meta.baseline` 从此普遍存在
3. **notices 生成器**：norms.yaml `trip_rules`+`norms.lcc` → 结构化 notices（服务端职责，客户端零知识）
4. **负向缓存**（P0-4）：`empty` 卡的 hint 更干净

## 5. 边界与回退

- 插件未装/不识别 schema → agent 按 trip-planner skill 的 markdown 模板输出（fallback 模板保留在 skill 内）
- 火车票**购买**不在卡上（→12306 MCP）；卡片只做"多选一决策"
- 卡上 actions 一期只做**回灌指令**（点击=把指令发回会话），不做直接支付/预订

## 6. 实施顺序

1. schema 定稿（本文件评审通过）
2. 服务端燃料四项（§4）
3. delivery-cards 渲染器：一期做 `price.select / price.single / status / empty` 四种卡
4. skill v2 瘦身（展示章节 → "写 schema 文件 + present"）
5. 二期卡：`rail.select / airrail.compare / verify / route.intl / weather / itinerary`
