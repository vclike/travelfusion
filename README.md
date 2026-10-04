# travelfusion

> **为 DeepSeek Harness（DSH）定制的门到门出行聚合服务** —— 17 个 MCP 工具 · 8 个数据源 · 14 类富卡片。
> 机票比价与核验 · 境内境外地面交通 · 景点知识库与行程校验 · 酒店检索（RollingGo） · 天气窗口 · 门到门时间线。
> 所有计算与结论在服务端完成，DSH 里以富卡片直出（依赖 [dsh-delivery-cards](https://github.com/vclike/dsh-delivery-cards) 渲染器，缺位时自动回退 markdown）。

---

## 功能说明

**✈️ 机票：比价 · 状态 · 核验 · 推荐**
- 机票比价：免费缓存参考价 + 付费精确校准（飞常准，逐次确认，永不自动扣费）
- 航班实时状态：当日 ±10h 内计划/预计/实际三组时刻 + 延误分钟 + 航站楼/登机口，
  支持 AirLabs × ADS-B 双源交叉核验与批量查询
- 远期班次推荐：航线级班期数据出推荐卡（时刻/机型/经停标注），附官网核验直链，
  出发前 24h 回到实时窗终验

**🚗 地面交通：境内境外一张卡**
- 境内走高德：驾车距离/时长/路况/过路费 + 打车估价；支持「家/公司」等常用地址别名
- 境外走 Google：transit（火车地铁巴士）/driving/walking 全覆盖，门到门不换工具

**🗓️ 景点与行程：知识库 + 可行性校验**
- 景点知识库：中国 10 城 3400+ 景点，含建议游览时长、开闭园、门票
- 行程可行性校验：景点存在性 / 开闭园冲突 / 建议时长 vs 排入时长 / 当日合计超窗，
  只出违规建议、绝不擅自改行程
- 每日行程安排卡：按日分组景点，时段/时长/门票/开放时间一眼可读

**🏨 酒店：检索免费 · 交易谨慎**
- RollingGo 实时可订检索：星级 / 价格 / 距离筛选，PC 预订深链一键直达
- 锁价 → 下单 → 取消全流程在技能层完成：锁价凭证 15-30 分钟防涨价，
  下单与取消均为两步人工确认（取消先查违约金），**服务端不碰资金**

**🧭 门到门时间线**
- ✈️🚄🚗 多段行程拼装为一条时间线；机场抵达底线自动倒推（默认提前 60 分钟，
  可调），并反推前一地面段的最迟出发时刻——"几点必须出门"直接可读

**🌦️ 天气窗口**：逐日预报（≤16 天）/ 气候常态（更远），行程排期自带天气依据

**🃏 富卡片系统（零 token 直出）**
- 14 类卡片全部由服务端组装，Agent 只搬运不排版——格式恒定、不吃上下文
- 错误也有卡：每个失败路径输出空态卡 + 下一步动作，不留死胡同

**🛠️ 管理面板（/admin）**
- API Key 管理（掩码回显）/ 数据源探针测试 / 数据源启停与预算
- 付费源三重闸门：永不自动触发 → 月度预算 → 单次确认
- RollingGo 面板原生 OAuth 授权（token 存服务端，不经第三方）
- 负向缓存查看与清理（坏数据源自动拉黑，可手动解除）

**🔐 安全模型**：MCP 全部请求过 `X-API-Key` 唯一门；管理操作另有 `admin_key`
二层；支持内网直连与公网隧道（HTTPS + 尾斜杠规则）两种接入。

---

## 一、部署服务（任意 Docker 主机）

```bash
git clone https://github.com/vclike/travelfusion.git
cd travelfusion
docker compose up -d --build        # 服务监听 :8900，首次启动自动播种种子数据
```

然后打开管理面板 `http://<主机>:8900/admin`：

- **首次启动为开放模式**（无密码）。请在「服务鉴权」区设置 `admin_key`（面板管理密码）
  与 `mcp_api_key`（MCP 接入密钥），设置后面板与 MCP 均加锁。
- 外网/隧道接入：MCP 地址务必带尾斜杠（`…/mcp/`），避免 307 重定向落到死端口。

## 二、需要注册的 API Key

在管理面板「② API 凭证」区逐行保存。**按必要性分级**——只填第一行即可用境内核心功能：

| 数据源 | 必要性 | 用途 | 注册地址（免费层即可） |
|---|---|---|---|
| **高德 amap** | ⭐ 最低必配 | 境内驾车/步行/打车估价/静态路线图 | [console.amap.com](https://console.amap.com) → 创建「Web 服务」类型 Key |
| **AirLabs** | 推荐 | 航班状态/班期实证（当日 ±10h） | [airlabs.co](https://airlabs.co) |
| Travelpayouts | 可选 | 国际机票参考价 | [travelpayouts.com](https://www.travelpayouts.com) → token |
| Aviationstack | 可选 | 航班状态备用源 | [aviationstack.com](https://aviationstack.com) |
| Google Maps | 可选（境外行程） | 境外地面交通（Routes API v2） | [console.cloud.google.com](https://console.cloud.google.com) |
| 飞常准 variflight | 可选 · 付费 | 国内精确票价校准（¥0.5/次；三重闸门，永不自动触发） | [open.variflight.com](https://open.variflight.com) |
| OpenSky / Open-Meteo | 免内置 | ADS-B 观测 / 天气（无需 key） | — |
| **RollingGo** | 酒店场景必配 | 酒店检索 / 锁价 / 下单 | **不填 key**——见下方「面板 OAuth 授权」 |

## 三、需要安装的插件与 Skill（DSH 侧）

| 组件 | 来源 | 作用 | 安装后动作 |
|---|---|---|---|
| **dsh-delivery-cards** 插件（≥ v2.1.0） | [vclike/dsh-delivery-cards](https://github.com/vclike/dsh-delivery-cards) | 富卡片渲染器（含 plan.days / hotel.select / flight.rec 旅程新卡模板） | 安装后**重建一次 dsh web 工件**；未安装时卡片自动回退 markdown |
| **trip-planner** Skill | 本仓库 `release/travelfusion-dsh/skills/trip-planner/` | 规划主技能：交通/航班/行程 SOP + 展示规范 | 复制到 DSH skills 目录即热生效 |
| **rollinggo-hotel-booking** Skill | 本仓库 `release/travelfusion-dsh/skills/rollinggo-hotel-booking/` | 酒店锁价/下单（两步人工确认，资金闸门在技能层） | 同上 |

## 四、MCP 接入（DSH 配置）

```
URL:    http://<主机>:8900/mcp/        # 公网隧道场景用 https 且带尾斜杠
Header: X-API-Key: <面板设置的 mcp_api_key>
```

## 五、RollingGo OAuth 授权（酒店检索前置）

管理面板「② API 凭证」区顶部 → **RollingGo 账号 → 发起授权** → 在打开的页面完成
RollingGo 登录授权 → 面板自动检测变「已登录」。token 保存在服务端（`data/` 卷），
不经过任何第三方；过期后在面板重新发起即可。

## 六、能力总览

| 场景 | 工具 | 卡片 |
|---|---|---|
| 机票比价 / 精确票价（付费闸门） | `flight_price` | price.select / price.single |
| 航班实时状态 / 批量核验 | `flight_status` / `flight_status_batch` | status |
| 远期班次推荐 + 官网核验按钮 | `flight_rec` | flight.rec |
| 境内/境外驾车 · 打车估价 · 沿途景点 | `route_ground` | route.cn / route.intl |
| 景点检索 · 行程可行性校验 · 每日安排 | `attraction_search` / `plan_validate` | validate + plan.days |
| 酒店实时检索（含归因配置） | `hotel_search` | hotel.select |
| 门到门时间线（锚点反推抵达底线） | `itinerary_plan` | itinerary |
| 天气窗口 / 全程推荐 / 额度审计 | `weather_context` / `trip_recommend` / `quota_status` | weather / recommend / quota |

## 七、边界（如实声明）

- 航班实时核验窗 = 当日 ±10h；更远日期推荐卡来自航司班期聚合，**出发前 24h 需终验**
- 国内线免费层无票价源，精确价格走付费校准（逐次确认）
- 景点知识库覆盖中国 10 城（ChinaTravel 快照），门票/开闭园以现场为准
- 酒店锁价/下单在 skill 内两步人工确认完成，服务端只做只读检索
- 部署参数（含可选的推广归因编号）在 `data/keys.yaml` / 管理面板配置，缺省最小化

## License

MIT
