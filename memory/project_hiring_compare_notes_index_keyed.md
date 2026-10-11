---
name: project_hiring_compare_notes_index_keyed
description: Candidate-Compare interview notes are keyed by ARRAY INDEX (qN = INTERVIEW_Q position); reindexing after Oct-12 2026 mis-attributes saved notes — keep indices stable or migrate to stable-id keying first.
metadata:
  node_type: memory
  type: project
  originSessionId: 71d8a955-480c-46cd-92bf-c963ba9d5a16
  modified: 2026-10-11T08:24:29.992Z
---

The Candidate Comparison page (`static/owner/hiring_compare.html`, Portal-owned, served at `/owner/hiring/compare`) stores every per-question interview note in Render Postgres table `hiring_compare_note`, one row per `(candidate_id, field)`. For the main interview questions the `field` is the **array index** of `INTERVIEW_Q` — `q0`, `q1`, … `qN` (see `ivItem(id,"q"+i,q)` + `INTERVIEW_Q.forEach((q,i)=>…)`). The candidate-specific "just for them" questions use `s0..sN` and the wrap-up uses `close`. The DJ/Cheryl/shared candidate notes use `dj`/`cheryl`/`shared` and are NOT question-indexed.

**Why it matters:** because the note key is the position, any change to `INTERVIEW_Q` that **adds, removes, or reorders** an item shifts every later index — a note saved under the old `qK` then renders under a *different* question. This is silent mis-attribution, not a crash.

**How to apply:**
- A reindex is SAFE only while `hiring_compare_note` has **zero `qN` rows**. Through 2026-10-11 we made several INTERVIEW_Q edits (10→9→10) safely because the store had 0 qN rows (verified live each time; the lone row was `field='shared'`).
- **★ Oct 12 2026 interviews are the cutoff.** Once they save real `qN` notes, treat the INTERVIEW_Q order/length as FROZEN. Before any further add/remove/reorder after that, either (a) keep existing indices stable (only append, never insert/reorder — and even appends are safer with a migration plan), or (b) FIRST migrate the note key from array index to a **stable question id** (give each question a durable id and key notes off that, not position) and backfill existing rows. The stable-id keying is the long-planned fix (Lead flagged it twice).
- Reword-in-place (changing a question's TEXT without changing its position/count) is always safe — same slot.
- Before ANY INTERVIEW_Q structural change, query `SELECT count(*) FILTER (WHERE field ~ '^q[0-9]+$') FROM hiring_compare_note` (DB `dpg-danl5vqjnfac7390g8g0-a`, read-only) and refuse/redesign if > 0.
- Count labels ("The N questions" / the genq summary `#ivqcount`) are already **dynamic off `INTERVIEW_Q.length`** (2026-10-11) so they never drift again — don't reintroduce a hardcoded count.

See [[feedback_data_location_odoo_vs_postgres]] (operational/high-write → Render Postgres) and [[feedback_sporadic_bugs_repeat_test]].
