---
name: project_voice_usage_tracking
description: "Voice-assistant Claude API token usage is tracked in Render PG (routers/owner/usage_store.py), read via GET /owner/api/usage/claude. Prompt caching is DOCUMENTED-not-built (turnkey in the module docstring); a one-time HUD card fires when 7-day usage crosses a threshold. SHIPPED LIVE 2026-10-05 (a41af4cc)."
metadata:
  node_type: memory
  type: project
  originSessionId: c2b57d38-a392-4882-ad3e-470c2240e939
  modified: 2026-10-05T07:43:47.155Z
---

**Shipped 2026-10-05 (deploy a41af4cc), DJ "deploy". Origin: Operator BUILD SPEC 2026-10-04 (DJ-directed)** — track voice-assistant Claude usage NOW (free); do NOT enable prompt caching yet (future use — the assistant uses too little; a cold cache write costs 1.25x, so low/one-off traffic pays MORE).

**What exists:**
- **`routers/owner/usage_store.py`** (NEW). `log_step(model, route, loop_i, usage)` is called from `dashboard._agent_loop` after every `client.messages.create` (the voice assistant's loop). Records `resp.usage` (input/output/cache_read/cache_write tokens) + model + route (`ask`/`ask_deep`) + step index into Render Postgres table **`wsc_claude_usage`** = a DAILY rollup keyed (day, model, route): requests/steps/multistep/token counts.
  - ★ **COUNTS ONLY** — never prompt text or customer data. No extra API calls, no behavior change.
  - ★ **Zero added latency:** `log_step()` only enqueues to an in-memory queue; a daemon worker thread batch-upserts to PG. FAIL-OPEN everywhere (queue full / PG down → dropped silently; telemetry never affects the assistant).
  - Needs env **`MEMORY_DB_URL`** (same Render PG as sched_shadow/telemetry). If unset, logging + stats no-op gracefully.
- **`GET /owner/api/usage/claude?days=7`** (owner-only, LIVE in dashboard.py — registered first, no shadow): per-day + per-model tokens, avg steps/request, estimated $ (a single `_RATES` config dict, matched by model family; estimate/signal only, not billing). In ENDPOINT_MAP.
- **One-time HUD card** ("Voice assistant: prompt caching would now pay off") via `feed.submit_item` + CAS meta flag (`wsc_claude_usage_meta`) = fires exactly once, when 7-day est spend ≥ `CLAUDE_USAGE_ALERT_USD` (default $5) OR 7-day multistep requests ≥ `CLAUDE_USAGE_ALERT_MULTISTEP` (default 50). Both env-configurable. Urgency `glance`.

**Prompt-caching = DOCUMENTED, NOT BUILT.** The turnkey design lives in the `usage_store.py` module docstring (bottom): split system into [static +cache_control]/[dynamic], cache_control on the LAST tool, Haiku min-prefix 4096 / Sonnet 1024 (our ~15K clears both), 5-min TTL, write 1.25x / read ~0.1x, Haiku+Sonnet separate caches, verify via `usage.cache_read_input_tokens > 0` (this module already records cache_read so the stats endpoint proves the hit rate after enabling). SDK pin `anthropic==0.122.0` supports cache_control.

**Scope = the VOICE ASSISTANT only** (`_agent_loop`). Other Claude usage (ideas/followups/field) is NOT logged. Model/record-of-truth stays Odoo; this is high-write operational data → Render PG (see [[feedback_data_location_odoo_vs_postgres]]). Pattern mirrors [[project_tech_app_architecture]]'s sibling store modules / sched_shadow.
