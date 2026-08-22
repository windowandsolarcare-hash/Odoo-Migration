---
name: project_attention_feed_contract
description: "Two-Claude build of the AI operating system: the seam is the Attention Feed Contract (3_Documentation/ATTENTION_FEED_CONTRACT.md v1). Specialists SUBMIT items via feed.py submit_item/delete_item (stable API, lead owns feed.py); they never push notifications or render UI. MY lane = specialists + PM engine."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T15:06:50.365Z
---

**2026-07-26.** The operating-system build ([[project_operating_system_vision]]) is split across TWO Claude Code sessions. A DIFFERENT (lead) session owns the HUD/spine/surfaces; THIS session's lane = the AI specialists + the PM engine. The seam between us is a written contract.

**The contract:** `3_Documentation/ATTENTION_FEED_CONTRACT.md` (v1, agreed; breaking changes need both sessions + DJ). The working-agreement/lane split is spec section 5c (lead's master spec, claude.ai artifact d6667c7a-88dd-4fbf-9dc9-88b6b18a27d2).

**How it works:** a specialist PRODUCES an item and is done — it never pushes a notification and never renders UI. The lead's priority engine + HUD feed + approval inbox rank/deliver/manage lifecycle.
- **Stable API (the seam):** `from .feed import submit_item, delete_item` — `submit_item(item_dict)` (validates + upserts by id), `delete_item(item_id)` (withdraw). **Lead owns `routers/owner/feed.py`** (ships Phase 1). Storage v0 behind it = `ir.config_parameter wsc.feed.items` (JSON dict by id) — never touch storage directly. HTTP mirror `POST /owner/api/feed/submit`. Until feed.py is on main, build/test against a LOCAL STUB with the same two signatures — no alternate delivery path.
- **Item shape:** `id` (`source:stable-suffix`, deterministic per subject = the dedupe/upsert key), `kind` (`approval` = has draft | `attention` = FYI), `source` (duty slug), `title` (≤80, plain, read-aloud), `why_now`, `urgency` (`interrupt|today|glance` — a REQUEST; the engine makes the final push call per DJ's interrupt list; specialists NEVER push), `dollars` (nullable), `action{label,href}` (deep link → lead's surface e.g. v2_inbox.html), `draft{summary,body,editable,on_approve{method,href,payload}}` for approvals, `expires` (nullable), `created`.
- **Hard rules I must honor:** (1) customer-facing output is ALWAYS `kind:approval` (no graduation, DJ's rule; a graduated duty submits `attention` with did-it phrasing). (2) Event-triggered, NEVER watching. (3) One item per subject (leads are the interrupt exception, one per lead). (4) **Withdraw (`delete_item`) the moment it's no longer true** — stale cards kill trust.

**Boundary (no shared files):** `action.href` → lead's surfaces (inbox, digest page); `draft.on_approve.href` → MY endpoints (the specialist's execution side, e.g. `/owner/api/payroll/execute`, must be idempotent + will be auth-gated when lead's Block B ships). I build new specialist modules; lead builds feed.py + inbox surface + engine + briefing delivery. **Approval inbox is a NEW file, NOT added to myday.py** (shared file — voicemail inbox lives there).

**MY lane:** specialist cards (payroll first — first step is confirming **Gusto data is callable**; Gusto ≠ the QuickBooks MCP tools, needs its own API check), weekly digest content, later accounting, voice re-test w/ pick-a-specialty selector, PM evolution (project types, portfolio/board views, dependencies, auto-schedule, templates) in goals.py/v2_goals.html. **Status 2026-07-26: everything on paper — DJ wants no code yet.** First allowed real motion = the Gusto-callable investigation (research, no code). DJ's separate action: chase Workiz to release the number (gates all text duties, see [[feedback_ported_means_twilio]]).
