---
name: project_reeng_duedate_audit_and_declutter
description: Re-engagement task due dates drive the auto-send timing (reengage.py gates on date_deadline<=today); how to declutter follow-ups from My Day; the 2026-06-25 bulk re-date.
metadata: 
  node_type: memory
  type: project
  originSessionId: ce472468-5c4c-4b62-be96-a95fc1c75f1b
---

**Re-engagement task DUE DATE = the auto-send trigger.** The auto-pilot `reengage.py` `find_due()` (daily 8AM cron, main.py) selects re-engagement `project.task`s by **`date_deadline <= today`** (open + gates: not Do-Not-Contact/STOP, has phone, 45-day cooldown) and pushes DJ a digest to one-tap Send/Skip on the Reactivations-Due screen. So the due date is NOT just a reminder — it controls WHEN each customer gets re-engaged. **Therefore due dates must = last-invoice + frequency**, not a hand-moved declutter date.

**DJ's mistake we corrected (2026-06-25):** DJ had bulk-moved ~150 re-eng tasks to ~2026-06-24 using My Day's group bulk-reschedule (📅) just to declutter his view — which silently broke the auto-send timing (all would come due at once). Fix = restore real dates + use the proper declutter tool below.

**DECLUTTER follow-ups the RIGHT way (already built in My Day, no code):** My Day has a view-MODE toggle (Date/**Type**/Category/Priority, `setMode`, localStorage `myday_mode`). In **Type** mode the groups are ✅ Tasks / 📞 Follow-ups / 🌱 Habits, each header has a **🙈 Hide** button → `hideKind('followup')` adds it to `HIDDEN` (localStorage `myday_hidden_kinds`), which filters that kind out of **ALL** modes (myday.html L522) until un-hidden via the "🙈 Hidden:" chip bar. So DJ can hide all follow-ups in one tap and his Tasks view stays clean — without touching due dates. All 150 open re-eng tasks are correctly typed `x_myday_type='followup'` (Phase 5 path 5B sets this; verified). See [[project_reengagement_vs_reactivation]].

**BULK RE-DATE done 2026-06-25:** re-dated **140** clean+maintenance open re-eng tasks → `date_deadline = last out_invoice date + frequency months` (freq: job `x_studio_x_studio_frequency_so` → partner `x_studio_x_frequency` → default 6mo; Sunday→Monday bump; written at 12:00:00 to avoid TZ rollover). SKIPPED 3 STALE (>1yr since last invoice = reactivation candidates, out of scope) + 7 FUTURE-JOB (already have a job booked → re-engagement redundant). ~56 of the new dates are in the past = genuinely overdue, now correctly surface as due. Scripts in scratchpad (`reeng_audit.py`, `reeng_redate_plan.py`, `reeng_redate_apply.py`); reports at project root `REENGAGEMENT_AUDIT.md` / `REENGAGEMENT_REDATE_PLAN.md`; **rollback** `C:\Users\dj\reeng_redate_ROLLBACK.json` (old→new per task). Last-invoice from sale.order `invoice_ids` → account.move `invoice_date` (move_type out_invoice). Customer↔jobs via parent/child partner (SO links property child). Done job = `x_studio_x_studio_workiz_status='Done'`. ALWAYS company_id=1.

**STILL OPEN (handle separately, NOT re-dated):** 3 stale-dormant (e.g. Bev Hartin, last inv 2023 — likely reactivation), 7 future-job (redundant re-eng tasks, candidates to cancel), 4 maintenance-last-job (Steve Acree, Rob Seedorf, Kristin Acker, Bev Hartin — last done job tos=Maintenance, belong on auto-schedule not re-engagement). Decide cancel vs keep per-customer. **How to apply:** re-run `reeng_audit.py` to refresh the audit anytime; re-engagement due dates should always trace to last invoice + frequency.
