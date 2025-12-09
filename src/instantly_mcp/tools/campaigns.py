"""
Instantly MCP Server - Campaign Tools

6 tools for email campaign management operations.

Implements the Instantly.ai V2 API campaign structure which requires:
- sequences[0].steps[].type = "email"
- sequences[0].steps[].variants = [{ subject, body }]
- sequences[0].steps[].delay = days (integer, not minutes)
- campaign_schedule.schedules[].name is REQUIRED
- campaign_schedule.schedules[].days uses string keys ("0"-"6")
"""

import json
import re
from typing import Any, Optional

from ..client import get_client
from ..models.campaigns import (
    CreateCampaignInput,
    ListCampaignsInput,
    GetCampaignInput,
    UpdateCampaignInput,
    ActivateCampaignInput,
    PauseCampaignInput,
    DeleteCampaignInput,
    SearchCampaignsByContactInput,
    DEFAULT_TIMEZONE,
)


def convert_line_breaks_to_html(text: str) -> str:
    """
    Convert plain text line breaks to HTML for Instantly.ai email rendering.

    - Normalizes different line ending formats (\\r\\n, \\r, \\n)
    - Converts double line breaks to paragraph separations
    - Converts single line breaks to <br /> tags
    - Wraps content in <p> tags for proper HTML structure

    Args:
        text: Plain text to convert to HTML

    Returns:
        HTML-formatted text
    """
    if not text or not isinstance(text, str):
        return ""

    # Normalize line endings to \n
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split by double line breaks to create paragraphs
    paragraphs = normalized.split("\n\n")

    result_parts = []
    for paragraph in paragraphs:
        # Skip empty paragraphs
        if not paragraph.strip():
            continue

        # Convert single line breaks within paragraphs to <br /> tags
        with_breaks = paragraph.strip().replace("\n", "<br />")

        # Wrap in paragraph tags for proper HTML structure
        result_parts.append(f"<p>{with_breaks}</p>")

    return "".join(result_parts)


