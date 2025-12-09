"""
Instantly MCP Server - Account Tools

6 tools for email account management operations.
"""

import json
from typing import Any, Optional
from urllib.parse import quote

from ..client import get_client
from ..models.accounts import (
    ListAccountsInput,
    GetAccountInput,
    CreateAccountInput,
    UpdateAccountInput,
    ManageAccountStateInput,
    DeleteAccountInput,
)


async def list_accounts(params: Optional[ListAccountsInput] = None) -> str:
    """
    List email accounts with cursor-based pagination (100 per page).
    
    PAGINATION: If response contains pagination.next_starting_after, there are 
    MORE results. Call again with starting_after=<that value> to get next page.
    Continue until pagination.next_starting_after is null.
    
    Status codes: 1=Active, 2=Paused, -1/-2/-3=Errors
    Provider codes: 1=IMAP, 2=Google, 3=Microsoft, 4=AWS
    
    Returns accounts with warmup status and campaign eligibility.
    """
    client = get_client()
    
    # Handle case where params is None (for OpenAI/non-Claude clients)
    # Set default limit=100 to return more results by default
    if params is None:
        params = ListAccountsInput(limit=100)
    
    query_params = {}
    if params.limit:
        query_params["limit"] = params.limit
    else:
        # Default to 100 results if no limit specified
        query_params["limit"] = 100
    if params.starting_after:
        query_params["starting_after"] = params.starting_after
    if params.search:
        query_params["search"] = params.search
    if params.status is not None:
        query_params["status"] = params.status
    if params.provider_code is not None:
        query_params["provider_code"] = params.provider_code
    if params.tag_ids:
        query_params["tag_ids"] = params.tag_ids
    
    result = await client.get("/accounts", params=query_params)
    
    # Add pagination guidance for LLMs
    if isinstance(result, dict):
        pagination = result.get("pagination", {})
        next_cursor = pagination.get("next_starting_after")
        if next_cursor:
            result["_pagination_hint"] = f"MORE RESULTS AVAILABLE. Call list_accounts with starting_after='{next_cursor}' to get next page."
    
    return json.dumps(result, indent=2)


async def get_account(params: GetAccountInput) -> str:
    """
    Get account details, warmup status, and campaign eligibility by email.
    
    Returns comprehensive account information including:
    - Connection status and provider info
    - Warmup configuration and progress
    - Daily limits and sending gaps
    - Tracking domain settings
    """
    client = get_client()
    email_encoded = quote(params.email, safe="")
    result = await client.get(f"/accounts/{email_encoded}")
    return json.dumps(result, indent=2)


async def create_account(params: CreateAccountInput) -> str:
    """
    Create email account with IMAP/SMTP credentials.
    
    Provider codes:
    - 1: IMAP (generic)
    - 2: Google Workspace
    - 3: Microsoft 365
    - 4: AWS SES
    
    Requires valid IMAP and SMTP credentials for email sending.
    """
    client = get_client()
    
    body = {
        "email": params.email,
        "first_name": params.first_name,
        "last_name": params.last_name,
        "provider_code": params.provider_code,
        "imap_username": params.imap_username,
        "imap_password": params.imap_password,
        "imap_host": params.imap_host,
        "imap_port": params.imap_port,
        "smtp_username": params.smtp_username,
        "smtp_password": params.smtp_password,
        "smtp_host": params.smtp_host,
        "smtp_port": params.smtp_port,
    }
    
    result = await client.post("/accounts", json=body)
    return json.dumps(result, indent=2)


async def update_account(params: UpdateAccountInput) -> str:
    """
    Update account settings (partial update).
    
    Common updates:
    - first_name, last_name: Display name
    - warmup: Warmup configuration (limit, advanced settings)
    - daily_limit: Max emails per day (1-100)
    - sending_gap: Minutes between emails (0-1440)
    - tracking_domain_name: Custom tracking domain
    
    Only include fields you want to update.
    """
    client = get_client()
    email_encoded = quote(params.email, safe="")
    
    body = {}
    if params.first_name is not None:
        body["first_name"] = params.first_name
    if params.last_name is not None:
        body["last_name"] = params.last_name
    if params.warmup is not None:
        warmup_dict = params.warmup.model_dump(exclude_none=True)
        if warmup_dict:
            body["warmup"] = warmup_dict
    if params.daily_limit is not None:
        body["daily_limit"] = params.daily_limit
    if params.sending_gap is not None:
        body["sending_gap"] = params.sending_gap
    if params.enable_slow_ramp is not None:
        body["enable_slow_ramp"] = params.enable_slow_ramp
    if params.tracking_domain_name is not None:
        body["tracking_domain_name"] = params.tracking_domain_name
    if params.tracking_domain_status is not None:
        body["tracking_domain_status"] = params.tracking_domain_status
    if params.skip_cname_check is not None:
        body["skip_cname_check"] = params.skip_cname_check
    if params.remove_tracking_domain is not None:
        body["remove_tracking_domain"] = params.remove_tracking_domain
    if params.inbox_placement_test_limit is not None:
        body["inbox_placement_test_limit"] = params.inbox_placement_test_limit
    
    result = await client.patch(f"/accounts/{email_encoded}", json=body)
    return json.dumps(result, indent=2)


async def manage_account_state(params: ManageAccountStateInput) -> str:
    """
    Manage account state: pause, resume, enable/disable warmup, or test vitals.
    
    Actions:
    - pause: Stop all sending from this account
    - resume: Re-enable sending
    - enable_warmup: Start warmup process
    - disable_warmup: Stop warmup process
    - test_vitals: Test IMAP/SMTP connectivity
    
    Use test_vitals to diagnose connection issues.
    """
    client = get_client()
    email_encoded = quote(params.email, safe="")
    
    action_endpoints = {
        "pause": f"/accounts/{email_encoded}/pause",
        "resume": f"/accounts/{email_encoded}/resume",
        "enable_warmup": "/accounts/warmup/enable",
        "disable_warmup": "/accounts/warmup/disable",
        "test_vitals": "/accounts/test/vitals",
    }
    
    endpoint = action_endpoints[params.action]
    
    # Different actions have different body requirements
    if params.action in ["pause", "resume"]:
        result = await client.post(endpoint)
    elif params.action in ["enable_warmup", "disable_warmup"]:
        # V2 API expects an array of emails for warmup enable/disable
        result = await client.post(endpoint, json={"emails": [params.email]})
    else:  # test_vitals
        # V2 API expects an array of emails for test vitals
        result = await client.post(endpoint, json={"emails": [params.email]})
    
    return json.dumps(result, indent=2)


async def delete_account(params: DeleteAccountInput) -> str:
    """
    🚨 PERMANENTLY delete an email account. CANNOT UNDO!
    
    This action:
    - Removes the account from all campaigns
    - Deletes all account data
    - Cannot be reversed
    
    Confirm with user before executing!
    """
    client = get_client()
    email_encoded = quote(params.email, safe="")
    result = await client.delete(f"/accounts/{email_encoded}")
    return json.dumps({"success": True, "deleted": params.email, **result}, indent=2)


# Export all account tools
ACCOUNT_TOOLS = [
    list_accounts,
    get_account,
    create_account,
    update_account,
    manage_account_state,
    delete_account,
]

