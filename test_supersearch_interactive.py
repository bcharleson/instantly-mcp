#!/usr/bin/env python3
"""
Interactive SuperSearch testing tool.

This script provides an interactive menu to test different SuperSearch features.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from instantly_mcp.tools.supersearch import (
    search_supersearch_leads,
    get_enrichment_status,
    get_enrichment_history,
    create_enrichment,
    create_ai_enrichment,
)
from instantly_mcp.models.supersearch import (
    SearchSuperSearchLeadsInput,
    SuperSearchFilters,
    LocationFilter,
    LocationItem,
    IncludeExcludeFilter,
    GetEnrichmentStatusInput,
    GetEnrichmentHistoryInput,
    CreateEnrichmentInput,
    CreateAIEnrichmentInput,
)


def print_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("  SuperSearch Interactive Test Menu")
    print("="*60)
    print("\n1. Search: CEOs in Technology")
    print("2. Search: Sales Leaders in California")
    print("3. Search: Marketing Directors (custom)")
    print("4. Get Enrichment Status (requires resource_id)")
    print("5. Get Enrichment History")
    print("6. Create Enrichment (requires resource_id)")
    print("7. Create AI Enrichment (requires resource_id)")
    print("8. Custom Search (build your own)")
    print("9. Exit")
    print("\n" + "="*60)


async def test_ceos_in_tech():
    """Test 1: CEOs in Technology."""
    print("\n🔍 Searching for CEOs in Technology...")
    
    params = SearchSuperSearchLeadsInput(
        list_name="Test - CEOs in Tech",
        search_filters=SuperSearchFilters(
            title=IncludeExcludeFilter(include=["CEO", "Chief Executive Officer"]),
            industry=IncludeExcludeFilter(include=["Technology", "Software"]),
        ),
        limit=5,
        search_name="Interactive Test - CEOs"
    )
    
    result = await search_supersearch_leads(params)
    print("\n📊 Result:")
    print(json.dumps(json.loads(result) if isinstance(result, str) else result, indent=2))
    return result


async def test_sales_in_ca():
    """Test 2: Sales Leaders in California."""
    print("\n🔍 Searching for Sales Leaders in California...")
    
    params = SearchSuperSearchLeadsInput(
        list_name="Test - CA Sales Leaders",
        search_filters=SuperSearchFilters(
            department=["Sales"],
            level=["Director-Level", "VP-Level"],
            locations=LocationFilter(
                include=[LocationItem(state="California", country="United States")]
            ),
        ),
        limit=3,
        search_name="Interactive Test - CA Sales"
    )
    
    result = await search_supersearch_leads(params)
    print("\n📊 Result:")
    print(json.dumps(json.loads(result) if isinstance(result, str) else result, indent=2))
    return result


async def test_marketing_directors():
    """Test 3: Marketing Directors."""
    print("\n🔍 Searching for Marketing Directors...")
    
    params = SearchSuperSearchLeadsInput(
        list_name="Test - Marketing Directors",
        search_filters=SuperSearchFilters(
            department=["Marketing"],
            level=["Director-Level", "VP-Level", "C-Level"],
            employee_count=["100 - 500", "500 - 1000", "1000+"],
        ),
        limit=5,
        search_name="Interactive Test - Marketing"
    )
    
    result = await search_supersearch_leads(params)
    print("\n📊 Result:")
    print(json.dumps(json.loads(result) if isinstance(result, str) else result, indent=2))
    return result


async def test_get_status():
    """Test 4: Get enrichment status."""
    resource_id = input("\nEnter resource_id (list or campaign ID): ").strip()
    if not resource_id:
        print("❌ Resource ID required!")
        return
    
    print(f"\n📊 Getting status for {resource_id}...")
    params = GetEnrichmentStatusInput(resource_id=resource_id)
    result = await get_enrichment_status(params)
    print("\n📊 Result:")
    print(json.dumps(json.loads(result) if isinstance(result, str) else result, indent=2))
    return result


async def test_get_history():
    """Test 5: Get enrichment history."""
    print("\n📊 Getting enrichment history...")
    params = GetEnrichmentHistoryInput(limit=10)
    result = await get_enrichment_history(params)
    print("\n📊 Result:")
    print(json.dumps(json.loads(result) if isinstance(result, str) else result, indent=2))
    return result


async def main():
    """Main interactive loop."""
    # Check API key
    api_key = os.environ.get("INSTANTLY_API_KEY")
    if not api_key:
        print("\n❌ ERROR: INSTANTLY_API_KEY not set!")
        print("Please run: export INSTANTLY_API_KEY='your-api-key'")
        sys.exit(1)
    
    print(f"\n✅ API Key found: {api_key[:10]}...")
    
    while True:
        print_menu()
        choice = input("\nSelect an option (1-9): ").strip()
        
        try:
            if choice == "1":
                await test_ceos_in_tech()
            elif choice == "2":
                await test_sales_in_ca()
            elif choice == "3":
                await test_marketing_directors()
            elif choice == "4":
                await test_get_status()
            elif choice == "5":
                await test_get_history()
            elif choice == "6":
                print("\n⚠️  Create Enrichment not yet implemented in interactive mode")
            elif choice == "7":
                print("\n⚠️  AI Enrichment not yet implemented in interactive mode")
            elif choice == "8":
                print("\n⚠️  Custom Search not yet implemented in interactive mode")
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please select 1-9.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())

