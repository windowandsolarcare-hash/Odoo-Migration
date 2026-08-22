---
name: Calendly MCP — connected via claude.ai
description: Calendly MCP is connected through claude.ai connector (NOT local config) and is authorized
type: project
originSessionId: 75cd1fdf-a7f2-4768-a19e-857871ea5c7c
---
Calendly MCP is connected and authorized via the **claude.ai connector** (same method as Gmail, Google Calendar, Zapier). It shows up as `claude.ai Calendly` in `/mcp`.

**How it was set up (2026-04-12):**
- Local config entry (`https://mcp.calendly.com/mcp`) was removed — it caused OAuth failures ("No client info found", "SDK auth error: hNH") because Calendly's MCP doesn't support dynamic client registration from local config
- Added via claude.ai → Settings → Integrations → Calendly → OAuth approved in browser
- Now shows as `claude.ai calendly · ✔ connected` in `/mcp`

**Why local config failed:** Calendly's auth server requires pre-registered OAuth client credentials. Claude Code's local MCP OAuth uses dynamic client registration which Calendly doesn't support. The claude.ai proxy handles this correctly.

**Correct URL (FYI):** `https://mcp.calendly.com` (no `/mcp` suffix) — but irrelevant now since it's connected via claude.ai.

**Confirmed working 2026-04-12:** Listed events, got current user (Window & Solar Care / windowandsolarcare@gmail.com). Tools are live and authorized.

**Why:** DJ wants Claude Code to manage Calendly — view/change availability, event types, booking links, meetings.

**How to apply:** Tools load as `mcp__claude_ai_calendly__*` (lowercase). Use `get_current_user` first to get the user URI, then pass it to `meetings-list_events` etc. No special setup needed — just start a new chat.
