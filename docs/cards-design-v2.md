# travelfusion 卡片系统设计 v2（ supersede v1 ）

> v1 是卡片清单与单个视觉规格；v2 升级三件事：
> ① **服务端卡片编排器**（meta.card）——"内容类型标记 → 程序化套用"的落地机制
> ② **旅程全生命周期卡片全景**（PM 视角五段 18 卡）
> ③ **地图线路卡低成本方案**（SVG 示意图，零瓦片依赖）

## 1. 架构升级：服务端编排器 = 三层分工

```
┌─ travelfusion 服务 ──────────────────────────────┐
│ capability 返回 → cards.compose(type, payload,    │
│ notices, actions, meta) → meta.card 完整卡片包     │
└──────────────┬───────────────────────────────────┘
               │ MCP 响应（meta.card 随行）
┌──────────────▼───────────────────────────────────┐
│ agent（搬运工）：取 meta.card → 写 .tf.json 工件    │
│ → present。不判断、不格式化、不增删字段             │
└──────────────┬───────────────────────────────────┘
               │ present 拦截（delivery-cards 链）
┌──────────────▼───────────────────────────────────┐
│ 插件渲染器：按 type 套模板 → 富卡片                  │
│ 不认识的 type → 通用预览回退（永不白屏）              │
└───────────────────────────────────────────────────┘
```

- 服务端新增 `app/core/cards.py`：每 capability 一个 compose 函数（~40 行/个），
  判定类逻辑（LCC/红眼/排序/置信/基线解读）全部在这里完成
- **判定与格式彻底离开模型**：skill 的展示章节整体退役，替换为一句话
  "把 meta.card 原样写入 .tf.json 并 present"
- 模型漏 present 也不破坏数据（.tf.json 工件仍在，v1.1.0 produced 兜底可扫）

## 2. 旅程全生命周期卡片全景（PM 视角）

### 决策前（选哪条线/哪天走）
| 卡 | type | 数据源 | 期 |
|---|---|---|---|
| 机票多选一 | `price.select` / `price.single` | TP缓存 / VF校准 | 一期 |
| 列车多选一 | `rail.select` | VF tripmatch trainTickets | 二期 |
| 机票vs高铁对比 | `airrail.compare` | S1+S2 复合 | 二期 |
| **价格趋势/低价日历** | `price.trend` | **基线采集器已有按日数据——零上游成本，纯可视化** | 二期★ |
| 历史基线卡 | `meta.baseline` 并入价格卡 | 同上 | 一期 |

### 出行前（准备与确认）
| 卡 | type | 期 |
|---|---|---|
| 付费确认卡（CONFIRM_REQUIRED 专属） | `confirm` | 一期（empty 特例） |
| 出行清单卡（证件/预约/值机提醒） | `checklist` | 三期（规则库驱动） |

### 出行当天（实时）
| 卡 | type | 期 |
|---|---|---|
| 航班状态时间线 | `status` | 一期 |
| 双源核验判定 | `verify` | 二期 |
| **延误/航变告警** | `alert`（status 的告警态，阈值染色） | 二期 |
| **中转衔接卡**（到达航站楼→下一班，`transfer`） | VF/airlabs 有航站楼字段，v1 可做摘要 | 三期 |

### 途中与周边
| 卡 | type | 期 |
|---|---|---|
| 境内驾车（限行/EV/打车价） | `route.cn` | 一期 |
| 境外交通（transit 链） | `route.intl` | 一期 |
| **行程线路图（SVG 示意地图）** | `route.map` / `itinerary.map` | **二期★（见 §3）** |
| 天气窗口 | `weather` | 一期 |

### 返程与系统
| 卡 | type | 期 |
|---|---|---|
| 多日行程汇总 | `itinerary` | 二期 |
| 花费复盘 | `cost.recap` | 三期 |
| 额度仪表 | `quota` | 一期五卡（quota_status 已有数据） |
| 错误/空态 | `empty`（含 CONFIRM_REQUIRED 特例） | 一期 |

★ = 新增亮点卡。

## 3. 地图线路卡（§你提的 slide 工具启发）——成本账

**结论：能低成本低做，关键是"不加载地图瓦片"。**

| 方案 | 成本 | 风险 |
|---|---|---|
| ✅ **SVG 示意地图**（v1 选） | 插件内 ~100 行：经纬度等距投影 → 画布上描点+弧线+序号标签。坐标**服务端已全有**（route 响应 `coords_wgs84` + 城市表 lat/lon），agent 零编码 | 无瓦片依赖、离线可用、CN 网络无关；风格=航空杂志航线图（干净） |
| ⏳ 交互瓦片地图（Leaflet+OSM/高德瓦片） | 插件内引入渲染库 + 瓦片源在 CN 的可用性风险 | 二期可选开关 |

`route.map` payload（服务端组装）：
```json
{"points": [{"name":"成都","lat":30.57,"lng":104.07,"seq":1},
            {"name":"乐山","lat":29.55,"lng":103.77,"seq":2}],
 "lines": [{"from":1,"to":2,"mode":"driving","label":"136.8km·93min"}],
 "bbox": {"minLng":103.77,"minLat":29.55,"maxLng":104.07,"maxLat":30.57}}
```

`itinerary.map` = 多 points 多 lines（多日交通段串联），itinerary 卡内嵌同一渲染器。

## 4. 一期范围收敛（评审后即动工）

- 服务端：`cards.py` 编排器 + 五卡 compose（`price.select/single`、`status`、`confirm`、`quota`）
  + `route.cn/route.intl/route.map`（数据现成，顺手一起）→ **八卡**
- 插件：delivery-cards 渲染器八模板 + 通用回退
- skill v2：展示章节退役 → `meta.card` 搬运指令 + markdown 回退模板保留
- 数据侧前置（P0 已列）：VF 价格归一化、自动基线、notices 生成器、负向缓存

## 5. 边界不变

卡片只渲染不计算；购票走 12306；actions 一期=回灌指令；不认识的 type 回退通用预览。
