#!/usr/bin/env python3
"""
Verify that all 44 tools are properly registered in the Instantly MCP server.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from instantly_mcp.tools import get_all_tools, get_available_categories

def main():
    print("=" * 60)
    print("Instantly MCP Tool Count Verification")
    print("=" * 60)
    
    # Get all tools
    all_tools = get_all_tools()
    
    print(f"\n✅ Total tools loaded: {len(all_tools)}")
    print(f"📦 Available categories: {', '.join(get_available_categories())}")
    
    # Count by category
    from instantly_mcp.tools.accounts import ACCOUNT_TOOLS
    from instantly_mcp.tools.campaigns import CAMPAIGN_TOOLS
    from instantly_mcp.tools.leads import LEAD_TOOLS
    from instantly_mcp.tools.emails import EMAIL_TOOLS
    from instantly_mcp.tools.analytics import ANALYTICS_TOOLS
    from instantly_mcp.tools.background_jobs import BACKGROUND_JOB_TOOLS
    from instantly_mcp.tools.supersearch import SUPERSEARCH_TOOLS
    
    print("\n📊 Tools by category:")
    print(f"  - Accounts: {len(ACCOUNT_TOOLS)}")
    print(f"  - Campaigns: {len(CAMPAIGN_TOOLS)}")
    print(f"  - Leads: {len(LEAD_TOOLS)}")
    print(f"  - Emails: {len(EMAIL_TOOLS)}")
    print(f"  - Analytics: {len(ANALYTICS_TOOLS)}")
    print(f"  - Background Jobs: {len(BACKGROUND_JOB_TOOLS)}")
    print(f"  - SuperSearch: {len(SUPERSEARCH_TOOLS)}")
    
    total = (len(ACCOUNT_TOOLS) + len(CAMPAIGN_TOOLS) + len(LEAD_TOOLS) + 
             len(EMAIL_TOOLS) + len(ANALYTICS_TOOLS) + len(BACKGROUND_JOB_TOOLS) + 
             len(SUPERSEARCH_TOOLS))
    
    print(f"\n  SUBTOTAL: {total}")
    print(f"  + get_server_info: 1")
    print(f"  = TOTAL: {total + 1}")
    
    # List all tool names
    print("\n📝 All tool names:")
    for i, tool in enumerate(all_tools, 1):
        print(f"  {i:2d}. {tool.__name__}")
    
    # Verify expected count
    expected = 44
    actual = len(all_tools) + 1  # +1 for get_server_info which is registered separately
    
    print("\n" + "=" * 60)
    if actual == expected:
        print(f"✅ SUCCESS: All {expected} tools are registered!")
    else:
        print(f"❌ MISMATCH: Expected {expected} tools, but found {actual}")
        print(f"   Difference: {actual - expected}")
    print("=" * 60)
    
    return 0 if actual == expected else 1

if __name__ == "__main__":
    sys.exit(main())

