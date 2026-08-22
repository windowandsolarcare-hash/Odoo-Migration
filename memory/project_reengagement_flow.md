---
name: Customer Re-engagement flow (formerly "Follow-Up") — terminology rename 2026-04-30
description: 2026-04-30 — Renamed Phase 5's customer cycle reminder from "Follow-up" to "Re-engagement" so DJ's voice "follow up with my uncle" stops colliding with the customer-SMS path. Phase 5 still creates project.task records (Odoo To-do app) named "Re-engagement: {customer} — {service}". The legacy 30 mail.activity records still match the SMS predicate via "follow up"/"reactivation"/"reach out" keywords. Voice "follow up" → create_todo (personal project.task, optional partner_id anchor).
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when editing Phase 5, the create_todo tool, the Activities SMS predicate, or the Render Claude system prompt around todos.**

## Why the rename

DJ uses "follow up" constantly in personal speech ("follow up with my uncle", "remind me to follow up with the dentist"). The same word was used by:
- Phase 5's project.task title: `"Follow-up: Customer — Service"`
- create_todo's project.task title: `"[Render] Follow-up: Customer"`
- Render Claude's tool description ("create a follow-up to-do")

Result: voice trigger ambiguity → Render Claude was asking too many CLARIFY questions, sometimes routing personal todos through customer-anchor logic.

**Rename**: Phase 5's customer-cycle-overdue flow is now **"Re-engagement"**. Personal voice todos use whatever DJ said as the title (no fixed prefix).

## Current architecture (post-rename)

| Trigger | Tool / Code path | Storage | Title pattern | SMS button? |
|---|---|---|---|---|
| Phase 5 fires (job done with frequency) | `zapier_phase5_FLATTENED_FINAL.py::create_followup_activity` | `project.task` (project_id=False) anchored to res.partner | `Re-engagement: {customer} — {service}` | No (predicate excludes source='task') |
| DJ voice: "follow up with X" / "remind me to Y" | Render Claude `create_todo` tool | `project.task` (project_id=False) anchored to partner_id (if customer named) or no partner | DJ's actual phrase, e.g. `"call uncle Bob"` | No |
| Phase 5's "On Demand" path (manual invoice, no Workiz job) | Same `create_followup_activity` (via `create_ondemand_followup`) | `project.task` | `Re-engagement: ...` | No |
| ~30 LEGACY records (pre-rename Phase 5) | `mail.activity` records still in DB | `mail.activity` | `Follow-up: {customer}` | **Yes** (predicate matches) |

## SMS button (`isFollowupTodo` predicate in activities.html)

Matches now: `re-engagement`, `reengagement` (new), PLUS legacy `follow up`, `follow-up`, `followup`, `reactivation`, `reach out`. The legacy keywords stay because the ~30 historical mail.activity records still need the SMS button. **Predicate also requires `source='activity'`** — project.task records never match regardless of title.

## Render Claude system prompt rule (commit 1645e679)

Added explicit terminology rule:
- "follow up with X" / "remind me to Y" / "note to self" / "add a task" → ALWAYS `create_todo`
- Pass `partner_id` only if X is a real customer (silent search_customers check first)
- Default `days=7` if unspecified; map "tomorrow"/"next week"/etc to integers
- DO NOT ask "personal or customer?" — search silently and decide
- "Re-engagement" is reserved for Phase 5's automated flow — NOT voice-triggerable

## Chatter breadcrumbs (already in Phase 5 — preserved through rename)

Phase 5 posts a chatter mail.message on the linked SO when it creates a Re-engagement task:
> `[Phase 5] Re-engagement Task created | Customer: X | Due: Y | Task: <url>`

For "On Demand" path (no SO, just an invoice), it posts on the invoice instead:
> `[Phase 5] Re-engagement Task created | Customer: X | Due: Y | Task: <url>`

## Files touched in the rename

| File | Repo | Change |
|---|---|---|
| `zapier_phase5_FLATTENED_FINAL.py` | windowandsolarcare-hash/Odoo-Migration | Title `Follow-up: ...` → `Re-engagement: ...`; chatter prefix `[Phase 5]` |
| `routers/owner/dashboard.py` | windowandsolarcare-hash/saunders-render-app | `create_todo`: drop `[Render] Follow-up:` prefix, accept personal todos (partner_id optional), better description; system prompt terminology rule |
| `static/owner/activities.html` | windowandsolarcare-hash/saunders-render-app | `isFollowupTodo()` matches `re-engagement` + legacy keywords |

## DJ's manual step (one-time)

Rename Workiz SubStatus from `"Follow Up Trigger"` to `"Re-engagement Trigger"` in Workiz UI. Phase 5 only reads the rendered activity title, not this SubStatus, so the rename is cosmetic for Workiz. Optional but consistent.

## Task #25 — closed as obsolete

Pre-rename, there was a pending task to "Extend SMS Follow-Up flow to project.task records." After the rename:
- The SMS flow stays bound to the legacy ~30 mail.activity records (uses `x_followup_workiz_uuid` field)
- Future Phase 5 records are project.tasks → never qualify for SMS button
- Personal voice todos are project.tasks → never qualify for SMS button

So extending SMS to project.task is no longer needed. The split is now clean:
- `mail.activity` = legacy SMS records only
- `project.task` = customer cycle reminders (Phase 5) + personal voice todos (create_todo) — neither uses SMS

## Related memory

- `project_followup_flow.md` — original Follow-Up flow doc (pre-rename, kept for history)
- `project_todo_models_in_odoo.md` — mail.activity vs project.task distinction
- `reference_render_claude_write_tools.md` — write tool catalog (create_todo entry)
- `feedback_no_re_listing.md` — DJ communication style
