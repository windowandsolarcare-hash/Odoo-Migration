---
name: feedback_api_keys_via_file
description: "How DJ wants to hand me API keys/secrets: put them in a dedicated file and tell me the path — NEVER paste in chat. Read without printing."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# Give me API keys via a file path, not in chat (DJ, 2026-07-04)

When I need an API key/secret, DJ will **put it in a dedicated file on his drive and tell me the path** — I should NOT ask him to paste it into chat.

**Why:** On 2026-07-04 DJ pasted his Render API key AND a **live Stripe secret key** (`sk_live_…`) straight into the chat to unblock a cron change. Anything pasted in chat lives in the transcript forever = compromised → we had to rotate both keys. A file path avoids that.

**How to apply:**
- Preferred: DJ keeps keys in a folder like `C:\Users\dj\keys\` (one file per key, e.g. `render.txt`, `stripe.txt`, key on its own line). He tells me "the X key is at <path>."
- When USING it, pull it straight into the command so it never prints: `RK=$(cat /c/Users/dj/keys/render.txt); curl -H "Authorization: Bearer $RK" ...`. Don't `echo` it, don't Read it into my context if a shell var will do.
- ★ The MCP server keys (Render, Stripe) live in `~/.claude/mcp.json` (`mcpServers.<name>.headers.Authorization` / stripe `--api-key`), BUT the auto-mode safety classifier BLOCKS me from scraping that file ("credential exploration") — do not try. Reading ONE specific file DJ deliberately points me to is fine; if it ever balks, DJ adds a permission rule for that path.
- Rotating a key: Render = dashboard → Account Settings → API Keys (delete+create), then update `mcp.json`. Stripe = Developers → API keys → Roll (the new key is permanent; the "expiration" picker only sets the OLD key's grace period, max ~7 days — not the new key). After rotating an MCP key mid-session, tools may hold the stale key until a Claude Code restart.
