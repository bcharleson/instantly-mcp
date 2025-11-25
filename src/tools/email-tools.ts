/**
 * Instantly MCP Server - Email Tools (Compacted)
 *
 * Tool definitions for email management operations.
 * Optimized for minimal context window overhead.
 * Total: 5 email tools
 */

export const emailTools = [
  {
    name: 'list_emails',
    title: 'List Emails',
    description: 'List emails with pagination. Filter by campaign, account, type, or status.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: '1-100, default: 100' },
        starting_after: { type: 'string', description: 'Cursor from pagination' },
        search: { type: 'string', description: 'Search (use "thread:UUID" for threads)' },
        campaign_id: { type: 'string' },
        i_status: { type: 'number', description: 'Interest status' },
        eaccount: { type: 'string', description: 'Sender accounts (comma-separated)' },
        is_unread: { type: 'boolean' },
        has_reminder: { type: 'boolean' },
        mode: { type: 'string', enum: ['emode_focused', 'emode_others', 'emode_all'] },
        preview_only: { type: 'boolean' },
        sort_order: { type: 'string', enum: ['asc', 'desc'] },
        scheduled_only: { type: 'boolean' },
        assigned_to: { type: 'string' },
        lead: { type: 'string', description: 'Lead email' },
        company_domain: { type: 'string' },
        marked_as_done: { type: 'boolean' },
        email_type: { type: 'string', enum: ['received', 'sent', 'manual'] }
      }
    }
  },

  {
    name: 'get_email',
    title: 'Get Email',
    description: 'Get email details by ID',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        email_id: { type: 'string', description: 'Email UUID' }
      },
      required: ['email_id']
    }
  },

  {
    name: 'reply_to_email',
    title: 'Reply to Email',
    description: '🚨 SENDS REAL EMAIL! Confirm with user first. Cannot undo!',
    annotations: { destructiveHint: true, confirmationRequiredHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        reply_to_uuid: { type: 'string', description: 'Email UUID to reply to' },
        eaccount: { type: 'string', description: 'Sender account (must be active)' },
        subject: { type: 'string', description: 'Subject line' },
        body: {
          type: 'object',
          properties: {
            html: { type: 'string' },
            text: { type: 'string' }
          }
        }
      },
      required: ['reply_to_uuid', 'eaccount', 'subject', 'body']
    }
  },

  {
    name: 'count_unread_emails',
    title: 'Count Unread',
    description: 'Count unread emails in inbox',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },

  {
    name: 'verify_email',
    title: 'Verify Email',
    description: 'Verify email deliverability (5-45s). Returns status, score, flags.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Email to verify' }
      },
      required: ['email']
    }
  },
];

