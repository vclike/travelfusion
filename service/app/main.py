"""FastAPI 入口：/health + MCP streamable-http 挂载于 /mcp。

启动时把种子数据（manifests/norms/kb/city_coords）播种到运行时数据目录——
运行时文件才是被读写的一方（iStoreOS 挂卷持久化）。
"""
from __future__ import annotations

import asyncio
import logging

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from app import __version__
from app.config import SEED_DATA_DIR, data_dir
from app.core import collector
from app.core import cards as tf_cards
from app.core import cardview
from app.core.keys import auth_config
from app.mcp_server import mcp as _mcp


def _mcp_auth_middleware(app: "FastAPI"):
    """MCP 端点 API key 鉴权：X-API-Key 头或 ?key= 查询参数。/health 保持开放。"""
    from fastapi.responses import JSONResponse

    async def middleware(request, call_next):
        path = request.url.path
        if path == "/mcp" or path.startswith("/mcp/"):
            expected = auth_config(data_dir()).get("mcp_api_key")
            if expected:
                provided = (request.headers.get("x-api-key")
                            or request.query_params.get("key"))
                if provided != expected:
                    return JSONResponse(
                        {"error": "unauthorized", "hint": "X-API-Key 头缺失或不匹配"},
                        status_code=401)
        return await call_next(request)

    return middleware

SEEDS = ("manifests.json", "norms.yaml", "airlines_kb.yaml", "city_coords.yaml")


def _seed_runtime() -> list[str]:
    d = data_dir()
    copied = []
    for name in SEEDS:
        src, dst = SEED_DATA_DIR / name, d / name
        if src.exists() and not dst.exists():
            dst.write_bytes(src.read_bytes())
            copied.append(name)
    return copied


@asynccontextmanager
async def lifespan(app: FastAPI):
    copied = _seed_runtime()
    app.state.seeded = copied
    # 挂载的 streamable_http_app 自身 lifespan 不会被宿主触发——
    # 必须在宿主 lifespan 里显式初始化会话管理器 task group
    async with _mcp.session_manager.run():
        baseline_task = asyncio.create_task(_baseline_loop())
        china_task = asyncio.create_task(_china_loop())
        try:
            yield
        finally:
            baseline_task.cancel()
            china_task.cancel()
            try:
                await baseline_task
            except (asyncio.CancelledError, Exception):
                pass
            try:
                await china_task
            except (asyncio.CancelledError, Exception):
                pass


async def _baseline_loop():
    """7×24 基线采集：按 settings.yaml 周期跑 watchlist（软路由核心价值）。"""
    while True:
        try:
            dd = data_dir()
            interval_h = collector.interval_hours(dd)
            summary = await asyncio.to_thread(collector.collect_once, dd, None)
            logging.getLogger("travelfusion.baseline").info(
                "baseline collect: %s", summary)
        except Exception as e:                       # noqa: BLE001 采集失败不致命
            logging.getLogger("travelfusion.baseline").warning(
                "baseline collect failed: %s", e)
        # 2026-10-02 修复：等待由本循环自己负责（此前 sleep 误挂 _china_loop → 采集热循环）
        await asyncio.sleep(max(1.0, interval_h) * 3600)


async def _china_loop():
    """ChinaTravel 知识库自动更新：启动即检查，缺失/超龄（>30 天）则拉新版。"""
    from app.core.chinatravel import get_store

    store = get_store(data_dir())
    while True:
        try:
            if store.needs_update():
                meta = await asyncio.to_thread(store.update)
                logging.getLogger("travelfusion.chinatravel").info(
                    "chinatravel updated: %s rows", meta.get("rows"))
        except Exception as e:                       # noqa: BLE001 更新失败不致命
            logging.getLogger("travelfusion.chinatravel").warning(
                "chinatravel update failed: %s", e)
        await asyncio.sleep(86400)                   # 每日复查一次
        # 2026-10-02 修复：移除误挂在本循环的采集间隔 sleep（原为双重等待）


app = FastAPI(title="travelfusion", version=__version__, lifespan=lifespan)


@app.middleware("http")
async def _mcp_slash_rewrite(request, call_next):
    """/mcp → /mcp/ 原地改写（不发 307）。挂载产生的尾斜杠重定向会丢会话头——
    DSH 的 MCP 客户端不跟随 POST 重定向，实测报"会话失效"。"""
    if request.url.path == "/mcp":
        request.scope["path"] = "/mcp/"
    return await call_next(request)


app.middleware("http")(_mcp_auth_middleware(app))


# 卡片自取通道：浏览器端 TfCard 按 <id>.tf.json 文件名里的 id 拉取（跨域来自
# DSH 网页源，放开 CORS；id 本身是 12 位能力令牌，内容均为公开交通数据，无鉴权）
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["GET"], allow_headers=[])


@app.get("/cards/recent")
def get_recent_cards(since: float = 0) -> list[dict]:
    """时间窗自取通道：渲染器挂载时拉最近暂存的卡片（since=epoch 秒）。"""
    return tf_cards.recent_cards(since)


@app.get("/cards/{cid}/view", response_class=HTMLResponse)
def view_card(cid: str):
    """卡片人读详情页（侧栏点击打开；服务端排版，替代原始 JSON）。"""
    card = tf_cards.get_card(cid)
    if not card:
        raise HTTPException(status_code=404, detail="card expired or unknown")
    return HTMLResponse(cardview.render_html(card))


@app.get("/cards/{cid}/text", response_class=PlainTextResponse)
def card_text(cid: str) -> str:
    """卡片纯文本分享摘要（卡片"复制文本"按钮取用处）。"""
    card = tf_cards.get_card(cid)
    if not card:
        raise HTTPException(status_code=404, detail="card expired or unknown")
    return cardview.render_text(card)


@app.get("/cards/{cid}")
def get_staged_card(cid: str) -> dict:
    card = tf_cards.get_card(cid)
    if not card:
        raise HTTPException(status_code=404, detail="card expired or unknown")
    return card


@app.get("/health")
def health() -> dict:
    # 2026-10-04 修复（B4）：工具数不再硬编码，运行时从 MCP 注册表动态取
    try:
        _tm = getattr(_mcp, "_tool_manager", None)
        _n_tools = len(_tm.list_tools()) if _tm is not None else 0
    except Exception:
        _n_tools = 0
    return {"ok": True, "version": __version__,
            "data_dir": str(data_dir()),
            "tools": f"mcp://{_n_tools}",
            "seeded_this_boot": getattr(app.state, "seeded", [])}


app.mount("/mcp", _mcp.streamable_http_app())
