---
name: project_so_numbering_post_workiz
description: "★ DECIDED (DJ 2026-07-31): post-Workiz sale.order numbering = YY + climbing 6-digit-style count, year from SERVICE date. Replaces the Workiz-SerialId-padded scheme. Part of Workiz retirement / New Job direct-Odoo cutover."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T05:27:44.370Z
---

**Locked-in numbering scheme for jobs created after Workiz retires** (see [[project_workiz_retirement]], [[project_new_job_intake]], [[project_odoo_so_name_format]]).

## The OLD scheme (how it worked while Workiz was live)
- `sale.order.name` = the **Workiz job SerialId, zero-padded to 6 digits** (`format_serial_id` = `str(int(serial)).zfill(6)`), e.g. `004935`. The two leading zeros were just padding on a 4-digit Workiz number.
- Set at CREATE time by Phase 3 (`create_sales_order(..., order_name=...)`) — **no rename, no unconfirm→confirm dance** in the current system. (DJ's memory of that dance = the OLD pure-Odoo era before Render/Phase-3.)
- The rename-to-Workiz-number actually lands on the **status-change** webhook (Phase 4), not the create webhook: a maintenance job is created in Workiz as **Submitted** → new-job webhook (Phase 3) makes the Odoo SO but leaves Odoo's **native `S00xxx`** name → DJ later adds tech + line items in Workiz and flips STATUS to a confirmation stage → status webhook (Phase 4) pulls everything across AND renames to the padded Workiz number.
- **Live-DB reality (queried 2026-07-31):** Odoo's native sale.order sequence (ir.sequence id=6, prefix `S`, padding 5, company_id=False/global) is at ~`S00200`. ~38 SOs currently carry native `S00xxx` names — these are **unscheduled future maintenance jobs that were going to be renumbered on status-change and now never will** (Workiz dying). 3511 SOs have the 6-digit numeric names, numeric range 5–4934. **The ~38 stranded S-jobs are a cleanup item for the maintenance-flow work.**

## The NEW scheme (DECIDED — build when we do the New Job direct-Odoo cutover)
Format: **`YY` + climbing number, 6 digits total** — the 2-digit YEAR takes the place of the two padded zeros.
- e.g. old `004935` → new `264935` (2026), `264936`, … next year continues `27xxxx`.
- **Year = the job's SERVICE date year** (from `date_order`), NOT the creation date. So a job booked in 2026 for spring 2027 reads as a `27` job. (Value to DJ: instant at-a-glance sense of WHEN a job happened.)
- **Number keeps CLIMBING (cumulative), never resets per year.** Continues the existing Workiz-style count (~4935 now). DJ explicitly wants the running count, not a per-year reset.
- **No-service-date fallback:** unscheduled jobs (e.g. Submitted maintenance) have no service year → stamp the CREATION year; it self-corrects if later scheduled into a different year. (Finalize this rule during the maintenance-flow build.)

## Why it sorts correctly (DJ asked me to verify)
`sale.order.name` is a CHAR field → sorts as text, left-to-right, so the **year prefix is the master sort key**. All `26xxxx` group before all `27xxxx` → chronological by service year, which is what DJ wants. Fixed width keeps numbers ordered within a year.
- **Transition from history is clean:** old names start with `0` (`004935`), new start with `2` (`264935`); `0` < `2`, so all history sorts ahead of all new jobs = correct (history is older).
- **The "counter looks out of order across years" case is HARMLESS:** create a 2027 job (counter 5000 → `275000`), then a next-week 2026 job (counter 5001 → `265001`); `265001` sorts BEFORE `275000`. That's CORRECT — the near-term job happens first. The counter is non-monotonic in the sorted view only because we deliberately sort by service year; the counter is just the uniqueness key. **No collisions possible** — the global counter never repeats, so no two names can match.
- **Within a single year, jobs sort by counter = creation order** (same as today), NOT exact service date. Acceptable to DJ — he wanted YEAR-level granularity, not intra-year service-date sorting.
- **Only edge, years away:** when the cumulative count passes 9999 it needs a 7th digit to keep sorting right (~5–10 yrs at current volume). Handle then; not a near-term concern.

## BUILD STATUS (2026-08-05)
- **Helper EXISTS + is the single source:** `new_job.py` `_next_job_name(service_dt)` → `'%02d%04d' % (yy, counter)` (e.g. `264938`); `_next_job_counter()` → ir.sequence **`wsc.job.seq`** (auto-creates at 4935 if missing; currently past 4937). Pass the PT service date string.
- **APPLIED to ALL live job-create paths (mapped + wired 2026-08-05):** new_job.py ×3 (501/569/854, already), reactivation.py ×2 (1822/1984, already), **duplicate_job** (dashboard.py 7226, lazy import — verified live `264938`), **booking.py** (online booking ~907, lazy `from routers.owner.new_job import _next_job_name`, name=`_next_job_name(date)`). All use the SAME `wsc.job.seq` counter (no collisions).
- **Correctly NOT numbered (skip):** quotes (dashboard `api_quote_save` 6093/6114 + dead quotes.py 65/86 — shadowed), Personal Time blocks (dashboard 5675). **Only remaining un-wired:** dashboard.py:1845 `_create_new` — a **Workiz-dead** graveyard-reactivation branch (uses workiz_post/get); it only names from a Workiz SerialId, but the branch is legacy/likely unreachable post-Workiz, so left alone (moot). Old max legacy counter 4934; 264935/264937 pre-existed from new_job.

## Implementation notes (for the build)
- New Job (`new_job.py` `api_intake_create_job`) already has the direct-Odoo-SO block COMMENTED OUT, marked "uncomment after Workiz retired." Re-enable it, but **set `name` explicitly in the create vals** (compute `f"{service_year:02d}{counter:04d}"`), do NOT let Odoo's native `S`-sequence assign it.
- Need a reliable climbing counter: either an Odoo `ir.sequence` (no prefix) whose next value we read, or max-existing-6-digit-numeric + 1. Single-user low volume → race risk negligible, but prefer a dedicated sequence. Start the counter at **4935** (one past current max 4934).
- Applies to EVERY post-Workiz SO-creation path (New Job, repeat/duplicate, booking approve, the field AI assistant), so the counter/name logic should live in ONE shared helper — ties into the "no single Workiz client / duplicated create paths" structural finding in [[project_workiz_retirement]].
