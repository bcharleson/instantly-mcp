#!/bin/bash
# Test the deployed MCP server

API_KEY="${INSTANTLY_API_KEY}"
BASE_URL="https://lionfish-app-evmjk.ondigitalocean.app"

if [ -z "$API_KEY" ]; then
    echo "❌ Error: INSTANTLY_API_KEY environment variable not set"
    echo "Usage: export INSTANTLY_API_KEY='your-key-here' && ./test_deployment.sh"
    exit 1
fi

echo "============================================================"
echo "Testing Deployed Instantly MCP Server"
echo "============================================================"
echo ""
echo "🌐 Server URL: $BASE_URL"
echo "🔑 API Key: ${API_KEY:0:10}..."
echo ""

# Test 1: Health check
echo "📊 Test 1: Health Check"
echo "---"
HEALTH=$(curl -s "$BASE_URL/health")
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
echo ""

# Test 2: Get server info via MCP
echo "📊 Test 2: Get Server Info (Tool Count)"
echo "---"
SERVER_INFO=$(curl -s -X POST "$BASE_URL/mcp/$API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_server_info",
      "arguments": {}
    },
    "id": 1
  }')

echo "$SERVER_INFO" | python3 -m json.tool 2>/dev/null || echo "$SERVER_INFO"
echo ""

# Extract tool count
TOOL_COUNT=$(echo "$SERVER_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', {}).get('total_tools', 'N/A'))" 2>/dev/null)
VERSION=$(echo "$SERVER_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', {}).get('version', 'N/A'))" 2>/dev/null)

echo "============================================================"
echo "📈 Results:"
echo "  - Server Version: $VERSION"
echo "  - Total Tools: $TOOL_COUNT"
echo ""

if [ "$TOOL_COUNT" = "47" ]; then
    echo "✅ SUCCESS: All 47 tools are registered!"
elif [ "$TOOL_COUNT" = "38" ] || [ "$TOOL_COUNT" = "37" ] || [ "$TOOL_COUNT" = "44" ]; then
    echo "⚠️  WARNING: Only $TOOL_COUNT tools found (expected 47)"
    echo "   This means the deployment hasn't picked up the latest changes yet."
    echo "   The server might still be deploying or needs a manual restart."
else
    echo "❌ UNEXPECTED: Found $TOOL_COUNT tools (expected 47)"
fi
echo "============================================================"

