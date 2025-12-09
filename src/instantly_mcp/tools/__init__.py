"""
Instantly MCP Server - Tool Implementations

All tool implementations organized by category.
Supports lazy loading via TOOL_CATEGORIES environment variable.
"""

import os
from typing import Callable

# Category mapping for lazy loading
CATEGORY_MAP: dict[str, list[Callable]] = {}


def get_available_categories() -> list[str]:
    """Get list of available tool categories."""
    return ["accounts", "campaigns", "leads", "emails", "analytics", "background_jobs"]


def is_lazy_loading_enabled() -> bool:
    """Check if lazy loading is active."""
    return bool(os.environ.get("TOOL_CATEGORIES"))


def get_requested_categories() -> list[str]:
    """Get list of categories requested via TOOL_CATEGORIES env var."""
    categories_env = os.environ.get("TOOL_CATEGORIES", "")
    if not categories_env:
        return get_available_categories()
    
    requested = [c.strip().lower() for c in categories_env.split(",") if c.strip()]
    valid = [c for c in requested if c in get_available_categories()]
    
    if not valid:
        print(f"[Instantly MCP] ⚠️ No valid categories in TOOL_CATEGORIES. Loading all.")
        return get_available_categories()
    
    invalid = set(requested) - set(valid)
    if invalid:
        print(f"[Instantly MCP] ⚠️ Unknown categories ignored: {invalid}")
    
    return valid


def load_tools_for_category(category: str) -> list[Callable]:
    """Load tools for a specific category."""
    if category == "accounts":
        from .accounts import ACCOUNT_TOOLS
        return ACCOUNT_TOOLS
    elif category == "campaigns":
        from .campaigns import CAMPAIGN_TOOLS
        return CAMPAIGN_TOOLS
    elif category == "leads":
        from .leads import LEAD_TOOLS
        return LEAD_TOOLS
    elif category == "emails":
        from .emails import EMAIL_TOOLS
        return EMAIL_TOOLS
    elif category == "analytics":
        from .analytics import ANALYTICS_TOOLS
        return ANALYTICS_TOOLS
    elif category == "background_jobs":
        from .background_jobs import BACKGROUND_JOB_TOOLS
        return BACKGROUND_JOB_TOOLS
    return []


def get_all_tools() -> list[Callable]:
    """Get all tools based on TOOL_CATEGORIES configuration."""
    categories = get_requested_categories()
    tools = []
    
    for category in categories:
        tools.extend(load_tools_for_category(category))
    
    if is_lazy_loading_enabled():
        print(f"[Instantly MCP] 🔧 Lazy loading enabled: {len(tools)} tools from categories: {', '.join(categories)}")
    
    return tools


__all__ = [
    "get_available_categories",
    "is_lazy_loading_enabled", 
    "get_requested_categories",
    "get_all_tools",
]

