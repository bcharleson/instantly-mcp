#!/usr/bin/env python3
"""
Manual test script for SuperSearch functionality.

This script allows you to test SuperSearch tools with real API calls.
Set your INSTANTLY_API_KEY environment variable before running.

Usage:
    export INSTANTLY_API_KEY="your-api-key"
    python test_supersearch.py
"""

import asyncio
import json
import os
import sys
from typing import Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from instantly_mcp.client import InstantlyClient
from instantly_mcp.models.supersearch import (
    SearchSuperSearchLeadsInput,
    SuperSearchFilters,
    LocationFilter,
    LocationItem,
    IncludeExcludeFilter,
    GetEnrichmentStatusInput,
    GetEnrichmentHistoryInput,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(result: Any):
    """Pretty print a result."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except:
            pass
    print(json.dumps(result, indent=2))


async def test_search_basic():
    """Test basic SuperSearch with simple filters."""
    print_section("TEST 1: Basic Search - CEOs in Technology")

    from instantly_mcp.tools.supersearch import search_supersearch_leads

    params = SearchSuperSearchLeadsInput(
        list_id=None,  # Will create a new list
        list_name="Test SuperSearch - CEOs in Tech",
        search_filters=SuperSearchFilters(
            title=IncludeExcludeFilter(include=["CEO", "Chief Executive Officer"]),
            industry=IncludeExcludeFilter(include=["Technology", "Software"]),
        ),
        limit=5,  # Small limit for testing
        search_name="Test Search - CEOs"
    )

    result = await search_supersearch_leads(params)
    print_result(result)

    return result


async def test_search_with_location():
    """Test SuperSearch with location filters."""
    print_section("TEST 2: Search with Location - Sales Leaders in California")
    
    from instantly_mcp.tools.supersearch import search_supersearch_leads
    
    params = SearchSuperSearchLeadsInput(
        list_name="Test SuperSearch - CA Sales Leaders",
        search_filters=SuperSearchFilters(
            department=["Sales"],
            level=["Director-Level", "VP-Level"],
            locations=LocationFilter(
                include=[
                    LocationItem(state="California", country="United States")
                ]
            ),
        ),
        limit=3,
        search_name="Test Search - CA Sales"
    )
    
    result = await search_supersearch_leads(params)
    print_result(result)
    
    return result


async def test_enrichment_status(resource_id: str):
    """Test getting enrichment status."""
    print_section(f"TEST 3: Get Enrichment Status for {resource_id}")
    
    from instantly_mcp.tools.supersearch import get_enrichment_status
    
    params = GetEnrichmentStatusInput(resource_id=resource_id)
    result = await get_enrichment_status(params)
    print_result(result)
    
    return result


async def test_enrichment_history():
    """Test getting enrichment history."""
    print_section("TEST 4: Get Enrichment History")
    
    from instantly_mcp.tools.supersearch import get_enrichment_history
    
    params = GetEnrichmentHistoryInput(limit=5)
    result = await get_enrichment_history(params)
    print_result(result)
    
    return result


async def main():
    """Run all tests."""
    # Check for API key
    api_key = os.environ.get("INSTANTLY_API_KEY")
    if not api_key:
        print("❌ ERROR: INSTANTLY_API_KEY environment variable not set!")
        print("\nPlease set your API key:")
        print("  export INSTANTLY_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print(f"✓ API Key found: {api_key[:10]}...")
    
    try:
        # Test 1: Basic search
        result1 = await test_search_basic()
        
        # Test 2: Search with location
        result2 = await test_search_with_location()
        
        # Test 3: Get enrichment history
        await test_enrichment_history()
        
        # Test 4: Check status of first search (if we got a resource_id)
        try:
            result1_data = json.loads(result1) if isinstance(result1, str) else result1
            resource_id = result1_data.get("resource_id")
            if resource_id:
                await test_enrichment_status(resource_id)
        except Exception as e:
            print(f"⚠️  Could not test enrichment status: {e}")
        
        print_section("✅ ALL TESTS COMPLETED")
        
    except Exception as e:
        print_section("❌ TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

