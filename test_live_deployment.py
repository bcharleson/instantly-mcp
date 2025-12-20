#!/usr/bin/env python3
"""
Test the live deployed MCP server to verify all 44 tools are registered.
"""

import os
import sys
import json
import requests

BASE_URL = "https://lionfish-app-evmjk.ondigitalocean.app"

def test_server_info(api_key: str):
    """Test get_server_info tool to verify tool count."""
    
    print("=" * 60)
    print("Testing Deployed Instantly MCP Server")
    print("=" * 60)
    print()
    print(f"🌐 Server URL: {BASE_URL}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print()
    
    # Test 1: Health check
    print("📊 Test 1: Health Check")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        health = response.json()
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"Server: {health.get('server', 'unknown')}")
        print(f"Version: {health.get('version', 'unknown')}")
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print()
    
    # Test 2: Get server info
    print("📊 Test 2: Get Server Info (Tool Count)")
    print("-" * 60)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_server_info",
            "arguments": {}
        },
        "id": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/mcp/{api_key}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        data = response.json()
        
        # Handle both direct result and JSON string result
        result = data.get("result", {})
        if isinstance(result, str):
            result = json.loads(result)
        
        print(f"Server: {result.get('server', 'N/A')}")
        print(f"Version: {result.get('version', 'N/A')}")
        print(f"Total Tools: {result.get('total_tools', 'N/A')}")
        print()
        
        print("Tool Counts by Category:")
        tool_counts = result.get('tool_counts', {})
        for category, count in tool_counts.items():
            print(f"  - {category}: {count}")
        print()
        
        # Verify
        total_tools = result.get('total_tools', 0)
        version = result.get('version', 'unknown')
        
        print("=" * 60)
        print("📈 Results:")
        print(f"  - Server Version: {version}")
        print(f"  - Total Tools: {total_tools}")
        print()
        
        if total_tools == 44:
            print("✅ SUCCESS: All 44 tools are registered!")
            print("✅ Deployment is up to date!")
            return 0
        elif total_tools in [37, 38]:
            print(f"⚠️  WARNING: Only {total_tools} tools found (expected 44)")
            print("   This means the deployment hasn't picked up the latest changes yet.")
            print()
            print("   Possible reasons:")
            print("   1. DigitalOcean is still deploying")
            print("   2. Auto-deploy is not enabled for feature/supersearch branch")
            print("   3. Manual deployment trigger needed")
            print()
            print("   Next steps:")
            print("   - Check DigitalOcean dashboard for deployment status")
            print("   - Manually trigger deployment if needed")
            return 1
        else:
            print(f"❌ UNEXPECTED: Found {total_tools} tools (expected 44)")
            return 1
            
    except Exception as e:
        print(f"❌ Error calling get_server_info: {e}")
        print()
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return 1
    
    print("=" * 60)


def main():
    # Get API key from environment or command line
    api_key = os.environ.get("INSTANTLY_API_KEY")
    
    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("❌ Error: API key required")
        print()
        print("Usage:")
        print("  export INSTANTLY_API_KEY='your-key-here' && python3 test_live_deployment.py")
        print("  OR")
        print("  python3 test_live_deployment.py YOUR_API_KEY")
        return 1
    
    return test_server_info(api_key)


if __name__ == "__main__":
    sys.exit(main())