async def create_campaign(params: CreateCampaignInput) -> str:
    """
    Create email campaign. Two-step process:

    Step 1: Call with name/subject/body to discover available sender accounts
    Step 2: Call again with email_list to assign senders

    Personalization variables:
    - {{firstName}}, {{lastName}}, {{companyName}}
    - {{email}}, {{website}}, {{phone}}
    - Any custom variables defined for leads

    Use sequence_steps for multi-step follow-up sequences.

    IMPORTANT API v2 Structure:
    - Each step must have type="email"
    - Subject/body wrapped in variants array: variants=[{subject, body}]
    - Delay is in DAYS (not minutes)
    - Body should be HTML formatted
    """
    client = get_client()

    # =========================================================================
    # STEP 0: Account Discovery (Two-step workflow)
    # =========================================================================
    # If no email_list provided, fetch eligible accounts and return guidance
    if not params.email_list:
        try:
            accounts_result = await client.get("/accounts", params={"limit": 100})
            accounts = accounts_result.get("items", []) if isinstance(accounts_result, dict) else []

            # Filter for eligible accounts (active, setup complete, warmup complete)
            eligible_accounts = [
                acc for acc in accounts
                if acc.get("status") == 1
                and not acc.get("setup_pending")
                and acc.get("warmup_status") == 1
            ]

            if not accounts:
                return json.dumps({
                    "success": False,
                    "stage": "no_accounts",
                    "message": "❌ No accounts found in your workspace.",
                    "instructions": [
                        "1. Go to your Instantly.ai dashboard",
                        "2. Navigate to Accounts section",
                        "3. Add and verify email accounts",
                        "4. Complete warmup process for each account",
                        "5. Then retry campaign creation"
                    ]
                }, indent=2)

            if not eligible_accounts:
                account_issues = [
                    {
                        "email": acc.get("email"),
                        "issues": [
                            issue for issue in [
                                "Account not active" if acc.get("status") != 1 else None,
                                "Setup pending" if acc.get("setup_pending") else None,
                                "Warmup not complete" if acc.get("warmup_status") != 1 else None
                            ] if issue
                        ]
                    }
                    for acc in accounts[:10]
                ]

                return json.dumps({
                    "success": False,
                    "stage": "no_eligible_accounts",
                    "message": "❌ No eligible sender accounts found for campaign creation.",
                    "total_accounts": len(accounts),
                    "account_issues": account_issues,
                    "requirements": [
                        "Account must be active (status = 1)",
                        "Setup must be complete (no pending setup)",
                        "Warmup must be complete (warmup_status = 1)"
                    ]
                }, indent=2)

            # Return eligible accounts for user to select
            eligible_list = [
                {
                    "email": acc.get("email"),
                    "warmup_score": acc.get("warmup_score", 0),
                    "status": "ready"
                }
                for acc in eligible_accounts
            ]

            return json.dumps({
                "success": False,
                "stage": "account_selection_required",
                "message": "📋 Eligible Sender Accounts Found",
                "total_eligible_accounts": len(eligible_accounts),
                "total_accounts": len(accounts),
                "eligible_accounts": eligible_list,
                "instructions": (
                    f"✅ Found {len(eligible_accounts)} eligible sender accounts.\n\n"
                    "📝 Next Step:\n"
                    "Call create_campaign again with the email_list parameter containing "
                    "the sender emails you want to use.\n\n"
                    f"Example: email_list=[\"{eligible_list[0]['email'] if eligible_list else 'email@domain.com'}\"]"
                ),
                "required_action": {
                    "step": "select_sender_accounts",
                    "parameter": "email_list",
                    "example": [acc["email"] for acc in eligible_list[:3]]
                }
            }, indent=2)

        except Exception as e:
            # If account discovery fails, proceed anyway with a warning
            pass

    # =========================================================================
    # STEP 1: Build Campaign Payload (API v2 compliant)
    # =========================================================================
    body: dict[str, Any] = {
        "name": params.name,
    }

    # -------------------------------------------------------------------------
    # Build sequences with CORRECT V2 API structure
    # CRITICAL: Uses type, delay (in days), and variants array
    # -------------------------------------------------------------------------
    num_steps = params.sequence_steps or 1
    step_delay_days = params.step_delay_days or 3
    steps = []

    for i in range(num_steps):
        # Determine subject for this step
        if params.sequence_subjects and i < len(params.sequence_subjects):
            subject = params.sequence_subjects[i]
        elif i == 0:
            subject = params.subject
        else:
            subject = f"Follow-up: {params.subject}"

        # Clean subject (no line breaks allowed)
        subject = re.sub(r"[\r\n]+", " ", subject).strip()

        # Determine body for this step
        if params.sequence_bodies and i < len(params.sequence_bodies):
            body_text = params.sequence_bodies[i]
        elif i == 0:
            body_text = params.body
        else:
            body_text = f"This is follow-up #{i}.\n\n{params.body}"

        # Convert body to HTML for proper email rendering
        html_body = convert_line_breaks_to_html(body_text)

        # Build step with CORRECT V2 API structure
        step: dict[str, Any] = {
            "type": "email",
            # delay: days to wait AFTER this step before next step
            # First step in single-step campaign = 0
            # First step in multi-step campaign = step_delay_days
            # Follow-up steps = step_delay_days
            "delay": step_delay_days if (num_steps > 1 or i > 0) else 0,
            "variants": [{
                "subject": subject,
                "body": html_body
            }]
        }

        steps.append(step)

    # V2 API: sequences is array, first element contains steps array
    body["sequences"] = [{"steps": steps}]

    # -------------------------------------------------------------------------
    # Add sender accounts
    # -------------------------------------------------------------------------
    if params.email_list:
        body["email_list"] = params.email_list

    # -------------------------------------------------------------------------
    # Tracking settings (disabled by default for better deliverability)
    # -------------------------------------------------------------------------
    body["open_tracking"] = params.track_opens if params.track_opens is not None else False
    body["link_tracking"] = params.track_clicks if params.track_clicks is not None else False

    # -------------------------------------------------------------------------
    # Schedule settings with CORRECT V2 API structure
    # CRITICAL: name is REQUIRED, days use STRING keys "0"-"6"
    # -------------------------------------------------------------------------
    body["campaign_schedule"] = {
        "schedules": [{
            "name": "Default Schedule",  # REQUIRED field
            "timezone": params.timezone or DEFAULT_TIMEZONE,
            "timing": {
                "from": params.timing_from or "09:00",
                "to": params.timing_to or "17:00",
            },
            "days": {
                "0": False,  # Sunday
                "1": True,   # Monday
                "2": True,   # Tuesday
                "3": True,   # Wednesday
                "4": True,   # Thursday
                "5": True,   # Friday
                "6": False,  # Saturday
            }
        }]
    }

    # -------------------------------------------------------------------------
    # Sending limits with sensible defaults
    # -------------------------------------------------------------------------
    body["daily_limit"] = params.daily_limit if params.daily_limit else 30
    body["email_gap"] = params.email_gap if params.email_gap else 10
    body["stop_on_reply"] = params.stop_on_reply if params.stop_on_reply is not None else True
    body["stop_on_auto_reply"] = params.stop_on_auto_reply if params.stop_on_auto_reply is not None else True

    # =========================================================================
    # STEP 2: Make API Request
    # =========================================================================
    result = await client.post("/campaigns", json=body)

    # Add success metadata
    if isinstance(result, dict):
        result["_success"] = True
        result["_payload_used"] = body
        result["_message"] = "Campaign created successfully with API v2 compliant payload"

    return json.dumps(result, indent=2)


