# travelfusion — 部署到 iStoreOS（OpenWrt）Docker
# 在路由器上构建:  docker build -t travelfusion:0.3.0 .
# 数据卷 ./data 持久化（SQLite 账本 / manifests / kb / keys）
# 注意：依赖直装（pyproject 未配 build backend，勿 pip install .）

FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
    fastapi "uvicorn[standard]" "mcp>=1.2,<2" pyyaml httpx pyarrow

COPY app ./app

# 2026-10-04 修复：移除 VOLUME ["/app/data"] —— legacy builder 会把 VOLUME
# 声明路径在镜像中的既有内容丢弃，导致烘焙种子（app/data 的
# manifests/norms/kb/city_coords）全部丢失、全新安装首启无数据。
# 持久化由 docker-compose.yml 的 ./data:/app/data bind mount 承担。
ENV TF_DATA_DIR=/app/data
EXPOSE 8900
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8900"]
