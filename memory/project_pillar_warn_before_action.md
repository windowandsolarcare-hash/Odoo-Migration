---
name: project_pillar_warn_before_action
description: "Memory Pillar's payoff phase = a PRE-action hook that WARNS before a risky tool call — observe-only recall doesn't PREVENT mistakes (DJ insight 2026-09-19)."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-20T06:14:29.163Z
---

## ★ SHADOW-MODE BUILT + LIVE (dormant) 2026-09-20 — commit cf607f73 (Builder-2, Lead-QC pending)
The inject-half is BUILT and deployed, un-wired (dormant). Spec: `saunders-render-app/3_Documentation/WARN_BEFORE_ACTION_BRIEF.md`.
- **★ KEY ARCHITECTURE (corrected the brief's "reuse hook_recall signature-match"):** at PreToolUse there is NO error yet — only the intended command — so an error-SIGNATURE match (hook_recall's scheme, normalized from error TEXT in a PostToolUse response) CANNOT align (command-space ≠ error-space). So the matcher is **command↔lesson TEXT match**, not signature. The store/DAL/read path IS reused; the matcher is new.
- **`/hook/prewarn`** (memory_store.py, NOTIFY_SECRET fail-closed): distinctive command tokens (len≥5, minus `_ASK_STOPWORDS`) IDF-weighted over the LESSON corpus — solved_errors (status=solved + fix) + fleet_decisions, fleet-scoped, on PG — returns the SINGLE top lesson above `_PREWARN_MIN_SCORE=0.5` (tight; the shadow-tunable precision knob) with a ready-to-inject `warning`, else `match:null`. ALWAYS logs the would-warn `[prewarn:<mode>] ...` to Render logs (BOTH modes) for the precision review. Fail-OPEN (any error/read-blip → match:null, never 500). Reuses mem_get + _ASK_STOPWORDS + the /ask IDF idea.
- **`mem_prewarn_hook.py`** (PreToolUse, `.claude/hooks/` + mirrored to `3_Documentation/roles/hooks/`): Bash-only, reads `tool_input.command`, coarse pre-filter (skip <8 chars), env `MEMORY_PREWARN_MODE` (default **shadow**; unset=shadow=safe), **~1.8s timeout** (hard latency guard — sits in front of EVERY Bash call), ADVISORY = `hookSpecificOutput.additionalContext` + **exit 0** ONLY when mode=live+match; NEVER `permissionDecision`/exit-2; fail-open on any error/timeout → exit 0, inject nothing, Bash proceeds.
- **PreToolUse mechanics (confirmed via claude-code-guide):** advisory = additionalContext + exit 0; permissionDecision:"deny" or exit 2 BLOCK (never use); every other error fails open. stdin has tool_name/tool_input/etc.
- **★ SHADOW SEQUENCING (Lead's correction):** a PreToolUse hook only fires if wired in settings.json → you CANNOT collect shadow data before wiring. So: wire settings.json ONCE (shadow, DJ-direct) → collect → **live-flip is just the env change `MEMORY_PREWARN_MODE=live`** (DJ-direct), NOT a second settings edit. Mirrors the observe hook's inject-flag pattern.
- **ACTIVATION = TWO DJ-DIRECT gates (a relay does NOT clear them — hold for DJ's OWN go, same as observe/migrate):** (a) authz PUBLIC_EXACT + R1-inventory add for `/owner/api/memory/hook/prewarn` (Specialists; endpoint is INERT/cookie-gated until then — verified) + (b) settings.json PreToolUse wiring (matcher "Bash", shadow). Then collect → precision review with DJ → DJ env-flip live → Lead QC.
- Gates so far: py_compile OK (endpoint+hook), additive, clobber-guarded push, deploy live 06:13:56, endpoint confirmed inert, app healthy.

**DJ's insight (2026-09-19), the defined next phase of the Memory Pillar:** observe-only memory does NOT prevent mistakes. Capturing errors + surfacing them on recall-on-demand comes TOO LATE — by the time you ask, the mistake is made. The proof: the "use merge, don't PUT" lesson only helped because DJ happened to REMEMBER it, not because the system surfaced it at the moment of risk.

**The payoff phase (the "inject half"):** a PRE-action hook (PreToolUse) that, before a risky tool call, checks memory for a matching lesson and WARNS the actor first — injecting the known lesson/fix into context BEFORE the action, not after. This is what turns the Pillar from a passive log into an actual guardrail. It's the whole point the Pillar was built toward.

**Current state:** the hooks are LIVE but OBSERVE-ONLY — injection is gated OFF (`MEMORY_HOOK_INJECT` unset). `hook_recall` already exists and can return a KNOWN FIX (gates on status=='solved' + fix present); the missing piece is wiring a PRE-action matcher that fires the warn BEFORE the tool runs, plus turning injection on.

**How to apply — build it carefully:**
- Injection/warn needs a SEPARATE explicit DJ nod (observe-first was deliberate — see the activation history).
- Precision matters more than recall here: it must WARN, never NAG. A false-positive that fires on every routine call trains the actor to ignore it. Match tightly (signature/context), warn only on a real matching lesson.
- Fail-open + never block the tool call (same posture as the observe hook) — a warn is advisory, not a gate.
- Reuse the existing `hook_recall` + signature-match machinery; this is the PreToolUse counterpart to the live PostToolUse observe hook.

See [[project_memory_read_fail_open_phantom_empty]] (the store this reads), [[feedback_durable_foundation_over_shortcut]] (build it to last). Tracked in BUILD_LOG QUEUED as "Memory Pillar — PROACTIVE WARN-BEFORE-ACTION."
