#!/usr/bin/env python3
"""
Validation script for SuperSearch implementation.

This script checks that all SuperSearch components are properly set up
without making any API calls.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def check_imports():
    """Verify all imports work correctly."""
    print("🔍 Checking imports...")
    
    try:
        from instantly_mcp.models.supersearch import (
            SearchSuperSearchLeadsInput,
            SuperSearchFilters,
            LocationFilter,
            LocationItem,
            GetEnrichmentStatusInput,
            CreateEnrichmentInput,
            CreateAIEnrichmentInput,
            RunEnrichmentInput,
            GetEnrichmentHistoryInput,
        )
        print("  ✅ Models imported successfully")
    except Exception as e:
        print(f"  ❌ Failed to import models: {e}")
        return False
    
    try:
        from instantly_mcp.tools.supersearch import (
            search_supersearch_leads,
            get_enrichment_status,
            create_enrichment,
            create_ai_enrichment,
            run_enrichment,
            get_enrichment_history,
            SUPERSEARCH_TOOLS,
        )
        print("  ✅ Tools imported successfully")
        print(f"  ✅ Found {len(SUPERSEARCH_TOOLS)} SuperSearch tools")
    except Exception as e:
        print(f"  ❌ Failed to import tools: {e}")
        return False
    
    return True


def check_model_validation():
    """Test model validation."""
    print("\n🔍 Checking model validation...")
    
    try:
        from instantly_mcp.models.supersearch import (
            SearchSuperSearchLeadsInput,
            SuperSearchFilters,
            LocationFilter,
            LocationItem,
        )
        
        # Test basic model creation
        filters = SuperSearchFilters(
            title=["CEO"],
            industry=["Technology"],
        )
        print("  ✅ Basic SuperSearchFilters created")
        
        # Test with location
        filters_with_location = SuperSearchFilters(
            title=["CEO"],
            locations=LocationFilter(
                include=[LocationItem(state="California", country="United States")]
            ),
        )
        print("  ✅ SuperSearchFilters with location created")
        
        # Test SearchSuperSearchLeadsInput
        search_input = SearchSuperSearchLeadsInput(
            list_name="Test",
            search_filters=filters,
            limit=5,
        )
        print("  ✅ SearchSuperSearchLeadsInput created")
        
        # Test serialization
        serialized = search_input.search_filters.model_dump(by_alias=True, exclude_none=True)
        print(f"  ✅ Serialization works (got {len(serialized)} fields)")
        
        return True
    except Exception as e:
        print(f"  ❌ Model validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_tool_registration():
    """Check if tools are registered in the MCP server."""
    print("\n🔍 Checking tool registration...")
    
    try:
        from instantly_mcp.tools import get_available_categories, load_tools_for_category
        
        categories = get_available_categories()
        if "supersearch" in categories:
            print("  ✅ SuperSearch category registered")
        else:
            print(f"  ❌ SuperSearch not in categories: {categories}")
            return False
        
        tools = load_tools_for_category("supersearch")
        print(f"  ✅ Loaded {len(tools)} tools from supersearch category")
        
        tool_names = [t.__name__ for t in tools]
        expected = [
            "search_supersearch_leads",
            "get_enrichment_status",
            "create_enrichment",
            "create_ai_enrichment",
            "run_enrichment",
            "get_enrichment_history",
        ]
        
        for name in expected:
            if name in tool_names:
                print(f"  ✅ {name} registered")
            else:
                print(f"  ❌ {name} NOT registered")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Tool registration check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api_key():
    """Check if API key is configured."""
    print("\n🔍 Checking API key configuration...")
    
    api_key = os.environ.get("INSTANTLY_API_KEY")
    if api_key:
        print(f"  ✅ API key found: {api_key[:10]}...")
        return True
    else:
        print("  ⚠️  No API key found (set INSTANTLY_API_KEY to test with real API)")
        return None  # Not a failure, just a warning


def main():
    """Run all validation checks."""
    print("="*60)
    print("  SuperSearch Implementation Validation")
    print("="*60)
    
    results = []
    
    # Run checks
    results.append(("Imports", check_imports()))
    results.append(("Model Validation", check_model_validation()))
    results.append(("Tool Registration", check_tool_registration()))
    api_key_result = check_api_key()
    
    # Summary
    print("\n" + "="*60)
    print("  Validation Summary")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        if result:
            print(f"  ✅ {name}: PASSED")
        else:
            print(f"  ❌ {name}: FAILED")
            all_passed = False
    
    if api_key_result is None:
        print(f"  ⚠️  API Key: NOT SET (optional for validation)")
    elif api_key_result:
        print(f"  ✅ API Key: CONFIGURED")
    
    print("="*60)
    
    if all_passed:
        print("\n✅ All validation checks passed!")
        print("\nNext steps:")
        print("  1. Set INSTANTLY_API_KEY environment variable")
        print("  2. Run: python test_supersearch.py")
        print("  3. Or run: python test_supersearch_interactive.py")
        return 0
    else:
        print("\n❌ Some validation checks failed!")
        print("Please fix the issues above before testing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

