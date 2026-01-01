#!/bin/bash
# Count all tools in the Instantly MCP server

echo "============================================================"
echo "Instantly MCP Tool Count Verification"
echo "============================================================"
echo ""

echo "📊 Counting tools by category:"
echo ""

# Count tools in each file
accounts=$(grep -c "^async def " src/instantly_mcp/tools/accounts.py)
campaigns=$(grep -c "^async def " src/instantly_mcp/tools/campaigns.py)
leads=$(grep -c "^async def " src/instantly_mcp/tools/leads.py)
emails=$(grep -c "^async def " src/instantly_mcp/tools/emails.py)
analytics=$(grep -c "^async def " src/instantly_mcp/tools/analytics.py)
background_jobs=$(grep -c "^async def " src/instantly_mcp/tools/background_jobs.py)
supersearch=$(grep -c "^async def " src/instantly_mcp/tools/supersearch.py)

echo "  - Accounts: $accounts"
echo "  - Campaigns: $campaigns"
echo "  - Leads: $leads"
echo "  - Emails: $emails"
echo "  - Analytics: $analytics"
echo "  - Background Jobs: $background_jobs"
echo "  - SuperSearch: $supersearch"
echo ""

subtotal=$((accounts + campaigns + leads + emails + analytics + background_jobs + supersearch))
total=$((subtotal + 1))  # +1 for get_server_info

echo "  SUBTOTAL: $subtotal"
echo "  + get_server_info: 1"
echo "  = TOTAL: $total"
echo ""

echo "============================================================"
if [ $total -eq 47 ]; then
    echo "✅ SUCCESS: All 47 tools are registered!"
else
    echo "❌ MISMATCH: Expected 47 tools, but found $total"
    echo "   Difference: $((total - 47))"
fi
echo "============================================================"

