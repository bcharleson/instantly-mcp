"""
Pydantic models for Background Job operations.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ListBackgroundJobsInput(BaseModel):
    """Input for listing background jobs with pagination."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    limit: Optional[int] = Field(
        default=100, ge=1, le=100,
        description="Results per page (1-100, default: 100)"
    )
    starting_after: Optional[str] = Field(
        default=None,
        description="Pagination cursor - use value from pagination.next_starting_after to get next page"
    )


class GetBackgroundJobInput(BaseModel):
    """Input for getting a specific background job."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    job_id: str = Field(..., description="Background job UUID")

