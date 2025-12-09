"""
Instantly MCP Server - Background Job Tools

2 tools for tracking asynchronous operations.

Background jobs are created when you perform bulk operations like:
- Moving large numbers of leads between campaigns
- Bulk importing leads
- Running enrichment on large lists

These tools let you check the status of those async operations.
"""

import json
from typing import Optional

from ..client import get_client
from ..models.background_jobs import (
    ListBackgroundJobsInput,
    GetBackgroundJobInput,
)


async def list_background_jobs(params: Optional[ListBackgroundJobsInput] = None) -> str:
    """
    List background jobs with cursor-based pagination (100 per page).
    
    PAGINATION: If response contains pagination.next_starting_after, there are 
    MORE results. Call again with starting_after=<that value> to get next page.
    Continue until pagination.next_starting_after is null.
    
    Background jobs are created for async operations like:
    - Bulk lead imports
    - Moving leads between campaigns/lists
    - Running enrichment tasks
    
    Job statuses:
    - pending: Queued, not started yet
    - running: In progress
    - completed: Done successfully
    - failed: Something went wrong
    
    Returns list of jobs with status, type, and progress info.
    """
    client = get_client()
    
    # Handle case where params is None
    if params is None:
        params = ListBackgroundJobsInput(limit=100)
    
    query_params = {}
    if params.limit:
        query_params["limit"] = params.limit
    else:
        query_params["limit"] = 100
    if params.starting_after:
        query_params["starting_after"] = params.starting_after
    
    result = await client.get("/background-jobs", params=query_params)
    
    # Add pagination guidance for LLMs
    if isinstance(result, dict):
        pagination = result.get("pagination", {})
        next_cursor = pagination.get("next_starting_after")
        if next_cursor:
            result["_pagination_hint"] = f"MORE RESULTS AVAILABLE. Call list_background_jobs with starting_after='{next_cursor}' to get next page."
    
    return json.dumps(result, indent=2)


async def get_background_job(params: GetBackgroundJobInput) -> str:
    """
    Get details of a specific background job by ID.
    
    Returns comprehensive job information including:
    - Job type (what operation was requested)
    - Current status (pending, running, completed, failed)
    - Progress information (items processed, total items)
    - Error details (if failed)
    - Timestamps (created, started, completed)
    
    Use this to check if a bulk operation has finished.
    """
    client = get_client()
    result = await client.get(f"/background-jobs/{params.job_id}")
    return json.dumps(result, indent=2)


# Export all background job tools
BACKGROUND_JOB_TOOLS = [
    list_background_jobs,
    get_background_job,
]

