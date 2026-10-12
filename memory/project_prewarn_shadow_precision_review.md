---
name: project_prewarn_shadow_precision_review
description: "First REAL prewarn (warn-before-action) precision review, 2026-10-12: at current tuning the matcher NAGS (~287 would-warns/day, 63% on routine commands) — recommendation KEEP OFF, tighten before any live flip. The tightening levers."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-12T16:45:48.074Z
---

The first precision review on REAL prewarn_shadow data (the matcher was silently dead until the 2026-10-05 format-string fix `1f0e1a63` — see [[project_prewarn_format_string_dead]]; data since 10/6). Lead queried `prewarn_shadow` in the **wsc-memory-pillar** PG (`dpg-danl5vqjnfac7390g8g0-a`, table `mem_records`, store='prewarn_shadow', company_id='fleet') firsthand on 2026-10-12.

**Verdict: at current tuning the matcher is a NAG, not a guardrail. Recommended KEEP OFF (shadow), do NOT flip `MEMORY_PREWARN_MODE=live`.** Routed a tightening spec to Specialists; posted a 3-option picker → DJ (keep-off+tighten [rec] / on-as-is / shelve). The shadow test SUCCEEDED precisely by proving this.

**The numbers (1,726 would-warn rows, 10/6→10/12, ~6 days):**
- ~287 would-warns/DAY across the fleet. (Shadow cap `_PREWARN_SHADOW_CAP=2000`, prune-oldest — was at 1,726, not yet pruned, full week intact.)
- **63%** fired on GENERIC/routine commands (bare `cd`, `sleep`, `ls`, `cat`, `gh api`, plain `python3 << PY` heredocs) — not risky ops.
- **58%** sat just above the 0.5 gate (confidence `<1.0`). Confidence is an IDF-weighted SUM, not 0–1 prob; observed range 0.5–7.94.
- **171 distinct lessons**, ALL `kind=solved_error`, every one tagged **"seen 1x"** — one-off past errors broadcast on token overlap, never recurring patterns. (Zero `fleet_decisions` matches.)
- Smoking gun: lesson `m27f2e6c41ec5` (a one-time "contact_id malformed error") fired 8+ times — incl. at the HIGHEST confidence in the whole set (7.94) — on a Design session's EDDM-postcard build script and bare `cd` into a temp dir. The IDF keys on common infra tokens (`python3`, `urllib.request`, `json`, file-path fragments), not genuine repeat-mistake signal.

This is the exact failure the feature was designed to avoid (see [[project_pillar_warn_before_action]]): "WARN, never NAG — a false-positive that fires on every routine call trains the actor to ignore it."

**Tightening levers (Specialists' domain = memory_store.py; biggest win first):**
1. **Require a lesson seen ≥2x** before it is warn-eligible — a one-off "seen 1x" error is not a pattern. (Biggest precision lever.)
2. **Raise `_PREWARN_MIN_SCORE`** well above 0.5 — 58% of fires are `<1.0`; real signal (if any) is the high-conf tail.
3. **Expand the token stopword set** (`_ASK_STOPWORDS` / `_prewarn_tokens`) to kill generic infra tokens (`python3`, `urllib`, `json`, path fragments, `cd`, `sleep`) so a match needs DISTINCTIVE domain tokens.
4. Optional: hook pre-filter skips bare `cd`/`sleep`/`ls` shapes.
Target: cut ~287/day to a handful of genuinely-relevant/day, THEN re-run this shadow precision check before any live flip.

**How to apply / reusable:** this is the template for every "flip a shadow feature live?" gate — pull the shadow table firsthand, measure VOLUME + a noise proxy (generic-command %, near-gate %, one-off-lesson %), judge representative (command→matched-lesson) pairs incl. the highest-confidence ones, and recommend from the data. Ties to [[feedback_sporadic_bugs_repeat_test]] (never conclude from one look), [[feedback_root_cause_not_just_instance]], [[feedback_durable_foundation_over_shortcut]].
