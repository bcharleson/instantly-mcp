# Instantly MCP Server (Python)

A lightweight, robust Model Context Protocol (MCP) server for the **Instantly.ai V2 API**, built with FastMCP.

## Features

- **38 tools** across 6 categories (accounts, campaigns, leads, emails, analytics, background_jobs)
- **Dual transport support**: HTTP (remote deployment) + stdio (local)
- **Lazy loading**: Reduce context window by loading only specific tool categories
- **Multi-tenant support**: Per-request API keys for HTTP deployments
- **Comprehensive error handling**: Detailed, actionable error messages
- **Rate limiting**: Automatic tracking from API response headers
- **Dynamic timeouts**: Extended timeouts for search and bulk operations

## Quick Start

### Installation

```bash
# Clone or navigate to the repository
cd instantly-mcp-python

# Install with pip
pip install -e .

# Or install dependencies directly
pip install fastmcp httpx pydantic python-dotenv
```

### Configuration

Set your Instantly API key:

```bash
export INSTANTLY_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```env
INSTANTLY_API_KEY=your-api-key-here
```

### Running the Server

#### HTTP Mode (Recommended for Remote Deployment)

```bash
# Using FastMCP CLI
fastmcp run src/instantly_mcp/server.py --transport http --port 8000

# Using Python directly
python -m instantly_mcp.server --transport http --port 8000

# Or with uvicorn for production
uvicorn instantly_mcp.server:mcp.app --host 0.0.0.0 --port 8000
```

#### stdio Mode (Local Development)

```bash
# Using FastMCP CLI
fastmcp run src/instantly_mcp/server.py

# Using Python directly
python -m instantly_mcp.server
```

## Tool Categories

### Accounts (6 tools)
| Tool | Description |
|------|-------------|
| `list_accounts` | List email accounts with filtering |
| `get_account` | Get account details and warmup status |
| `create_account` | Create account with IMAP/SMTP credentials |
| `update_account` | Update account settings |
| `manage_account_state` | Pause, resume, warmup control, test vitals |
| `delete_account` | ⚠️ Permanently delete account |

### Campaigns (8 tools)
| Tool | Description |
|------|-------------|
| `create_campaign` | Create email campaign (two-step process) |
| `list_campaigns` | List campaigns with pagination |
| `get_campaign` | Get campaign details and sequences |
| `update_campaign` | Update campaign settings |
| `activate_campaign` | Start campaign sending |
| `pause_campaign` | Stop campaign sending |
| `delete_campaign` | ⚠️ Permanently delete campaign |
| `search_campaigns_by_contact` | Find campaigns a contact is enrolled in |

### Leads (12 tools)
| Tool | Description |
|------|-------------|
| `list_leads` | List leads with filtering |
| `get_lead` | Get lead details |
| `create_lead` | Create single lead |
| `update_lead` | Update lead (⚠️ custom_variables replaces all) |
| `list_lead_lists` | List lead lists |
| `create_lead_list` | Create lead list |
| `update_lead_list` | Update lead list |
| `get_verification_stats_for_lead_list` | Get email verification stats |
| `add_leads_to_campaign_or_list_bulk` | Bulk add up to 1,000 leads |
| `delete_lead` | ⚠️ Permanently delete lead |
| `delete_lead_list` | ⚠️ Permanently delete lead list |
| `move_leads_to_campaign_or_list` | Move/copy leads between campaigns/lists |

### Emails (6 tools)
| Tool | Description |
|------|-------------|
| `list_emails` | List emails with filtering |
| `get_email` | Get email details |
| `reply_to_email` | 🚨 Send real email reply |
| `count_unread_emails` | Count unread inbox emails |
| `verify_email` | Verify email deliverability |
| `mark_thread_as_read` | Mark email thread as read |

### Analytics (3 tools)
| Tool | Description |
|------|-------------|
| `get_campaign_analytics` | Campaign metrics (opens, clicks, replies) |
| `get_daily_campaign_analytics` | Day-by-day performance |
| `get_warmup_analytics` | Account warmup metrics |

### Background Jobs (2 tools)
| Tool | Description |
|------|-------------|
| `list_background_jobs` | List async background jobs with pagination |
| `get_background_job` | Get details of a specific background job |

## Lazy Loading (Context Window Optimization)

Reduce context window usage by loading only the categories you need:

```bash
# Load only accounts and campaigns (14 tools instead of 38)
export TOOL_CATEGORIES="accounts,campaigns"

