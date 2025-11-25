/**
 * Tool Pagination Configuration
 * 
 * Implements MCP 2025-06-18 tool pagination support for lazy loading.
 * This allows clients to load tools incrementally rather than all at once,
 * significantly reducing initial context window overhead.
 * 
 * Per MCP spec:
 * - tools/list supports cursor-based pagination
 * - Servers can return tools in chunks with nextCursor
 * - Clients use cursor parameter to fetch next page
 */

export interface ToolPaginationConfig {
  /**
   * Number of tools to return per page
   * Default: 10 (optimized for context window efficiency)
   * Set to 0 or Infinity to disable pagination (return all tools)
   */
  pageSize: number;

  /**
   * Enable pagination (default: true for context efficiency)
   * Set to false for backward compatibility with older clients
   */
  enabled: boolean;
}

/**
 * Default pagination configuration
 * 
 * Returns 10 tools per page by default for optimal context window usage.
 * Clients that don't support pagination will still work but get all tools.
 */
export const DEFAULT_TOOL_PAGINATION: ToolPaginationConfig = {
  pageSize: 10,
  enabled: true
};

/**
 * Environment-based pagination config
 * 
 * Can be overridden via environment variables:
 * - TOOL_PAGINATION_ENABLED: 'true' or 'false'
 * - TOOL_PAGINATION_PAGE_SIZE: number of tools per page
 */
export function getToolPaginationConfig(): ToolPaginationConfig {
  const envEnabled = process.env.TOOL_PAGINATION_ENABLED;
  const envPageSize = process.env.TOOL_PAGINATION_PAGE_SIZE;

  return {
    enabled: envEnabled !== undefined ? envEnabled === 'true' : DEFAULT_TOOL_PAGINATION.enabled,
    pageSize: envPageSize ? parseInt(envPageSize, 10) : DEFAULT_TOOL_PAGINATION.pageSize
  };
}

/**
 * Pagination cursor utilities
 */
export class ToolPaginationCursor {
  /**
   * Encode pagination state to cursor string
   */
  static encode(startIndex: number): string {
    return Buffer.from(JSON.stringify({ s: startIndex })).toString('base64url');
  }

  /**
   * Decode cursor string to pagination state
   */
  static decode(cursor: string): { startIndex: number } | null {
    try {
      const decoded = JSON.parse(Buffer.from(cursor, 'base64url').toString('utf-8'));
      if (typeof decoded.s === 'number') {
        return { startIndex: decoded.s };
      }
      return null;
    } catch {
      return null;
    }
  }
}

/**
 * Paginate tools array
 * 
 * @param tools - Full array of tool definitions
 * @param cursor - Optional cursor from previous request
 * @param config - Pagination configuration
 * @returns Paginated result with tools and nextCursor
 */
export function paginateTools<T>(
  tools: T[],
  cursor?: string,
  config: ToolPaginationConfig = getToolPaginationConfig()
): { tools: T[]; nextCursor?: string } {
  // If pagination disabled, return all tools
  if (!config.enabled || config.pageSize <= 0 || config.pageSize >= tools.length) {
    return { tools };
  }

  // Decode cursor to get start index
  let startIndex = 0;
  if (cursor) {
    const decoded = ToolPaginationCursor.decode(cursor);
    if (decoded) {
      startIndex = decoded.startIndex;
    }
  }

  // Validate start index
  if (startIndex < 0 || startIndex >= tools.length) {
    startIndex = 0;
  }

  // Calculate end index
  const endIndex = Math.min(startIndex + config.pageSize, tools.length);
  const pageTools = tools.slice(startIndex, endIndex);

  // Generate next cursor if more tools available
  const hasMore = endIndex < tools.length;
  const nextCursor = hasMore ? ToolPaginationCursor.encode(endIndex) : undefined;

  return {
    tools: pageTools,
    nextCursor
  };
}

/**
 * Get pagination metadata for logging/debugging
 */
export function getPaginationInfo(
  totalTools: number,
  cursor?: string,
  config: ToolPaginationConfig = getToolPaginationConfig()
): {
  totalTools: number;
  pageSize: number;
  currentPage: number;
  totalPages: number;
  startIndex: number;
  endIndex: number;
} {
  if (!config.enabled || config.pageSize <= 0) {
    return {
      totalTools,
      pageSize: totalTools,
      currentPage: 1,
      totalPages: 1,
      startIndex: 0,
      endIndex: totalTools
    };
  }

  let startIndex = 0;
  if (cursor) {
    const decoded = ToolPaginationCursor.decode(cursor);
    if (decoded) {
      startIndex = decoded.startIndex;
    }
  }

  const pageSize = config.pageSize;
  const totalPages = Math.ceil(totalTools / pageSize);
  const currentPage = Math.floor(startIndex / pageSize) + 1;
  const endIndex = Math.min(startIndex + pageSize, totalTools);

  return {
    totalTools,
    pageSize,
    currentPage,
    totalPages,
    startIndex,
    endIndex
  };
}

