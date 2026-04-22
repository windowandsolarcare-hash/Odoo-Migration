# W&SC Backlog — Things to Come Back To

**Purpose:** Parking lot for investigations, bugs, ideas, and fixes we've identified but decided not to tackle immediately. Each row links to detail (either inline notes below or an external file).

**Conventions:**
- **Status:** `open` / `in-progress` / `blocked` / `done` / `dropped`
- **Severity:** `crit` (blocks normal ops) / `high` (real-user impact) / `med` (data quality / hygiene) / `low` (nice-to-have)
- When something is resolved, set status = `done` and move to the **Resolved** section at the bottom

---

## Open Items

| # | Item | Severity | Added | Last Touch | Detail |
|---|---|---|---|---|---|
| 1 | **Reactivation filter false positives** — 18 of 70 contacts with future Workiz-linked SOs have empty `x_studio_next_job_date`, so they're incorrectly showing up on the reactivation list. Trigger case: Beth Shelton (id 23023, ref 1393) with job scheduled today. All confirmed to be maintenance customers (post-payment reschedules via Phase 6 → Phase 5). | high | 2026-04-21 | 2026-04-21 | See [§1 below](#1-reactivation-filter-false-positives) |
| 2 | **Stale `Annual Reactivation Pipeline` filter** (`ir.filters` id 20) doesn't check `next_job_date` — if anyone still uses it, scheduled-job customers wrongly appear on the reactivation list. | med | 2026-04-21 | 2026-04-21 | One-line fix: `ir.filters.unlink([20])`. Verify first no saved actions reference it. |
| 3 | **Known stale-date bug** — jobs deleted in Workiz without being canceled first leave stale `next_job_date` on the contact, causing false exclusions. 11 contacts affected on 2026-04-19. | med | 2026-04-19 | 2026-04-21 | Root fix: Phase 4 needs a periodic reconciliation against Workiz open-jobs list. Quick fix: policy of cancel-before-delete in Workiz. |
---

## Resolved

| # | Item | Resolved | Notes |
|---|---|---|---|
| 4 | **Phase 3 / 4 / 5 flowcharts** | 2026-04-22 | All four phase diagrams (3, 4, 5, 6) now complete with MMD + SVG + PNG + narrative MD at `3_Documentation/phase_diagrams/`. Same silent-fail-gate color coding across all four. Phase 5A identified as the load-bearing path for the `next_job_date` write, Phase 5B flagged with an architectural gap (no write at all). |

---

## Details

### 1. Reactivation filter false positives

**Discovered:** 2026-04-21 during Beth Shelton investigation.

**Symptom:** Customer has a real future Workiz job (tracked as `sale.order` with `date_order` in the future in Odoo) but `res.partner.x_studio_next_job_date` is empty, so the reactivation filter includes them.

**Count as of 2026-04-21:** 18 of 70 contacts with future Workiz-linked SOs. ~26% false-positive rate.

**Pattern:** All 18 are maintenance customers (post-payment reschedules). The pipeline is: Odoo Payment → Phase 6 → Phase 5 (Maintenance Path 5A) → writes `next_job_date`. Failure is somewhere in this chain or in a pre-migration backfill gap.

**Silent-fail gates identified** (any one of these causes a missed write with no alert):
1. Phase 6 can't resolve contact id (`cid`) from property's parent_id when category isn't exactly "Contact" → Phase 5 never fired
2. Phase 5 `contact_id` coerces to 0 or None if Zapier passes "False" / empty string
3. Phase 5A's `if contact_id:` guard silently skips the write
4. `write_next_job_date_to_contact`'s internal `if not contact_id or not scheduled_datetime_str:` silently returns
5. Phase 5B (on-demand/on-request) path doesn't write next_job_date at all
6. Workiz-API-created jobs may not fire Workiz's "New Job" webhook, meaning Phase 3 wouldn't run as a backup writer
7. Pre-2026-04-02 backfill may have missed these 18; backfill script not reviewed

**Most likely cause ranking:**
1. Pre-backfill stragglers (explains consistent pattern across 18 different customers)
2. Phase 6 `cid` resolution failed (property record has `parent_id` empty and `record_category` != "Contact")
3. Phase 5 webhook got `contact_id` as empty string or "False"
4. Phase 5A write succeeded but was later overwritten by Phase 4 mis-firing on intermediate status

**Next diagnostic step:** compare the 18 mismatched vs. the 52 correctly-set contacts. What's systematically different about the 18 — creation date, property parent, record_category, migration origin?

**Full 18 list** (ordered by earliest future job):
- Beth Shelton (id 23023, ref 1393) — 2026-04-21
- Leon Hurwitz (id 23455, ref 1664) — 2026-04-24
- Linda Lusk (id 22979, ref 1272) — 2026-04-24
- Naresh Bellara (id 23394, ref 1721) — 2026-05-05
- Lanny And Sue Lund (id 23067, ref 1033) — 2026-05-12
- Grace Kaelin (id 23056, ref 1025) — 2026-05-19
- Linda Stoddart (id 23240, ref 1668) — 2026-06-10
- Marie White (id 23055, ref 1015) — 2026-06-16
- Gayle Ormond (id 23005, ref 1700) — 2026-06-18
- Mark Seiler (id 22985, ref 1079) — 2026-06-23
- Nancy Hughes (id 23024, ref 1126) — 2026-06-30
- Roberta Davis (id 23016, ref 1006) — 2026-06-30
- Caroline Graham Ashford (id 23030, ref 1074) — 2026-07-14
- Larry And Teresa Ballinger (id 23019, ref 1003) — 2026-07-21
- Sandy And John King (id 23429, ref 1039) — 2026-07-21
- Sharon Sims (id 23180, ref 1799) — 2026-09-15
- Stacey Speiser (id 23187, ref 1255) — 2026-09-24
- Alexander Burck (id 23449, ref 1676) — 2026-09-27
