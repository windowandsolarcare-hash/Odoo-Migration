---
name: project_accept_to_job_amount_override
description: "accept_to_job_core (quotes.py) gained an optional amount_override — DJ's agreed/rounded price on the accept-to-job step, parity with send_quote. Reuses brain._apply_quote_override. Also: x_studio_x_studio_pricing_snapshot is a TEXT memo, NOT the quote amount."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-11-04T20:55:17.821Z
---

**What (built 2026-11-04, Operator gap, Lead-approved):** the "quote accepted → put price on this job" step can now take DJ's agreed/rounded FINAL price instead of only the computed total — parity with Send Quote's override. Before this, `accept_to_job_core` recomputed strictly from pane counts, so DJ had to route AROUND it (Operator did, via /api/job/lines, to land Mark Bradshaw SO 265060 at a flat $350 vs computed $371.50).

**How:** `accept_to_job_core(so_id, mode, difficulty, counts, amount_override=None)` (routers/owner/quotes.py). After `_replace_quote_line` writes the computed windows line, if `amount_override` is given it **REUSES `brain._apply_quote_override`** (NOT reimplemented — feedback_reuse_canonical_endpoint) to rewrite the windows line price_unit in place. Same money guards (posted-invoice refuse, add-on-priced-lines refuse, 0<amt<=100000). **Honors refusal** — returns the error instead of claiming a price it didn't set (closes the build_sell_card MEDIUM class at the caller). GUARD(b) verifies against the effective target (override amt when applied, else computed). Threaded through the endpoint `/api/quote/accept_to_job` + the #6 voice tool `quote_to_current_job` (schema + preview). UI: v2_quote.html accept action prompts for the price (seeded w/ computed), sends `amount_override` only when it differs. Commits: quotes.py ca1c9d52, dashboard.py 1e604df7, v2_quote.html a16ae471.

**★ Works on a single windows-line job only.** If the job already has add-on service lines, `_apply_quote_override`'s `_quote_other_priced_lines` guard refuses (you can't force a target TOTAL through one line when siblings add to it) — same as send_quote; set the price in the quote itself then. The accept path still PRESERVES siblings (DJ 2026-09-28); the override just can't run on top of them.

**★ pricing_snapshot is a TEXT memo, NOT the amount (corrects a design note).** `x_studio_x_studio_pricing_snapshot` (sale.order) is the customer's "Pricing · this job" **textarea memo** (dashboard.py:9493; written only from text pricing memos / Workiz sync at :2092/:12375). NEITHER `send_quote` NOR `_apply_quote_override` writes the quote dollar amount into it. The job "carries the adjusted number" purely via the WINDOWS line price_unit → amount_total → what gets invoiced. So do NOT write an override dollar figure into pricing_snapshot (would corrupt the memo). Lead's build note said to "snapshot the price the way send_quote does (pricing_snapshot)" — verified against code that send_quote does not; built without it and flagged to Lead.

**No customer-facing send:** verified — accept_to_job_core has zero send primitives (no messaging.send / mail.mail). Pure Odoo write. Money-adjacent → pending Lead byte-QC + Audit §15 at time of writing. Related: [[feedback_reuse_canonical_endpoint]], [[feedback_no_guessing_on_fields]], [[project_quote_line_clobber_fix]] (IN_OUT=141/OUTSIDE=103 windows products), [[feedback_happy_path_e2e_before_dj]].
