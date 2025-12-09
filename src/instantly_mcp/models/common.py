"""
Common Pydantic models for pagination and shared types.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class PaginationParams(BaseModel):
    """Common pagination parameters for list operations."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )
    
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Results per page (1-100, default: 100)"
    )
    starting_after: Optional[str] = Field(
        default=None,
        description="Cursor from pagination.next_starting_after for next page"
    )


class PaginationResponse(BaseModel):
    """Standard pagination response wrapper."""
    
    items: list[Any] = Field(default_factory=list)
    next_starting_after: Optional[str] = None
    has_more: bool = False
    
    @classmethod
    def from_response(cls, data: dict, items_key: str = "items") -> "PaginationResponse":
        """Parse API response into pagination response."""
        items = data.get(items_key, data.get("data", []))
        return cls(
            items=items if isinstance(items, list) else [items],
            next_starting_after=data.get("next_starting_after"),
            has_more=bool(data.get("next_starting_after")),
        )

