---
name: project_maint_advance_status_is_truth
description: "★ The Workiz STATUS is the truth about whether a customer was told about their next job. 'Next Appointment - Text' = message went out = TREAT AS ACKNOWLEDGED even with no reply (customers forget). 'Submitted' = nobody knows the job exists. Do NOT trust wsc.maint.advance.* state params — an Aug-2026 phrase backfill wrote bogus 'ok' onto jobs that were never texted, which hides them from the Stage-0 card forever."
metadata:
  node_type: memory
  type: project
  modified: 2026-09-01T00:00:00.000Z
---

**Established with DJ 2026-09-01, verified against live data (16/16 exact split).**

## The Workiz mechanic this comes from
Workiz created EVERY job as **Submitted**. The advance "here's your next service" text only went out
when DJ manually flipped the status to **Next Appointment - Text** (or `Next Appointment 2 - Text`).
So the status is not decoration — it *is* the record of whether the customer was contacted.

Workiz went dark 2026-08-03 and **nothing replaced that flip.** Jobs sit in Submitted, the customer
is never told, and the 4-day confirm batch skips them because `_jobs_on` requires
`state in ('sale','done')` and a Submitted job is still a `draft`. Silent on both ends.

## ★ DJ'S RULE — how to read it
- **`Next Appointment - Text` / `Next Appointment 2 - Text` → TREAT AS ACKNOWLEDGED.** The message
  went out. A missing reply means nothing — **customers frequently just forget to answer.** Do NOT
  chase, re-send, or surface these as needing attention.
- **Only an explicit NO counts as not-acknowledged** — a reschedule/cancel/"can't do that day" reply.
- **`Submitted` → NOBODY KNOWS THE JOB EXISTS.** This is the real work queue.

## Proof (2026-09-01, 16 jobs sampled from the 27 carrying an 'ok' advance state)
Perfect correlation, no exceptions: every job whose text thread contained a real advance message
naming that job's date was `Next Appointment - Text` (+ `state: sale`); every job with NO advance
message for that date was `Submitted` (+ `state: draft`).

## Do not trust the advance-state params
`wsc.maint.advance.<so_id>` values written `"via": "ok-reply backfill (phrase)"` on 2026-08-08 are a
PHRASE MATCH over imported Workiz texts, not evidence of a send. 25 jobs got `state: ok`; only TWO
real sends exist in the `wsc.msg.sent` ledger (`maint_advance:17559`, `maint_advance:17301`).
For genuinely-flipped jobs the backfill was RIGHT (Barry Matthews 004735: advance 2026-07-10, "Ok"
reply 8:02 the same morning). For never-flipped ones it is WRONG — and because the Stage-0 card only
surfaces jobs with NO state, a bogus `ok` hides that customer from DJ **permanently**.

## How to apply
- Deciding "was this customer told?" → read `x_studio_x_studio_workiz_status`. Do not read the
  advance-state param, and do not go digging in text threads (a whole audit was built for this on
  2026-09-01 before DJ pointed out the status already answers it in one query).
- Anything that surfaces "needs the advance touch" should key on **future job + status Submitted**,
  not on the absence of an advance-state param.
- Sending via `send_maint_advance` overwrites the bogus `ok` with a real `sent`, so the record
  self-corrects as DJ works the list.
