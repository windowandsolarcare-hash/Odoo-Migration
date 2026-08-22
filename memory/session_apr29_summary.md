---
name: Apr 29 session — Window Quote Tool, dashboard fixes, activity-flow unification
description: 2026-04-29 — Big build session. New /owner/quote tool replaces AppSheets pricing app. Activities pivot: detail modal first, follow-up as a button inside. 5-second undo grace on Mark Done. Field-assistant three-dots menu fixed for non-today rows. Stats drill-down + payment-history modal. Google Places API key wired. Multiple architectural pivots.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---

# Apr 29 — Big strokes

## Window Quote Tool — new major feature

**See `project_quote_tool.md` for the full reference.**

- Replaces the AppSheets "Our Pricing" app DJ disliked
- New routes: `/owner/quote` and `/tech/quote` (same HTML, role detected by URL)
- Counter-based UI for 6 line types (Regular Panes $7 → Triple Sliders $35)
- Mode toggle: In&Out vs Outside Only (÷2 × 1.10)
- Difficulty: Standard / Hard +15% / Very Hard +30%
- Address autocomplete via **Google Places API (New)** — see `reference_google_cloud_apis.md` for key + project info
- Saves as Odoo `sale.order` with 3 watermarks: `client_order_ref="🔶 QUOTE ONLY"`, `job_type="Quote"`, "QUOTE ONLY" tag
- Two save paths: pick from schedule → update existing Workiz-linked SO; walk-up → auto-create partner + new SO
- Edit flow: tap saved quote → loads back into form via JSON blob in line description (with legacy text-parser fallback)

DJ pivoted the architecture **mid-session** from "Render creates new draft SOs" to "Render updates existing Workiz-linked SOs (or creates fresh for walk-ups)" — leverages existing Phase 3/4 infrastructure. The duplicate-from-prior-SO `copy()` logic I built earlier in the session was ripped out.

## Activities module — major UX pivot

Built earlier in `project_activities_module.md` and `project_activities_unified_flow.md`. Key changes today:

- **Unified routing**: ALL activities open the detail modal first (shows every populated field)
- Specialized actions (follow-up SMS) become **buttons inside** the detail modal, not separate routing branches. Predicate `isFollowupTodo(t)` decides if the button appears.
- Detail-modal Mark Done button now has a **5-second undo grace period** — button morphs to "↶ Undo (5)" countdown, tap-again or close-modal cancels. Same pattern applied to follow-up modal's "Mark Done (no send)" button.
- Detail-modal field display now includes Summary, Type, Due, Linked-to, Model, Record ID, Activity ID, full note. `fieldRow()` helper auto-skips blanks.
- "Open Follow-Up Editor →" button (renamed from "Send Follow-Up SMS →" because the latter sounded like it sent immediately).

## Activity notes — link rules

Saved as `feedback_activity_notes_self_contained.md`:
- Memory files (Claude-local) → embed content directly, name file for Claude lookup
- Anything with a public URL → real `<a href>` anchor with descriptive text, never paste raw URLs

Linkified the 30 existing follow-up activities so the Workiz UUID is now a clickable link (`https://app.workiz.com/root/job/{UUID}/`). Backend `_strip_activity_html` now emits markdown `[text](url)` for anchors with distinct inner text; frontend `linkify()` handles markdown + plain URLs cleanly.

## Field Assistant — three-dots menu fix

Pre-fix: "today" rows had 4 menu items (Workiz, Odoo SO, Property, Add Note); other days only had 2. Cause: `/api/upcoming` didn't return `partner_id` or `workiz_uuid`. Added them. Now all days show all 4.

## Field Assistant — clicking other-day rows

DJ asked. Decision: leave it (other-day clicks do nothing) until we add something to the active panel that's actually useful for non-today jobs. Active panel has timer + payment buttons that don't apply to future jobs.

## Stats tab — daily drill-down

Stats page sales rows are now tappable. Tap a day → modal shows that day's jobs (time, customer, status, $) with totals. Backend endpoint `/api/sales/day?date=YYYY-MM-DD`.

## Payment History button on open job screen

New "📜 Payment History" button below the Record Payment button. Tap → modal lists all `account.payment` records for the customer (date, method, memo, $). Walks Property→Contact for partner resolution. Backend endpoint `/api/customer/payment_history?partner_id=N`.

## Last-payment-method preselect — diagnosis

