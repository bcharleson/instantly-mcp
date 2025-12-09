"""
Instantly MCP Server - SuperSearch Enrichment Tools

6 tools for lead discovery and enrichment using Instantly's SuperSearch.

SuperSearch allows you to:
1. Search Instantly's lead database by ICP (Ideal Customer Profile)
2. Import matching leads to campaigns/lists
3. Enrich leads with contact info, company data, and AI-generated content

💰 CREDIT-BASED: All SuperSearch operations consume credits from your Instantly account.
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
)


async def search_supersearch_leads(params: SearchSuperSearchLeadsInput) -> str:
    """
    🔍 Search SuperSearch for leads matching your ICP and import them.
    
    💰 CREDITS: Each lead found/enriched consumes credits. Use 'limit' to control costs.
    
    This is the primary SuperSearch tool. It:
    1. Searches Instantly's database using your ICP filters
    2. Imports matching leads to your specified list or campaign
    3. Automatically enriches them with the requested enrichment types
    
    WORKFLOW:
    1. Call this tool with your ICP filters
    2. Returns a resource_id (list/campaign where leads were added)
    3. Use get_enrichment_status to check progress
    4. Use list_leads to retrieve the enriched leads
    
    Example filters:
    - Find CEOs at tech companies: title.include=["CEO"], industry.include=["Technology"]
    - Find sales leaders in California: department=["Sales"], level=["Director-Level", "VP-Level"], locations.include=[{state: "California", country: "United States"}]
    """
    client = get_client()

    body: dict[str, Any] = {
        "search_filters": params.search_filters.model_dump(exclude_none=True),
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

    result = await client.post("/supersearch-enrichment/enrich-leads-from-supersearch", json=body)
    
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
        "enrichment_type": params.enrichment_type,
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

    💰 CREDITS: AI enrichment costs vary by model. GPT-4o-mini is most cost-effective.

    Use cases:
    - Personalized email openers: "Write a warm intro for {{first_name}} who is {{title}} at {{company_name}}"
    - Lead scoring: "Rate this lead 1-10 based on: Title: {{title}}, Company: {{company_name}}, Industry: {{industry}}"
    - Research: "Summarize what {{company_name}} does in 2 sentences"

    Available models:
    - gpt-4o-mini (recommended - fast & cheap)
    - gpt-4o, gpt-4
    - claude-3-5-sonnet, claude-3-opus, claude-3-haiku
    - gemini-1.5-pro, gemini-1.5-flash
    - instantly-ai-agent (Instantly's own AI)
    """
    client = get_client()

    body: dict[str, Any] = {
        "resource_id": params.resource_id,
        "prompt": params.prompt,
        "output_column": params.output_column,
        "model": params.model,
    }

    if params.input_columns:
        body["input_columns"] = params.input_columns

    result = await client.post("/supersearch-enrichment/ai", json=body)

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


# Export all SuperSearch tools
SUPERSEARCH_TOOLS = [
    search_supersearch_leads,
    get_enrichment_status,
    create_enrichment,
    create_ai_enrichment,
    run_enrichment,
    get_enrichment_history,
]

