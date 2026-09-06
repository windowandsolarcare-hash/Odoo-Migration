---
name: project_cadence_engine
description: "Per-service maintenance cadence engine (opt-in) in new_job.py: multi-service customers on different intervals get per-service next_due, grouped into ONE visit per completion (nearest+co-due within 14d) = Combination job, else single. Opt-in via ir.config_parameter wsc.cadence.<pid>; no config = existing single-freq path unchanged. GOTCHA: rank_days best.time is NOT %H:%M."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-06T09:32:45.973Z
---

**Built + throwaway-QC'd 2026-09-06 (commits 026db9c → c804941), gated behind Lead QC + DJ bless before running on real customers (Nick/Norman).** Solves: customers with MULTIPLE services on DIFFERENT intervals (Nick: solar 2mo + windows 4mo; Norman: windows monthly + panels 3mo) were mis-dated by the single-frequency next-job generator.

**Where:** `new_job.py` `create_next_maintenance_so(completed_so_id)` — the ONE live next-job spawn (called by `payment_finalize.finalize_payment` ← `dashboard._execute_payment`; submitted_jobs.py is sync/display only, NOT a generator). Added ONE opt-in branch right after prop_id resolution; the existing single-freq body is byte-unchanged and runs whenever there's no config.

**Opt-in config (rule-4 clean, no model/seat):** `ir.config_parameter 'wsc.cadence.<pid>'` (property id first, parent customer fallback) = JSON `{"services":{key:{interval_months,job_type,product_id[,price]}}, "anchor":{key:"YYYY-MM-DD"}}`. No config → `_cadence_config` returns None → single-freq path. This is the whole safety (QC proved a non-configured customer is byte-identical to before).

**Algorithm — ONE VISIT PER COMPLETION (the key to clean combos):** on completion, compute next_due(service) = last_done(service) + interval for every service; D = min(next_due) = the next visit; visit = every service due within `CADENCE_GROUP_WINDOW_DAYS` (=14, a NAMED tunable) of D → ONE job (job_type 'Combination of Services' if >1, else the service's label; lines = one per due service's product). Services due later are NOT pre-created — a later completion creates them. This mirrors the single-freq "one next job per completion" so services reconverge into a Combination naturally instead of racing into two same-date solo jobs. last_done(service) = max(config anchor, most-recent unambiguous DONE job that included it — resolved from job_type single-label, else Combination order-line product_id via PRODUCT_TO_JOB_TYPE). **Fail-safe:** a service that can't be dated confidently (unresolvable Combination + no anchor) is SKIPPED + raises a → DJ alert (never auto-mis-dated).

**Merge safety net:** before creating, query an existing future Submitted SO for the property within ±window and MERGE the missing services into it (add lines, upgrade job_type→Combination) instead of duplicating (handles re-runs / a hand-pre-created job / near-date races). Per-source idempotency flag `wsc.maint.next_created.<completed_so_id>` still set (single-freq shares it).

**Entry point:** `POST /owner/api/maint/spawn_next {so_id}` (new_job.py, owner-gated) — runs create_next_maintenance_so on demand; the QC harness entry AND a manual "generate next job now" for DJ/Operator. Idempotent + opt-in, so safe on any completed maintenance SO and can't run cadence on a customer without a config.

**★ GOTCHA that the multi-cycle QC caught (would have mis-dated real jobs):** `scheduler.rank_days(...)['best']['time']` is NOT `%H:%M` (it's like "9:00 AM"). Building the visit datetime via `strptime(date+' '+time, '%Y-%m-%d %H:%M')` THREW → the except fell back to `datetime.now()` → EVERY cadence job got date_order = TODAY, and the merge window centered on today so merge never fired. Grouping still looked right (it's computed pre-anchor) so label-only assertions MISSED it; the FUTURE-DATE assertion exposed it. Fix: anchor the DATE only from `rank_days best['date']` (weekday-anchored) + a fixed 09:00; ignore best['time']. **Lesson: when QC'ing a generator, assert the DATES are what you expect, not just the composition.** Solar has NO product constant yet (option A pending DJ) — the anchor-seed (option B) makes the initial run correct without it. See [[project_voice_tool_add_pattern]] pattern discipline + [[project_shared_star_import_scoping_gap]].
