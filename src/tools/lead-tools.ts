/**
 * Instantly MCP Server - Lead Tools (Compacted)
 *
 * Tool definitions for lead and lead list management.
 * Optimized for minimal context window overhead.
 * Total: 11 lead tools
 */

export const leadTools = [
  {
    name: 'list_leads',
    title: 'List Leads',
    description: 'List leads with pagination. Filter by campaign, list, search, or status.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        campaign: { type: 'string', description: 'Campaign UUID' },
        list_id: { type: 'string', description: 'List UUID' },
        list_ids: { type: 'array', items: { type: 'string' } },
        status: { type: 'string' },
        created_after: { type: 'string', description: 'YYYY-MM-DD' },
        created_before: { type: 'string', description: 'YYYY-MM-DD' },
        search: { type: 'string', description: 'Name or email' },
        filter: { type: 'string', description: 'FILTER_VAL_CONTACTED, FILTER_VAL_NOT_CONTACTED, FILTER_VAL_COMPLETED, FILTER_VAL_ACTIVE, etc.' },
        distinct_contacts: { type: 'boolean', description: 'Dedupe by email' },
        limit: { type: 'number', description: '1-100, default: 100' },
        starting_after: { type: 'string', description: 'Cursor from pagination.next_starting_after' }
      }
    }
  },

  {
    name: 'get_lead',
    title: 'Get Lead',
    description: 'Get lead details by ID',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'Lead UUID' }
      },
      required: ['lead_id']
    }
  },

  {
    name: 'create_lead',
    title: 'Create Lead',
    description: 'Create lead with custom variables. Use skip_if_in_campaign to prevent duplicates.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        campaign: { type: 'string', description: 'Campaign UUID' },
        email: { type: 'string', description: 'Required' },
        first_name: { type: 'string' },
        last_name: { type: 'string' },
        company_name: { type: 'string' },
        phone: { type: 'string' },
        website: { type: 'string' },
        personalization: { type: 'string' },
        lt_interest_status: { type: 'number', description: '-3 to 4' },
        pl_value_lead: { type: 'string' },
        list_id: { type: 'string' },
        assigned_to: { type: 'string' },
        skip_if_in_workspace: { type: 'boolean' },
        skip_if_in_campaign: { type: 'boolean', description: 'Recommended' },
        skip_if_in_list: { type: 'boolean' },
        blocklist_id: { type: 'string' },
        verify_leads_on_import: { type: 'boolean' },
        custom_variables: { type: 'object', description: 'Match campaign field names' }
      }
    }
  },

  {
    name: 'update_lead',
    title: 'Update Lead',
    description: 'Update lead (partial). ⚠️ custom_variables replaces entire object.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'Lead UUID' },
        personalization: { type: 'string' },
        website: { type: 'string' },
        last_name: { type: 'string' },
        first_name: { type: 'string' },
        company_name: { type: 'string' },
        phone: { type: 'string' },
        lt_interest_status: { type: 'number' },
        pl_value_lead: { type: 'string' },
        assigned_to: { type: 'string' },
        custom_variables: { type: 'object', description: 'Replaces all - include existing!' }
      },
      required: ['lead_id']
    }
  },

  {
    name: 'list_lead_lists',
    title: 'List Lead Lists',
    description: 'List lead lists with pagination and search',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: '1-100, default: 100' },
        starting_after: { type: 'string', description: 'Cursor from pagination' },
        has_enrichment_task: { type: 'boolean' },
        search: { type: 'string', description: 'Search by name' }
      }
    }
  },

  {
    name: 'create_lead_list',
    title: 'Create Lead List',
    description: 'Create list. Set has_enrichment_task=true for auto-enrich.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'List name' },
        has_enrichment_task: { type: 'boolean' },
        owned_by: { type: 'string', description: 'Owner UUID' }
      },
      required: ['name']
    }
  },

  {
    name: 'update_lead_list',
    title: 'Update Lead List',
    description: 'Update list name, enrichment, or owner',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        list_id: { type: 'string' },
        name: { type: 'string' },
        has_enrichment_task: { type: 'boolean' },
        owned_by: { type: 'string' }
      },
      required: ['list_id']
    }
  },

  {
    name: 'get_verification_stats_for_lead_list',
    title: 'Verification Stats',
    description: 'Get email verification stats for list',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        list_id: { type: 'string', description: 'List UUID' }
      },
      required: ['list_id']
    }
  },

  {
    name: 'add_leads_to_campaign_or_list_bulk',
    title: 'Bulk Add Leads',
    description: 'Add up to 1,000 leads. 10-100x faster than create_lead.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        leads: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              email: { type: 'string' },
              first_name: { type: 'string' },
              last_name: { type: 'string' },
              company_name: { type: 'string' },
              phone: { type: 'string' },
              website: { type: 'string' },
              personalization: { type: 'string' },
              lt_interest_status: { type: 'number' },
              pl_value_lead: { type: 'string' },
              assigned_to: { type: 'string' },
              custom_variables: { type: 'object' }
            }
          },
          description: '1-1000 leads'
        },
        campaign_id: { type: 'string', description: 'Use OR list_id' },
        list_id: { type: 'string', description: 'Use OR campaign_id' },
        blocklist_id: { type: 'string' },
        assigned_to: { type: 'string' },
        verify_leads_on_import: { type: 'boolean' },
        skip_if_in_workspace: { type: 'boolean' },
        skip_if_in_campaign: { type: 'boolean', description: 'Recommended' },
        skip_if_in_list: { type: 'boolean' }
      },
      required: ['leads']
    }
  },

  {
    name: 'delete_lead',
    title: 'Delete Lead',
    description: '🗑️ PERMANENTLY delete. CANNOT UNDO!',
    annotations: { destructiveHint: true, confirmationRequiredHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        lead_id: { type: 'string', description: 'Lead UUID to DELETE' }
      },
      required: ['lead_id']
    }
  },

  {
    name: 'move_leads_to_campaign_or_list',
    title: 'Move/Copy Leads',
    description: 'Move or copy leads between campaigns/lists (background job)',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        to_campaign_id: { type: 'string', description: 'Destination (OR to_list_id)' },
        to_list_id: { type: 'string', description: 'Destination (OR to_campaign_id)' },
        ids: { type: 'array', items: { type: 'string' }, description: 'Lead IDs' },
        search: { type: 'string' },
        filter: { type: 'string', description: 'Contact status filter' },
        campaign: { type: 'string', description: 'Source campaign' },
        list_id: { type: 'string', description: 'Source list' },
        in_campaign: { type: 'boolean' },
        in_list: { type: 'boolean' },
        queries: { type: 'array', items: { type: 'object' } },
        excluded_ids: { type: 'array', items: { type: 'string' } },
        contacts: { type: 'array', items: { type: 'string' } },
        check_duplicates_in_campaigns: { type: 'boolean' },
        skip_leads_in_verification: { type: 'boolean' },
        limit: { type: 'number' },
        assigned_to: { type: 'string' },
        esp_code: { type: 'number', description: '0=Queue, 1=Google, 2=MS, etc.' },
        esg_code: { type: 'number', description: '0=Queue, 1=Barracuda, etc.' },
        copy_leads: { type: 'boolean', description: 'Copy instead of move' },
        check_duplicates: { type: 'boolean' }
      }
    }
  },
];

