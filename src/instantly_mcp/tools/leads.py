"""
Instantly MCP Server - Lead Tools

11 tools for lead and lead list management operations.
The most comprehensive tool category with bulk operations and custom variables.
"""

import json
from typing import Any, Optional

from ..client import get_client
from ..models.leads import (
    ListLeadsInput,
    GetLeadInput,
    CreateLeadInput,
    UpdateLeadInput,
    ListLeadListsInput,
    CreateLeadListInput,
    UpdateLeadListInput,
    GetVerificationStatsInput,
    BulkAddLeadsInput,
    DeleteLeadInput,
    DeleteLeadListInput,
    MoveLeadsInput,
)


async def list_leads(params: Optional[ListLeadsInput] = None) -> str:
    """
    List leads with cursor-based pagination (100 per page).
    
    PAGINATION: If response contains pagination.next_starting_after, there are 
    MORE results. Call again with starting_after=<that value> to get next page.
    Continue until pagination.next_starting_after is null.
    
    Filter values:
    - FILTER_VAL_CONTACTED: Leads that have been contacted
    - FILTER_VAL_NOT_CONTACTED: Leads not yet contacted
    - FILTER_VAL_COMPLETED: Leads that completed sequence
    - FILTER_VAL_ACTIVE: Currently active leads
    
    Use distinct_contacts=true to deduplicate by email.
    """
    client = get_client()
    
    # Handle case where params is None (for OpenAI/non-Claude clients)
    # Set default limit=100 to return more results by default
    if params is None:
        params = ListLeadsInput(limit=100)
    
    # Build request body for POST /leads/list
    body: dict[str, Any] = {}
    
    # Default to 100 results if no limit specified
    body["limit"] = params.limit or 100
    
    if params.campaign:
        body["campaign"] = params.campaign
    if params.list_id:
        body["list_id"] = params.list_id
    if params.list_ids:
        body["list_ids"] = params.list_ids
    if params.status:
        body["status"] = params.status
    if params.created_after:
        body["created_after"] = params.created_after
    if params.created_before:
        body["created_before"] = params.created_before
    if params.search:
        body["search"] = params.search
    if params.filter:
        body["filter"] = params.filter
    if params.distinct_contacts is not None:
        body["distinct_contacts"] = params.distinct_contacts
    if params.starting_after:
        body["starting_after"] = params.starting_after
    
    result = await client.post("/leads/list", json=body)
    
    # Add pagination guidance for LLMs
    if isinstance(result, dict):
        pagination = result.get("pagination", {})
        next_cursor = pagination.get("next_starting_after")
        if next_cursor:
            result["_pagination_hint"] = f"MORE RESULTS AVAILABLE. Call list_leads with starting_after='{next_cursor}' to get next page."
    
    return json.dumps(result, indent=2)


async def get_lead(params: GetLeadInput) -> str:
    """
    Get lead details by ID.
    
    Returns comprehensive lead information including:
    - Contact details (email, name, company, phone)
    - Custom variables
    - Campaign/list membership
    - Sequence status and history
    - Interest status
    """
    client = get_client()
    result = await client.get(f"/leads/{params.lead_id}")
    return json.dumps(result, indent=2)


async def create_lead(params: CreateLeadInput) -> str:
    """
    Create a single lead with custom variables.
    
    Use skip_if_in_campaign=true to prevent duplicates (recommended).
    
    Custom variables must match field names defined in the campaign.
    Example: {"industry": "Technology", "company_size": "50-100"}
    
    For bulk imports (10+ leads), use add_leads_to_campaign_or_list_bulk instead.
    """
    client = get_client()
    
    body: dict[str, Any] = {
        "email": params.email,
    }
    
    if params.campaign:
        body["campaign"] = params.campaign
    if params.first_name:
        body["first_name"] = params.first_name
    if params.last_name:
        body["last_name"] = params.last_name
    if params.company_name:
        body["company_name"] = params.company_name
    if params.phone:
        body["phone"] = params.phone
    if params.website:
        body["website"] = params.website
    if params.personalization:
        body["personalization"] = params.personalization
    if params.lt_interest_status is not None:
        body["lt_interest_status"] = params.lt_interest_status
    if params.pl_value_lead:
        body["pl_value_lead"] = params.pl_value_lead
    if params.list_id:
        body["list_id"] = params.list_id
    if params.assigned_to:
        body["assigned_to"] = params.assigned_to
    if params.skip_if_in_workspace is not None:
        body["skip_if_in_workspace"] = params.skip_if_in_workspace
    if params.skip_if_in_campaign is not None:
        body["skip_if_in_campaign"] = params.skip_if_in_campaign
    if params.skip_if_in_list is not None:
        body["skip_if_in_list"] = params.skip_if_in_list
    if params.blocklist_id:
        body["blocklist_id"] = params.blocklist_id
    if params.verify_leads_on_import is not None:
        body["verify_leads_on_import"] = params.verify_leads_on_import
    if params.custom_variables:
        body["custom_variables"] = params.custom_variables
    
    result = await client.post("/leads", json=body)
    return json.dumps(result, indent=2)


