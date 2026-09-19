---
name: project_memory_pillar_slice2
description: Memory Pillar Part B Slice 2 — the error-triggered .claude hooks + fleet read-view; how/where fleet hooks are wired (fleet-session settings.json precedence)
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-19T22:01:03.938Z
---

Memory Pillar Part B **Slice 2** (built by Builder-2, 2026-09-19, Lead-QC'd). Slice 1 (the DAL + fleet_decisions + solved_errors stores + `normalize_error_signature`/`observe_error`/`resolve_error`/`_distill_error_fix` + the 6 human + 3 headless `/hook/*` endpoints in `routers/owner/memory_store.py`) was already LIVE — Slice 2 is only the remainder. Authoritative spec: `saunders-render-app/3_Documentation/MEMORY_PILLAR_BUILD_SPEC.md` §B5/§B6/§B10.

**What Slice 2 shipped (all QC'd + live except activation):**
- Two NEW harness hook scripts (net-new, Builder-2-owned): `mem_error_hook.py` (PostToolUse: scan tool_response for an error → compute signature → GET `/owner/api/memory/hook/recall` → inject a known fix OR POST `/hook/observe` + drop a breadcrumb) and `mem_error_capture.py` (Stop: read the breadcrumb → POST `/hook/resolve`, which Haiku-distills root_cause+fix server-side and closes the record to `solved` — no human save). Mirrored (reset-proofing) to `saunders-render-app/3_Documentation/roles/hooks/`.
- `memory_store.py`: folded fleet_decisions + solved_errors into `/api/memory/ask` (§B6, cross-store "did we already decide/solve X?") + made `_hook_auth_ok` **fail-CLOSED** (deny if `NOTIFY_SECRET` unset). Commit 5f7a9cf5.
- `v2_memory.html`: 🧠 **Fleet knowledge** chip/view (fleet decisions + solved errors) + `cardFor` cases + `errCard`/`fleetDecCard` so `/ask` fleet results render. Commit ac3d44e9.
- HELD for DJ's nod: wiring `.claude/settings.json` (observe-first, matcher **"Bash"** only to start).

**★ CRITICAL VERIFIED FACT — fleet-session settings.json precedence (corrects a real wrong assumption):** a Claude Code session loads `settings.json` ONLY from its `-d` launch dir (`.../Migration to Odoo/.claude/`) **+ user-level `~/.claude/`** — NOT from the `saunders-render-app` repo. So the repo's `.claude/hooks/known_bad_fields.py` does NOT even run in fleet sessions. **Why:** fleet sessions launch `-d "Migration to Odoo"`, not in the app repo. **How to apply:** any harness hook meant to fire fleet-wide must live at a STABLE ABSOLUTE path (`~/.claude/hooks/…`) and be referenced by ABSOLUTE path in the command (NOT `$CLAUDE_PROJECT_DIR`, which resolves to each session's launch dir); wire it in either `Migration to Odoo/.claude/settings.json` (fleet-only) or `~/.claude/settings.json` (every DJ session). Editing settings.json = a config change affecting every session → needs DJ's explicit nod.

**★ GOTCHAS worth keeping:**
- Hook I/O (verified via claude-code-guide): PostToolUse stdin has `tool_name`/`tool_input`/`tool_response` (Bash: `{type,exit_code,stdout,stderr}`; MCP: `{type:'mcp_tool',result,isError}`); inject context via stdout `{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"…"}}`; **exit 0 = always non-blocking**. Stop stdin has `transcript_path`/`last_assistant_message`/`tool_calls`; Stop can't block, so always-exit-0 = no loop risk.
- **Two different "fail" directions, don't conflate:** the hook SCRIPTS must fail-OPEN (app-down/garbage-stdin/no-secret → exit 0, never break a session); the endpoint AUTH `_hook_auth_ok` is fail-CLOSED (deny if no secret). Both are correct.
- `mem_error_hook.py` carries a VERBATIM copy of `memory_store.normalize_error_signature` (a standalone harness script can't import the app) — `/hook/recall` takes a pre-computed signature, so the mirror MUST stay in lockstep with the server (12 logic lines + 7 regexes; verified byte-identical). Change one → change both.
- Error-marker regex tuning (avoid store pollution): `"error"\s*:` must require a TRUTHY value — success bodies carry `"error": null/""/false`. Fold the whitespace INTO the lookahead (`"error"\s*:(?!\s*(?:null\b|false\b|""|''|[,}\]]))`) or `\s*` backtracks to zero and the check passes. `\bexception\b` → `\b\w*exception\b\s*:` (raised form, not prose); line-start error marker allows dotted qualifiers (`^\s*[\w.]*error\s*:`) so `odoo.exceptions.AccessError:` is caught.
- Rollout is OBSERVE-FIRST (recall-read + observe/capture on; context-injection gated OFF via `MEM_HOOK_INJECT` until proven). Matcher starts **"Bash" only** (the recurring solved errors — Odoo field names, reserved server-action vars, deploy JSON, HTTP faults — surface in Bash/curl/python); expand to `mcp__.*` only if field data justifies.
- Local `NOTIFY_SECRET` for the hooks: `~/_notify_secret.txt` is the canonical local source (fleet standard, per [[feedback_api_keys_via_file]]) — same secret `/owner/api/fleet/register` uses.
- Backend is still the JSON-blob (`ir.config_parameter`) — DJ's deliberate visible shortcut; durable = Render Postgres (~$7/mo, a DAL swap) when a §B7 trigger fires ([[feedback_durable_foundation_over_shortcut]]). solved_errors is the likeliest first to hit the write-concurrency/volume trigger.

Related: [[feedback_check_endpoint_map_first]], [[feedback_reuse_function_follow_full_logic]], [[feedback_odoo_verify_content_not_status]].
