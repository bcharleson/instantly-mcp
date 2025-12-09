"""
Pydantic models for Campaign operations.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

# Default timezone for business operations
# NOTE: Instantly.ai officially recommends America/Chicago as default
# America/New_York is mapped to America/Detroit in Instantly.ai's verified timezone list
DEFAULT_TIMEZONE = "America/Chicago"
BUSINESS_PRIORITY_TIMEZONES = [
    "America/Chicago",      # Central Time (US) - RECOMMENDED DEFAULT
    "America/Detroit",      # Eastern Time (US) - maps from America/New_York
    "America/Boise",        # Mountain Time (US) - maps from America/Denver
    "America/Dawson",       # Pacific Time (US) - maps from America/Los_Angeles
    "Europe/Belgrade",      # Central European Time
    "Asia/Dubai",           # Gulf Standard Time
    "Asia/Hong_Kong",       # Hong Kong Time
    "Australia/Melbourne",  # Australian Eastern Time
]


class CreateCampaignInput(BaseModel):
    """
    Input for creating an email campaign.
    
    Two-step process:
    1) Call with name/subject/body to discover available sender accounts
    2) Call again with email_list to assign senders
    
    Use sequence_steps for multi-step email sequences.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    name: str = Field(..., description="Campaign name")
    subject: str = Field(
        ..., max_length=100,
        description="Subject (<50 chars recommended). Personalization: {{firstName}}, {{companyName}}"
    )
    body: str = Field(
        ...,
        description="Email body (\\n for line breaks). Personalization: {{firstName}}, {{lastName}}, {{companyName}}"
    )
    email_list: Optional[list[str]] = Field(
        default=None,
        description="Sender emails (from Step 1 eligible list)"
    )
    track_opens: Optional[bool] = Field(default=False)
    track_clicks: Optional[bool] = Field(default=False)
    timezone: Optional[str] = Field(
        default=DEFAULT_TIMEZONE,
        description=f"Supported: {', '.join(BUSINESS_PRIORITY_TIMEZONES[:5])}..."
    )
    timing_from: Optional[str] = Field(default="09:00", description="24h format start time")
    timing_to: Optional[str] = Field(default="17:00", description="24h format end time")
    daily_limit: Optional[int] = Field(
        default=30, ge=1, le=50,
        description="Emails/day/account (max 50)"
    )
    email_gap: Optional[int] = Field(
        default=10, ge=1, le=1440,
        description="Minutes between emails (1-1440)"
    )
    stop_on_reply: Optional[bool] = Field(default=True)
    stop_on_auto_reply: Optional[bool] = Field(default=True)
    sequence_steps: Optional[int] = Field(
        default=1, ge=1, le=10,
        description="Steps in sequence (1-10)"
    )
    step_delay_days: Optional[int] = Field(
        default=3, ge=1, le=30,
        description="Days between steps (1-30)"
    )
    sequence_subjects: Optional[list[str]] = Field(
        default=None,
        description="Custom subjects per step"
    )
    sequence_bodies: Optional[list[str]] = Field(
        default=None,
        description="Custom bodies per step"
    )


class ListCampaignsInput(BaseModel):
    """Input for listing campaigns with pagination."""
    
    # Use extra="ignore" to be tolerant of unexpected fields from LLMs
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    limit: Optional[int] = Field(
        default=100, ge=1, le=100,
        description="Results per page (1-100, default: 100)"
    )
    starting_after: Optional[str] = Field(
        default=None,
        description="Pagination cursor - use value from pagination.next_starting_after to get next page"
    )
    search: Optional[str] = Field(
        default=None,
        description="Search by campaign NAME only (not status)"
    )
    tag_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated tag IDs"
    )


class GetCampaignInput(BaseModel):
    """Input for getting campaign details."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign_id: str = Field(..., description="Campaign UUID")


class UpdateCampaignInput(BaseModel):
    """
    Input for updating campaign settings (partial update).
    
    Common updates: name, sequences, tracking, limits, email_list.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign_id: str = Field(..., description="Campaign to update")
    name: Optional[str] = Field(default=None)
    pl_value: Optional[float] = Field(default=None, description="Pipeline value")
    is_evergreen: Optional[bool] = Field(default=None)
    campaign_schedule: Optional[dict[str, Any]] = Field(
        default=None,
        description="Schedule configuration with 'schedules' array"
    )
    sequences: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Email sequence steps"
    )
    email_gap: Optional[int] = Field(default=None, ge=1, le=1440)
    random_wait_max: Optional[int] = Field(default=None)
    text_only: Optional[bool] = Field(default=None)
    email_list: Optional[list[str]] = Field(default=None, description="Sender accounts")
    daily_limit: Optional[int] = Field(default=None, ge=1, le=50)
    stop_on_reply: Optional[bool] = Field(default=None)
    email_tag_list: Optional[list[str]] = Field(default=None)
    link_tracking: Optional[bool] = Field(default=None)
    open_tracking: Optional[bool] = Field(default=None)
    stop_on_auto_reply: Optional[bool] = Field(default=None)
    daily_max_leads: Optional[int] = Field(default=None)
    prioritize_new_leads: Optional[bool] = Field(default=None)
    auto_variant_select: Optional[dict[str, Any]] = Field(default=None)
    match_lead_esp: Optional[bool] = Field(default=None)
    stop_for_company: Optional[bool] = Field(default=None)
    insert_unsubscribe_header: Optional[bool] = Field(default=None)
    allow_risky_contacts: Optional[bool] = Field(default=None)
    disable_bounce_protect: Optional[bool] = Field(default=None)
    cc_list: Optional[list[str]] = Field(default=None)
    bcc_list: Optional[list[str]] = Field(default=None)


class ActivateCampaignInput(BaseModel):
    """
    Input for activating a campaign.
    
    Prerequisites: accounts, leads, sequences, schedule must be configured.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign_id: str = Field(..., description="Campaign UUID to activate")


class PauseCampaignInput(BaseModel):
    """
    Input for pausing a campaign.

    Stops sending but leads remain. Use activate_campaign to resume.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    campaign_id: str = Field(..., description="Active campaign UUID")


class DeleteCampaignInput(BaseModel):
    """
    Input for deleting a campaign. ⚠️ PERMANENT - CANNOT UNDO!

    Requires user confirmation before executing.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    campaign_id: str = Field(..., description="Campaign UUID to DELETE PERMANENTLY")


class SearchCampaignsByContactInput(BaseModel):
    """
    Input for searching campaigns by contact email.

    Finds all campaigns a specific lead/contact is enrolled in.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    contact_email: str = Field(..., description="Email address of the contact to search for")