async def update_lead(params: UpdateLeadInput) -> str:
    """
    Update lead (partial update).
    
    ⚠️ IMPORTANT: custom_variables REPLACES the entire object!
    To preserve existing custom variables:
    1. First call get_lead to retrieve current values
    2. Merge your changes with existing values
    3. Pass the complete merged object
    
    Example: If lead has {"industry": "Tech"} and you want to add {"size": "Large"},
    you must pass {"industry": "Tech", "size": "Large"} - not just {"size": "Large"}
    """
    client = get_client()
    
    body: dict[str, Any] = {}
    
    if params.personalization is not None:
        body["personalization"] = params.personalization
    if params.website is not None:
        body["website"] = params.website
    if params.last_name is not None:
        body["last_name"] = params.last_name
    if params.first_name is not None:
        body["first_name"] = params.first_name
    if params.company_name is not None:
        body["company_name"] = params.company_name
    if params.phone is not None:
        body["phone"] = params.phone
    if params.lt_interest_status is not None:
        body["lt_interest_status"] = params.lt_interest_status
    if params.pl_value_lead is not None:
        body["pl_value_lead"] = params.pl_value_lead
    if params.assigned_to is not None:
        body["assigned_to"] = params.assigned_to
    if params.custom_variables is not None:
        body["custom_variables"] = params.custom_variables
    
    result = await client.patch(f"/leads/{params.lead_id}", json=body)
    return json.dumps(result, indent=2)


async def list_lead_lists(params: Optional[ListLeadListsInput] = None) -> str:
    """
    List lead lists with cursor-based pagination (100 per page).
    
    PAGINATION: If response contains pagination.next_starting_after, there are 
    MORE results. Call again with starting_after=<that value> to get next page.
    Continue until pagination.next_starting_after is null.
    
    Lead lists are containers for organizing leads outside of campaigns.
    Use has_enrichment_task filter to find lists with auto-enrichment enabled.
    """
    client = get_client()
    
    # Handle case where params is None (for OpenAI/non-Claude clients)
    # Set default limit=100 to return more results by default
    if params is None:
        params = ListLeadListsInput(limit=100)
    
    query_params = {}
    if params.limit:
        query_params["limit"] = params.limit
    else:
        # Default to 100 results if no limit specified
        query_params["limit"] = 100
    if params.starting_after:
        query_params["starting_after"] = params.starting_after
    if params.has_enrichment_task is not None:
        query_params["has_enrichment_task"] = params.has_enrichment_task
    if params.search:
        query_params["search"] = params.search
    
    result = await client.get("/lead-lists", params=query_params)
    
    # Add pagination guidance for LLMs
    if isinstance(result, dict):
        pagination = result.get("pagination", {})
        next_cursor = pagination.get("next_starting_after")
        if next_cursor:
            result["_pagination_hint"] = f"MORE RESULTS AVAILABLE. Call list_lead_lists with starting_after='{next_cursor}' to get next page."
    
    return json.dumps(result, indent=2)


async def create_lead_list(params: CreateLeadListInput) -> str:
    """
    Create a lead list.
    
    Set has_enrichment_task=true to enable automatic lead enrichment.
    Enrichment adds company info, social profiles, and other data.
    """
    client = get_client()
    
    body: dict[str, Any] = {
        "name": params.name,
    }
    
    if params.has_enrichment_task is not None:
        body["has_enrichment_task"] = params.has_enrichment_task
    if params.owned_by:
        body["owned_by"] = params.owned_by
    
    result = await client.post("/lead-lists", json=body)
    return json.dumps(result, indent=2)


async def update_lead_list(params: UpdateLeadListInput) -> str:
    """
    Update lead list name, enrichment settings, or owner.
    """
    client = get_client()
    
    body: dict[str, Any] = {}
    
    if params.name is not None:
        body["name"] = params.name
    if params.has_enrichment_task is not None:
        body["has_enrichment_task"] = params.has_enrichment_task
    if params.owned_by is not None:
        body["owned_by"] = params.owned_by
    
    result = await client.patch(f"/lead-lists/{params.list_id}", json=body)
    return json.dumps(result, indent=2)


async def get_verification_stats_for_lead_list(params: GetVerificationStatsInput) -> str:
    """
    Get email verification statistics for a lead list.
    
    Returns breakdown of verification results:
    - Valid emails
    - Invalid/bounced emails
    - Risky emails
    - Unknown status
    """
    client = get_client()
    result = await client.get(f"/lead-lists/{params.list_id}/verification-stats")
    return json.dumps(result, indent=2)


