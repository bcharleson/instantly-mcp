"""
Instantly MCP Server - Main Server

A lightweight, robust FastMCP server for the Instantly.ai V2 API.

Features:
- 38 tools across 6 categories (accounts, campaigns, leads, emails, analytics, background_jobs)
- Dual transport support (HTTP for remote, stdio for local)
- Lazy loading via TOOL_CATEGORIES environment variable
- Per-request API key support for multi-tenant deployments
- MCP 2025-06-18 annotations (readOnlyHint, destructiveHint, etc.)

Usage:
  # HTTP mode (remote deployment)
  fastmcp run src/instantly_mcp/server.py --transport http --port 8000

  # stdio mode (local Claude Desktop)
  fastmcp run src/instantly_mcp/server.py

  # With lazy loading (reduce context window)
  TOOL_CATEGORIES=accounts,campaigns fastmcp run src/instantly_mcp/server.py
"""

import os
import sys
from typing import Any

from fastmcp import FastMCP
from fastmcp.server import Context

from .client import get_client, set_api_key
from .tools import get_all_tools, get_requested_categories, is_lazy_loading_enabled

# Server metadata
SERVER_NAME = "instantly-mcp"
SERVER_VERSION = "1.0.0"
SERVER_INSTRUCTIONS = """
Instantly.ai V2 API MCP Server - Email automation and campaign management.

Categories: accounts, campaigns, leads, emails, analytics, background_jobs
Total tools: 38 (configurable via TOOL_CATEGORIES env var)

Authentication methods for HTTP deployments:
1. URL path: /mcp/YOUR_API_KEY
2. Header: Authorization: YOUR_API_KEY (Bearer prefix optional)
3. Header: x-instantly-api-key: YOUR_API_KEY
"""

# Initialize FastMCP server
mcp = FastMCP(
    name=SERVER_NAME,
    version=SERVER_VERSION,
    instructions=SERVER_INSTRUCTIONS,
)


def register_tools():
    """Register all tools with MCP annotations."""
    
    # Import tool modules dynamically based on categories
    tools = get_all_tools()
    
    # Tool annotations mapping
    # readOnlyHint: Tool only reads data
    # destructiveHint: Tool modifies/deletes data
    # confirmationRequiredHint: Requires user confirmation
    TOOL_ANNOTATIONS = {
        # Account tools
        "list_accounts": {"readOnlyHint": True},
        "get_account": {"readOnlyHint": True},
        "create_account": {"destructiveHint": False},
        "update_account": {"destructiveHint": False},
        "manage_account_state": {"destructiveHint": False},
        "delete_account": {"destructiveHint": True, "confirmationRequiredHint": True},

        # Campaign tools
        "create_campaign": {"destructiveHint": False},
        "list_campaigns": {"readOnlyHint": True},
        "get_campaign": {"readOnlyHint": True},
        "update_campaign": {"destructiveHint": False},
        "activate_campaign": {"destructiveHint": False},
        "pause_campaign": {"destructiveHint": False},
        "delete_campaign": {"destructiveHint": True, "confirmationRequiredHint": True},
        "search_campaigns_by_contact": {"readOnlyHint": True},

        # Lead tools
        "list_leads": {"readOnlyHint": True},
        "get_lead": {"readOnlyHint": True},
        "create_lead": {"destructiveHint": False},
        "update_lead": {"destructiveHint": False},
        "list_lead_lists": {"readOnlyHint": True},
        "create_lead_list": {"destructiveHint": False},
        "update_lead_list": {"destructiveHint": False},
        "get_verification_stats_for_lead_list": {"readOnlyHint": True},
        "add_leads_to_campaign_or_list_bulk": {"destructiveHint": False},
        "delete_lead": {"destructiveHint": True, "confirmationRequiredHint": True},
        "delete_lead_list": {"destructiveHint": True, "confirmationRequiredHint": True},
        "move_leads_to_campaign_or_list": {"destructiveHint": False},

        # Email tools
        "list_emails": {"readOnlyHint": True},
        "get_email": {"readOnlyHint": True},
        "reply_to_email": {"destructiveHint": True, "confirmationRequiredHint": True},
        "count_unread_emails": {"readOnlyHint": True},
        "verify_email": {"readOnlyHint": True},
        "mark_thread_as_read": {"destructiveHint": False},

        # Analytics tools
        "get_campaign_analytics": {"readOnlyHint": True},
        "get_daily_campaign_analytics": {"readOnlyHint": True},
        "get_warmup_analytics": {"readOnlyHint": True},

        # Background job tools
        "list_background_jobs": {"readOnlyHint": True},
        "get_background_job": {"readOnlyHint": True},
    }
    
    for tool_func in tools:
        tool_name = tool_func.__name__
        annotations = TOOL_ANNOTATIONS.get(tool_name, {})
        
        # Register tool with FastMCP
        mcp.tool(
            name=tool_name,
            annotations=annotations,
        )(tool_func)
    
    print(f"[Instantly MCP] ✅ Registered {len(tools)} tools", file=sys.stderr)
    if is_lazy_loading_enabled():
        categories = get_requested_categories()
        print(f"[Instantly MCP] 📦 Categories: {', '.join(categories)}", file=sys.stderr)


