#!/bin/bash
# Quick test of deployed server - requires API key as argument

if [ -z "$1" ]; then
    echo "Usage: ./quick_test.sh YOUR_API_KEY"
    exit 1
fi

API_KEY="$1"
BASE_URL="https://lionfish-app-evmjk.ondigitalocean.app"

echo "============================================================"
echo "Testing Deployed Instantly MCP Server"
echo "============================================================"
echo ""

# Test: Get server info
echo "📊 Fetching server info..."
echo ""

curl -s -X POST "$BASE_URL/mcp/$API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_server_info",
      "arguments": {}
    },
    "id": 1
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    result = data.get('result', {})
    
    # Parse if result is a JSON string
    if isinstance(result, str):
        result = json.loads(result)
    
    print('Server:', result.get('server', 'N/A'))
    print('Version:', result.get('version', 'N/A'))
    print('Total Tools:', result.get('total_tools', 'N/A'))
    print('')
    print('Tool Counts by Category:')
    for cat, count in result.get('tool_counts', {}).items():
        print(f'  - {cat}: {count}')
    print('')
    
    total = result.get('total_tools', 0)
    if total == 47:
        print('✅ SUCCESS: All 47 tools are registered!')
    elif total in [37, 38, 44]:
        print(f'⚠️  WARNING: Only {total} tools (expected 47)')
        print('   Deployment may not have updated yet.')
    else:
        print(f'❌ Found {total} tools (expected 47)')
except Exception as e:
    print(f'Error parsing response: {e}')
    print('Raw response:', file=sys.stderr)
    sys.stdin.seek(0)
    print(sys.stdin.read(), file=sys.stderr)
"

echo ""
echo "============================================================"