async def add_leads_to_campaign_or_list_bulk(params: BulkAddLeadsInput) -> str:
    """
    Bulk add up to 1,000 leads. 10-100x faster than create_lead.
    
    Provide EITHER campaign_id OR list_id (not both).
    
    Each lead requires at minimum an email address.
    Custom variables must match campaign field definitions.
    
    Use skip_if_in_campaign=true to prevent duplicates (recommended).
    """
    client = get_client()
    
    body: dict[str, Any] = {
        "leads": [lead.model_dump(exclude_none=True) for lead in params.leads],
    }
    
    if params.campaign_id:
        body["campaign_id"] = params.campaign_id
    if params.list_id:
        body["list_id"] = params.list_id
    if params.blocklist_id:
        body["blocklist_id"] = params.blocklist_id
    if params.assigned_to:
        body["assigned_to"] = params.assigned_to
    if params.verify_leads_on_import is not None:
        body["verify_leads_on_import"] = params.verify_leads_on_import
    if params.skip_if_in_workspace is not None:
        body["skip_if_in_workspace"] = params.skip_if_in_workspace
    if params.skip_if_in_campaign is not None:
        body["skip_if_in_campaign"] = params.skip_if_in_campaign
    if params.skip_if_in_list is not None:
        body["skip_if_in_list"] = params.skip_if_in_list
    
    result = await client.post("/leads/add", json=body)
    return json.dumps(result, indent=2)


async def delete_lead(params: DeleteLeadInput) -> str:
    """
    🗑️ PERMANENTLY delete a lead. CANNOT UNDO!
    
    This action:
    - Removes the lead from all campaigns and lists
    - Deletes all lead data and history
    - Cannot be reversed
    
    Confirm with user before executing!
    """
    client = get_client()
    result = await client.delete(f"/leads/{params.lead_id}")
    return json.dumps({"success": True, "deleted": params.lead_id, **result}, indent=2)


async def move_leads_to_campaign_or_list(params: MoveLeadsInput) -> str:
    """
    Move or copy leads between campaigns/lists.

    Runs as background job for large operations.

    Source selection (use one):
    - ids: Specific lead IDs to move
    - search + campaign/list_id: Filter leads by search term
    - filter + campaign/list_id: Filter by status

    Destination (use one):
    - to_campaign_id: Target campaign
    - to_list_id: Target list

    Set copy_leads=true to copy instead of move.
    """
    client = get_client()

    body: dict[str, Any] = {}

    if params.to_campaign_id:
        body["to_campaign_id"] = params.to_campaign_id
    if params.to_list_id:
        body["to_list_id"] = params.to_list_id
    if params.ids:
        body["ids"] = params.ids
    if params.search:
        body["search"] = params.search
    if params.filter:
        body["filter"] = params.filter
    if params.campaign:
        body["campaign"] = params.campaign
    if params.list_id:
        body["list_id"] = params.list_id
    if params.in_campaign is not None:
        body["in_campaign"] = params.in_campaign
    if params.in_list is not None:
        body["in_list"] = params.in_list
    if params.queries:
        body["queries"] = params.queries
    if params.excluded_ids:
        body["excluded_ids"] = params.excluded_ids
    if params.contacts:
        body["contacts"] = params.contacts
    if params.check_duplicates_in_campaigns is not None:
        body["check_duplicates_in_campaigns"] = params.check_duplicates_in_campaigns
    if params.skip_leads_in_verification is not None:
        body["skip_leads_in_verification"] = params.skip_leads_in_verification
    if params.limit is not None:
        body["limit"] = params.limit
    if params.assigned_to:
        body["assigned_to"] = params.assigned_to
    if params.esp_code is not None:
        body["esp_code"] = params.esp_code
    if params.esg_code is not None:
        body["esg_code"] = params.esg_code
    if params.copy_leads is not None:
        body["copy_leads"] = params.copy_leads
    if params.check_duplicates is not None:
        body["check_duplicates"] = params.check_duplicates

    result = await client.post("/leads/move", json=body)
    return json.dumps(result, indent=2)


async def delete_lead_list(params: DeleteLeadListInput) -> str:
    """
    🚨 PERMANENTLY delete a lead list. CANNOT UNDO!

    ⚠️ REQUIRES USER CONFIRMATION before executing!

    This action:
    - Permanently removes the lead list
    - Leads in the list may be orphaned (check your workflow)
    - Cannot be reversed

    Before calling this tool, you MUST:
    1. Confirm with the user that they want to delete this list
    2. Verify the list_id is correct
    3. Warn them this action cannot be undone
    """
    client = get_client()
    result = await client.delete(f"/lead-lists/{params.list_id}")
    return json.dumps({
        "success": True,
        "deleted_list_id": params.list_id,
        "message": "Lead list permanently deleted",
        **result
    }, indent=2)


# Export all lead tools
LEAD_TOOLS = [
    list_leads,
    get_lead,
    create_lead,
    update_lead,
    list_lead_lists,
    create_lead_list,
    update_lead_list,
    get_verification_stats_for_lead_list,
    add_leads_to_campaign_or_list_bulk,
    delete_lead,
    delete_lead_list,
    move_leads_to_campaign_or_list,
]

