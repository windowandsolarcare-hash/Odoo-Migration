---
name: project_client_autoretry_fetch_wrapper
description: "Auto-retry v1 (LIVE 2026-11-13): a global window.fetch monkeypatch on 3 client surfaces silently retries idempotent GET/HEAD on Render platform-recycle 5xx (502/503/504) or conn-refused. Explains why a GET may fire 2-3x; mutations are NEVER retried."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-11-13T08:12:33.629Z
---

**What shipped (LIVE 2026-11-13, commits v2_apps c2438266 / field.html 56b81052 / wsc_page e81d856f):** a ~47-line IIFE that wraps `window.fetch` is installed as the FIRST executable statement on three surfaces:
- `static/owner/v2_apps.js` (top-of-file) — on 52 owner pages
- `static/owner/field.html` (first inline `<script>` @ line 1588) — owner + techs at `/tech/field`
- `static/pub/wsc_page.js` (top-of-file) — booking + portal (customer surface)

The three copies are **byte-identical twins** (shim sha 7e77cc6c; each carries a `// twin of … KEEP ALL THREE BYTE-IDENTICAL` comment). There is NO shared fetch helper — `jfetch` is defined inline in ~49 owner pages — so wrapping the ONE underlying `window.fetch` catches every `jfetch` with zero per-page edits (avoided the ~70-include Rule-9 trap).

**Behavior:** retries ONLY idempotent `GET`/`HEAD` on status ∈ {502,503,504} OR a thrown network error (connection-refused), up to 3 attempts total, backoff 400/1200ms + jitter. **Mutations (POST/PUT/PATCH/DELETE) return BEFORE the retry loop = never retried** (a retried write = double-submit/double-money — excluded by construction). **AbortError is never retried** on any path (thrown-by-name, signal-flag, loop-top during-backoff) so the app's 10s/30s AbortController timeouts (CLAUDE rule 13) are respected. **Fails open**: on final failure it returns the 5xx Response or throws exactly as before — no behavior change on success/final-failure. Guard `window.__wscFetchRetry` prevents double-install.

**Why:** Render platform recycles BOTH instances (~2min, instance_count 2→0→1) intermittently → a burst of 502/503/504 + conn-refused for requests landing in the gap (mechanism #1 in [[project_render_oom_memory_leak_502s]]). v1 makes the COMMON short-burst/tail case invisible (page load / status fetch just succeeds a beat later). It does NOT mask a sustained ~14s both-down window — those still fail open to the existing error UI (same manual refresh as before; no regression).

**How to apply:**
- If you see a GET fire 2-3× in logs/network, this wrapper is why — it's intended, not a bug.
- Editing any of the 3 host files: the shim must stay the FIRST executable statement AND byte-identical across all three. Change one → change all three.
- The correct-by-construction fix (hold-nothing / reserve-at-send equivalent for fetch = server middleware injecting the shim truly-first) is the v1.1 consolidation, deferred; promote only if telemetry shows meaningful early-parse-time-fetch misses (a fetch firing before the bootstrap executes is the only coverage gap, and it just fails-open as today).
- Gate posture: inert client-only → shipped on Lead byte-QC (DJ greenlit the feature 2026-11-13); NOT dual-GREEN. See [[feedback_money_adjacent_staging_risk_calibrated]].

Related: [[project_render_oom_memory_leak_502s]], [[feedback_picker_plain_english_synopsis]] (auto-deploy-on-QC model).
