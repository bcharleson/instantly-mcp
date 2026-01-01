"""
Instantly MCP Server - SuperSearch Enrichment Tools

9 tools for lead discovery and enrichment using Instantly's SuperSearch.

SuperSearch allows you to:
1. Search Instantly's lead database by ICP (Ideal Customer Profile)
2. Import matching leads to campaigns/lists
3. Enrich leads with contact info, company data, and AI-generated content

💰 CREDIT-BASED: Most SuperSearch operations consume credits from your Instantly account.
💡 FREE TOOLS: count_leads and preview_leads are free and help you validate searches before committing credits.
"""

import json
from typing import Any, Optional

from ..client import get_client
from ..models.supersearch import (
    SearchSuperSearchLeadsInput,
    GetEnrichmentStatusInput,
    CreateEnrichmentInput,
    CreateAIEnrichmentInput,
    RunEnrichmentInput,
    GetEnrichmentHistoryInput,
    CountLeadsInput,
    PreviewLeadsInput,
    UpdateEnrichmentSettingsInput,
)


async def search_supersearch_leads(params: SearchSuperSearchLeadsInput) -> str:
    """
    🔍 Search SuperSearch for leads matching your ICP and import them.

    💰 CREDITS: Each lead imported consumes credits. Use 'limit' to control costs.
    💡 TIP: Use count_leads or preview_leads FIRST (free) to validate your search.

    ⏳ ASYNC OPERATION: Enrichment runs in the background. The response returns immediately
    with a resource_id, but enrichment may take seconds to minutes depending on volume.

    RECOMMENDED WORKFLOW:
    1. count_leads - Free, get the count matching your criteria
    2. preview_leads - Free, see sample leads before committing
    3. search_supersearch_leads - Paid, import and enrich leads
    4. get_enrichment_status - Check if enrichment is complete (in_progress: true/false)
    5. list_leads - Retrieve the enriched leads once complete

    Example filters:
    - CEOs: title.include=["CEO", "Chief Executive Officer"]
    - Sales VPs in California: department=["Sales"], level=["VP-Level"], locations.include=[{state: "California", country: "United States"}]
    - Small tech companies: employeeCount=["25 - 100"], industry.include=["Software"]
    """
    client = get_client()

    # Build search_filters - use mode='json' to apply serialization_alias (snake_case for API)
    # Note: skip_owned_leads and show_one_lead_per_company need to be present even as false
    raw_filters = params.search_filters.model_dump(mode='json', exclude_none=True)

    # Clean up None values - most fields are simple arrays now
    # Only locations uses the {"include": [...]} format
    search_filters: dict[str, Any] = {}
    for key, value in raw_filters.items():
        if value is None:
            continue
        search_filters[key] = value

    # Ensure boolean flags are always present (API requires them)
    if "skip_owned_leads" not in search_filters:
        search_filters["skip_owned_leads"] = False
    if "show_one_lead_per_company" not in search_filters:
        search_filters["show_one_lead_per_company"] = False

    body: dict[str, Any] = {
        "search_filters": search_filters,
    }

    # API uses resource_id for both lists and campaigns
    if params.list_id:
        body["resource_id"] = params.list_id
        body["resource_type"] = 2  # 2 = List
    if params.campaign_id:
        body["resource_id"] = params.campaign_id
        body["resource_type"] = 1  # 1 = Campaign

    # Handle enrichment types - API expects top-level boolean flags
    if params.enrichment_types:
        for etype in params.enrichment_types:
            body[etype] = True
    else:
        # Default to work email enrichment
        body["work_email_enrichment"] = True

    if params.limit:
        body["limit"] = params.limit

    # Optional naming fields
    if params.search_name:
        body["search_name"] = params.search_name
    if params.list_name:
        body["list_name"] = params.list_name

    try:
        result = await client.post("/supersearch-enrichment/enrich-leads-from-supersearch", json=body)
    except Exception as e:
        # Return debug info on error
        return json.dumps({
            "error": str(e),
            "debug_payload": body
        }, indent=2)
    
    # Add guidance for next steps
    if isinstance(result, dict):
        resource_id = result.get("resource_id") or result.get("list_id") or result.get("campaign_id")
        if resource_id:
            result["_next_steps"] = (
                f"Enrichment started. Use get_enrichment_status(resource_id='{resource_id}') "
                f"to check progress, then list_leads to retrieve results."
            )
    
    return json.dumps(result, indent=2)


async def get_enrichment_status(params: GetEnrichmentStatusInput) -> str:
    """
    Check enrichment status for a list or campaign.
    
    Returns:
    - Enrichment configuration (types, settings)
    - Progress (leads enriched, pending, failed)
    - Credit usage
    - Last run timestamp
    
    Use this after search_supersearch_leads or create_enrichment
    to monitor progress.
    """
    client = get_client()
    result = await client.get(f"/supersearch-enrichment/{params.resource_id}")
    return json.dumps(result, indent=2)


