/**
 * Instantly MCP Server - Analytics Tools (Compacted)
 * 
 * Tool definitions for analytics and reporting.
 * Optimized for minimal context window overhead.
 * Total: 3 analytics tools
 */

export const analyticsTools = [
  {
    name: 'get_campaign_analytics',
    title: 'Campaign Analytics',
    description: 'Get campaign metrics: opens, clicks, replies, bounces. Filter by campaign(s) and dates.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Single campaign UUID (omit for all)' },
        campaign_ids: { type: 'array', items: { type: 'string' }, description: 'Multiple campaign UUIDs' },
        start_date: { type: 'string', description: 'YYYY-MM-DD' },
        end_date: { type: 'string', description: 'YYYY-MM-DD' },
        exclude_total_leads_count: { type: 'boolean', description: 'Faster response' }
      }
    }
  },

  {
    name: 'get_daily_campaign_analytics',
    title: 'Daily Analytics',
    description: 'Day-by-day campaign performance analytics',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign UUID (omit for all)' },
        start_date: { type: 'string', description: 'YYYY-MM-DD' },
        end_date: { type: 'string', description: 'YYYY-MM-DD' },
        campaign_status: { type: 'number', description: '0=Draft, 1=Active, 2=Paused, 3=Completed', enum: [0, 1, 2, 3, 4, -99, -1, -2] }
      }
    }
  },

  {
    name: 'get_warmup_analytics',
    title: 'Warmup Analytics',
    description: 'Get warmup metrics for account(s)',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        emails: { type: 'array', items: { type: 'string' }, description: 'Account emails' },
        email: { type: 'string', description: 'Single email (alternative)' },
        start_date: { type: 'string', description: 'YYYY-MM-DD' },
        end_date: { type: 'string', description: 'YYYY-MM-DD' }
      }
    }
  },
];

