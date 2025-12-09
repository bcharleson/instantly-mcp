"""
Pydantic models for Analytics operations.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class GetCampaignAnalyticsInput(BaseModel):
    """
    Input for getting campaign analytics.
    
    Metrics: opens, clicks, replies, bounces. Filter by campaign(s) and dates.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign_id: Optional[str] = Field(
        default=None,
        description="Single campaign UUID (omit for all)"
    )
    campaign_ids: Optional[list[str]] = Field(
        default=None,
        description="Multiple campaign UUIDs"
    )
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    exclude_total_leads_count: Optional[bool] = Field(
        default=None,
        description="Faster response"
    )


class GetDailyCampaignAnalyticsInput(BaseModel):
    """Input for getting day-by-day campaign performance analytics."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign_id: Optional[str] = Field(
        default=None,
        description="Campaign UUID (omit for all)"
    )
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    campaign_status: Optional[Literal[0, 1, 2, 3, 4, -99, -1, -2]] = Field(
        default=None,
        description="0=Draft, 1=Active, 2=Paused, 3=Completed"
    )


class GetWarmupAnalyticsInput(BaseModel):
    """Input for getting warmup metrics for account(s)."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    emails: Optional[list[str]] = Field(default=None, description="Account emails")
    email: Optional[str] = Field(default=None, description="Single email (alternative)")
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")

