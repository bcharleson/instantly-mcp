"""
Pydantic models for SuperSearch Enrichment operations.

SuperSearch allows searching Instantly's lead database by ICP criteria
and enriching leads with contact information, company data, and AI-generated content.

💰 CREDIT-BASED: SuperSearch operations consume credits from your Instantly account.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Search Filter Models
# =============================================================================

class IncludeExcludeFilter(BaseModel):
    """Filter with include/exclude lists."""
    model_config = ConfigDict(extra="ignore")

    include: Optional[list[str]] = Field(default=None, description="Values to include")
    exclude: Optional[list[str]] = Field(default=None, description="Values to exclude")

    def model_dump(self, **kwargs) -> dict:
        """Override to only include non-empty fields."""
        # Use exclude_none to remove empty fields
        kwargs.setdefault("exclude_none", True)
        result = super().model_dump(**kwargs)

        # Remove empty arrays - API doesn't want them
        if "include" in result and (result["include"] is None or result["include"] == []):
            del result["include"]
        if "exclude" in result and (result["exclude"] is None or result["exclude"] == []):
            del result["exclude"]

        # If both are empty, return at least include as empty array
        if "include" not in result and "exclude" not in result:
            result["include"] = []

        return result


class LocationItem(BaseModel):
    """Single location specification."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    # Either use place_id OR city/state/country
    place_id: Optional[str] = Field(
        default=None,
        alias="placeId",
        serialization_alias="placeId",
        description="Google Place ID"
    )
    label: Optional[str] = Field(default=None, description="Display label for the location")
    city: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)

    def model_dump(self, **kwargs) -> dict:
        """Override to exclude None values - API doesn't want city/state/country as null."""
        # Always exclude None values for LocationItem
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class LocationFilter(BaseModel):
    """Location filter with include/exclude."""
    model_config = ConfigDict(extra="ignore")

    include: Optional[list[LocationItem]] = Field(default=None)
    exclude: Optional[list[LocationItem]] = Field(default=None)

    def model_dump(self, **kwargs) -> dict:
        """Override to only include specified fields - don't add exclude:[] if not specified."""
        kwargs.setdefault("exclude_none", True)
        # Don't use by_alias here since LocationItem handles its own serialization
        result = super().model_dump(**kwargs)
        return result


class SuperSearchFilters(BaseModel):
    """
    Filters for SuperSearch lead discovery.

    Use these to define your Ideal Customer Profile (ICP).
    All filters are optional - combine as needed.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    # Location
    locations: Optional[LocationFilter] = Field(
        default=None,
        description="Filter by location (city/state/country or place_id)"
    )

    # Job-related filters
    title: Optional[IncludeExcludeFilter] = Field(
        default=None,
        description="Job titles filter with include/exclude. E.g., IncludeExcludeFilter(include=['CEO', 'CTO'])"
    )
    department: Optional[list[str]] = Field(
        default=None,
        description="Departments: Engineering, Finance & Administration, Human Resources, IT & IS, Marketing, Operations, Sales, Support, Other"
    )
    level: Optional[list[str]] = Field(
        default=None,
        description="Seniority levels: C-Level, VP-Level, Director-Level, Manager-Level, Staff, Entry level, Mid-Senior level, Director, Associate, Owner"
    )

    # Company-related filters
    company_name: Optional[IncludeExcludeFilter] = Field(
        default=None,
        alias="companyName",
        serialization_alias="company_name",
        description="Company names filter with include/exclude"
    )
    industry: Optional[IncludeExcludeFilter] = Field(
        default=None,
        description="Industries filter with include/exclude. E.g., IncludeExcludeFilter(include=['Technology', 'Software'])"
    )
    employee_count: Optional[list[str]] = Field(
        default=None,
        alias="employeeCount",
        serialization_alias="employee_count",
        description="Company size ranges: '0 - 25', '25 - 100', '100 - 250', '250 - 1000', '1K - 10K', '10K - 50K', '50K - 100K', '> 100K'"
    )
    revenue: Optional[list[str]] = Field(
        default=None,
        description="Revenue ranges: '$0 - 1M', '$1 - 10M', '$10 - 50M', '$50 - 100M', '$100 - 250M', '$250 - 500M', '$500M - 1B', '> $1B'"
    )
    domains: Optional[list[str]] = Field(
        default=None,
        description="Specific company domains to search"
    )

    # Advanced
    look_alike: Optional[str] = Field(
        default=None,
        alias="lookAlike",
        serialization_alias="look_alike",
        description="Find companies similar to this domain"
    )
    keyword_filter: Optional[IncludeExcludeFilter] = Field(
        default=None,
        alias="keywordFilter",
        serialization_alias="keyword_filter",
        description="Keywords filter with include/exclude for company descriptions"
    )
    funding_type: Optional[list[str]] = Field(
        default=None,
        alias="fundingType",
        serialization_alias="funding_type",
        description="Funding stages: angel, seed, pre_seed, series_a, series_b, series_c, series_d, series_e, series_f, series_g"
    )
    news: Optional[list[str]] = Field(
        default=None,
        description="Company news triggers: launches, expands_offices_to, hires, partners_with, leaves, receives_financing, recognized_as, closes_offices_in, is_developing, has_issues_with"
    )

    # Boolean options - default to false (API requires these to be present)
    skip_owned_leads: bool = Field(
        default=False,
        alias="skipOwnedLeads",
        serialization_alias="skip_owned_leads",
        description="Skip leads already owned by the user"
    )
    show_one_lead_per_company: bool = Field(
        default=False,
        alias="showOneLeadPerCompany",
        serialization_alias="show_one_lead_per_company",
        description="Show only one lead per company"
    )


# =============================================================================
# Enrichment Type Definitions
# =============================================================================

EnrichmentType = Literal[
    "work_email_enrichment",      # Find work email addresses
    "fully_enriched_profile",     # LinkedIn enrichment (full profile)
    "email_verification",         # Verify email deliverability
    "joblisting",                 # Job listing enrichment
    "technologies",               # Tech stack enrichment
    "news",                       # Company news enrichment
    "funding",                    # Funding information
    "ai_enrichment",              # AI-powered enrichment
    "custom_flow",                # Custom enrichment flow
]

AIModelType = Literal[
    "gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-4.1",
    "claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku",
    "gemini-1.5-pro", "gemini-1.5-flash",
    "grok-2",
    "perplexity-sonar",
    "instantly-ai-agent",
]


# =============================================================================
# Tool Input Models
# =============================================================================

class SearchSuperSearchLeadsInput(BaseModel):
    """
    Input for searching SuperSearch and importing leads.
    
    💰 CREDITS: Each lead found/enriched consumes credits.
    Use 'limit' to control costs.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    # Where to import leads
    list_id: Optional[str] = Field(
        default=None,
        description="Import leads to this list (OR campaign_id)"
    )
    campaign_id: Optional[str] = Field(
        default=None,
        description="Import leads to this campaign (OR list_id)"
    )
    
    # Search filters
    search_filters: SuperSearchFilters = Field(
        ...,
        description="ICP filters to find matching leads"
    )
    
    # Enrichment options
    enrichment_types: Optional[list[EnrichmentType]] = Field(
        default=None,
        description="Types of enrichment to apply. Default: work_email_enrichment"
    )
    
    # Limits
    limit: Optional[int] = Field(
        default=100,
        ge=1,
        le=10000,
        description="Max leads to import (1-10000). Start small to control costs!"
    )

    # Optional naming
    search_name: Optional[str] = Field(
        default=None,
        description="Name for this search (for tracking purposes)"
    )
    list_name: Optional[str] = Field(
        default=None,
        description="Name for new list if no resource_id provided"
    )


