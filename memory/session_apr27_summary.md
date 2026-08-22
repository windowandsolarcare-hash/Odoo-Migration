---
name: Apr 27 session — Activities page, Follow-Up flow, SO cleanup methodology
description: Long session covering: built /owner/activities (4th hub card), built parallel-to-reactivation Follow-Up flow, fixed odoo_write to auto-cancel SOs before unlink, extended Phase 3 filter, deleted ~85 stale SOs, surfaced 2 paid-not-invoiced jobs.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
# Apr 27 Session — Big strokes

## Built: Follow-Up flow (parallel to reactivation, but pure Render)

Architectural pivot: Reactivation uses Odoo SAs 562/563. Follow-up does NOT — entire flow lives in `dashboard.py`. DJ explicitly endorsed moving away from SA pattern when Render is the trigger surface. Eventually reactivation should be ported the same way (future work, not in this session).

Files added/changed:
- `dashboard.py` `/api/followup/{preview,launch,markdone}` endpoints
- `dashboard.py` `_build_followup_sms()` template function — edit this for copy changes
- `field.html` (then moved to) `activities.html` — modal with editable SMS, Open/Done sub-tabs
- New Odoo field `x_studio_last_followup_sent` (date) on res.partner — id 20151
- New Odoo field `x_followup_workiz_uuid` (char) on mail.activity — id 20154

Cooldown 45 days. SubStatus `Follow Up Trigger` (DJ creates the Workiz automation on this).

After successful send: posts "📨 Text sent · Workiz job UUID · link" to contact chatter, archives activity manually (skipping `action_done` which would auto-write "Call done").

See `project_followup_flow.md` for full architecture.

## Built: /owner/activities page (4th hub card)

DJ asked for an "Activities" / admin section separate from Field Assistant. Pulled the To-Dos tab out of `field.html` right panel, dropped it into a standalone `activities.html` page. Hub `index.html` now has 4 cards: Time Clock, Field Assistant, Reactivation, **Activities (emerald)**.

Activities is a placeholder for "a whole bunch of other things" DJ wants to add later — not just to-dos.

## Fixed: workiz_post lost UUID + Status auto-injection

When I deployed dashboard.py for follow-up, my local file was OLDER than the deployed version. The deploy regressed two earlier `workiz_post` quirk fixes (commits 7cbd848 + 405a31d). DJ hit a 400 on Bev Hartin Send. Patched and redeployed. See `feedback_local_vs_deployed_drift.md` — diff before pushing.

## Fixed: odoo_write tool now auto-cancels sale.order before unlink

DJ asked Render Claude to delete 3 SOs — got Odoo's `_unlink_except_draft_or_cancel` UserError. Patched the generic `odoo_write` tool in dashboard.py: when `model=sale.order` + `method=unlink`, it loops action_cancel each ID first then unlinks. Render Claude no longer needs to remember the two-step. See `project_so_unlink_needs_cancel.md`.

## Fixed: Phase 3 trigger filter extended to Follow Up Lead

Phase 3's existing graveyard skip filter only matched `JobType="Reactivation Lead"`. Extended to a tuple `("Reactivation Lead", "Follow Up Lead")` so the new follow-up flow's Workiz jobs don't bring SOs into Odoo. Phase 4 didn't need changes — it delegates to Phase 3 for missing SOs.

Commit `ed24c02e` to `Odoo-Migration` repo. Local Phase 3 file: `1_Production_Code/zapier_phase3_FLATTENED_FINAL.py`.

## SO Cleanup — 85+ deleted across two passes

**Pass 1 — historical reactivation graveyards (65 SOs)**
- Filter: `workiz_status='API SMS Test Trigger' AND JobType='Reactivation Lead'`
- Cancel-then-unlink pattern (20 cancelled from state=sale, 43 direct unlink from draft)
- Spotted 2 anomalies (Les Berkey 003376, Linda Willingham 003885) that had wrong workiz_status — DJ took care of those manually
- Bulk deleted 63

**Pass 2 — past-2026 stuck Submitted (initial scan: 66 SOs)**
- 6 Workiz=Done, Odoo=Submitted (sync gap) → wrote workiz_status=Done in Odoo, deleted 4 dups
- 3 orphans (Workiz job deleted) → bulk delete
- 18 cleanup (8 Personal Time + 10 Clark Argeris dups from a Calendly storm)

**Major discovery on the remaining 39:** payment-aware Workiz scan revealed 2 paid-not-invoiced jobs:
- 003504 Laura Gregory $275 (1/20) — Workiz JobAmountDue=$0 but never invoiced in Odoo
- 003892 Norma Gould $85 (2/3) — same

These need DJ to run the Credit-method invoice flow in Odoo. Total revenue exposure: $360.

The other 12 unpaid stuck Submitted jobs total $1,380 — DJ has to decide per-row: completed-but-not-marked-done (mark Done), or no-show/cancellation (cancel).

9 4/5-batch SOs are Workiz-deleted but had real $-amounts ($75-$220 each, total $1,075). Worth investigating whether DJ ran them through some other channel.

## Methodology I want to remember

When debugging a "stuck Submitted" SO list, the right triage is:
1. Pull all SOs matching the filter
2. For each, fetch Workiz `job/get/{UUID}/` (use Odoo proxy for IP allowlist)
3. Categorize by `JobAmountDue`:
   - `=0` and `JobTotalPrice>0` → **PAID, do not delete** — needs invoicing in Odoo
   - `>0` → genuinely unpaid, balance still due
   - `=0` and `JobTotalPrice=0` → no-money job, probably safe to delete
   - HTTP 204/404 from job/get → orphan SO, Workiz job deleted
4. Don't bulk-delete by Odoo state alone — always cross-reference Workiz first.

This came out of DJ's question "look at Workiz before deleting — credit cards generate $0 due but the job IS paid." Memory: `project_credit_card_payment_flow.md` has the rule.

## What still needs DJ to act on

- 12 unpaid past-Jan SOs ($1,380) — mark Done if completed, cancel if no-show
- 16 $0 stuck SOs — most are likely safe to delete (Jane Doe, Fred Test, Dan Saunders test, etc.)
- 9 Workiz-deleted SOs with $-amounts ($1,075) — verify whether work was done via other channel
- 2 paid-not-invoiced SOs — high priority, $360 revenue exposure

## DJ feedback captured

- "I want full automation, not copy-paste" — for follow-up. Triggered the architectural pivot.
- "Always deploy without asking" — already in `feedback_confirmation_policy.md`.
- "Pick up the UUID from the SO and look at Workiz... if zero balance that means paid by CC" — payment-aware triage rule.

## Files touched today

- `Saunders Render App/routers/owner/dashboard.py` — many edits (followup endpoints, todos, odoo_write fix, workiz_post restore, /activities route)
- `Saunders Render App/static/owner/field.html` — to-do tab removed, tab order swap, font/layout changes
- `Saunders Render App/static/owner/index.html` — 4th hub card
- `Saunders Render App/static/owner/activities.html` — new file
- `Migration to Odoo/1_Production_Code/zapier_phase3_FLATTENED_FINAL.py` — filter extension
- Several Odoo data: 65+ SO deletes, 4 SO writes, 2 new Odoo custom fields