async def create_enrichment(params: CreateEnrichmentInput) -> str:
    """
    Create enrichment for existing leads in a list or campaign.
    
    Use this when you have leads already imported and want to enrich them.
    For finding NEW leads, use search_supersearch_leads instead.
    
    💰 CREDITS: Enrichment consumes credits based on leads and enrichment type.
    
    Enrichment types:
    - work_email_enrichment: Find work email addresses
    - fully_enriched_profile: LinkedIn enrichment (name, title, company, etc.)
    - email_verification: Verify email deliverability
    - technologies: Company tech stack
    - news: Recent company news
    - funding: Funding information
    """
    client = get_client()
    
    body: dict[str, Any] = {
        "resource_id": params.resource_id,
        "type": params.enrichment_type,  # API uses 'type' not 'enrichment_type'
    }
    
    if params.auto_update is not None:
        body["auto_update"] = params.auto_update
    if params.is_evergreen is not None:
        body["is_evergreen"] = params.is_evergreen
    if params.skip_already_enriched is not None:
        body["skip_already_enriched"] = params.skip_already_enriched
    
    result = await client.post("/supersearch-enrichment", json=body)

    # Add guidance
    if isinstance(result, dict):
        result["_next_steps"] = (
            f"Enrichment created. Use get_enrichment_status(resource_id='{params.resource_id}') "
            f"to check progress."
        )

    return json.dumps(result, indent=2)


async def create_ai_enrichment(params: CreateAIEnrichmentInput) -> str:
    """
    Create AI-powered enrichment with custom prompts.

    This runs an LLM on each lead to generate custom content.
    Results are stored in the specified output_column.

    💰 CREDITS: AI enrichment costs vary by model.

    Use cases:
    - Personalized email openers: "Write a warm intro for {{first_name}} who is {{jobTitle}} at {{companyName}}"
    - Lead scoring: "Rate this lead 1-10 based on: Title: {{jobTitle}}, Company: {{companyName}}"
    - Research: "Summarize what {{companyName}} does in 2 sentences"

    Available model_version values:
    - "gpt-4.1-mini" (recommended - fast & cost-effective)
    - "3.5" (GPT-3.5 Turbo)
    - "4.0" (GPT-4)
    - "gpt-4o" (GPT-4o)
    - "gpt-4.1" (GPT-4.1)
    - "claude-3.7-sonnet" (Claude 3.7 Sonnet)
    - "o3" (OpenAI o3)

    ⏳ ASYNC: This operation runs in the background. Use get_enrichment_status to check progress.
    """
    client = get_client()

    body: dict[str, Any] = {
        "resource_id": params.resource_id,
        "resource_type": params.resource_type,  # 1=Campaign, 2=List
        "prompt": params.prompt,
        "output_column": params.output_column,
        "model_version": params.model_version,
    }

    if params.input_columns:
        body["input_columns"] = params.input_columns
    if params.overwrite is not None:
        body["overwrite"] = params.overwrite
    if params.auto_update is not None:
        body["auto_update"] = params.auto_update
    if params.limit is not None:
        body["limit"] = params.limit

    try:
        result = await client.post("/supersearch-enrichment/ai", json=body)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "debug_payload": body,
            "hint": "Check that model_version is one of: 3.5, 4.0, gpt-4o, gpt-4.1, gpt-4.1-mini, claude-3.7-sonnet, o3"
        }, indent=2)

    if isinstance(result, dict):
        result["_next_steps"] = (
            f"AI enrichment started. Use get_enrichment_status(resource_id='{params.resource_id}') "
            f"to check progress. Results will appear in the '{params.output_column}' column."
        )

    return json.dumps(result, indent=2)


async def run_enrichment(params: RunEnrichmentInput) -> str:
    """
    Manually trigger enrichment on specific leads or all leads in a resource.

    Use this to:
    - Re-run enrichment on specific leads that failed
    - Enrich newly added leads that weren't auto-enriched
    - Run a different enrichment type on existing leads

    If lead_ids is not provided, enriches all unenriched leads in the resource.
    """
    client = get_client()

    body: dict[str, Any] = {
        "resource_id": params.resource_id,
    }

    if params.lead_ids:
        body["lead_ids"] = params.lead_ids
    if params.enrichment_type:
        body["enrichment_type"] = params.enrichment_type

    result = await client.post("/supersearch-enrichment/run", json=body)

    if isinstance(result, dict):
        result["_next_steps"] = (
            f"Enrichment triggered. Use get_enrichment_status(resource_id='{params.resource_id}') "
            f"to check progress."
        )

    return json.dumps(result, indent=2)


