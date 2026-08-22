---
name: Activities module — full reference (Render app /owner/activities)
description: Comprehensive guide to the Activities module: 4th hub card, To-Dos + Follow-Up flow, all endpoints, data flow, gotchas, and rules for safe changes. Read this BEFORE editing anything related to /owner/activities, /api/todos, /api/followup/*, or activities.html.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
# Activities Module — Read this before editing

This module is small in code volume but has subtle data-flow rules. Future chats keep getting it wrong because they assume it works like Field Assistant. It doesn't.

## What it is

The 4th hub card on `/owner/`. Standalone page at `/owner/activities`. Currently houses two things:
- **Open** sub-tab — to-do list (mail.activity records assigned to DJ)
- **Done** sub-tab — recently completed activities (last 30 days)

It is **intended to grow** — DJ said "a whole bunch of other things will go here." Don't refactor it as a single-purpose to-do screen. Treat it as a generic admin/activities hub.

The To-Dos used to live in the right panel of Field Assistant (`field.html`). That tab + dispatcher entry was removed when this module was built (2026-04-27). Dead modal HTML/JS may still be in `field.html` — it's intentionally left there as a safety belt; do **NOT** clean it up unless DJ explicitly asks.

## Files (canonical paths)

| File | Role |
|---|---|
| `Saunders Render App/routers/owner/dashboard.py` | All backend endpoints |
| `Saunders Render App/static/owner/activities.html` | The page (Open/Done tabs, follow-up modal) |
| `Saunders Render App/static/owner/index.html` | Hub card (4th tile, emerald `--card-activities #10b981`) |
| `Saunders Render App/static/owner/field.html` | Field Assistant — to-do tab REMOVED here. Don't touch unless asked |

Repo: `windowandsolarcare-hash/saunders-render-app` (NOT the Odoo-Migration repo).

## Endpoints (all in dashboard.py)

| Method + Path | Purpose | Notes |
|---|---|---|
| `GET /activities` | Serves `activities.html` | Just file read, no auth at server level — page itself reads `localStorage.wsc_ac` and bounces to `/owner/` if missing |
| `GET /api/todos` | Open to-dos for the Open tab | Optimized 2026-04-27: batched partner reads + 60d window. `TODOS_USE_LEGACY` flag rolls back |
| `GET /api/todos/done` | Last 30d archived activities for Done tab | Reads `active=False` with `active_test:False` context. Pulls `x_followup_workiz_uuid` to render the Workiz pill |
| `POST /api/followup/preview` | Builds SMS text + cooldown info — read-only | NEVER writes to Odoo or Workiz. Front-end shows the result in the modal so DJ can edit before sending |
| `POST /api/followup/launch` | Actually sends the text via Workiz | Heavy: Odoo reads + Workiz job-create + Workiz substatus update + Odoo writes + chatter post + activity archive |
| `POST /api/followup/markdone` | Close to-do without sending | For when DJ handled the follow-up another way |

## Constants (top of follow-up section, ~line 3236)

```python
FOLLOWUP_COOLDOWN_DAYS = 45
FOLLOWUP_SUBSTATUS     = 'Follow Up Trigger'   # parent Status="Pending"
FOLLOWUP_JOB_TYPE      = 'Follow Up Lead'

# /api/todos optimization flags (~line 2456)
TODOS_USE_LEGACY = False
TODOS_DEADLINE_WINDOW_DAYS = 0   # 0 disables the date filter; was 60 but hid 29 of 31 todos
```

## SMS template — single edit point

`_build_followup_sms(first_name, property_addr, last_visit_str, frequency, city, full_name, street)` at ~line 3241 in dashboard.py. **This is the only place to edit follow-up SMS wording.** It also embeds the Calendly URL with city-based slug (same map reactivation uses: pmsg, rm, pd, iw, indlaq, ht, gb fallback).

## The Follow-Up flow — what actually happens on /api/followup/launch

This is where future chats get confused. The flow is:

1. Re-validate contact (cooldown, blacklist, Do Not Contact) — front-end values are NEVER trusted
2. Find a source Workiz UUID by searching latest sale.order with `x_studio_x_studio_workiz_uuid != False` for this partner OR any of their Property children (via `partner_shipping_id`)
3. `workiz_get(job/get/{source_uuid}/)` — pull the source job
4. Validate phone (≥10 digits) and PostalCode (5 digits) from the source
5. Build a NEW Workiz job payload with:
   - `JobType = 'Follow Up Lead'`
   - **No JobDateTime** (unscheduled — important; this is why job/all/ won't find it later)
   - `information_to_remember = sms_text` (Workiz automation reads this field on substatus change)
6. `workiz_post('job/create/', payload)` — get back new UUID
7. `time.sleep(3)` race-condition workaround (same as reactivation)
8. `workiz_post('job/update/{new_uuid}/', {'SubStatus': 'Follow Up Trigger'})` — this fires the Workiz automation that sends the SMS
9. Post chatter to **the contact** (not the SO): `📨 Text sent · Workiz job link · SubStatus: ...`
10. Write `x_studio_last_followup_sent = today` on res.partner (cooldown anchor)
11. Archive the to-do **manually**: `mail.activity.write({'active': False, 'date_done': today, 'x_followup_workiz_uuid': new_uuid})`

### CRITICAL — DO NOT call `mail.activity.action_done()` on follow-up activities

Odoo auto-generates "Call done" in chatter when you call `action_done()` on an activity whose type is "Call" — and our follow-up activities use the Call type. That message is misleading because we just sent a TEXT, not made a call. The launch endpoint deliberately uses `write({active: False, date_done: ...})` instead. Only the `markdone` endpoint (when DJ presses "Mark Done" without sending) uses `action_done`, with `unlink` as a fallback.

If you "fix" this to call action_done, you reintroduce the "Call done" chatter bug DJ already flagged once. Don't.

## Workiz POST body quirks (handled by `workiz_post` helper)

These are auto-injected — you don't need to remember them, but you should know they exist:
- `UUID` is required in the body for `job/update/{UUID}/` (URL alone is not enough — 400 otherwise)
- `ID` is required in the body for `job/delete/{UUID}/`
- `Status='Pending'` must be sent alongside any `SubStatus` (otherwise 400 "Could not update sub status with no parent status provided")
- `auth_secret` must be in the JSON body for POST endpoints (URL works only for GET)

The helper handles all of these. **If you ever rewrite or replace `workiz_post`, preserve these auto-injections** or send fails. Drift between local and deployed `dashboard.py` regressed these once already (see `feedback_local_vs_deployed_drift.md`).

## Custom Odoo fields used

| Field | Model | Type | ID | Purpose |
|---|---|---|---|---|
| `x_studio_last_followup_sent` | `res.partner` | date | 20151 | 45-day cooldown anchor. Cleared = eligible. Today = blocked |
| `x_followup_workiz_uuid` | `mail.activity` | char | 20154 | Stamped on launch so the Done tab can rebuild the Workiz link |

## Data resolution — the partner_id rule (where chats get this wrong)

A `mail.activity` can be linked to `res.partner` OR `sale.order`. The follow-up flow needs the **contact** partner, NOT a Property record. Resolution rules:

- `res_model = 'res.partner'` and the partner has `x_studio_x_studio_record_category = 'Property'` → walk up to `parent_id`. Otherwise use `res_id` directly.
- `res_model = 'sale.order'` → read SO's `partner_id`, then apply the same Property→parent walk to that.
- `res_model` is anything else (e.g. `hr.employee`) → `partner_id` stays `None`.

`/api/todos` has this baked in. If you write a new endpoint that operates on activities, replicate it.

## /api/todos performance notes

Pre-optimization (legacy): one search_read for activities (limit 30) + one read for SOs + **one separate read.partner per row inside the loop**. With 30 activities that's 30+ sequential round-trips at ~150ms each ≈ 4-5s total.

Post-optimization (2026-04-27, current default): batched into:
- 1 search_read for activities (with `date_deadline` window filter)
- 1 read for all sale.orders referenced
- 1 read for ALL res.partners referenced (collected from both res.partner activities and SO partner_ids)

Rollback path: flip `TODOS_USE_LEGACY = True` and redeploy. The legacy function is preserved verbatim as `_api_todos_legacy()` below the new one.

**Date window currently DISABLED** (`TODOS_DEADLINE_WINDOW_DAYS = 0`) because DJ has ~29 of 31 to-dos scheduled >60d out, and the filter was hiding them. Set to a non-zero value (e.g. 90, 180) to re-enable the cut. The batched-reads optimization is the real perf win and stays on regardless. Undated activities (`date_deadline = False`) are always included when the filter is active.

## activities.html structure

- Header with WSC/Saunders branding, emerald accent
- Two sub-tabs at top: Open / Done (`#sub-open`, `#sub-done`, JS `showSubTab(name)`)
- Open tab: card list per to-do — clicking a card opens follow-up modal OR detail modal (see routing below)
- Done tab: card list with Workiz pill (rendered if `workiz_uuid` exists)
- **Two modals share the `.fu-*` CSS classes:**
  - **Follow-up modal** (`#followup-modal`): editable textarea with SMS, Send + Mark Done + Cancel buttons. Default for all to-dos.
  - **Detail modal** (`#detail-modal`): plain read-only view of the full activity (customer, type, date, full note). Close + Mark Done buttons only. NO SMS path. Used for Calendly bookings + any other non-followup activity.
- localStorage.wsc_ac for access code persistence (same pattern as field.html / reactivation.html)
- After successful Send: 3000ms pause, then `closeFollowupModal(); loadOpen(); showSubTab('done');` so DJ visually sees the activity move

### Modal routing rule (added 2026-04-27)

`isCalendlyTodo(t)` checks if `summary` or `type` contains "calendly" (case-insensitive). Card click routes:
- **Calendly to-do** → `openDetailModal(cardEl)` — shows full activity contents from `note_full`. Mark Done via `/api/followup/markdone`.
- **Anything else** → `openFollowupModal(cardEl)` — existing flow.

The frontend caches the loaded `/api/todos` response in `openTodosById` so the detail modal can read `note_full` without a second fetch.

If you add a new "this is not a follow-up" activity type in the future, extend `isCalendlyTodo` (rename if needed — it's just the routing predicate).

### note vs note_full

`/api/todos` returns BOTH:
- `note` — first 120 chars of the cleaned text (used for the small preview line on the card)
- `note_full` — full text with HTML stripped, paragraph/line breaks preserved

Stripping done by `_strip_activity_html()` helper in dashboard.py: converts `</p>` → `\n\n`, `<br>` → `\n`, strips remaining tags, decodes basic HTML entities. The detail modal renders `note_full` inside `<div class="dt-note">` which uses `white-space: pre-wrap` to preserve the breaks.

If you need to add a new sub-tab or section to Activities (DJ said "a whole bunch of other things"), add it as a sibling sub-tab — do not bury it inside Open/Done.

## What DJ still has to do on the Workiz side (one-time setup)

1. Create SubStatus value `Follow Up Trigger` in Workiz (under parent Status `Pending`)
2. Create a Workiz automation that fires when a job's SubStatus changes to `Follow Up Trigger`, sending the contents of the `information_to_remember` field as an SMS to the customer

Without those, the launch endpoint will create a Workiz job and set the substatus successfully, but no text will actually go out.

## Phase 3 / Phase 4 interaction

Phase 3's graveyard skip filter was extended on 2026-04-27 (commit `ed24c02e` in Odoo-Migration repo) from `JobType="Reactivation Lead"` to `("Reactivation Lead", "Follow Up Lead")`. This stops Follow-Up jobs from triggering SO creation in Odoo. Phase 4 didn't need changes — it delegates to Phase 3 for missing SOs.

If you ever add a new "trigger-only" Workiz JobType, extend that tuple too. File: `Migration to Odoo/1_Production_Code/zapier_phase3_FLATTENED_FINAL.py`.

## Architectural pivot — why this is NOT an Odoo server action

Reactivation runs out of Odoo Server Actions 562/563 because reactivation was originally triggered FROM the Odoo Studio UI. Follow-Up's trigger surface is the Render app — there is no reason to round-trip through Odoo. Everything lives in `dashboard.py`. DJ explicitly endorsed this.

**Future:** reactivation should eventually be ported to the same pure-Render pattern. Not in scope right now, but if you find yourself adding new server actions for a Render-triggered flow, stop and reconsider.

## Common ways future chats break this

1. **Calling `action_done()` on follow-up activities** → "Call done" chatter regression. Use `write({active: False, date_done: today})`.
2. **Using `job/all/` to verify a follow-up was created** → returns nothing because the job is unscheduled. Use `job/get/{UUID}/` directly. (See `project_workiz_job_all_quirk.md`.)
3. **Forgetting `Status='Pending'` when setting SubStatus** → 400 from Workiz. The `workiz_post` helper auto-injects it; don't rewrite that helper without preserving the rule.
4. **Looking up partner_id without the Property→parent walk** → follow-up gets sent to the property record's chatter (often blank), not the contact.
5. **Local dashboard.py drifting from deployed** → diff before pushing, or you'll regress the UUID + Status auto-injection. (See `feedback_local_vs_deployed_drift.md`.)
6. **Cleaning up "dead" code in field.html** (the old to-do modal/CSS/JS that was moved to activities.html) → DJ left it intentionally. Don't touch.
7. **Refactoring activities.html into a single-purpose to-do screen** → DJ wants this page to grow. Keep it modular.

## How to test the flow end-to-end

1. Pick a contact (e.g. Bev Hartin, partner 23629)
2. Clear cooldown: `res.partner.write([id], {'x_studio_last_followup_sent': False})`
3. Create a `mail.activity`: `res_model_id=90` (res.partner), `res_model='res.partner'`, `res_id=<partner>`, `activity_type_id=2` (Call), `summary='Follow up text'`, `user_id=2`, `date_deadline=today`
4. Open `/owner/activities`, Open tab — the to-do should appear
5. Click it → modal with SMS preview
6. Edit if needed → Send → wait 3s → activity should appear in Done tab with Workiz pill
7. Verify: contact chatter should have "📨 Text sent · Workiz job link · SubStatus: Follow Up Trigger"

## Field Assistant additions layered on top of Activities (2026-04-28)

Several field-assistant changes added today that share infrastructure with the activities module:

- **Tag pill next to dollar amount** is now the SO's real `tag_ids` (OK, CF, etc. — resolved through `crm.tag`), not service words. `_resolve_so_tag_names()` helper batches the lookup.
- **Subtitle (`Window` / `Solar` / `Combo`)** is computed by `_service_labels_by_so()`. **Source of truth = JobType**, not order lines — by design. The order-line analysis is run too, and when it disagrees with JobType, an orange `⚠` is rendered next to the subtitle. This deliberately surfaces data hygiene issues (e.g. JobType says "Outside Windows and Screens" but the SO has both Solar + Window order lines → ⚠ tells DJ to fix the JobType). DJ explicitly chose this over auto-correcting the display.
- **"Combination" was renamed to "Combo"** — shorter on the card.
- **Zero-value `sale.order.line` rows are skipped** in the order-line analysis. Odoo blocks hard-delete of order lines on confirmed SOs; DJ's workflow zeroes qty+price as soft-delete. See `project_so_lines_zero_means_deleted.md`.
- **Pay button is greyed and reads `✓ Already Paid`** when the SO has any posted invoice with `payment_state in ('paid', 'in_payment')`. Logic in `_paid_status_by_so()`. Becomes active again automatically if DJ deletes the payment in Odoo (next schedule refresh re-evaluates).
- **Pay button preselects the method** (Check/Cash/Zelle/Venmo/Credit) based on the customer's most recent `account.payment`. Method detection: `payment_method_line_id` 8=check, 7=credit, 6=cash/zelle/venmo (disambiguated by the `memo` field — "Zelle" or "Venmo" substring → that, else cash). Walks Property → parent Contact since payments live on contacts. See `project_account_payment_no_ref_field.md` (account.payment has NO `ref` field — only `memo`).
- **`openJob()` now fully resets payment section state** — button text, disabled flag, memo input — so a previous job's `✅ Paid` doesn't carry over into the next.
- **`/api/job/append_note` endpoint added** (was missing — the three-dots "Add Workiz Note" was a frontend-only stub returning 404). Reads existing `JobNotes` from Workiz, prepends `[YYYY-MM-DD HH:MM] [Render] <note>`, writes back. Newest note on top.
- **`/api/todos` performance fix** — partner lookups are now batched into 2-3 calls instead of 30+ sequential ones. `TODOS_USE_LEGACY` flag for one-line rollback. Date window filter is currently DISABLED (`TODOS_DEADLINE_WINDOW_DAYS = 0`) because DJ's activities skew far into the future.
- **Detail modal for Calendly bookings** — when a to-do's summary or type contains "calendly," tapping opens a plain detail modal showing the full activity contents (HTML stripped to plain text by `_strip_activity_html`, anchor URLs preserved + frontend `linkify()` makes them clickable). No SMS path. Mark Done uses `/api/followup/markdone`.

## Voice-driven activity creation (planned, not built)

**Goal:** DJ talks into the field assistant, the system creates the right kind of activity automatically. Generalizable to other businesses (W&SC + Cheryl + future).

**Design agreed 2026-04-28:**

- One mic button on /owner/field (probably floating) and on /owner/activities
- Whisper transcribes → small LLM call parses into structured fields:
  - **Customer** (matched against Odoo contacts; AI handles fuzzy match for typos like "Hamm" vs "Ham")
  - **When** (`"in two months"` → ISO date)
  - **Type** (dropdown — explicit confirm, no auto-pick. Surprises = bad)
  - **Draft message** (if SMS-type, AI writes first pass; DJ edits)
- Preview card pops up with all four fields editable. Confirm → save → lands in /owner/activities Open tab with due date.
- **Two starter activity types:**
  1. **`scheduled_sms`** ("prep now, send later") — the SMS body is stored alongside the activity. Cron fires it on the due date through Workiz.
  2. **`reminder`** — just surfaces in /owner/activities on the due date for DJ to act on. No auto-fire.
- Activity catalog (`ACTIVITIES = {...}`) lives in code, not in Workiz/Odoo config. New types = code change. Easy.
- All scheduled-SMS firings reuse the existing follow-up Workiz substatus + automation pattern (one substatus, one automation, dynamic message via `information_to_remember`). New jobs each fire so the "Workiz automation only fires once per status" limit doesn't matter.
- **Render cron** (mcp__render__create_cron_job) runs daily, queries Odoo for activities due today with type `scheduled_sms`, fires each via the same code path as immediate fires, marks the activity done. Daily resolution is fine for service comms; can go hourly if precision matters later.
- **Twilio approval SMS (separate channel for DJ-to-system messaging):** DJ gets a personal Twilio number. When the system needs DJ's approval (e.g. "send this text to Bud now?"), it texts him. He replies Y/N/tomorrow/etc. — Twilio webhook hits Render, Render acts. Twilio is for DJ approval flow; customer-facing SMS still goes through Workiz. Cost is trivial (~$2-3/mo). DJ has not yet set up the Twilio account — needs sign-up + payment card himself.
- **Failure handling:** if Workiz is unreachable when the cron tries to fire, alert DJ (push or email — TBD) rather than silently slip.
- **Generalizability:** same UX (mic → Whisper → LLM parse → preview → save) works for any business; only the activity catalog and SMS templates differ per business.

**Decisions made:**
- Type dropdown is editable in preview, NOT auto-picked — user always confirms explicitly.
- Draft message stored at activity creation time (not regenerated at fire time) — DJ wrote it while context was fresh.
- One Workiz substatus + one automation across all activity types (simpler than per-type substatuses).

**Open / not-yet-built:**
- DJ needs to create the Twilio account.
- Activity catalog content — start with 2-3 types as proof, then add the rest.
- Whether scheduled fires need approval SMS to DJ before they go out, or fire silently. Open question.
- 2-month follow-ups for Bud Piraino + Gary Marsalone (today's "skipped solar" cases) — not yet scheduled. Will be the first real test of the system once built.

## Related memories (cross-references)

- `project_followup_flow.md` — original architectural notes from when this was built
- `project_workiz_job_all_quirk.md` — why job/all/ won't find these jobs
- `project_workiz_substatus_needs_status.md` — the Pending parent Status rule
- `project_workiz_update_needs_uuid_in_body.md` — UUID-in-body rule
- `project_so_unlink_needs_cancel.md` — odoo_write auto-cancel (used elsewhere but related to SO cleanup)
- `feedback_local_vs_deployed_drift.md` — diff-before-pushing rule
- `feedback_never_remove_working_code.md` — don't clean up dead code without DJ
- `session_apr27_summary.md` — full context of when this was built
