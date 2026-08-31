---
name: project_command_confirm_ribbon
description: "Command Center job cards now show THREE confirmation states, not two: green CONFIRMED / amber SENT-NO-REPLY / red NOT SENT (in-window only). api_sched_states() gained 'awaiting' + 'confirm_lead_days' from wsc.reminders.awaiting. Also documents the build_batch gap: jobs added after a day's batch was built never get a confirmation text."
metadata:
  node_type: memory
  type: project
---

**Shipped 2026-08-30 (cloud Lead, PR #2 → `15fba33`).** DJ: *"when i look at card now I can't tell
if confirmation was sent."* Spec: `3_Documentation/CONFIRM_STATUS_ON_CARD_BRIEF.md`.

## The problem

A Command Center job card had only TWO visual states: green `✓ CONFIRMED`, or **nothing**. "Nothing"
conflated two situations that need opposite actions:

- *We texted them, no reply yet* → wait, or nudge.
- *We never texted them at all* → send one NOW.

## Root cause — the data existed, it was just never exposed

`reminders.py:34` — `PENDING_KEY = 'wsc.reminders.awaiting'`, a single `ir.config_parameter` holding
JSON `{norm_phone: {so_id, so_name, sent}}`. That is exactly "sent, awaiting reply", **including the
sent timestamp**. `MAINT_AWAIT_KEY = 'wsc.maint.advance.awaiting'` is the same shape for the
maint-stage queue. Neither was ever returned by `api_sched_states()`, so `v2_command.html` could not
render what it did not receive — `jobCard()` could only branch on `_CONF[entity_id]`.

## The change

**Server — `routers/owner/scheduler.py` `api_sched_states()`** (additive; existing
`states`/`confirmed`/`acknowledged` shapes untouched, because the client hydrates those from
localStorage and an unknown shape breaks first render):

```python
await_map = {}
for key in ('wsc.reminders.awaiting', 'wsc.maint.advance.awaiting'):
    ...  # invert phone -> so_id; skip anything already in `conf`
try: from .reminders import CONFIRM_LEAD_DAYS as _cld
except Exception: _cld = 2
return JSONResponse({..., 'awaiting': await_map, 'confirm_lead_days': _cld})
```

**Client — `static/owner/v2_command.html`:** `_AWAIT` / `_CLD` added beside `_CONF`/`_ACK`, hydrated
synchronously from the same `wsc_cc_states` localStorage key and included in `_saveSchedStates()` —
the exact pattern established in [[project_command_conf_pills_cached]]. Precedence:

```
confirmed        → green  ✓ CONFIRMED        (unchanged, still wins)
else awaiting    → amber  ⏳ SENT — NO REPLY   .await-side  #e8a317
else in-window   → red    ⚠️ NOT SENT         .notsent-side var(--danger)
else             → blank
```

**★ The in-window guard is load-bearing.** Red only shows when
`0 <= (job_date - today) <= CONFIRM_LEAD_DAYS`. Without it every future job on the calendar screams
red — a job three weeks out legitimately has no confirmation yet.

## Gotchas hit while building (all real, all cost a cycle)

- **`_dk(r)` is defined AFTER `confSide` inside `jobCard()`** — calling it from the ribbon branch is a
  TDZ/undefined error. Inline the date instead: `var _jd = r._date || r._draw || ''`.
- **There is no `.b.bad` badge class** — the danger variant is `.b.danger`. Grep before inventing a class.
- **`dnc` was not on the row objects.** Without adding `dnc:!!j.dnc` to BOTH row builders, a
  Do-Not-Contact customer sits permanently red for a text we will never send. Fixed in the same PR.

## ★ Separate bug this exposed — REAL, still unfixed

`build_batch()` in `reminders.py` persists a day's confirm batch **once** and is never re-run for
that date. **Any job added to a day AFTER its batch was built never gets a confirmation text.**

Live example 2026-09-01: Debbie Church (SO `264960`) was created after the batch — the pipeline never
texted her. It only got covered because **DJ noticed and sent it by hand.** So the gap is currently
absorbed by DJ's attention, not by anything failing loudly.

The red ribbon makes it *visible*; visibility is not a fix. Two options, neither built:
- a daily sweep that re-checks the target day for un-texted jobs and appends them to the batch, or
- rebuild-and-merge on read — **preserving `sent[]` and `status`**, because a naive `build_batch()`
  call **overwrites** the stored batch (`_pset(BATCH_KEY, ...)`). A plain rebuild is NOT safe.

## Related

- [[project_command_conf_pills_cached]] — the localStorage hydration pattern this extends.
- [[project_reminder_texts_build]] · [[project_confirmation_ack_approval_gate]]
