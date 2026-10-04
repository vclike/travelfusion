# travelfusion — 部署到 iStoreOS（OpenWrt）Docker
# 在路由器上构建:  docker build -t travelfusion:0.2.0 .
# 数据卷 ./data 持久化（SQLite 账本 / manifests / kb / keys）
# 注意：依赖直装（pyproject 未配 build backend，勿 pip install .）

FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
    fastapi "uvicorn[standard]" "mcp>=1.2,<2" pyyaml httpx pyarrow

COPY app ./app

ENV TF_DATA_DIR=/app/data
VOLUME ["/app/data"]
EXPOSE 8900
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8900"]