class GetEnrichmentStatusInput(BaseModel):
    """Input for checking enrichment status."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    resource_id: str = Field(
        ...,
        description="List or Campaign UUID to check enrichment status for"
    )


class CreateEnrichmentInput(BaseModel):
    """
    Input for creating enrichment on existing leads.

    Use this to enrich leads already in a list/campaign (not from SuperSearch).
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    resource_id: str = Field(
        ...,
        description="List or Campaign UUID containing leads to enrich"
    )
    enrichment_type: EnrichmentType = Field(
        default="work_email_enrichment",
        description="Type of enrichment to apply"
    )
    auto_update: Optional[bool] = Field(
        default=None,
        description="Automatically enrich new leads added to this resource"
    )
    is_evergreen: Optional[bool] = Field(
        default=None,
        description="Keep enriching to maintain data freshness"
    )
    skip_already_enriched: Optional[bool] = Field(
        default=True,
        description="Skip leads that were already enriched"
    )


class CreateAIEnrichmentInput(BaseModel):
    """
    Input for creating AI-powered enrichment.

    AI enrichment runs a custom prompt through an LLM for each lead,
    storing the result in a new column.

    Use cases:
    - Personalized email openers
    - Lead scoring
    - Company research summaries
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    resource_id: str = Field(
        ...,
        description="List or Campaign UUID"
    )
    prompt: str = Field(
        ...,
        description="Prompt template. Use {{column_name}} for lead data. E.g., 'Write a personalized intro for {{first_name}} at {{company_name}}'"
    )
    output_column: str = Field(
        ...,
        description="Column name to store AI output"
    )
    model: AIModelType = Field(
        default="gpt-4o-mini",
        description="AI model to use"
    )
    input_columns: Optional[list[str]] = Field(
        default=None,
        description="Lead columns to include as context (auto-detected from prompt if not specified)"
    )


class RunEnrichmentInput(BaseModel):
    """
    Input for manually triggering enrichment on specific leads.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    resource_id: str = Field(
        ...,
        description="List or Campaign UUID"
    )
    lead_ids: Optional[list[str]] = Field(
        default=None,
        description="Specific lead IDs to enrich (if not provided, enriches all)"
    )
    enrichment_type: Optional[EnrichmentType] = Field(
        default=None,
        description="Type of enrichment to run (uses resource default if not specified)"
    )


class GetEnrichmentHistoryInput(BaseModel):
    """Input for getting enrichment history."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    resource_id: str = Field(
        ...,
        description="List or Campaign UUID"
    )
    limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=100,
        description="Max history entries to return"
    )
    starting_after: Optional[str] = Field(
        default=None,
        description="Pagination cursor"
    )