# Register tools at import time
register_tools()


@mcp.tool(
    name="get_server_info",
    annotations={"readOnlyHint": True},
)
async def get_server_info() -> str:
    """
    Get Instantly MCP server information.
    
    Returns server version, loaded categories, and configuration status.
    Useful for debugging and verifying server setup.
    """
    import json
    
    client = get_client()
    categories = get_requested_categories()
    
    info = {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "api_key_configured": client.has_api_key,
        "lazy_loading_enabled": is_lazy_loading_enabled(),
        "loaded_categories": categories,
        "tool_counts": {
            "accounts": 6 if "accounts" in categories else 0,
            "campaigns": 8 if "campaigns" in categories else 0,  # +2: delete_campaign, search_campaigns_by_contact
            "leads": 12 if "leads" in categories else 0,  # +1: delete_lead_list
            "emails": 6 if "emails" in categories else 0,  # +1: mark_thread_as_read
            "analytics": 3 if "analytics" in categories else 0,
            "background_jobs": 2 if "background_jobs" in categories else 0,
        },
        "total_tools": sum([
            6 if "accounts" in categories else 0,
            8 if "campaigns" in categories else 0,
            12 if "leads" in categories else 0,
            6 if "emails" in categories else 0,
            3 if "analytics" in categories else 0,
            2 if "background_jobs" in categories else 0,
        ]) + 1,  # +1 for get_server_info
        "rate_limit": {
            "remaining": client.rate_limit.remaining,
            "limit": client.rate_limit.limit,
            "reset_at": client.rate_limit.reset_at.isoformat() if client.rate_limit.reset_at else None,
        },
    }
    
    return json.dumps(info, indent=2)


def extract_api_key_from_request(ctx: Context) -> str | None:
    """
    Extract API key from request context for multi-tenant HTTP mode.
    
    Checks headers in order:
    1. x-instantly-api-key
    2. Authorization: Bearer <key>
    """
    if not ctx or not hasattr(ctx, "request"):
        return None
    
    request = ctx.request
    if not request or not hasattr(request, "headers"):
        return None
    
    headers = request.headers
    
    # Check custom header first
    api_key = headers.get("x-instantly-api-key")
    if api_key:
        return api_key
    
    # Check Authorization header
    auth_header = headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:]
    
    return None


def main():
    """Main entry point for the Instantly MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Instantly MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="HTTP host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="HTTP port (default: 8000)",
    )
    parser.add_argument(
        "--api-key",
        help="Instantly API key (overrides INSTANTLY_API_KEY env var)",
    )
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        set_api_key(args.api_key)
    
    # Log startup info
    client = get_client()
    print(f"[Instantly MCP] 🚀 Starting server v{SERVER_VERSION}", file=sys.stderr)
    print(f"[Instantly MCP] 🔑 API key: {'✅ Configured' if client.has_api_key else '❌ Not set (multi-tenant mode)'}", file=sys.stderr)
    print(f"[Instantly MCP] 🚌 Transport: {args.transport}", file=sys.stderr)
    
    if args.transport == "http":
        print(f"[Instantly MCP] 🌐 HTTP endpoints:", file=sys.stderr)
        print(f"[Instantly MCP]    - http://{args.host}:{args.port}/mcp", file=sys.stderr)
        print(f"[Instantly MCP]    - http://{args.host}:{args.port}/mcp/YOUR_API_KEY", file=sys.stderr)
        if not client.has_api_key:
            print(f"[Instantly MCP] ⚠️  Multi-tenant mode: Provide API key via URL or headers", file=sys.stderr)
        
        # Use custom HTTP app with URL-based auth support
        from .http_app import run_http_server
        run_http_server(mcp, host=args.host, port=args.port)
    else:
        if not client.has_api_key:
            print("[Instantly MCP] ❌ API key required for stdio mode", file=sys.stderr)
            print("[Instantly MCP] Set INSTANTLY_API_KEY env var or use --api-key", file=sys.stderr)
            sys.exit(1)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

