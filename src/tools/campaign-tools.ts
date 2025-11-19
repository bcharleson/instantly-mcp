/**
 * Instantly MCP Server - Campaign Tools
 * 
 * Tool definitions for campaign management operations.
 * Total: 6 campaign tools
 */

import { BUSINESS_PRIORITY_TIMEZONES, DEFAULT_TIMEZONE } from '../timezone-config.js';

export const campaignTools = [
  {
    name: 'create_campaign',
    title: 'Create Campaign',
    description: 'Create email campaign with two-step workflow. STEP 1: Call with name, subject, body to discover eligible accounts. STEP 2: Call with email_list from Step 1. ⚠️ NEVER use placeholder emails. Multi-step sequences: Use sequence_steps (2-10) and step_delay_days (1-30).',
    inputSchema: {
      type: 'object',
      properties: {
        // Core required fields
        name: {
          type: 'string',
          description: 'Campaign name for identification (e.g., "Q4 Product Launch Campaign")'
        },
        subject: {
          type: 'string',
          description: '⚠️ CRITICAL: MUST be under 50 characters for deliverability. Use personalization: {{firstName}}, {{companyName}}. If validation fails, shorten before retrying.'
        },
        body: {
          type: 'string',
          description: 'Email body (plain text, \\n for line breaks → auto-converts to <br />). Personalization: {{firstName}}, {{lastName}}, {{companyName}}. Get straight to point, high-value content.'
        },
        email_list: {
          type: 'array',
          items: { type: 'string' },
          description: '⚠️ SENDER EMAILS (optional). If omitted: Tool fetches eligible accounts and asks user. If provided: ONLY use emails from eligible list shown in Step 1. NEVER use placeholders (test@example.com). Multiple emails = ONE campaign with ALL in single array (max 100).',
          example: ['john@yourcompany.com', 'jane@yourcompany.com']
        },

        // Tracking settings (disabled by default for better deliverability)
        track_opens: {
          type: 'boolean',
          description: 'Track when recipients open emails (disabled by default for better deliverability and privacy compliance)',
          default: false
        },
        track_clicks: {
          type: 'boolean',
          description: 'Track when recipients click links (disabled by default for better deliverability and privacy compliance)',
          default: false
        },

        // Scheduling options
        timezone: {
          type: 'string',
          description: `Timezone for sending schedule. Supported timezones: ${BUSINESS_PRIORITY_TIMEZONES.join(', ')}. Unsupported timezones will be automatically mapped to closest supported timezone.`,
          default: DEFAULT_TIMEZONE,
          example: DEFAULT_TIMEZONE
        },
        timing_from: {
          type: 'string',
          description: 'Start time for sending (24h format)',
          default: '09:00',
          pattern: '^([01][0-9]|2[0-3]):([0-5][0-9])$'
        },
        timing_to: {
          type: 'string',
          description: 'End time for sending (24h format)',
          default: '17:00',
          pattern: '^([01][0-9]|2[0-3]):([0-5][0-9])$'
        },

        // Sending limits
        daily_limit: {
          type: 'number',
          description: 'Maximum emails per day per account (30 recommended for cold email compliance)',
          default: 30,
          minimum: 1,
          maximum: 30
        },
        email_gap: {
          type: 'number',
          description: 'Minutes between emails from same account (1-1440 minutes)',
          default: 10,
          minimum: 1,
          maximum: 1440
        },

        // Campaign behavior
        stop_on_reply: {
          type: 'boolean',
          description: 'Stop campaign when recipient replies',
          default: true
        },

        // Advanced options (optional)
        stop_on_auto_reply: {
          type: 'boolean',
          description: 'Stop campaign when auto-reply is detected (out-of-office, etc.)',
          default: true
        },

        // Multi-step sequence configuration
        sequence_steps: {
          type: 'number',
          description: 'Number of steps in the email sequence (optional, default: 1 for single email, max: 10).\n\n⚠️ MULTI-STEP CAMPAIGNS SUPPORTED:\n• Set to 2 or more to create follow-up sequences\n• Step 1 sends immediately when campaign starts\n• Each step waits step_delay_days before sending next step\n• Example: sequence_steps=3 with step_delay_days=2 creates:\n  Step 1 → Wait 2 days → Step 2 → Wait 2 days → Step 3\n\nUse this for cold outreach sequences, nurture campaigns, and follow-up workflows.',
          minimum: 1,
          maximum: 10,
          default: 1
        },
        step_delay_days: {
          type: 'number',
          description: 'Days to wait AFTER sending each step before sending the next step (optional, default: 3 days).\n\n⚠️ DELAY BEHAVIOR:\n• Applies to ALL steps in the sequence (including Step 1)\n• Step 1: delay=X (wait X days after Step 1 before Step 2)\n• Step 2: delay=X (wait X days after Step 2 before Step 3)\n• Best practices: Use 2-7 days for cold outreach\n• Only used when sequence_steps > 1',
          minimum: 1,
          maximum: 30,
          default: 3
        },
        sequence_subjects: {
          type: 'array',
          items: { type: 'string' },
          description: 'Optional: Custom subject lines for each step (array of strings). Must match sequence_steps count. If not provided, follow-ups use "Follow-up: {original subject}". Example: ["Initial Email", "Follow-up 1", "Follow-up 2"]'
        },
        sequence_bodies: {
          type: 'array',
          items: { type: 'string' },
          description: 'Optional: Custom email bodies for each step (array of strings). Must match sequence_steps count. Use \\n for line breaks. If not provided, follow-ups use auto-generated content. Example: ["Hi {{firstName}},...", "Following up...", "Last attempt..."]'
        }
      },
      required: ['name', 'subject', 'body']
    }
  },

  {
    name: 'list_campaigns',
    title: 'List Campaigns',
    description: 'List campaigns with pagination. Filter by search (name only). Use exact cursor from next_starting_after. Filter by status client-side.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: {
          type: 'number',
          description: 'Number of items per page (1-100, default: 100)',
          minimum: 1,
          maximum: 100
        },
        starting_after: {
          type: 'string',
          description: 'Pagination cursor from previous response. CRITICAL: Use the EXACT value from response.pagination.next_starting_after field (NOT a campaign ID from the data). Example: If previous response had "next_starting_after": "cursor123", use starting_after="cursor123". Omit for first page.'
        },
        search: {
          type: 'string',
          description: 'Search campaigns by campaign NAME only (optional). CRITICAL: Do NOT use this for status filtering (e.g., do NOT search for "running", "active", "paused"). Only use when user explicitly wants to find a campaign by its name. Examples: search="Product Launch", search="Q4 Campaign". Leave empty to list all campaigns.'
        },
        tag_ids: {
          type: 'string',
          description: 'Filter by tag IDs, comma-separated (optional)'
        }
      },
      additionalProperties: false
    }
  },

  {
    name: 'get_campaign',
    title: 'Get Campaign',
    description: 'Get complete campaign details by ID. Returns configuration, sequences, schedules, sender accounts, tracking settings, and status.',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign ID (UUID) - REQUIRED. Get from list_campaigns if you don\'t have it. Example: "9a309ee6-2908-4158-a2c5-431c9bfadf40"' }
      },
      required: ['campaign_id'],
      additionalProperties: false
    }
  },

  {
    name: 'update_campaign',
    title: 'Update Campaign',
    description: 'Update campaign settings (partial updates). Only provide fields to change. Common: name, sequences, tracking, limits, email_list.',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: {
          type: 'string',
          description: 'REQUIRED: ID of the existing campaign to modify. This parameter is mandatory.'
        },
        name: {
          type: 'string',
          description: 'OPTIONAL: New campaign name to UPDATE the existing campaign name. Only provide this if you want to CHANGE the campaign name.'
        },
        pl_value: {
          type: 'number',
          description: 'OPTIONAL: New positive lead value to UPDATE. Only provide this if you want to MODIFY the pl_value setting.'
        },
        is_evergreen: {
          type: 'boolean',
          description: 'OPTIONAL: New evergreen status to UPDATE. Only provide this if you want to CHANGE whether the campaign is evergreen.'
        },
        campaign_schedule: {
          type: 'object',
          description: 'OPTIONAL: New schedule configuration to UPDATE the existing campaign schedule. Only provide this if you want to MODIFY the schedule settings.',
          properties: {
            schedules: {
              type: 'array',
              items: {
                type: 'object'
              }
            }
          }
        },
        sequences: {
          type: 'array',
          description: 'OPTIONAL: New email sequences to UPDATE the existing sequences. Only provide this if you want to MODIFY the email sequences.',
          items: {
            type: 'object'
          }
        },
        email_gap: {
          type: 'number',
          description: 'OPTIONAL: New email gap value (in minutes) to UPDATE. Only provide this if you want to CHANGE the gap between emails.'
        },
        random_wait_max: {
          type: 'number',
          description: 'OPTIONAL: New maximum random wait time (in minutes) to UPDATE. Only provide this if you want to MODIFY the random wait setting.'
        },
        text_only: {
          type: 'boolean',
          description: 'OPTIONAL: New text-only setting to UPDATE. Only provide this if you want to CHANGE whether the campaign is text only.'
        },
        email_list: {
          type: 'array',
          description: 'OPTIONAL: New list of account emails to UPDATE for sending. Only provide this if you want to MODIFY which email accounts are used.',
          items: { type: 'string' }
        },
        daily_limit: {
          type: 'number',
          description: 'OPTIONAL: New daily sending limit to UPDATE per account. Only provide this if you want to CHANGE the daily limit.'
        },
        stop_on_reply: {
          type: 'boolean',
          description: 'OPTIONAL: New stop-on-reply setting to UPDATE. Only provide this if you want to MODIFY whether the campaign stops on reply.'
        },
        email_tag_list: {
          type: 'array',
          description: 'OPTIONAL: New list of email tag UUIDs to UPDATE. Only provide this if you want to CHANGE the email tags.',
          items: { type: 'string' }
        },
        link_tracking: {
          type: 'boolean',
          description: 'OPTIONAL: New link tracking setting to UPDATE. Only provide this if you want to MODIFY whether links are tracked.'
        },
        open_tracking: {
          type: 'boolean',
          description: 'OPTIONAL: New open tracking setting to UPDATE. Only provide this if you want to MODIFY whether opens are tracked.'
        },
        stop_on_auto_reply: {
          type: 'boolean',
          description: 'OPTIONAL: New stop-on-auto-reply setting to UPDATE. Only provide this if you want to CHANGE whether to stop on auto-replies.'
        },
        daily_max_leads: {
          type: 'number',
          description: 'OPTIONAL: New daily maximum leads value to UPDATE. Only provide this if you want to MODIFY the daily max leads setting.'
        },
        prioritize_new_leads: {
          type: 'boolean',
          description: 'OPTIONAL: New prioritize-new-leads setting to UPDATE. Only provide this if you want to CHANGE the lead prioritization.'
        },
        auto_variant_select: {
          type: 'object',
          description: 'OPTIONAL: New auto variant selection settings to UPDATE. Only provide this if you want to MODIFY the auto variant selection configuration.'
        },
        match_lead_esp: {
          type: 'boolean',
          description: 'OPTIONAL: New match-lead-ESP setting to UPDATE. Only provide this if you want to CHANGE whether to match leads by ESP.'
        },
        stop_for_company: {
          type: 'boolean',
          description: 'OPTIONAL: New stop-for-company setting to UPDATE. Only provide this if you want to MODIFY whether to stop for entire company on reply.'
        },
        insert_unsubscribe_header: {
          type: 'boolean',
          description: 'OPTIONAL: New unsubscribe header setting to UPDATE. Only provide this if you want to CHANGE whether to insert unsubscribe headers.'
        },
        allow_risky_contacts: {
          type: 'boolean',
          description: 'OPTIONAL: New risky contacts setting to UPDATE. Only provide this if you want to MODIFY whether to allow risky contacts.'
        },
        disable_bounce_protect: {
          type: 'boolean',
          description: 'OPTIONAL: New bounce protection setting to UPDATE. Only provide this if you want to CHANGE whether bounce protection is disabled.'
        },
        cc_list: {
          type: 'array',
          description: 'OPTIONAL: New CC email addresses list to UPDATE. Only provide this if you want to MODIFY the CC list.',
          items: { type: 'string' }
        },
        bcc_list: {
          type: 'array',
          description: 'OPTIONAL: New BCC email addresses list to UPDATE. Only provide this if you want to MODIFY the BCC list.',
          items: { type: 'string' }
        }
      },
      required: ['campaign_id'],
      additionalProperties: false
    }
  },

  {
    name: 'activate_campaign',
    title: 'Activate Campaign',
    description: 'Activate campaign to start sending. ⚠️ Prerequisites: sender accounts, leads, sequences, schedule. Verify with get_campaign first.',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign ID (UUID) to activate. Get from list_campaigns or create_campaign. Example: "9a309ee6-2908-4158-a2c5-431c9bfadf40"' }
      },
      required: ['campaign_id'],
      additionalProperties: false
    }
  },

  {
    name: 'pause_campaign',
    title: 'Pause Campaign',
    description: 'Pause active campaign to stop sending. Leads remain in campaign. Use activate_campaign to resume. Only works on Active campaigns.',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign ID (UUID, must be Active)' }
      },
      required: ['campaign_id'],
      additionalProperties: false
    }
  },
];