async def list_campaigns(params: Optional[ListCampaignsInput] = None) -> str:
    """
    List campaigns with cursor-based pagination (100 per page).
    
    PAGINATION: If response contains pagination.next_starting_after, there are 
    MORE results. Call again with starting_after=<that value> to get next page.
    Continue until pagination.next_starting_after is null.
    
    Note: search filters by campaign NAME only, not by status.
    To filter by status, use campaign_status in get_daily_campaign_analytics.
    
    Returns campaign list with status, lead counts, and performance metrics.
    """
    client = get_client()
    
    # Handle case where params is None (for OpenAI/non-Claude clients)
    # Set default limit=100 to return more results by default
    if params is None:
        params = ListCampaignsInput(limit=100)
    
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
    if params.tag_ids:
        query_params["tag_ids"] = params.tag_ids
    
    result = await client.get("/campaigns", params=query_params)
    
    # Add pagination guidance for LLMs
    if isinstance(result, dict):
        pagination = result.get("pagination", {})
        next_cursor = pagination.get("next_starting_after")
        if next_cursor:
            result["_pagination_hint"] = f"MORE RESULTS AVAILABLE. Call list_campaigns with starting_after='{next_cursor}' to get next page."
    
    return json.dumps(result, indent=2)


async def get_campaign(params: GetCampaignInput) -> str:
    """
    Get campaign details: config, sequences, schedules, sender accounts, tracking, status.
    
    Returns comprehensive campaign information including:
    - Email sequences and their content
    - Schedule configuration
    - Sender account assignments
    - Tracking settings (opens, clicks)
    - Campaign status and statistics
    """
    client = get_client()
    result = await client.get(f"/campaigns/{params.campaign_id}")
    return json.dumps(result, indent=2)


