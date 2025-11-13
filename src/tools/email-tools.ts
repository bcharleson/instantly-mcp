/**
 * Instantly MCP Server - Email Tools
 *
 * Tool definitions for email management and communication operations.
 * Total: 5 email tools
 */

export const emailTools = [
  {
    name: 'list_emails',
    title: 'List Emails',
    description: 'List emails with pagination. Filter by campaign_id, search, account, or type. Use exact cursor from next_starting_after.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: 'Items per page (1-100, default: 100)', minimum: 1, maximum: 100 },
        starting_after: { type: 'string', description: 'Cursor from next_starting_after' },
        search: { type: 'string', description: 'Email/thread search (use "thread:UUID")' },
        campaign_id: { type: 'string', description: 'Campaign ID (recommended)' },
        i_status: { type: 'number', description: 'Interest status' },
        eaccount: { type: 'string', description: 'Sender account (comma-separated)' },
        is_unread: { type: 'boolean', description: 'Unread filter' },
        has_reminder: { type: 'boolean', description: 'Reminder filter' },
        mode: { type: 'string', description: 'Mode filter', enum: ['emode_focused', 'emode_others', 'emode_all'] },
        preview_only: { type: 'boolean', description: 'Preview only' },
        sort_order: { type: 'string', description: 'Sort order', enum: ['asc', 'desc'] },
        scheduled_only: { type: 'boolean', description: 'Scheduled only' },
        assigned_to: { type: 'string', description: 'Assigned user ID' },
        lead: { type: 'string', description: 'Lead email' },
        company_domain: { type: 'string', description: 'Company domain' },
        marked_as_done: { type: 'boolean', description: 'Marked as done' },
        email_type: { type: 'string', description: 'Email type', enum: ['received', 'sent', 'manual'] }
      },
      additionalProperties: false
    }
  },

  {
    name: 'get_email',
    title: 'Get Email',
    description: 'Get email details by ID',
    inputSchema: {
      type: 'object',
      properties: {
        email_id: { type: 'string', description: 'Email ID' }
      },
      required: ['email_id'],
      additionalProperties: false
    }
  },

  {
    name: 'reply_to_email',
    title: 'Reply to Email',
    description: '🚨 SENDS REAL EMAILS! ⚠️ ALWAYS confirm with user BEFORE calling. Cannot undo! Requires reply_to_uuid, eaccount, subject, body.',
    inputSchema: {
      type: 'object',
      properties: {
        reply_to_uuid: {
          type: 'string',
          description: 'Email UUID to reply to (from list_emails)'
        },
        eaccount: {
          type: 'string',
          description: 'Sender account (must be active)'
        },
        subject: {
          type: 'string',
          description: 'Subject line (e.g., "Re: [original]")'
        },
        body: {
          type: 'object',
          description: 'Email body (html/text or both)',
          properties: {
            html: { type: 'string', description: 'HTML content' },
            text: { type: 'string', description: 'Plain text content' }
          },
          additionalProperties: false
        }
      },
      required: ['reply_to_uuid', 'eaccount', 'subject', 'body'],
      additionalProperties: false
    }
  },

  {
    name: 'count_unread_emails',
    title: 'Count Unread Emails',
    description: 'Count unread emails in inbox (read-only)',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false
    }
  },

  {
    name: 'verify_email',
    title: 'Verify Email',
    description: 'Verify email deliverability (5-45s). Returns status, score, reason, flags. For bulk verification, use verify_leads_on_import in create_lead.',
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Email to verify (user@domain.com)' }
      },
      required: ['email'],
      additionalProperties: false
    }
  },
];

