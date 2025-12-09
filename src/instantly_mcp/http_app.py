"""
Instantly MCP Server - Custom HTTP Application

Provides an ASGI wrapper for FastMCP that supports:
- URL-based authentication: /mcp/YOUR_API_KEY
- Header authentication: Authorization: YOUR_API_KEY (no Bearer prefix required)
- Custom header: x-instantly-api-key

Matches the authentication patterns from the TypeScript version.
"""

import json
import re
from contextvars import ContextVar
from typing import Optional, Callable, Any

# Context variable to store per-request API key
request_api_key: ContextVar[Optional[str]] = ContextVar("request_api_key", default=None)


def get_request_api_key() -> Optional[str]:
    """Get the API key for the current request from context."""
    return request_api_key.get()


def extract_api_key_from_headers(headers: list) -> Optional[str]:
    """
    Extract API key from request headers.
    
    Supports:
    1. x-instantly-api-key header
    2. Authorization: KEY (without Bearer)
    3. Authorization: Bearer KEY
    """
    headers_dict = {k.decode().lower(): v.decode() for k, v in headers}
    
    # Check custom header first
    api_key = headers_dict.get("x-instantly-api-key")
    if api_key:
        return api_key
    
    # Check Authorization header
    auth_header = headers_dict.get("authorization", "")
    if auth_header:
        # Support both "Bearer KEY" and plain "KEY" formats
        if auth_header.lower().startswith("bearer "):
            return auth_header[7:]
        return auth_header
    
    return None


def create_api_key_middleware(app: Callable) -> Callable:
    """
    ASGI middleware that extracts API key from URL path or headers.
    
    URL patterns:
    - /mcp/YOUR_API_KEY -> rewrites to /mcp
    - /mcp/YOUR_API_KEY/sse -> rewrites to /mcp/sse
    """
    
    async def middleware(scope: dict, receive: Callable, send: Callable):
        if scope["type"] not in ("http", "websocket"):
            await app(scope, receive, send)
            return
        
        api_key = None
        path = scope.get("path", "")
        
        # Match /mcp/{api_key} pattern
        # Don't match known MCP subpaths: sse, messages
        match = re.match(r"^/mcp/([^/]+)(/.*)?$", path)
        if match:
            potential_key = match.group(1)
            # Don't treat known MCP subpaths as API keys
            if potential_key not in ("sse", "messages"):
                api_key = potential_key
                # Rewrite path to remove the API key segment
                suffix = match.group(2) or ""
                scope = dict(scope)  # Make a copy
                scope["path"] = "/mcp" + suffix
        
        # Fall back to headers if no URL key
        if not api_key:
            headers = scope.get("headers", [])
            api_key = extract_api_key_from_headers(headers)
        
        # Set the API key in context for this request
        token = request_api_key.set(api_key)
        
        try:
            await app(scope, receive, send)
        finally:
            request_api_key.reset(token)
    
    return middleware


def create_health_handler() -> Callable:
    """Create a simple health check handler."""
    
    async def health_app(scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            return
        
        response_body = json.dumps({
            "status": "healthy",
            "server": "instantly-mcp",
            "version": "1.0.0",
            "endpoints": {
                "mcp": "/mcp",
                "mcp_with_key": "/mcp/{api_key}",
            },
            "authentication": {
                "methods": [
                    "URL path: /mcp/YOUR_API_KEY",
                    "Header: Authorization: YOUR_API_KEY",
                    "Header: x-instantly-api-key: YOUR_API_KEY",
                ],
                "note": "Bearer prefix is optional for Authorization header"
            }
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(response_body)).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": response_body,
        })
    
    return health_app


def create_http_app(mcp_app) -> Callable:
    """
    Create an ASGI app that wraps FastMCP with URL-based auth support.
    
    Routes:
    - GET /, /health : Health check
    - /mcp/* : MCP endpoints (handled by FastMCP)
    - /mcp/{api_key}/* : MCP endpoints with URL-based API key
    """
    
    # Get the ASGI app from FastMCP
    fastmcp_asgi = mcp_app.http_app()
    health_app = create_health_handler()
    
    async def router(scope: dict, receive: Callable, send: Callable):
        if scope["type"] not in ("http", "websocket"):
            await fastmcp_asgi(scope, receive, send)
            return
        
        path = scope.get("path", "")
        
        # Health check endpoints
        if path in ("/", "/health"):
            await health_app(scope, receive, send)
            return
        
        # All /mcp paths go to FastMCP (API key middleware rewrites /mcp/{key} -> /mcp)
        if path.startswith("/mcp"):
            await fastmcp_asgi(scope, receive, send)
            return
        
        # 404 for unknown paths
        response_body = json.dumps({
            "error": "Not found",
            "hint": "MCP endpoint is at /mcp or /mcp/{api_key}"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(response_body)).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": response_body,
        })
    
    # Wrap router with API key middleware
    return create_api_key_middleware(router)


def run_http_server(mcp_app, host: str = "0.0.0.0", port: int = 8000):
    """Run the HTTP server with URL-based auth support."""
    import uvicorn
    
    app = create_http_app(mcp_app)
    uvicorn.run(app, host=host, port=port)
