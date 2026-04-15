# Render Setup Guide — Window & Solar Care AI Assistant
**Last Updated:** 2026-04-15
**Purpose:** Replicate the field assistant app on Render using Claude (Anthropic) instead of ChatGPT (OpenAI)

---

## OVERVIEW

The Render app is a Python/Flask web service that acts as an AI field assistant. It currently uses OpenAI's GPT via the ChatGPT API. This guide covers replacing that with Anthropic's Claude API while keeping all other integrations identical.

The app exposes tools to Claude/GPT that read/write Workiz jobs, Odoo records, and send emails. DJ uses it in the field via a chat interface.

---

## ARCHITECTURE

```
[DJ on phone] → [Render Flask app] → [Claude API (Anthropic)]
                       ↓
              [Workiz REST API]
              [Odoo JSON-RPC API]
              [Gmail / Email]
```

---

## ENVIRONMENT VARIABLES (set in Render dashboard)

These go in Render → Your Service → Environment tab.

### Odoo
| Variable | Value |
|---|---|
| `ODOO_URL` | `https://window-solar-care.odoo.com/jsonrpc` |
| `ODOO_DB` | `window-solar-care` |
| `ODOO_USER_ID` | `2` |
| `ODOO_API_KEY` | `[see RENDER_SETUP_PRIVATE.md — never commit]` |

### Workiz
| Variable | Value |
|---|---|
| `WORKIZ_API_TOKEN` | `[see RENDER_SETUP_PRIVATE.md — never commit]` |
| `WORKIZ_AUTH_SECRET` | `[see RENDER_SETUP_PRIVATE.md — never commit]` |

### AI Provider (CHANGE THIS when switching from OpenAI to Anthropic)
| Variable | Old (OpenAI) | New (Anthropic) |
|---|---|---|
| `OPENAI_API_KEY` | your OpenAI key | remove this |
| `ANTHROPIC_API_KEY` | — | `[your Anthropic API key]` |

### Optional
| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | If app reads from GitHub repo directly |
| `FROM_EMAIL` | Sender address for email tool |
| `SMTP_PASSWORD` | App password for Gmail SMTP |

---

## CURRENT TOOLS (20 total in app.py)

### Read Tools (no confirmation needed)
| Tool | What it does |
|---|---|
| `search_customers` | Search Odoo contacts by name |
| `get_customer_profile` | Full contact record + history |
| `get_job_details` | Single Workiz job by UUID or serial ID |
| `get_schedule` | Today's/upcoming jobs from Workiz |
| `get_next_job` | Next scheduled job |
| `get_sales` | Revenue for a date range |
| `get_sales_week` | Weekly revenue Mon–Sat only |
| `get_jobs_list` | Browse Workiz jobs list |
| `navigate_to` | Generate maps/directions link |

### Write Tools (require confirmation before executing)
| Tool | What it does |
|---|---|
| `update_workiz_field` | Update any field on a Workiz job |
| `update_odoo_contact` | Update fields on an Odoo contact |
| `post_odoo_note` | Add a chatter note to an Odoo record |
| `create_todo` | Create a task/activity in Odoo |
| `mark_job_done` | Mark Workiz job as Done |
| `create_workiz_job` | Create a new job in Workiz |
| `duplicate_workiz_job` | Copy most recent job to a new date |
| `start_task_timer` | Start Odoo field service timer |
| `stop_task_timer` | Stop Odoo field service timer |

### Utility Tools
| Tool | What it does |
|---|---|
| `send_email` | Send email via Gmail SMTP |
| `save_memory` | Persist a note to app memory |
| `delete_memory` | Remove a memory entry |

**Important rules baked into tool descriptions:**
- `get_sales_week` = Mon–Sat only, never use for revenue on Sundays
- `get_jobs_list` = browse only, NEVER for revenue calculation
- `duplicate_workiz_job` = copies all fields from most recent job for that customer
- All tasks/notes created by Render app are tagged `[Render]` in the title

---

## SWITCHING FROM OPENAI TO ANTHROPIC

### 1. Install Anthropic SDK
```
pip install anthropic
```
Add to `requirements.txt`:
```
anthropic>=0.25.0
```

### 2. Replace the client initialization in app.py
```python
# OLD (OpenAI)
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# NEW (Anthropic)
import anthropic
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

### 3. Replace the chat completion call
```python
# OLD (OpenAI)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools
)

# NEW (Anthropic)
response = client.messages.create(
    model="claude-sonnet-4-6",          # or claude-opus-4-6 for most capable
    max_tokens=8096,
    system=system_prompt,               # system goes here, not in messages
    messages=messages,                  # user/assistant turns only
    tools=tools                         # same structure works
)
```

### 4. Tool call handling differences
OpenAI and Anthropic handle tool calls slightly differently:

```python
# OpenAI pattern
if response.choices[0].finish_reason == "tool_calls":
    tool_calls = response.choices[0].message.tool_calls

# Anthropic pattern
if response.stop_reason == "tool_use":
    tool_calls = [b for b in response.content if b.type == "tool_use"]
```

Tool result format difference:
```python
# OpenAI
{"role": "tool", "tool_call_id": tc.id, "content": result_string}

