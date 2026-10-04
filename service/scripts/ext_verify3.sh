#!/bin/bash
# 外网 MCP 全流程 v3：body 由脚本 heredoc 生成，无外部依赖
BASE="http://127.0.0.1:8900/mcp/"
KEY="f6791d6c2bd5d806caa905504ec0e67b"

cat > /tmp/e_init.json <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"ext-aliyun","version":"0"}}}
EOF
cat > /tmp/e_call.json <<'EOF'
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"flight_status","arguments":{"flight_no":"CA165"}}}
EOF
echo "init bytes: $(wc -c < /tmp/e_init.json)"

curl -s -m 25 -D /tmp/e_hdrs -o /tmp/e_resp.txt -X POST "$BASE" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  --data @/tmp/e_init.json
SID=$(grep -i '^mcp-session-id:' /tmp/e_hdrs | awk '{print $2}' | tr -d '\r')
echo "session: ${SID:0:16}... resp: $(head -c 120 /tmp/e_resp.txt)"

curl -s -m 15 -o /dev/null -X POST "$BASE" \
  -H "X-API-Key: $KEY" -H "mcp-session-id: $SID" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

echo "--- tools/call flight_status CA165 (external) ---"
curl -s -m 30 -X POST "$BASE" \
  -H "X-API-Key: $KEY" -H "mcp-session-id: $SID" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  --data @/tmp/e_call.json > /tmp/e_call_resp.txt
echo "resp bytes: $(wc -c < /tmp/e_call_resp.txt)"
head -c 400 /tmp/e_call_resp.txt
echo
