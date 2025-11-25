/**
 * Instantly MCP Server - Tools Registry (Optimized v2.0)
 *
 * Central registry combining all tool definitions.
 * Optimized for minimal context window overhead with:
 * - Compacted descriptions
 * - Consolidated duplicate tools
 * - MCP 2025-06-18 annotations support
 * - Category-based lazy loading via TOOL_CATEGORIES env var
 *
 * Total: 31 tools across 5 categories (reduced from 36)
 * - Account tools: 6 (consolidated from 11)
 * - Campaign tools: 6
 * - Lead tools: 11
 * - Email tools: 5
 * - Analytics tools: 3
 * 
 * LAZY LOADING:
 * Set TOOL_CATEGORIES env var to load only specific categories.
 * Example: TOOL_CATEGORIES="accounts,campaigns" loads only 12 tools
 * Valid categories: accounts, campaigns, leads, email, analytics
 * Default: all categories loaded
 */

import { accountTools } from './account-tools.js';
import { campaignTools } from './campaign-tools.js';
import { leadTools } from './lead-tools.js';
import { emailTools } from './email-tools.js';
import { analyticsTools } from './analytics-tools.js';

// Category mapping for lazy loading
const CATEGORY_MAP: Record<string, any[]> = {
  accounts: accountTools,
  campaigns: campaignTools,
  leads: leadTools,
  email: emailTools,
  analytics: analyticsTools,
};

/**
 * Build tools array based on TOOL_CATEGORIES env var
 * If not set, all categories are loaded (full 31 tools)
 */
function buildToolsDefinition(): any[] {
  const categoriesEnv = process.env.TOOL_CATEGORIES;
  
  if (!categoriesEnv) {
    // Default: load all tools
    return [
      ...accountTools,
      ...campaignTools,
      ...leadTools,
      ...emailTools,
      ...analyticsTools,
    ];
  }
  
  // Parse comma-separated categories
  const requestedCategories = categoriesEnv
    .toLowerCase()
    .split(',')
    .map(c => c.trim())
    .filter(c => c.length > 0);
  
  const tools: any[] = [];
  const loadedCategories: string[] = [];
  
  for (const category of requestedCategories) {
    if (CATEGORY_MAP[category]) {
      tools.push(...CATEGORY_MAP[category]);
      loadedCategories.push(category);
    } else {
      console.error(`[Instantly MCP] ⚠️ Unknown tool category: "${category}". Valid: ${Object.keys(CATEGORY_MAP).join(', ')}`);
    }
  }
  
  if (tools.length > 0) {
    console.error(`[Instantly MCP] 🔧 Lazy loading enabled: ${tools.length} tools from categories: ${loadedCategories.join(', ')}`);
  } else {
    console.error(`[Instantly MCP] ⚠️ No valid categories in TOOL_CATEGORIES. Loading all tools.`);
    return [
      ...accountTools,
      ...campaignTools,
      ...leadTools,
      ...emailTools,
      ...analyticsTools,
    ];
  }
  
  return tools;
}

/**
 * Complete tool definitions array
 * 
 * This array is used by the MCP server to register all available tools.
 * Tools are filtered by TOOL_CATEGORIES env var if set.
 */
export const TOOLS_DEFINITION = buildToolsDefinition();

/**
 * Tool count by category (reflects loaded tools, not all available)
 */
export const TOOL_COUNTS = {
  account: accountTools.length,
  campaign: campaignTools.length,
  lead: leadTools.length,
  email: emailTools.length,
  analytics: analyticsTools.length,
  loaded: TOOLS_DEFINITION.length,
  maxAvailable: 31,  // Total when all categories loaded
};

/**
 * Get available categories for lazy loading
 */
export function getAvailableCategories(): string[] {
  return Object.keys(CATEGORY_MAP);
}

/**
 * Check if lazy loading is active
 */
export function isLazyLoadingEnabled(): boolean {
  return !!process.env.TOOL_CATEGORIES;
}

/**
 * Validate tool definitions
 * 
 * Ensures all tools have required properties and no duplicate names
 */
export function validateToolDefinitions(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  const toolNames = new Set<string>();

  for (const tool of TOOLS_DEFINITION) {
    // Check required properties
    if (!tool.name) {
      errors.push('Tool missing name property');
    }
    if (!tool.description) {
      errors.push(`Tool ${tool.name || 'unknown'} missing description`);
    }
    if (!tool.inputSchema) {
      errors.push(`Tool ${tool.name || 'unknown'} missing inputSchema`);
    }

    // Check for duplicate names
    if (tool.name) {
      if (toolNames.has(tool.name)) {
        errors.push(`Duplicate tool name: ${tool.name}`);
      }
      toolNames.add(tool.name);
    }
  }

  // Dynamic validation: check loaded count is reasonable
  if (TOOLS_DEFINITION.length === 0) {
    errors.push('No tools loaded - check TOOL_CATEGORIES env var');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Get tool by name
 * 
 * @param name - Tool name to search for
 * @returns Tool definition or undefined if not found
 */
export function getToolByName(name: string): any | undefined {
  return TOOLS_DEFINITION.find(tool => tool.name === name);
}

/**
 * Get tools by category
 * 
 * @param category - Category name (account, campaign, lead, email, analytics)
 * @returns Array of tool definitions for the category
 */
export function getToolsByCategory(category: 'account' | 'campaign' | 'lead' | 'email' | 'analytics'): any[] {
  switch (category) {
    case 'account':
      return accountTools;
    case 'campaign':
      return campaignTools;
    case 'lead':
      return leadTools;
    case 'email':
      return emailTools;
    case 'analytics':
      return analyticsTools;
    default:
      return [];
  }
}