async def update_campaign(params: UpdateCampaignInput) -> str:
    """
    Update campaign settings (partial update).
    
    Common updates:
    - name: Campaign display name
    - sequences: Email sequence steps
    - email_list: Sender account assignments
    - daily_limit: Max emails per day per account
    - email_gap: Minutes between sends
    - open_tracking, link_tracking: Tracking toggles
    
    Only include fields you want to update.
    """
    client = get_client()
    
    body = {}
    
    # Add all optional fields if provided
    if params.name is not None:
        body["name"] = params.name
    if params.pl_value is not None:
        body["pl_value"] = params.pl_value
    if params.is_evergreen is not None:
        body["is_evergreen"] = params.is_evergreen
    if params.campaign_schedule is not None:
        body["campaign_schedule"] = params.campaign_schedule
    if params.sequences is not None:
        body["sequences"] = params.sequences
    if params.email_gap is not None:
        body["email_gap"] = params.email_gap
    if params.random_wait_max is not None:
        body["random_wait_max"] = params.random_wait_max
    if params.text_only is not None:
        body["text_only"] = params.text_only
    if params.email_list is not None:
        body["email_list"] = params.email_list
    if params.daily_limit is not None:
        body["daily_limit"] = params.daily_limit
    if params.stop_on_reply is not None:
        body["stop_on_reply"] = params.stop_on_reply
    if params.email_tag_list is not None:
        body["email_tag_list"] = params.email_tag_list
    if params.link_tracking is not None:
        body["link_tracking"] = params.link_tracking
    if params.open_tracking is not None:
        body["open_tracking"] = params.open_tracking
    if params.stop_on_auto_reply is not None:
        body["stop_on_auto_reply"] = params.stop_on_auto_reply
    if params.daily_max_leads is not None:
        body["daily_max_leads"] = params.daily_max_leads
    if params.prioritize_new_leads is not None:
        body["prioritize_new_leads"] = params.prioritize_new_leads
    if params.auto_variant_select is not None:
        body["auto_variant_select"] = params.auto_variant_select
    if params.match_lead_esp is not None:
        body["match_lead_esp"] = params.match_lead_esp
    if params.stop_for_company is not None:
        body["stop_for_company"] = params.stop_for_company
    if params.insert_unsubscribe_header is not None:
        body["insert_unsubscribe_header"] = params.insert_unsubscribe_header
    if params.allow_risky_contacts is not None:
        body["allow_risky_contacts"] = params.allow_risky_contacts
    if params.disable_bounce_protect is not None:
        body["disable_bounce_protect"] = params.disable_bounce_protect
    if params.cc_list is not None:
        body["cc_list"] = params.cc_list
    if params.bcc_list is not None:
        body["bcc_list"] = params.bcc_list
    
    result = await client.patch(f"/campaigns/{params.campaign_id}", json=body)
    return json.dumps(result, indent=2)


async def activate_campaign(params: ActivateCampaignInput) -> str:
    """
    Activate campaign to start sending.
    
    Prerequisites (all required):
    1. At least one sender account assigned (email_list)
    2. At least one lead added to the campaign
    3. Email sequences configured
    4. Schedule configured
    
    Use get_campaign to verify all prerequisites are met.
    """
    client = get_client()
    result = await client.post(f"/campaigns/{params.campaign_id}/activate")
    return json.dumps(result, indent=2)


async def pause_campaign(params: PauseCampaignInput) -> str:
    """
    Pause campaign to stop sending.

    Effects:
    - Immediately stops all email sending
    - Leads remain in the campaign
    - In-progress sequences are paused

    Use activate_campaign to resume sending.
    """
    client = get_client()
    result = await client.post(f"/campaigns/{params.campaign_id}/pause")
    return json.dumps(result, indent=2)


async def delete_campaign(params: DeleteCampaignInput) -> str:
    """
    🚨 PERMANENTLY delete a campaign. CANNOT UNDO!

    ⚠️ REQUIRES USER CONFIRMATION before executing!

    This action:
    - Permanently removes the campaign
    - Deletes all campaign data, sequences, and settings
    - Removes leads from this campaign (leads themselves are NOT deleted)
    - Cannot be reversed

    Before calling this tool, you MUST:
    1. Confirm with the user that they want to delete this campaign
    2. Verify the campaign_id is correct
    3. Warn them this action cannot be undone
    """
    client = get_client()
    result = await client.delete(f"/campaigns/{params.campaign_id}")
    return json.dumps({
        "success": True,
        "deleted_campaign_id": params.campaign_id,
        "message": "Campaign permanently deleted",
        **result
    }, indent=2)


async def search_campaigns_by_contact(params: SearchCampaignsByContactInput) -> str:
    """
    Find all campaigns that a specific contact/lead is part of.

    Useful for:
    - Checking if a lead is already in any campaigns
    - Finding duplicate enrollments
    - Auditing lead campaign membership

    Returns list of campaigns the contact email is enrolled in.
    """
    client = get_client()

    query_params = {"contact_email": params.contact_email}

    result = await client.get("/campaigns/search-by-contact", params=query_params)
    return json.dumps(result, indent=2)


# Export all campaign tools
CAMPAIGN_TOOLS = [
    create_campaign,
    list_campaigns,
    get_campaign,
    update_campaign,
    activate_campaign,
    pause_campaign,
    delete_campaign,
    search_campaigns_by_contact,
]

