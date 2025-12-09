"""
Instantly MCP Server - API Client

HTTP client for making requests to the Instantly.ai API v2.
Features:
- Triple authentication (env variable + URL path + headers)
- Rate limiting with header tracking
- Dynamic timeouts based on operation type
- Comprehensive error handling
"""

import os
import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

import httpx

# Import per-request API key context (lazy import to avoid circular deps)
def _get_request_api_key() -> Optional[str]:
    """Get API key from request context if available."""
    try:
        from .http_app import get_request_api_key
        return get_request_api_key()
    except ImportError:
        return None

# API Configuration
INSTANTLY_API_URL = "https://api.instantly.ai/api/v2"
DEFAULT_TIMEOUT = 60.0  # seconds
EXTENDED_TIMEOUT = 90.0  # for list operations
SEARCH_TIMEOUT = 120.0  # for search operations


@dataclass
class RateLimitInfo:
    """Track rate limit information from API responses."""
    remaining: Optional[int] = None
    limit: Optional[int] = None
    reset_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None


@dataclass
class InstantlyClient:
    """
    HTTP client for Instantly.ai API v2.
    
    Supports dual authentication:
    - Environment variable: INSTANTLY_API_KEY
    - Per-request: api_key parameter (for multi-tenant HTTP mode)
    """
    
    _api_key: Optional[str] = field(default=None, repr=False)
    rate_limit: RateLimitInfo = field(default_factory=RateLimitInfo)
    
    def __post_init__(self):
        # Try to get API key from environment if not provided
        if not self._api_key:
            self._api_key = os.environ.get("INSTANTLY_API_KEY")
    
    @property
    def has_api_key(self) -> bool:
        """Check if an API key is configured."""
        return bool(self._api_key)
    
    def set_api_key(self, api_key: str) -> None:
        """Set API key programmatically."""
        self._api_key = api_key
    
    def _get_timeout(self, endpoint: str, has_search: bool = False) -> float:
        """
        Determine appropriate timeout based on endpoint and operation.
        
        Search operations and large list operations need longer timeouts
        due to potential dataset sizes (10k+ leads).
        """
        if has_search:
            return SEARCH_TIMEOUT
        if "/leads" in endpoint and "list" in endpoint:
            return EXTENDED_TIMEOUT
        return DEFAULT_TIMEOUT
    
    def _update_rate_limit(self, headers: httpx.Headers) -> None:
        """Update rate limit tracking from response headers."""
        try:
            if "x-ratelimit-remaining" in headers:
                self.rate_limit.remaining = int(headers["x-ratelimit-remaining"])
            if "x-ratelimit-limit" in headers:
                self.rate_limit.limit = int(headers["x-ratelimit-limit"])
            if "x-ratelimit-reset" in headers:
                self.rate_limit.reset_at = datetime.fromtimestamp(
                    int(headers["x-ratelimit-reset"])
                )
            self.rate_limit.last_updated = datetime.now()
        except (ValueError, KeyError):
            pass  # Silently ignore parsing errors
    
    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Make an authenticated request to the Instantly API.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (e.g., '/accounts', '/campaigns/{id}')
            params: Query parameters for GET requests
            json: JSON body for POST/PATCH requests
            api_key: Optional per-request API key (overrides configured key)
            timeout: Optional custom timeout
        
        Returns:
            Parsed JSON response
        
        Raises:
            ValueError: If no API key is available
            httpx.HTTPStatusError: For API errors
        """
        # Resolve API key (per-request param > request context > instance > environment)
        use_api_key = api_key or _get_request_api_key() or self._api_key
        if not use_api_key:
            raise ValueError(
                "Instantly API key is required. Provide via:\n"
                "  - URL path: /mcp/YOUR_API_KEY\n"
                "  - Header: Authorization: YOUR_API_KEY\n"
                "  - Header: x-instantly-api-key: YOUR_API_KEY\n"
                "  - Environment: INSTANTLY_API_KEY"
            )
        
        # Build request
        url = f"{INSTANTLY_API_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {use_api_key}"}
        
        # Determine timeout
        has_search = bool(json and json.get("search"))
        request_timeout = timeout or self._get_timeout(endpoint, has_search)
        
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                )
                
                # Update rate limit tracking
                self._update_rate_limit(response.headers)
                
                # Handle errors
                if response.status_code >= 400:
                    error_detail = self._parse_error(response)
                    raise httpx.HTTPStatusError(
                        message=error_detail,
                        request=response.request,
                        response=response,
                    )
                
                # Return parsed response
                if response.status_code == 204:
                    return {"success": True}
                
                return response.json()
                
            except httpx.TimeoutException as e:
                raise TimeoutError(
                    f"Request timed out after {request_timeout}s. "
                    f"For large datasets, try using pagination with smaller limits."
                ) from e
            except httpx.RequestError as e:
                raise ConnectionError(
                    f"Failed to connect to Instantly API: {e}"
                ) from e
    
    def _parse_error(self, response: httpx.Response) -> str:
        """Parse error response and return descriptive message."""
        try:
            data = response.json()
            
            # Handle various error formats from Instantly API
            if isinstance(data, dict):
                # Standard error format
                if "error" in data:
                    error = data["error"]
                    if isinstance(error, dict):
                        return error.get("message", str(error))
                    return str(error)
                
                # Validation error format
                if "message" in data:
                    return data["message"]
                
                # Detail format
                if "detail" in data:
                    return data["detail"]
            
            return f"HTTP {response.status_code}: {response.text[:200]}"
            
        except Exception:
            return f"HTTP {response.status_code}: {response.text[:200]}"
    
    # Convenience methods
    async def get(self, endpoint: str, **kwargs) -> Any:
        """GET request."""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Any:
        """POST request."""
        return await self.request("POST", endpoint, **kwargs)
    
    async def patch(self, endpoint: str, **kwargs) -> Any:
        """PATCH request."""
        return await self.request("PATCH", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Any:
        """DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)


# Global client instance
client = InstantlyClient()


def get_client() -> InstantlyClient:
    """Get the global API client instance."""
    return client


def set_api_key(api_key: str) -> None:
    """Set the API key for the global client."""
    client.set_api_key(api_key)

