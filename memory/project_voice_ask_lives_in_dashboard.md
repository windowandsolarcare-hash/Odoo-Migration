---
name: project_voice_ask_lives_in_dashboard
description: "★ The LIVE field voice assistant /owner/ask is in dashboard.py, NOT field.py — dashboard registers first and SHADOWS field.py's identical /ask. Edit dashboard.py for any voice-assistant change."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-19T21:31:29.461Z
---

**★ CRITICAL (discovered 2026-08-19, cost hours): the field voice assistant's `/owner/ask` is served by `routers/owner/dashboard.py`, NOT `routers/owner/field.py`.** BOTH files define `@router.post('/ask')` with their own `TOOLS`, `READ_TOOL_MAP`, `SYSTEM_PROMPT`, `_agent_loop`, `run_agent`. In `main.py`, `owner_dashboard.router` is included (line ~241) BEFORE `owner_field.router` (~242), both under prefix `/owner` — so FastAPI routes `/owner/ask` to **dashboard.py** and field.py's `/ask` is DEAD (shadowed, same as dashboard shadows hemet.py per CLAUDE.md's paired-changes table).

**How it bit us:** I built the whole voice text-draft tool + agentic prompt + Think-hard deep mode in **field.py** and it had ZERO effect — the model kept drafting inline and mentioning Workiz. The tell was the session log showing tools `search_customers`/`get_customer_profile` (which live in dashboard.py, NOT field.py) — proof the running toolset was dashboard's. Fixed by porting everything to dashboard.py (commit d4282e4): `tool_open_text_draft` + READ_TOOL_MAP + TOOLS schema + the `open_text_draft` early-return in `_agent_loop`, the "BE AGENTIC" + "TEXT A CUSTOMER (always use open_text_draft)" + "WORKIZ RETIRED" prompt blocks, and deep mode (`run_agent(deep=)`, `_agent_loop(thinking_budget=)`, `CLAUDE_DEEP_MODEL`/`DEEP_THINKING_BUDGET`, ask-route `deep` flag + spoken triggers). Verified live: "Draft a text to Michael Krauss…" → open_text_draft fired, grounded card ("Friday, August 21 at 8:30 AM at 12 University Cir").

**RULE: for ANY field-voice-assistant change (tools, prompt, model routing, loop), edit `dashboard.py` — that's the live one. field.py's /ask twin is dead; don't waste time there.** Two other differences to remember: dashboard.py is the pre-Workiz-retirement version (its SYSTEM_PROMPT still has "WORKIZ FACTS" + active Workiz tools; I added an overriding "WORKIZ RETIRED — don't mention it" block at the top rather than ripping them out — a full Workiz cleanup of dashboard.py is still pending and is separate/risky). dashboard.py is also the project's highest regression-risk file (13.8k lines) — surgical additive edits + line-count guard only.

Related: [[project_voice_text_draft_tool]], [[project_voice_deep_think_mode]], [[project_field_voice_history_sanitize]] (the anthropic==0.122.0 pin that fixed the separate toolset_name 400).
