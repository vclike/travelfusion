# travelfusion 服务

门到门交通规划聚合服务：航班（国内外）+ 火车 + 地面交通。
免费额度池化治理、多源交叉复核、付费仅做确定性校准。

设计文档：`../docs/`（01–10）。工具契约：`../docs/09-tool-contracts.md`。
Canonical schema：`../docs/10-canonical-schema.md`。

## 快速开始（开发）

```bash
cd service
python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ \
  fastapi "uvicorn[standard]" "mcp>=1.2,<2" pyyaml httpx pytest
python -m pytest tests -q          # 31 passed
TF_DATA_DIR=./_rundata python -m uvicorn app.main:app --port 8899
# health:  curl http://127.0.0.1:8899/health
# MCP:     POST http://127.0.0.1:8899/mcp   （streamable-http）
```

⚠️ 依赖钉 `mcp>=1.2,<2`：SDK 2.x 把 FastMCP 更名为 MCPServer，导入路径不兼容。

## 部署（iStoreOS 软路由 · Docker）

```bash
docker build -t travelfusion:0.1.0 .
docker compose up -d              # 挂卷 ./data 持久化；端口 8899
```

- DSH 侧接入：MCP 地址 `http://<路由器IP>:8899/mcp`
- key 管理：Phase 1 面板；当前可直接编辑 `data/settings.yaml` 与各 provider 的 key 字段
- 数据即资产：`data/`（SQLite 账本、KB、基线）随卷持久化，升级镜像不丢

## 工具（9）

| 工具 | 状态 |
|---|---|
| quota_status | ✅ 五源账本分桶审计 |
| provider_admin | ✅ 热插拔管理（enable/disable/quota/reorder/budget） |
| airline_kb | ✅ 航司知识库（hints/别名/修订台账） |
| resolve_place | ✅ 城市表（31 城） |
| flight_status | ✅ AirLabs 双端点合并（schedules+flights）+ Aviationstack 备用 |
| flight_price | ✅ Travelpayouts 缓存价（国际，CNY） |
| flight_verify | ✅ AirLabs×OpenSky 双源交叉核验（一致性判定+置信分级） |
| route_ground | ✅ 高德驾车（官方打车价/过路费/限行规避/EV 充电次数） |
| weather_context | ⏳ Phase 2 后段（Open-Meteo） |

真机验证（2026-09-29）：TG615 延误 367min 双源核验高置信；MOW→BKK ¥3,606 缓存价；
成都→乐山 136.8km/93min/过路费¥52/官方打车¥445。

## 目录

```
app/
  main.py          FastAPI + MCP 挂载 + 种子播种
  mcp_server.py    9 工具定义
  config.py        治理参数/车辆画像（env > settings.yaml > 默认）
  core/            registry(每请求重读) ledger(惰性周期重置) negmark(1h→24h升级冷却)
                   eligibility(距离带资格) canon(统一信封+错误码7种) airline_kb(KB存储+修订台账)
  providers/_template/   新源接入模板（五步指南）
  data/            种子：manifests.json / norms.yaml / airlines_kb.yaml / city_coords.yaml
tests/             31 用例：账本周期重置/资格带/别名归一/负标升级/manifest 校验
```

## 数据与知识（运行时全部可改，下一请求生效）

- `data/manifests.json` —— provider 策略（配额/降级序/计费模式）
- `data/norms.yaml` —— 行业基线（航司 hints 只记与基线的偏离）
- `data/airlines_kb.yaml` —— 航司知识库（hints 短句 + aliases + append-only 修订）