async def get_enrichment_history(params: GetEnrichmentHistoryInput) -> str:
    """
    Get enrichment history for a list or campaign.

    Returns past enrichment runs including:
    - Run timestamps
    - Enrichment types used
    - Leads processed/enriched/failed
    - Credits consumed

    Useful for auditing and debugging enrichment issues.

    PAGINATION: If response contains pagination.next_starting_after,
    call again with starting_after=<that value> for more results.
    """
    client = get_client()

    query_params: dict[str, Any] = {}
    if params.limit:
        query_params["limit"] = params.limit
    if params.starting_after:
        query_params["starting_after"] = params.starting_after

    result = await client.get(
        f"/supersearch-enrichment/history/{params.resource_id}",
        params=query_params
    )

    # Add pagination guidance
    if isinstance(result, dict):
        pagination = result.get("pagination", {})
        next_cursor = pagination.get("next_starting_after")
        if next_cursor:
            result["_pagination_hint"] = (
                f"MORE RESULTS AVAILABLE. Call get_enrichment_history with "
                f"starting_after='{next_cursor}' to get next page."
            )

    return json.dumps(result, indent=2)


async def count_leads(params: CountLeadsInput) -> str:
    """
    Count leads matching your ICP criteria WITHOUT consuming credits.

    ✅ FREE OPERATION - Use this before search_supersearch_leads to:
    - Estimate the size of your target audience
    - Validate your search filters work as expected
    - Make informed decisions about credit usage

    Returns the number of leads matching your criteria (capped at 1,000,000).
    A count of 0 means no leads match the specified filters.
    """
    client = get_client()

    raw_filters = params.search_filters.model_dump(mode='json', exclude_none=True)
    search_filters: dict[str, Any] = {}
    for key, value in raw_filters.items():
        if value is not None:
            search_filters[key] = value

    if "skip_owned_leads" not in search_filters:
        search_filters["skip_owned_leads"] = False
    if "show_one_lead_per_company" not in search_filters:
        search_filters["show_one_lead_per_company"] = False

    body: dict[str, Any] = {"search_filters": search_filters}

    try:
        result = await client.post("/supersearch-enrichment/count-leads-from-supersearch", json=body)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "debug_payload": body
        }, indent=2)

    if isinstance(result, dict):
        count = result.get("number_of_leads", 0)
        result["_guidance"] = (
            f"Found {count:,} leads matching your criteria. "
            f"To import and enrich these leads, use search_supersearch_leads with the same filters."
        )

    return json.dumps(result, indent=2)


async def preview_leads(params: PreviewLeadsInput) -> str:
    """
    Preview sample leads matching your ICP criteria WITHOUT consuming credits.

    ✅ FREE OPERATION - Use this before search_supersearch_leads to:
    - See real examples of leads that match your criteria
    - Verify the quality and relevance of potential leads
    - Review titles, companies, and locations before committing credits

    Returns up to 10 sample leads for review.
    """
    client = get_client()

    raw_filters = params.search_filters.model_dump(mode='json', exclude_none=True)
    search_filters: dict[str, Any] = {}
    for key, value in raw_filters.items():
        if value is not None:
            search_filters[key] = value

    if "skip_owned_leads" not in search_filters:
        search_filters["skip_owned_leads"] = False
    if "show_one_lead_per_company" not in search_filters:
        search_filters["show_one_lead_per_company"] = False

    body: dict[str, Any] = {"search_filters": search_filters}

    try:
        result = await client.post("/supersearch-enrichment/preview-leads-from-supersearch", json=body)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "debug_payload": body
        }, indent=2)

    if isinstance(result, dict):
        count = result.get("number_of_leads", 0)
        leads = result.get("leads", [])
        result["_guidance"] = (
            f"Previewing {len(leads)} sample leads from {count:,} total matches. "
            f"To import and enrich these leads, use search_supersearch_leads with the same filters."
        )

    return json.dumps(result, indent=2)


async def update_enrichment_settings(params: UpdateEnrichmentSettingsInput) -> str:
    """
    Update enrichment settings for a list or campaign.

    Settings you can modify:
    - auto_update: Automatically enrich new leads added to this resource
    - skip_rows_without_email: Skip leads that don't have an email address
    - is_evergreen: Keep enriching periodically to maintain data freshness
    """
    client = get_client()

    body: dict[str, Any] = {}
    if params.auto_update is not None:
        body["auto_update"] = params.auto_update
    if params.skip_rows_without_email is not None:
        body["skip_rows_without_email"] = params.skip_rows_without_email
    if params.is_evergreen is not None:
        body["is_evergreen"] = params.is_evergreen

    if not body:
        return json.dumps({
            "error": "No settings provided to update",
            "hint": "Provide at least one of: auto_update, skip_rows_without_email, is_evergreen"
        }, indent=2)

    try:
        result = await client.patch(
            f"/supersearch-enrichment/{params.resource_id}/settings",
            json=body
        )
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "debug_payload": body
        }, indent=2)

    return json.dumps(result, indent=2)


# Export all SuperSearch tools
# Order matters for AI guidance: free tools first, then credit-consuming tools
SUPERSEARCH_TOOLS = [
    # FREE: Preview/count before committing credits
    count_leads,
    preview_leads,
    # PAID: Core enrichment operations
    search_supersearch_leads,
    get_enrichment_status,
    create_enrichment,
    create_ai_enrichment,
    run_enrichment,
    get_enrichment_history,
    update_enrichment_settings,
]

