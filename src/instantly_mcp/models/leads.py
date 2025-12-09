"""
Pydantic models for Lead and Lead List operations.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class ListLeadsInput(BaseModel):
    """Input for listing leads with pagination and filtering."""
    
    # Use extra="ignore" to be tolerant of unexpected fields from LLMs
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign: Optional[str] = Field(default=None, description="Campaign UUID")
    list_id: Optional[str] = Field(default=None, description="List UUID")
    list_ids: Optional[list[str]] = Field(default=None, description="Multiple list UUIDs")
    status: Optional[str] = Field(default=None)
    created_after: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    created_before: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    search: Optional[str] = Field(default=None, description="Name or email")
    filter: Optional[str] = Field(
        default=None,
        description="FILTER_VAL_CONTACTED, FILTER_VAL_NOT_CONTACTED, FILTER_VAL_COMPLETED, FILTER_VAL_ACTIVE, etc."
    )
    distinct_contacts: Optional[bool] = Field(default=None, description="Dedupe by email")
    limit: Optional[int] = Field(default=100, ge=1, le=100, description="Results per page (1-100, default: 100)")
    starting_after: Optional[str] = Field(
        default=None,
        description="Pagination cursor - use value from pagination.next_starting_after to get next page"
    )


class GetLeadInput(BaseModel):
    """Input for getting lead details."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    lead_id: str = Field(..., description="Lead UUID")


class CreateLeadInput(BaseModel):
    """
    Input for creating a lead with custom variables.
    
    Use skip_if_in_campaign to prevent duplicates.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    campaign: Optional[str] = Field(default=None, description="Campaign UUID")
    email: str = Field(..., description="Required - lead email address")
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    personalization: Optional[str] = Field(default=None)
    lt_interest_status: Optional[int] = Field(
        default=None, ge=-3, le=4,
        description="Interest status (-3 to 4)"
    )
    pl_value_lead: Optional[str] = Field(default=None, description="Pipeline value")
    list_id: Optional[str] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None, description="User UUID")
    skip_if_in_workspace: Optional[bool] = Field(default=None)
    skip_if_in_campaign: Optional[bool] = Field(default=None, description="Recommended")
    skip_if_in_list: Optional[bool] = Field(default=None)
    blocklist_id: Optional[str] = Field(default=None)
    verify_leads_on_import: Optional[bool] = Field(default=None)
    custom_variables: Optional[dict[str, Any]] = Field(
        default=None,
        description="Match campaign field names"
    )


class UpdateLeadInput(BaseModel):
    """
    Input for updating a lead (partial update).
    
    ⚠️ custom_variables replaces entire object - include existing values!
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    lead_id: str = Field(..., description="Lead UUID")
    personalization: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    lt_interest_status: Optional[int] = Field(default=None)
    pl_value_lead: Optional[str] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    custom_variables: Optional[dict[str, Any]] = Field(
        default=None,
        description="⚠️ REPLACES ALL - include existing values!"
    )


class ListLeadListsInput(BaseModel):
    """Input for listing lead lists with pagination."""
    
    # Use extra="ignore" to be tolerant of unexpected fields from LLMs
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    limit: Optional[int] = Field(default=100, ge=1, le=100, description="Results per page (1-100, default: 100)")
    starting_after: Optional[str] = Field(
        default=None, 
        description="Pagination cursor - use value from pagination.next_starting_after to get next page"
    )
    has_enrichment_task: Optional[bool] = Field(default=None)
    search: Optional[str] = Field(default=None, description="Search by name")


class CreateLeadListInput(BaseModel):
    """
    Input for creating a lead list.
    
    Set has_enrichment_task=true for auto-enrich.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    name: str = Field(..., description="List name")
    has_enrichment_task: Optional[bool] = Field(default=None)
    owned_by: Optional[str] = Field(default=None, description="Owner UUID")


class UpdateLeadListInput(BaseModel):
    """Input for updating a lead list."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    list_id: str = Field(..., description="List UUID")
    name: Optional[str] = Field(default=None)
    has_enrichment_task: Optional[bool] = Field(default=None)
    owned_by: Optional[str] = Field(default=None)


class GetVerificationStatsInput(BaseModel):
    """Input for getting email verification stats for a list."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    list_id: str = Field(..., description="List UUID")


class LeadData(BaseModel):
    """Single lead data for bulk operations."""
    
    model_config = ConfigDict(extra="ignore")
    
    email: str = Field(..., description="Lead email (required)")
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    personalization: Optional[str] = Field(default=None)
    lt_interest_status: Optional[int] = Field(default=None)
    pl_value_lead: Optional[str] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    custom_variables: Optional[dict[str, Any]] = Field(default=None)


class BulkAddLeadsInput(BaseModel):
    """
    Input for bulk adding leads (up to 1,000).
    
    10-100x faster than create_lead for large imports.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    leads: list[LeadData] = Field(
        ..., min_length=1, max_length=1000,
        description="1-1000 leads"
    )
    campaign_id: Optional[str] = Field(default=None, description="Use OR list_id")
    list_id: Optional[str] = Field(default=None, description="Use OR campaign_id")
    blocklist_id: Optional[str] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    verify_leads_on_import: Optional[bool] = Field(default=None)
    skip_if_in_workspace: Optional[bool] = Field(default=None)
    skip_if_in_campaign: Optional[bool] = Field(default=None, description="Recommended")
    skip_if_in_list: Optional[bool] = Field(default=None)


class DeleteLeadInput(BaseModel):
    """Input for deleting a lead. 🗑️ PERMANENTLY delete. CANNOT UNDO!"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    lead_id: str = Field(..., description="Lead UUID to DELETE")


class DeleteLeadListInput(BaseModel):
    """
    Input for deleting a lead list. ⚠️ PERMANENT - CANNOT UNDO!

    Requires user confirmation before executing.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    list_id: str = Field(..., description="Lead List UUID to DELETE PERMANENTLY")


class MoveLeadsInput(BaseModel):
    """
    Input for moving or copying leads between campaigns/lists.
    
    Runs as background job for large operations.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    to_campaign_id: Optional[str] = Field(
        default=None,
        description="Destination (OR to_list_id)"
    )
    to_list_id: Optional[str] = Field(
        default=None,
        description="Destination (OR to_campaign_id)"
    )
    ids: Optional[list[str]] = Field(default=None, description="Lead IDs")
    search: Optional[str] = Field(default=None)
    filter: Optional[str] = Field(default=None, description="Contact status filter")
    campaign: Optional[str] = Field(default=None, description="Source campaign")
    list_id: Optional[str] = Field(default=None, description="Source list")
    in_campaign: Optional[bool] = Field(default=None)
    in_list: Optional[bool] = Field(default=None)
    queries: Optional[list[dict[str, Any]]] = Field(default=None)
    excluded_ids: Optional[list[str]] = Field(default=None)
    contacts: Optional[list[str]] = Field(default=None)
    check_duplicates_in_campaigns: Optional[bool] = Field(default=None)
    skip_leads_in_verification: Optional[bool] = Field(default=None)
    limit: Optional[int] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    esp_code: Optional[int] = Field(
        default=None,
        description="0=Queue, 1=Google, 2=MS, etc."
    )
    esg_code: Optional[int] = Field(
        default=None,
        description="0=Queue, 1=Barracuda, etc."
    )
    copy_leads: Optional[bool] = Field(default=None, description="Copy instead of move")
    check_duplicates: Optional[bool] = Field(default=None)

