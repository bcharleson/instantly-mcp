/**
 * Instantly MCP Server - Account Tools (Compacted)
 * 
 * Tool definitions for account management operations.
 * Optimized for minimal context window overhead.
 * Total: 10 account tools (consolidated get_account_details + get_account_info)
 */

export const accountTools = [
  {
    name: 'list_accounts',
    title: 'List Accounts',
    description: 'List email accounts with pagination. Filter by status, provider, or tags.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: '1-100, default: 100' },
        starting_after: { type: 'string', description: 'Cursor from pagination.next_starting_after' },
        search: { type: 'string', description: 'Search by email domain' },
        status: { type: 'number', description: '1=Active, 2=Paused, -1/-2/-3=Errors', enum: [1, 2, -1, -2, -3] },
        provider_code: { type: 'number', description: '1=IMAP, 2=Google, 3=Microsoft, 4=AWS', enum: [1, 2, 3, 4] },
        tag_ids: { type: 'string', description: 'Comma-separated tag IDs' }
      }
    }
  },

  {
    name: 'get_account',
    title: 'Get Account',
    description: 'Get account details, warmup status, and campaign eligibility by email',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Account email address' }
      },
      required: ['email']
    }
  },

  {
    name: 'create_account',
    title: 'Create Account',
    description: 'Create email account with IMAP/SMTP credentials',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string' },
        first_name: { type: 'string' },
        last_name: { type: 'string' },
        provider_code: { type: 'number', description: '1=IMAP, 2=Google, 3=Microsoft, 4=AWS' },
        imap_username: { type: 'string' },
        imap_password: { type: 'string' },
        imap_host: { type: 'string', description: 'e.g., imap.gmail.com' },
        imap_port: { type: 'number', description: 'e.g., 993' },
        smtp_username: { type: 'string' },
        smtp_password: { type: 'string' },
        smtp_host: { type: 'string', description: 'e.g., smtp.gmail.com' },
        smtp_port: { type: 'number', description: 'e.g., 587' }
      },
      required: ['email', 'first_name', 'last_name', 'provider_code', 'imap_username', 'imap_password', 'imap_host', 'imap_port', 'smtp_username', 'smtp_password', 'smtp_host', 'smtp_port']
    }
  },

  {
    name: 'update_account',
    title: 'Update Account',
    description: 'Update account settings (partial). Supports name, warmup, daily_limit, sending_gap, tracking_domain.',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Account to update' },
        first_name: { type: 'string' },
        last_name: { type: 'string' },
        warmup: {
          type: 'object',
          properties: {
            limit: { type: 'number' },
            advanced: {
              type: 'object',
              properties: {
                warm_ctd: { type: 'boolean' },
                open_rate: { type: 'number' },
                important_rate: { type: 'number' },
                read_emulation: { type: 'boolean' },
                spam_save_rate: { type: 'number' },
                weekday_only: { type: 'boolean' }
              }
            },
            warmup_custom_ftag: { type: 'string' },
            increment: { type: 'string' },
            reply_rate: { type: 'number' }
          }
        },
        daily_limit: { type: 'number' },
        sending_gap: { type: 'number', description: 'Minutes between emails (0-1440)' },
        enable_slow_ramp: { type: 'boolean' },
        tracking_domain_name: { type: 'string' },
        tracking_domain_status: { type: 'string' },
        skip_cname_check: { type: 'boolean' },
        remove_tracking_domain: { type: 'boolean' },
        inbox_placement_test_limit: { type: 'number' }
      },
      required: ['email']
    }
  },

  {
    name: 'manage_account_state',
    title: 'Manage Account State',
    description: 'Pause, resume, enable/disable warmup, or test account vitals',
    annotations: { destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Account email' },
        action: { 
          type: 'string', 
          description: 'Action to perform',
          enum: ['pause', 'resume', 'enable_warmup', 'disable_warmup', 'test_vitals']
        }
      },
      required: ['email', 'action']
    }
  },

  {
    name: 'delete_account',
    title: 'Delete Account',
    description: '🚨 PERMANENTLY delete account. CANNOT UNDO. All data lost forever!',
    annotations: { destructiveHint: true, confirmationRequiredHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: 'Email to DELETE PERMANENTLY' }
      },
      required: ['email']
    }
  },
];