Verified the code is working correctly end-to-end (Gary Marsalone partner 24153 → contact 23031 → today's $85 Zelle payment → returns 'zelle'). The reason it "doesn't seem to work" is that most customers have **no `account.payment` records in Odoo yet** — only a handful from invoices DJ has processed in Odoo. The accounting migration (Phases 4-5) will populate this. DJ chose Path A (wait for migration, no Workiz API fallback). Saved as `project_preselect_coverage_check.md` with a 2-week reminder activity (#66) for coverage check.

## Google Cloud API key

Saved as `reference_google_cloud_apis.md`:
- Project: "Odoo" (id `gen-lang-client-0790905441`), billing already enabled
- API key "API key Render": `AIzaSyA2D5Sd7IPOi2h65G4pew7QuXAko3bOO60`, restricted to `wsc-field-assistant.onrender.com/*`, allowed APIs: Places API (New) + Maps JavaScript API
- Weather API also enabled (DJ has a future idea — not yet wired)
- Key is embedded in `quote.html` as a constant — safe because of referrer restriction

## Apps launcher discussion

Discussed but **not built**. DJ shared his Android folder showing 17 native apps. We agreed: a single ⚡ Apps button on dashboard opens a tile grid of web-linkable apps (Workiz, Odoo, Calendar, Gusto, Thumbtack Pro, Angi Pro, Yelp Biz, Nextdoor, Home Advisor, Calendly). Native-only apps (Multi Counter etc.) can't be deep-linked. Deferred — DJ went deeper on the quote tool instead.

## Activities created (Odoo mail.activity)

- **#66** — "Verify field-assistant payment preselect coverage" (initially due 42 weeks out, then DJ corrected to 2 weeks → 2026-05-13)
- **#67** — "Build Phase 4 auto-clear: drop QUOTE ONLY watermarks when Workiz status leaves Quote" (due today)
- **#68** — "Set up Workiz 'Quote' substatus + automation webhook for instant Render sync" (due today, DJ-blocked)
- **#69** — "Build 'Push to Workiz' button" (due today, DJ-blocked on target field decision)

All notes self-contained per the activity-note rule. GitHub URLs are real `<a href>` links.

## Files touched

- `Saunders Render App/routers/owner/dashboard.py` — many edits (quote endpoints, /api/upcoming address+phone, /api/sales/day, /api/customer/payment_history, _strip_activity_html markdown anchors)
- `Saunders Render App/static/owner/quote.html` — entire new file
- `Saunders Render App/static/owner/field.html` — list-modal CSS, Payment History button + handlers, three-dots menu fix (already deployed earlier)
- `Saunders Render App/static/owner/activities.html` — unified detail modal, follow-up button bridge, 5s undo grace, linkify markdown support
- `Saunders Render App/static/owner/index.html` — added Window Quote tile
- `Saunders Render App/static/tech/index.html` — added Window Quote tile
- `Saunders Render App/routers/tech/jobs.py` — added /tech/quote route

## Patterns + gotchas captured

- `feedback_activity_notes_self_contained.md` — embed runbooks; real `<a href>` for URLs
- `project_activities_unified_flow.md` — detail-first routing pattern
- `reference_google_cloud_apis.md` — Google Cloud project + API key registry
- `project_quote_tool.md` — full quote-tool reference (read first when editing /quote)
- `project_preselect_coverage_check.md` — pending coverage check post-accounting-migration
- `feedback_github_deploy_python_fallback.md` — when bash+powershell base64 chokes, use Python (this session)

## DJ-blocked items waiting for action

1. Create Workiz "Quote" substatus + automation (activity #68)
2. Confirm target Workiz field for "Push to Workiz" button (activity #69)
3. Decide whether Phase 4 auto-clear (activity #67) builds now or later

---

## Later in the session — additional polish

### Activities organization v2 — sections + type filter + search + snooze

DJ's complaint: activities list felt like an "out-of-control inbox". Built:
- **Search bar** at top with X clear button (case-insensitive on summary/customer/type/note)
- **Type filter pills**: All / Follow-Ups / To-Dos
- **Date-based sections** with colored dots + count badges:
  - 🔴 Overdue / 🟠 Today / 🔵 This Week / ⚪ Later
  - All sections start expanded; user toggles persist for the session (DJ pushed back on Later being collapsed-by-default — preferred all open)
- **Snooze chips** in detail modal — 4 options: +1 day / +3 days / +1 week / +1 month
- New backend endpoint `/api/todos/snooze` clamps past dates to today + N (so a 30-day-overdue activity snoozed 1 week becomes 1 week from today)

Filter bar hidden when on Done sub-tab.

### Quote tool list filter — bug fix

Originally filtered by `job_type='Quote'` — caught 18 historical Workiz Quote jobs going back to 2022 that DJ never created in the Render tool. Narrowed to `client_order_ref='🔶 QUOTE ONLY'` (only set by Render tool, cleared on conversion). See updated `project_quote_tool.md` for the canonical filter.

### Quote tool post-save success card

Replaced auto-reset behavior with a deliberate success card showing:
- Big total amount
- ✅ Saved/Updated — SO name
- "📊 View in Odoo" link (`https://window-solar-care.odoo.com/odoo/sales/{so_id}`)
- "📋 View in Workiz" link (only if `x_studio_x_workiz_link` populated — i.e., Workiz-linked SOs)
- "+ New Quote" button to clear and start over

`/api/quote/save` and `/api/quote/update` both now return `workiz_link` in the response.

### Field Assistant — 10-Day tab removed

Right office panel: dropped the 10-Day tab (redundant with the future days visible on the left field panel). Now: Stats / Customers / Voice only. `/api/upcoming` endpoint kept — still used by the Quote tool's "Pick from scheduled jobs".

### Bugs caught + memories

- Flegel SO S00107 walk-up save was missing watermarks — possibly a deploy-timing race. Patched manually. If the issue recurs on future saves, dig into `_apply_quote_watermark` or look for an Odoo automation that's stripping `client_order_ref` on draft SOs.
- The list-filter bug (job_type='Quote' too broad) is a good general lesson: when picking a uniqueness signal for a "did our tool create this?" filter, prefer the watermark we explicitly set rather than a field that could be set by other systems too.

### Activity #66 deadline correction

DJ asked for it 42 weeks out, then immediately corrected to 2 weeks. Updated to 2026-05-13. Future-self lesson: when DJ gives a relative date and follows up with a correction, treat the correction as authoritative without asking for re-confirmation.
