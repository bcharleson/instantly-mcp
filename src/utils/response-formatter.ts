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
 */
function isUniformArray(arr: any[]): boolean {
  if (arr.length === 0) return false;
  
  // Check if all items are objects
  if (!arr.every(item => typeof item === 'object' && item !== null && !Array.isArray(item))) {
    return false;
  }

  // Get keys from first object
  const firstKeys = Object.keys(arr[0]).sort();
  
  // Check if all objects have same keys and primitive values
  return arr.every(item => {
    const itemKeys = Object.keys(item).sort();
    
    // Same keys?
    if (itemKeys.length !== firstKeys.length) return false;
    if (!itemKeys.every((key, i) => key === firstKeys[i])) return false;
    
    // All values primitive?
    return Object.values(item).every(value => {
      const type = typeof value;
      return type === 'string' || type === 'number' || type === 'boolean' || value === null;
    });
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
      const toonOutput = encodeTOON(data, {
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

