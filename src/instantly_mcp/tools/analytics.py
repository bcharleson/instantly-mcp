"""
Instantly MCP Server - Analytics Tools

3 tools for analytics and reporting operations.
"""

import json
from typing import Any, Optional

from ..client import get_client
from ..models.analytics import (
    GetCampaignAnalyticsInput,
    GetDailyCampaignAnalyticsInput,
    GetWarmupAnalyticsInput,
)


async def get_campaign_analytics(params: Optional[GetCampaignAnalyticsInput] = None) -> str:
    """
    Get campaign metrics: opens, clicks, replies, bounces.
    
    Filter by campaign(s) and date range.
    Omit campaign_id to get analytics for all campaigns.
    
    Use campaign_ids array to get analytics for multiple specific campaigns.
    Set exclude_total_leads_count=true for faster response.
    
    Returns:
    - sent: Total emails sent
    - opens: Unique opens
    - clicks: Unique clicks
    - replies: Total replies
    - bounces: Bounced emails
    - unsubscribes: Unsubscribe count
    """
    client = get_client()
    
    # Handle case where params is None (for OpenAI/non-Claude clients)
    if params is None:
        params = GetCampaignAnalyticsInput()
    
    query_params: dict[str, Any] = {}
    
    if params.campaign_id:
        query_params["id"] = params.campaign_id
    if params.campaign_ids:
        # API expects multiple id params for multiple campaigns
        for cid in params.campaign_ids:
            if "id" not in query_params:
                query_params["id"] = []
            if isinstance(query_params["id"], list):
                query_params["id"].append(cid)
            else:
                query_params["id"] = [query_params["id"], cid]
    if params.start_date:
        query_params["start_date"] = params.start_date
    if params.end_date:
        query_params["end_date"] = params.end_date
    if params.exclude_total_leads_count is not None:
        query_params["exclude_total_leads_count"] = params.exclude_total_leads_count
    
    result = await client.get("/campaigns/analytics", params=query_params)
    return json.dumps(result, indent=2)


async def get_daily_campaign_analytics(params: Optional[GetDailyCampaignAnalyticsInput] = None) -> str:
    """
    Get day-by-day campaign performance analytics.
    
    Returns daily breakdown of:
    - Emails sent
    - Opens and open rate
    - Clicks and click rate
    - Replies and reply rate
    - Bounces
    
    Campaign status filter:
    - 0: Draft
    - 1: Active
    - 2: Paused
    - 3: Completed
    - 4: Scheduled
    - -99: All statuses
    - -1: Error
    - -2: Deleted
    
    Useful for tracking performance trends over time.
    """
    client = get_client()
    
    # Handle case where params is None (for OpenAI/non-Claude clients)
    if params is None:
        params = GetDailyCampaignAnalyticsInput()
    
    query_params: dict[str, Any] = {}
    
    if params.campaign_id:
        query_params["campaign_id"] = params.campaign_id
    if params.start_date:
        query_params["start_date"] = params.start_date
    if params.end_date:
        query_params["end_date"] = params.end_date
    if params.campaign_status is not None:
        query_params["campaign_status"] = params.campaign_status
    
    result = await client.get("/campaigns/analytics/daily", params=query_params)
    return json.dumps(result, indent=2)


async def get_warmup_analytics(params: Optional[GetWarmupAnalyticsInput] = None) -> str:
    """
    Get warmup metrics for email account(s).

    Provide either:
    - emails: Array of account emails
    - email: Single account email

    Returns warmup performance data:
    - Warmup emails sent/received
    - Inbox placement rate
    - Spam rate
    - Reply rate
    - Daily progress

    Use date filters to analyze specific time periods.
    """
    client = get_client()

    # Handle case where params is None (for OpenAI/non-Claude clients)
    if params is None:
        params = GetWarmupAnalyticsInput()

    # Build JSON body for POST request (per v2 API spec)
    body: dict[str, Any] = {}

    if params.emails:
        body["emails"] = params.emails
    elif params.email:
        body["emails"] = [params.email]

    if params.start_date:
        body["start_date"] = params.start_date
    if params.end_date:
        body["end_date"] = params.end_date

    # API requires POST with JSON body, not GET with query params
    result = await client.post("/accounts/warmup-analytics", json=body)
    return json.dumps(result, indent=2)


# Export all analytics tools
ANALYTICS_TOOLS = [
    get_campaign_analytics,
    get_daily_campaign_analytics,
    get_warmup_analytics,
]

