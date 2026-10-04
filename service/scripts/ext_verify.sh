#!/bin/bash
# 外网 MCP 全流程验证（在阿里云=真外网视角跑）
BASE="https://wotu6dcl.gd.ddnsto.com/mcp"
KEY="f6791d6c2bd5d806caa905504ec0e67b"
H_KEY="X-API-Key: $KEY"
H_CT="Content-Type: application/json"
H_ACC="Accept: application/json, text/event-stream"
INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"ext-aliyun","version":"0"}}}'

echo "--- initialize (follow redirect) ---"
RESP=$(curl -s -L -m 25 -D /tmp/hdrs -X POST "$BASE" -H "$H_KEY" -H "$H_CT" -H "$H_ACC" -d "$INIT")
echo "$RESP" | head -c 200; echo
SID=$(grep -i '^mcp-session-id:' /tmp/hdrs | awk '{print $2}' | tr -d '\r')
echo "session: ${SID:0:16}..."

if [ -n "$SID" ]; then
  curl -s -m 15 -o /dev/null -X POST "$BASE" -H "$H_KEY" -H "mcp-session-id: $SID" -H "$H_CT" -H "$H_ACC" \
    -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
fi

echo "--- tools/call flight_status CA165 ---"
CALL='{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"flight_status","arguments":{"flight_no":"CA165"}}}'
RESP2=$(curl -s -L -m 30 -X POST "$BASE" ${SID:+-H "mcp-session-id: $SID"} -H "$H_KEY" -H "$H_CT" -H "$H_ACC" -d "$CALL")
echo "$RESP2" | head -c 400; echo

echo "--- tools/call route_ground 东京→大阪 ---"
CALL2='{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"route_ground","arguments":{"origin":"大阪","destination":"东京","mode":"driving"}}}'
RESP3=$(curl -s -L -m 30 -X POST "$BASE" ${SID:+-H "mcp-session-id: $SID"} -H "$H_KEY" -H "$H_CT" -H "$H_ACC" -d "$CALL2")
echo "$RESP3" | head -c 300; echo