# Load only leads and analytics
export TOOL_CATEGORIES="leads,analytics"
```

Valid categories: `accounts`, `campaigns`, `leads`, `emails`, `analytics`, `background_jobs`

## Authentication Methods

The server supports multiple authentication methods for flexibility:

### 1. URL-based Authentication

Include your API key directly in the URL path:

```
https://your-server.com/mcp/YOUR_API_KEY
```

### 2. Header Authentication

```
URL: https://your-server.com/mcp
Header: Authorization: YOUR_API_KEY
```

*Note: Bearer token prefix is optional*

### 3. Custom Header

```
URL: https://your-server.com/mcp
Header: x-instantly-api-key: YOUR_API_KEY
```

### 4. Environment Variable

```bash
export INSTANTLY_API_KEY="your-api-key-here"
```

## MCP Client Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

#### stdio Mode (Local)
```json
{
  "mcpServers": {
    "instantly": {
      "command": "python",
      "args": ["-m", "instantly_mcp.server"],
      "env": {
        "INSTANTLY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### HTTP Mode with URL Auth (Recommended)
```json
{
  "mcpServers": {
    "instantly": {
      "url": "https://your-server.com/mcp/YOUR_API_KEY"
    }
  }
}
```

#### HTTP Mode with Header Auth
```json
{
  "mcpServers": {
    "instantly": {
      "url": "https://your-server.com/mcp",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "your-api-key-here"
      }
    }
  }
}
```

### Cursor IDE

Add to `~/.cursor/mcp.json`:

#### With URL Authentication
```json
{
  "mcpServers": {
    "instantly": {
      "url": "https://your-server.com/mcp/YOUR_API_KEY"
    }
  }
}
```

#### With Header Authentication
```json
{
  "mcpServers": {
    "instantly": {
      "url": "https://your-server.com/mcp",
      "transport": "streamable-http",
      "headers": {
        "x-instantly-api-key": "your-api-key-here"
      }
    }
  }
}
```

## DigitalOcean App Platform Deployment

### App Spec

```yaml
name: instantly-mcp
services:
  - name: instantly-mcp
    source:
      git:
        branch: main
        repo_clone_url: https://github.com/your-username/instantly-mcp-python.git
    build_command: pip install -e .
    run_command: python -m instantly_mcp.server --transport http --port 8080
    http_port: 8080
    instance_size_slug: basic-xxs
    instance_count: 1
    envs:
      - key: INSTANTLY_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: PORT
        scope: RUN_TIME
        value: "8080"
```

### Dockerfile (Alternative)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install -e .

EXPOSE 8000

CMD ["python", "-m", "instantly_mcp.server", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
```

## Multi-Tenant HTTP Mode

For deployments serving multiple users, the server supports per-request API keys:

```bash
# Start server without default API key
python -m instantly_mcp.server --transport http --port 8000

# Clients provide API key via header
curl -X POST http://localhost:8000/mcp \
  -H "x-instantly-api-key: user-specific-api-key" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## Error Handling

The server provides detailed, actionable error messages:

```json
{
  "error": {
    "code": "invalid_api_key",
    "message": "Instantly API key is required. Provide via:\n  - INSTANTLY_API_KEY environment variable\n  - api_key parameter\n  - x-instantly-api-key header (HTTP mode)"
  }
}
```

## Rate Limiting

The server automatically tracks rate limits from API response headers:

```python
# Access via get_server_info tool
{
  "rate_limit": {
    "remaining": 95,
    "limit": 100,
    "reset_at": "2024-01-15T12:00:00"
  }
}
```

## Project Structure

```
instantly-mcp-python/
├── src/
│   └── instantly_mcp/
│       ├── __init__.py          # Package exports
│       ├── server.py            # FastMCP server (~180 lines)
│       ├── client.py            # API client (~200 lines)
│       ├── models/              # Pydantic models
│       │   ├── __init__.py
│       │   ├── common.py        # Pagination
│       │   ├── accounts.py      # Account models
│       │   ├── campaigns.py     # Campaign models
│       │   ├── leads.py         # Lead models
│       │   ├── emails.py        # Email models
│       │   └── analytics.py     # Analytics models
│       └── tools/               # Tool implementations
│           ├── __init__.py      # Lazy loading logic
│           ├── accounts.py      # 6 account tools
│           ├── campaigns.py     # 8 campaign tools
│           ├── leads.py         # 12 lead tools
│           ├── emails.py        # 6 email tools
│           ├── analytics.py     # 3 analytics tools
│           └── background_jobs.py # 2 background job tools
├── pyproject.toml               # Dependencies
├── env.example                  # Environment template
└── README.md                    # This file
```

## Comparison with TypeScript Version

| Aspect | TypeScript | Python FastMCP |
|--------|------------|----------------|
| Lines of Code | ~5,000+ | ~1,500 |
| Tool Registration | Manual handlers | `@mcp.tool` decorator |
| Input Validation | Zod schemas | Pydantic (auto) |
| Error Messages | Manual | Auto from Pydantic |
| HTTP Server | Custom transport | Built-in |
| Context Window | Larger schemas | Smaller, cleaner |

## API Reference

For detailed API documentation, see: [Instantly V2 API Docs](https://developer.instantly.ai/api/v2)

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or PR.

