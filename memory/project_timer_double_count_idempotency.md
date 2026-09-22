---
name: project_timer_double_count_idempotency
description: "Field timer records (timeclock.py) are a JSON list in ir.config_parameter timer.so.<so_id>; /api/timer/log appended with NO idempotency → a double-tapped/retried Stop duplicated a record and DOUBLED pay (Carolyn Straub 004332/17061). Fix = _timer_dedupe + idempotent log + self-heal on read."
metadata:
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T21:30:27.559Z
---

**Timer double-count / pay-doubling bug (fixed 2026-09-22, commit eac13752).** Carolyn Straub, SO name `004332` = so_id `17061`, showed 2h42m/$81 — actually 1h21m/$40.50. **Why:** field timer records live as a JSON list in `ir.config_parameter['timer.so.<so_id>']` (keyed by NUMERIC so_id, not name); `/api/timer/log` did a bare `records.append(record)` with **no idempotency**, so a double-tapped Stop / no-signal retry / a re-fire (the 502 retries earlier that day were a plausible trigger) appended a **byte-identical** record (same start_iso+stop_iso+employee_id → same minutes/$). Violated CLAUDE rule #13 (idempotent keys on replayed actions).

**Diagnosis method (read-only odoo_rpc):** `ir.config_parameter get_param 'timer.so.17061'` → two records, both `2026-09-22T16:46:11.695Z → 18:06:44.163Z`, 81 min, emp 1, identical to the millisecond = one Stop submitted twice (real DB dup, NOT a display bug). Same start_iso to the ms is the tell.

**Fix (timeclock.py, +36 lines, surgical):**
- `_timer_dedupe(records)` — collapses records with identical `(start_iso, stop_iso, employee_id)`, keeps the FIRST, returns `(deduped, removed_count)`. **Money-safe: two genuinely-distinct sessions differ by start_iso, so ONLY exact re-submits merge — real work is never collapsed.**
- `/api/timer/log` now IDEMPOTENT — dedupes existing first, and if the exact record is already present (`_is_dup`) skips the append + chatter + debug, returns `{ok, idempotent:True}`.
- `/api/timer/records` SELF-HEALS on read — dedupes + persists if changed, so a pre-existing dup (like Carolyn's) shows correct the moment DJ reopens the timer (the FE re-fetches records on open). Did NOT raw-delete Carolyn's dup — self-heals in-app.

**How to apply:** any timer/log write must stay idempotent (exact-record guard); the dedupe key is `(start_iso, stop_iso, employee_id)` — never widen it (would merge distinct sessions). Timer data is keyed by numeric so_id in `timer.so.<id>`. See [[feedback_reuse_function_follow_full_logic]], CLAUDE #12/#13 (localStorage + phone edge cases: double-tap, retry).
