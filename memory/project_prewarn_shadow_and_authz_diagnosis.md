---
name: project_prewarn_shadow_and_authz_diagnosis
description: "A39 warn-before-action inject half (live, shadow) + the reusable 401-vs-403 diagnosis for fleet-hook endpoints"
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-27T16:19:21.244Z
---

**A39 WARN-BEFORE-ACTION (the "inject half") — current LIVE state (2026-09-27):**
- **Endpoint** `POST /owner/api/memory/hook/prewarn` (memory_store.py:~1515). Given an INTENDED Bash command (no error yet → command↔lesson TEXT match, NOT hook_recall's error-signature scheme), IDF-weights the command's distinctive tokens (`_prewarn_tokens`, minlen 5) over the fleet lesson corpus (solved_errors known-fixes + fleet_decisions), returns the single top lesson above `_PREWARN_MIN_SCORE=0.5` (tight; precision>recall) as `{match:{kind,id,score,warning}|null}`. `_hook_auth_ok` FAIL-CLOSED. Fail-open (any error → match:null, never 500). ALWAYS logs the would-warn to Render logs (both modes).
- **Hook** `.claude/hooks/mem_prewarn_hook.py` (mirror 3_Documentation/roles/hooks/): PreToolUse, Bash-scoped, `MEMORY_PREWARN_MODE` default **shadow**, 1.8s hard timeout, fail-open every path, advisory-only (injects `additionalContext` ONLY in live; never blocks/exits-2).
- **Shadow-review store `prewarn_shadow`** (Builder-2 2026-09-27, commit 19f7f90c): PG-native store (added to `_PG_STORES`, no migration). `hook_prewarn` writes ONE row per MATCH only (past the tight gate → rare) `{ts,tool,command[:500],kind,matched_id,confidence,lesson,mode}`, best-effort/FAIL-OPEN (write sits in try/except, match-return is OUTSIDE it → a hung/failed write never affects the response; hook 1.8s = ceiling), bounded to `_PREWARN_SHADOW_CAP=2000` (prune-oldest by ts). This is Lead's COUNTABLE precision-review dataset (real-mistake-vs-noise RATE — not Render-log grepping).
- **Rollout = shadow-first.** Shadow collects would-warns, injects NOTHING. Live-warning flip = a DJ-nod + precision review, done by env `MEMORY_PREWARN_MODE=live` (NOT a 2nd settings edit).

**Activation model (who does what — NOT DJ, NOT self-wire):**
1. Endpoint + hook + shadow store: Builder-2 build → Lead byte-QC → Dispatcher deploy-clear. ✅ LIVE.
2. Authz `PUBLIC_EXACT` add for `/hook/prewarn`: **Specialists** (authz.py, commit b7f92b7f). Required or the route 401s before the endpoint.
3. settings.json PreToolUse Bash matcher (shadow): **Lead** wires it via the update-config skill — DJ's clarified scope = the FLEET wires settings.json, DJ touches NO config. A builder still NEVER self-edits settings.json (self-modification boundary; a peer's "go" doesn't clear the classifier). See [[feedback_never_relay_credential_via_session]] neighbor-rule on config edits.

**★ REUSABLE INFRA LESSON — 401 vs 403 pinpoints WHERE a fleet-hook request dies:**
On this stack a headless fleet-hook endpoint sits behind TWO gates: (1) the authz middleware's PUBLIC_EXACT allowlist, then (2) the endpoint's own `_hook_auth_ok` (NOTIFY_SECRET). **A `401` = rejected by the authz layer BEFORE the endpoint (route not in PUBLIC_EXACT). A `403` = reached the endpoint, but `_hook_auth_ok` denied (missing/wrong secret).** So to diagnose "my new hook endpoint isn't reachable": POST it with NO secret and compare to a known-good sibling (`/hook/recall`, `/hook/observe`): sibling→403 but yours→401 ⇒ your route needs the PUBLIC_EXACT add (Specialists), NOT an endpoint fix. This is how the A39 blocker was pinpointed (2026-09-27) — code was fully built + deployed; the only gap was the authz allowlist. Ties to [[feedback_verify_collection_and_live_pipe]] (green deploy ≠ working; prove the live pipe) + [[feedback_odoo_verify_content_not_status]].