# Anthropic
{"role": "user", "content": [{"type": "tool_result", "tool_use_id": tc.id, "content": result_string}]}
```

### 5. Recommended model
Use `claude-sonnet-4-6` for the field assistant — fast, capable, cost-effective.
Use `claude-opus-4-6` if you need maximum reasoning for complex queries.

---

## MCP SERVERS (Claude Code / claude.ai only — NOT available on Render)

These are connected to DJ's personal claude.ai account and run in Claude Code sessions only. They cannot be replicated on a Render server — they require OAuth authorization through claude.ai.

| MCP Server | What it does | How to reconnect |
|---|---|---|
| Gmail | Read/search/draft emails | claude.ai → Integrations → Gmail |
| Google Calendar | Read/create/update events | claude.ai → Integrations → Google Calendar |
| Google Drive | File access | claude.ai → Integrations → Google Drive |
| QuickBooks (Intuit) | P&L reports, transaction import | claude.ai → Integrations → QuickBooks |
| Calendly | Scheduling links, event types | claude.ai → Integrations → Calendly |
| Zapier | Trigger zaps, webhooks | claude.ai → Integrations → Zapier |

**To replicate these on Render:** You would need to build direct API integrations using each service's OAuth flow. This is a significant project. For the Render field assistant, the Workiz + Odoo tools cover day-to-day operations — the MCPs are for back-office/admin tasks done in Claude Code desktop.

---

## API CONNECTIONS SUMMARY

### Odoo (JSON-RPC)
- **Endpoint:** `https://window-solar-care.odoo.com/jsonrpc`
- **Auth:** User ID + API Key (basic auth via execute_kw)
- **Used for:** Contacts, Sales Orders, Tasks, Invoices, Activities, Notes
- **IP restriction:** None — accessible from anywhere

### Workiz (REST API)
- **Base URL:** `https://api.workiz.com/api/v1/{TOKEN}/`
- **Auth:** Token in URL path + `?auth_secret={SECRET}` query param on every request
- **Used for:** Job CRUD, client data, status updates
- **IP restriction:** YES — Workiz blocks non-whitelisted IPs. Render server IP must be whitelisted in Workiz. Local machines get 403.
- **Rate limit:** ~30 calls before HTTP 429 — sleep 15–30s between batches

### GitHub (gh CLI / REST API)
- **Used by:** Claude Code desktop only (for deploying Zapier code)
- **Auth:** gh CLI authenticated to windowandsolarcare-hash account
- **Not needed on Render**

### Zapier (webhook triggers)
- **Direction:** Zapier calls Render/Odoo webhooks (inbound), not the other way around
- **Phases 3, 4, 5, 6** are Zapier-hosted Python scripts that call Odoo/Workiz
- **Not needed as env var on Render** — Zapier has its own credential store

---

## RENDER SERVICE CONFIGURATION

- **Runtime:** Python 3
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app` (or `python app.py` for dev)
- **Health check path:** `/` or `/health`
- **Plan:** Free tier works for low-traffic; upgrade if timeouts occur on Workiz calls

---

## WORKIZ IP WHITELIST

The Render server's outbound IP must be whitelisted in Workiz settings.
- Find Render's outbound IP: check Render dashboard or run `curl ifconfig.me` in a Render shell
- Add to Workiz: Settings → API → Allowed IPs

---

## ZAPIER WEBHOOKS (inbound to Odoo — not Render)

These Zapier phases call Odoo directly, not the Render app:
- **Phase 3:** New Workiz job → creates Odoo SO
- **Phase 4:** Job status updates → syncs to Odoo
- **Phase 5:** Auto-schedule next maintenance job
- **Phase 6:** Payment sync → Workiz ← Odoo invoice paid

**STOP webhook** (Workiz → Odoo direct):
`https://window-solar-care.odoo.com/web/hook/f64d0bc1-54fd-45a1-b645-0dcae6ae1728`

---

## FILES IN THIS REPO

| File | Location | Purpose |
|---|---|---|
| Phase 3 | `1_Production_Code/zapier_phase3_FLATTENED_FINAL.py` | New job sync Workiz→Odoo |
| Phase 4 | `1_Production_Code/zapier_phase4_FLATTENED_FINAL.py` | Status update sync |
| Phase 5 | `1_Production_Code/zapier_phase5_FLATTENED_FINAL.py` | Auto-schedule next job |
| Phase 6 | `1_Production_Code/zapier_phase6_FLATTENED_FINAL.py` | Payment sync |
| Calendly | `1_Production_Code/zapier_calendly_booking_FLATTENED_FINAL.py` | Booking handler |
| Reactivation | `1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` | SMS reactivation |
| STOP handler | `1_Production_Code/odoo_webhook_stop_handler.py` | STOP compliance |

**Note:** The Render `app.py` is NOT in this repo — it lives on Render directly. Contact DJ for a copy.

---

## NOTES FOR FUTURE CLAUDE SESSIONS

- This doc lives at: `3_Documentation/RENDER_SETUP.md`
- Private credentials doc (local only, never push): `3_Documentation/RENDER_SETUP_PRIVATE.md`
- The goal is to replace OpenAI GPT in the Render app with Anthropic Claude
- All tool logic stays the same — only the AI client library changes
