---
name: project_pillar_warn_before_action
description: "Memory Pillar's payoff phase = a PRE-action hook that WARNS before a risky tool call — observe-only recall doesn't PREVENT mistakes (DJ insight 2026-09-19)."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-20T03:37:41.957Z
---

**DJ's insight (2026-09-19), the defined next phase of the Memory Pillar:** observe-only memory does NOT prevent mistakes. Capturing errors + surfacing them on recall-on-demand comes TOO LATE — by the time you ask, the mistake is made. The proof: the "use merge, don't PUT" lesson only helped because DJ happened to REMEMBER it, not because the system surfaced it at the moment of risk.

**The payoff phase (the "inject half"):** a PRE-action hook (PreToolUse) that, before a risky tool call, checks memory for a matching lesson and WARNS the actor first — injecting the known lesson/fix into context BEFORE the action, not after. This is what turns the Pillar from a passive log into an actual guardrail. It's the whole point the Pillar was built toward.

**Current state:** the hooks are LIVE but OBSERVE-ONLY — injection is gated OFF (`MEMORY_HOOK_INJECT` unset). `hook_recall` already exists and can return a KNOWN FIX (gates on status=='solved' + fix present); the missing piece is wiring a PRE-action matcher that fires the warn BEFORE the tool runs, plus turning injection on.

**How to apply — build it carefully:**
- Injection/warn needs a SEPARATE explicit DJ nod (observe-first was deliberate — see the activation history).
- Precision matters more than recall here: it must WARN, never NAG. A false-positive that fires on every routine call trains the actor to ignore it. Match tightly (signature/context), warn only on a real matching lesson.
- Fail-open + never block the tool call (same posture as the observe hook) — a warn is advisory, not a gate.
- Reuse the existing `hook_recall` + signature-match machinery; this is the PreToolUse counterpart to the live PostToolUse observe hook.

See [[project_memory_read_fail_open_phantom_empty]] (the store this reads), [[feedback_durable_foundation_over_shortcut]] (build it to last). Tracked in BUILD_LOG QUEUED as "Memory Pillar — PROACTIVE WARN-BEFORE-ACTION."
