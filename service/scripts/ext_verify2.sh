#!/bin/bash
# 外网 MCP 全流程（/mcp/ 带斜杠零重定向 + body 文件化）
BASE="https://wotu6dcl.gd.ddnsto.com/mcp/"
KEY="f6791d6c2bd5d806caa905504ec0e67b"

SID=$(curl -s -m 25 -D - -o /tmp/init_resp.txt -X POST "$BASE" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  --data @/tmp/ext_init.json | grep -i '^mcp-session-id:' | awk '{print $2}' | tr -d '\r')
echo "session: ${SID:0:16}... init-resp: $(head -c 80 /tmp/init_resp.txt)"

curl -s -m 15 -o /dev/null -X POST "$BASE" \
  -H "X-API-Key: $KEY" -H "mcp-session-id: $SID" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

echo "--- tools/call flight_status CA165 (external) ---"
curl -s -m 30 -X POST "$BASE" \
  -H "X-API-Key: $KEY" -H "mcp-session-id: $SID" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  --data @/tmp/ext_call.json | head -c 400
echo
