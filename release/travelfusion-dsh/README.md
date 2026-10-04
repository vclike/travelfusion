# travelfusion — 为 DeepSeek Harness (DSH) 定制的门到门出行聚合服务

> **本插件/服务是为 DSH 定制的**：MCP 工具协议对接 DSH 的 MCP 客户端，富卡片系统
> 依赖 DSH 插件 `dsh-delivery-cards` 的渲染器（`.tf.json` 协议 + turnTail 通道），
> 管理面板与面板原生 OAuth 面向 DSH Web 使用方式设计。脱离 DSH 也能当普通 MCP
> 服务用（卡片降级为 markdown 文本），但完整体验以 DSH 为准。

**17 个 MCP 工具 · 8 个数据源 · 14 类卡片**：机票比价/航班状态/双源核验/境内境外
地面交通/景点知识库/行程校验/酒店检索（RollingGo）/天气窗口/全程时间线/额度审计。
免费额度内可用；付费源（飞常准/Google Maps）有永不自动触发的三重闸门。

## 快速开始（三步）

1. **部署服务**：任意 Docker 主机
   ```bash
   git clone <本仓库> && cd dsh-flight-aggregator
   docker-compose up -d --build     # 服务 :8900，首次启动自动播种种子数据
   ```
2. **填 API key**：浏览器打开 `http://<主机>:8900/admin`（首次为开放模式，设置
   admin_key 后加锁）→ ② API 凭证区逐行保存。最低可用 = 高德 Key；推荐再加
   AirLabs（航班核验）与 Travelpayouts（国际票价）。RollingGo 账号在同区点
   「发起授权」完成 OAuth（酒店检索必需）。
3. **接入 DSH**：DSH MCP 配置添加
   `http://<主机>:8900/mcp`，Header `X-API-Key: <面板里设置的 mcp_api_key>`；
   安装 `skills/trip-planner` 与 `skills/rollinggo-hotel-booking` 两个 skill；
   安装 `dsh-delivery-cards` 插件（v2.1+，含旅程三新卡模板）后**重建一次 web 工件**。

之后在 DSH 里说"两周后从家去杭州玩四天"即可获得：航班班期核验 → 以线定房 →
酒店/航班推荐卡 → 每日行程卡 → 门到门时间线的全链路。

## API Key 申请矩阵

| 数据源 | 必要性 | 用途 | 申请处 |
|---|---|---|---|
| 高德 amap | **最低必配** | 境内驾车/打车/静态地图 | lbs.amap.com（Web服务 Key） |
| AirLabs | 推荐 | 航班状态/班期实证 | airlabs.co 免费层 |
| Travelpayouts | 可选 | 国际机票参考价 | travelpayouts.com token |
| Aviationstack | 可选 | 航班状态备用源 | aviationstack.com 免费层 |
| Google Maps | 可选 | 境外地面交通 | console.cloud.google.com |
| 飞常准 variflight | 可选·付费 | 国内精确票价校准（¥0.5/次，永不自动触发） | variflight.com 开放平台 |
| OpenSky/Meteo | 免·无需 key | ADS-B 观测 / 天气 | 内置 |
| RollingGo | 酒店场景必配 | 酒店检索/锁价/下单（面板 OAuth，不落 key） | rollinggo.cn |

## 推广归因（可选，默认关闭）

酒店预订链接可携带你自己的 RollingGo 推广编号：在 `data/keys.yaml` 设
`rgh_promo_code: '<你的编号>'`（或管理面板改），所有 bookingUrl 的
`utm_source` 将统一为你的编号——他人经你的部署产出的链接下单，佣金归你。
**缺省不配置时链接原样输出，不做任何归因。**

## 边界（如实声明）

- 航班实时核验窗 = 当日 ±10h；更远日期的推荐卡来自航司班期聚合，出发前 24h 需终验
- 国内线免费层无票价源；精确价格走付费校准（需逐次确认）
- 景点知识库覆盖中国 10 城（ChinaTravel 快照），门票/开闭园以现场为准
- 酒店锁价/下单在 rollinggo-hotel-booking skill 内完成（两步人工确认），服务端只做只读检索
- 卡片完整视觉需 `dsh-delivery-cards` v2.1+ 并重建 web 工件；缺位时自动回退 markdown

## 发布物清单

- 本仓库根：服务源码（`app/`、`docker-compose.yml`、`Dockerfile`、`data/` 种子）
- `release/travelfusion-dsh/skills/`：trip-planner + rollinggo-hotel-booking
  （推广码已替换为 `<YOUR_PROMO_CODE>` 占位，配置你自己的编号即可启用）
- `release/travelfusion-dsh/plugins/dsh-delivery-cards-README.md`：渲染器插件说明
  （源码仓库：vclike/dsh-delivery-cards，v2.1 起含 plan.days / hotel.select / flight.rec 模板）
