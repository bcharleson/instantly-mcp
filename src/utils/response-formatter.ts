/**
 * Response Formatter Utility
 * 
 * Converts tool responses to optimal format (TOON or JSON) based on data structure.
 * TOON provides 30-60% token savings for uniform tabular data while maintaining
 * full compatibility with MCP protocol (text content is valid).
 */

import { encode as encodeTOON } from '@toon-format/toon';

/**
 * Configuration for response formatting
 */
export interface FormatOptions {
  /**
   * Enable TOON encoding for responses (default: true)
   * When true, automatically converts uniform arrays to TOON format
   */
  enableTOON?: boolean;

  /**
   * Delimiter for TOON arrays (default: ',')
   * Options: ',' (comma), '\t' (tab), '|' (pipe)
   * Tab often provides best token efficiency
   */
  delimiter?: ',' | '\t' | '|';

  /**
   * Minimum array length to use TOON (default: 3)
   * Smaller arrays may not benefit from TOON overhead
   */
  minArrayLength?: number;

  /**
   * Enable key folding for nested objects (default: false)
   * Collapses single-key wrapper chains into dotted paths
   */
  keyFolding?: 'off' | 'safe';
}

const DEFAULT_OPTIONS: Required<FormatOptions> = {
  enableTOON: true,
  delimiter: '\t', // Tab is most token-efficient
  minArrayLength: 3,
  keyFolding: 'off'
};

/**
 * Determines if data structure is suitable for TOON encoding
 * 
 * TOON excels at:
 * - Uniform arrays of objects (same fields, primitive values)
 * - Time-series data
 * - Tabular data
 * 
 * JSON is better for:
 * - Non-uniform data
 * - Deeply nested structures
 * - Small arrays (< 3 items)
 */
function shouldUseTOON(data: any, options: Required<FormatOptions>): boolean {
  if (!options.enableTOON) return false;

  // Check if data contains arrays suitable for TOON
  if (Array.isArray(data)) {
    return data.length >= options.minArrayLength && isUniformArray(data);
  }

  // Check if object contains array properties suitable for TOON
  if (typeof data === 'object' && data !== null) {
    return Object.values(data).some(value => 
      Array.isArray(value) && 
      value.length >= options.minArrayLength && 
      isUniformArray(value)
    );
  }

  return false;
}

/**
 * Checks if array contains uniform objects (same keys, primitive values)
 *
 * Updated to be more lenient with real-world API data:
 * - Allows optional fields (not all objects need same keys)
 * - Requires at least 50% key overlap
 * - Normalizes data by filling missing fields with null
 */
function isUniformArray(arr: any[]): boolean {
  if (arr.length === 0) return false;

  // Check if all items are objects
  if (!arr.every(item => typeof item === 'object' && item !== null && !Array.isArray(item))) {
    return false;
  }

  // Collect all unique keys across all objects
  const allKeys = new Set<string>();
  arr.forEach(item => {
    Object.keys(item).forEach(key => allKeys.add(key));
  });

  const uniqueKeys = Array.from(allKeys);

  // Check if objects have reasonable key overlap (at least 50%)
  const keyOverlapThreshold = 0.5;
  const hasGoodOverlap = arr.every(item => {
    const itemKeys = Object.keys(item);
    const overlap = itemKeys.filter(key => uniqueKeys.includes(key)).length;
    return overlap / uniqueKeys.length >= keyOverlapThreshold;
  });

  if (!hasGoodOverlap) return false;

  // Check if all values are primitives or simple objects
  return arr.every(item => {
    return Object.values(item).every(value => {
      const type = typeof value;
      // Allow primitives, null, and empty objects (like warmup: {})
      if (type === 'string' || type === 'number' || type === 'boolean' || value === null) {
        return true;
      }
      // Allow empty objects
      if (type === 'object' && value !== null && !Array.isArray(value) && Object.keys(value as object).length === 0) {
        return true;
      }
      return false;
    });
  });
}

/**
 * Normalizes array of objects to have consistent keys
 * Fills missing fields with null for TOON compatibility
 */
function normalizeArray(arr: any[]): any[] {
  if (arr.length === 0) return arr;

  // Collect all unique keys
  const allKeys = new Set<string>();
  arr.forEach(item => {
    Object.keys(item).forEach(key => allKeys.add(key));
  });

  const keys = Array.from(allKeys).sort();

  // Normalize each object to have all keys
  return arr.map(item => {
    const normalized: any = {};
    keys.forEach(key => {
      normalized[key] = item[key] !== undefined ? item[key] : null;
    });
    return normalized;
  });
}

/**
 * Formats tool response data for optimal token efficiency
 *
 * @param data - Response data to format
 * @param options - Formatting options
 * @returns Formatted string (TOON or JSON)
 */
export function formatResponse(data: any, options: Partial<FormatOptions> = {}): string {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  try {
    // Determine if TOON encoding would be beneficial
    if (shouldUseTOON(data, opts)) {
      // Normalize data for TOON encoding
      let normalizedData = data;

      // If data is an array, normalize it
      if (Array.isArray(data)) {
        normalizedData = normalizeArray(data);
      }
      // If data is an object with array properties, normalize those arrays
      else if (typeof data === 'object' && data !== null) {
        normalizedData = { ...data };
        Object.keys(normalizedData).forEach(key => {
          if (Array.isArray(normalizedData[key]) && isUniformArray(normalizedData[key])) {
            normalizedData[key] = normalizeArray(normalizedData[key]);
          }
        });
      }

      const toonOutput = encodeTOON(normalizedData, {
        delimiter: opts.delimiter,
        keyFolding: opts.keyFolding
      });

      // Add format indicator for LLM
      return `[TOON Format - Tab-delimited]\n${toonOutput}`;
    }
  } catch (error) {
    // Fallback to JSON if TOON encoding fails
    console.error('[Response Formatter] TOON encoding failed, falling back to JSON:', error);
  }

  // Default to pretty-printed JSON
  return JSON.stringify(data, null, 2);
}

/**
 * Creates MCP-compatible content response
 * 
 * @param data - Response data
 * @param options - Formatting options
 * @returns MCP content array
 */
export function createMCPResponse(data: any, options: Partial<FormatOptions> = {}) {
  return {
    content: [
      {
        type: 'text' as const,
        text: formatResponse(data, options)
      }
    ]
  };
}

