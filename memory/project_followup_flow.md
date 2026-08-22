---
name: Follow-Up flow — pure Render, no Odoo server actions
description: 2026-04-27 — DJ asked for parallel-to-reactivation follow-up flow. Built entirely in Render Python. Mirrors reactivation's Workiz-side mechanism (information_to_remember + SubStatus trigger) but no Odoo SAs.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Built 2026-04-27. Lives in `routers/owner/dashboard.py` + `static/owner/field.html` in `windowandsolarcare-hash/saunders-render-app`.

**Architectural decision:** moved away from the reactivation pattern of Odoo server actions (SA 562 Preview / SA 563 Launch). DJ explicitly questioned whether server actions still earn their keep now that Render exists. They don't — the trigger is in Render, the UI is in Render, the SMS template can be a Python function. Server actions only earn their keep when the trigger lives *inside* Odoo (cron, button on form view, automated rule).

**Why this matters for future work:** when reactivation needs maintenance, consider porting SA 562/563 into Render endpoints too. Then the two-step Odoo-deploy pain (CLAUDE.md rule #2) for reactivation goes away. Don't touch reactivation reactively — only when reactivation work is already in scope.

## Workiz-side mechanism (cribbed from reactivation)

The SMS text travels through Workiz, not through SMS provider APIs directly:
1. Render creates a Workiz job with custom field `information_to_remember` = the SMS body
2. After 3-second pause (Workiz commit race), Render updates job's SubStatus
3. Workiz automation fires on the SubStatus change and sends SMS using `information_to_remember`

**Reactivation uses SubStatus = "API SMS Test Trigger".**
**Follow-up uses SubStatus = "Follow Up Trigger"** (DJ created this in Workiz).

Both ride parent Status="Pending". `workiz_post()` auto-injects `Status="Pending"` whenever `SubStatus` is in body — see `project_workiz_substatus_needs_status.md`.

## Endpoints

- `GET /owner/api/todos` — extended to return `id`, `res_model`, `res_id`, `partner_id`. Resolves partner_id by walking up from Property → Contact when needed; resolves SO-linked activities by reading `partner_id` on the SO and walking up.
- `POST /owner/api/followup/preview` — read-only. Builds SMS from Python template, returns history + cooldown status. Does NOT write to Odoo.
- `POST /owner/api/followup/launch` — clones latest Workiz job for contact, fires SubStatus, writes `x_studio_last_followup_sent`, marks `mail.activity` done.
- `POST /owner/api/followup/markdone` — closes to-do without sending (when DJ handled it another way).

## Cooldown

- Field: `x_studio_last_followup_sent` on `res.partner` (date, id=20151, created 2026-04-27)
- Days: 45
- Enforced on `/launch` (blocking, returns ok:false). Preview only warns.
- Reactivation cooldown is 90 days via `x_studio_last_reactivation_sent` — different field, independent counter.

## SMS template

In `_build_followup_sms()` in `dashboard.py`. DJ said wording is a starter and he'll iterate. To change copy: edit one Python function, push, live in 2 min. No Odoo Studio editing.

Calendly slug-by-city map is duplicated from reactivation PREVIEW script (`ODOO_REACTIVATION_PREVIEW.py` lines 124-139). If reactivation's slug map changes, follow-up's must change too — or refactor both to share.

## UI

- To-do cards in field.html become clickable when `partner_id` is set (i.e., resolvable to a contact). Cards without a partner stay read-only.
- Tap → bottom-sheet modal (`#followup-modal`) styled like the existing voice modal. Three buttons: Cancel / Mark Done (no send) / Send Follow-Up.
- Send button is disabled when cooldown warning fires.

## What DJ has to do in Workiz

1. Create new SubStatus "Follow Up Trigger" under parent Status "Pending"
2. Set up Workiz automation on that SubStatus that sends SMS using `information_to_remember` field — same as the reactivation automation, just on a different SubStatus

Until DJ does step 2, the launch endpoint will create the job and set the SubStatus, but no SMS will go out.

## Why: Knowing this saves time when

- Someone asks "why doesn't follow-up use SA 600 like I expected?" — answer: deliberate architectural shift, not an oversight.
- Someone asks "does follow-up share fields with reactivation?" — answer: shares `information_to_remember` and parent Status="Pending", but uses its own cooldown field and own SubStatus.
- A new follow-up template wording request comes in: edit `_build_followup_sms()` and deploy. Don't touch any Odoo server action.

## How to apply

- Bug reports against follow-up: check Render logs first, not Odoo chatter — the code path is pure Python.
- Calendly link broken? Same root cause as reactivation (the slug map). Fix in both places or refactor.
- "Cooldown is wrong" → adjust `FOLLOWUP_COOLDOWN_DAYS` constant at top of the follow-up section.
- "SubStatus name is different now" → adjust `FOLLOWUP_SUBSTATUS` constant. Don't hardcode it in JS.
