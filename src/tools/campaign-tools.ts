/**
 * Instantly MCP Server - Campaign Tools (Compacted)
 * 
 * Tool definitions for campaign management operations.
 * Optimized for minimal context window overhead.
 * Total: 6 campaign tools
 */

import { BUSINESS_PRIORITY_TIMEZONES, DEFAULT_TIMEZONE } from '../timezone-config.js';

export const campaignTools = [
  {
    name: 'create_campaign',
    title: 'Create Campaign',
    description: 'Create email campaign. Two-step: 1) Call with name/subject/body to discover accounts, 2) Call again with email_list. Use sequence_steps for multi-step sequences.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Campaign name' },
        subject: { type: 'string', description: 'Subject (<50 chars). Personalization: {{firstName}}, {{companyName}}' },
        body: { type: 'string', description: 'Email body (\\n for line breaks). Personalization: {{firstName}}, {{lastName}}, {{companyName}}' },
        email_list: { type: 'array', items: { type: 'string' }, description: 'Sender emails (from Step 1 eligible list)' },
        track_opens: { type: 'boolean', default: false },
        track_clicks: { type: 'boolean', default: false },
        timezone: { type: 'string', default: DEFAULT_TIMEZONE, description: `Supported: ${BUSINESS_PRIORITY_TIMEZONES.slice(0, 5).join(', ')}...` },
        timing_from: { type: 'string', default: '09:00', description: '24h format' },
        timing_to: { type: 'string', default: '17:00', description: '24h format' },
        daily_limit: { type: 'number', default: 30, description: 'Emails/day/account (max 30)' },
        email_gap: { type: 'number', default: 10, description: 'Minutes between emails (1-1440)' },
        stop_on_reply: { type: 'boolean', default: true },
        stop_on_auto_reply: { type: 'boolean', default: true },
        sequence_steps: { type: 'number', default: 1, description: 'Steps in sequence (1-10)' },
        step_delay_days: { type: 'number', default: 3, description: 'Days between steps (1-30)' },
        sequence_subjects: { type: 'array', items: { type: 'string' }, description: 'Custom subjects per step' },
        sequence_bodies: { type: 'array', items: { type: 'string' }, description: 'Custom bodies per step' }
      },
      required: ['name', 'subject', 'body']
    }
  },

  {
    name: 'list_campaigns',
    title: 'List Campaigns',
    description: 'List campaigns with pagination. Filter by name search or tags.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: '1-100, default: 100' },
        starting_after: { type: 'string', description: 'Cursor from pagination.next_starting_after' },
        search: { type: 'string', description: 'Search by campaign NAME only (not status)' },
        tag_ids: { type: 'string', description: 'Comma-separated tag IDs' }
      }
    }
  },

  {
    name: 'get_campaign',
    title: 'Get Campaign',
    description: 'Get campaign details: config, sequences, schedules, sender accounts, tracking, status',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign UUID' }
      },
      required: ['campaign_id']
    }
  },

  {
    name: 'update_campaign',
    title: 'Update Campaign',
    description: 'Update campaign settings (partial). Common: name, sequences, tracking, limits, email_list.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign to update' },
        name: { type: 'string' },
        pl_value: { type: 'number' },
        is_evergreen: { type: 'boolean' },
        campaign_schedule: { type: 'object', properties: { schedules: { type: 'array', items: { type: 'object' } } } },
        sequences: { type: 'array', items: { type: 'object' } },
        email_gap: { type: 'number' },
        random_wait_max: { type: 'number' },
        text_only: { type: 'boolean' },
        email_list: { type: 'array', items: { type: 'string' } },
        daily_limit: { type: 'number' },
        stop_on_reply: { type: 'boolean' },
        email_tag_list: { type: 'array', items: { type: 'string' } },
        link_tracking: { type: 'boolean' },
        open_tracking: { type: 'boolean' },
        stop_on_auto_reply: { type: 'boolean' },
        daily_max_leads: { type: 'number' },
        prioritize_new_leads: { type: 'boolean' },
        auto_variant_select: { type: 'object' },
        match_lead_esp: { type: 'boolean' },
        stop_for_company: { type: 'boolean' },
        insert_unsubscribe_header: { type: 'boolean' },
        allow_risky_contacts: { type: 'boolean' },
        disable_bounce_protect: { type: 'boolean' },
        cc_list: { type: 'array', items: { type: 'string' } },
        bcc_list: { type: 'array', items: { type: 'string' } }
      },
      required: ['campaign_id']
    }
  },

  {
    name: 'activate_campaign',
    title: 'Activate Campaign',
    description: 'Start sending. Prerequisites: accounts, leads, sequences, schedule.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Campaign UUID to activate' }
      },
      required: ['campaign_id']
    }
  },

  {
    name: 'pause_campaign',
    title: 'Pause Campaign',
    description: 'Stop sending (leads remain). Use activate_campaign to resume.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: { type: 'string', description: 'Active campaign UUID' }
      },
      required: ['campaign_id']
    }
  },
];

