---
name: project_memory_store_load_failopen_looks_like_dataloss
description: "memory_store DAL _load() fails open to [] on any Odoo read error → a transient 429 renders as \"No decisions recorded yet\" (looks like data loss but isn't). Always read the raw ir.config_parameter blob first."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-20T03:07:01.490Z
---

**A37 (2026-09-19):** DJ's Memory page (`v2_memory.html`, decisions view) showed **"No decisions recorded yet"** — looked like his decisions were wiped. They were NOT. `wsc.memory.decisions` held **61 intact records** (valid JSON, all `company_id=1`, newest 2026-09-18).

**Root cause:** `memory_store.py::_load()` wraps the Odoo read in `try/except Exception: return []`. So ANY transient Odoo failure — a **429 rate-limit** (from stacked deploys + newly-live fleet hooks hammering `/jsonrpc` on the ~0.5-CPU worker) or a timeout — makes `_load` return `[]`. `get_decision` then returns 0 decisions, and the page renders the empty list **identically to a genuinely empty store**. Self-recovers on the next successful read (a reload fixes it).

**Ruled out:** clobber (blob was valid JSON with 61 rows); `company_id` type mismatch (records are int `1`, `_COMPANY` is int `1` — match; a sim of the deployed `get_decision` logic against the live blob returned 59 deduped-by-topic). Fleet hooks write DIFFERENT keys (`wsc.memory.fleet_decisions` / `solved_errors`, `company_id='fleet'`) — they never touch DJ's `decisions` blob.

**Why:** a fail-open-to-empty read is indistinguishable from "you have nothing," so a transient error looks like catastrophic data loss to the user. Alarming + wastes a recovery scramble.

**How to apply:**
1. **Diagnosing any "my memory/decisions/notes vanished" report → read the RAW `ir.config_parameter` blob first** (`get_param` for `wsc.memory.<store>`, key = `_PREFIX` `'wsc.memory.'` + store) via a read-only RPC. Blob has rows → it's a READ/DISPLAY failure, NOT a clobber. Empty/missing → real clobber (Odoo Online daily backups hold the last good blob).
2. **The durable fix (error ≠ empty):** `_load` must signal read-FAILURE distinctly (raise/sentinel), not swallow to `[]`; endpoints return `{ok:false,error:'read_failed'}`; the page shows "Couldn't load — tap to retry" (+ auto-retry once) instead of the "nothing yet" copy. Add bounded retry/backoff on `get_param` for 429s. Carry into the Postgres read path post-flip.
3. **⚠ Migration guard:** the same fail-open means a store-copy/migration step could read `[]` during a 429 and migrate an EMPTY store. Any migration read MUST retry + verify `count>0` before trusting it.

Ownership note: `memory_store.py` + `v2_memory.html` were Builder-2's held files during the Memory Pillar → Render Postgres migration (Lead-serialized) — Postgres reads remove the 429-prone Odoo read, so the migration is itself much of the durable fix. Related: [[feedback_hud_cards_live_not_inbox]], the CLAUDE.md "Odoo rate-limits (HTTP 429)" gotcha, and the Odoo "HTTP 200 ≠ success" rule.
