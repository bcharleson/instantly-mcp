"""
Instantly MCP Server - A lightweight FastMCP server for Instantly.ai V2 API

This package provides a Model Context Protocol (MCP) server for interacting
with the Instantly.ai email automation platform through AI assistants.
"""

__version__ = "1.0.0"
__author__ = "Brandon Charleson"

# Lazy imports to avoid circular import issues
def __getattr__(name):
    if name == "mcp":
        from .server import mcp
        return mcp
    elif name == "main":
        from .server import main
        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["mcp", "main", "__version__"]

