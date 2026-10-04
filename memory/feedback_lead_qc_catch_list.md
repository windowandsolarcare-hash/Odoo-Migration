---
name: feedback_lead_qc_catch_list
description: "Lead QC catch-list (2026-10-01..04): the recurring defects a byte-QC must actively hunt — silent fail-open hiding a bad field name, a 'canonical delegation' that drops unique steps, a regroup that loses member actions, route shadow (check ENDPOINT_MAP LIVE column), stale staged-mirror collisions between units that share a file, public-endpoint state gates, and 'no send' being necessary-not-sufficient."
metadata:
  type: feedback
---

Each of these slipped past (or nearly past) a QC pass and cost real time. Check them EVERY QC:

1. **Fail-open hides a bad field name.** A search_read/read that names a nonexistent Odoo field raises, a blanket `except` returns []/{} and the feature silently shows nothing (addons endpoint read `mobile` — doesn't exist on res.partner in Odoo 19; board holds would have shown no holds). **Why:** my QC read the diff but did not verify names. **How to apply:** for every field in a new read, demand a `fields_get` proof in the BUILD_NOTE before ship.
2. **Delegating to a canonical function can silently drop the duplicate's unique steps** (payment_link delegation dropped STRIPE_PENDING narration + chatter note that only payments.py did). **How to apply:** diff the OLD body's side-effects against the canonical's; re-apply what's missing in the wrapper, NOT inside the shared builder.
3. **A regroup/re-render must keep every member's actions** (hud-declutter dropped Approve on billing cards -> 3 payments unrecorded). **Why:** "no send" was checked, "no action lost" wasn't. **How to apply:** render-test one member of EACH kind (rule in LEAD.md).
4. **Route shadow:** before QC'ing/accepting an endpoint edit, check ENDPOINT_MAP's LIVE column — the fix landed in the dashboard.py shadow while the field button hit payments.py.
5. **Shared-file collisions between staged units:** two units built from the same live base each lack the other's hunks (slot_offers.py, sms.py, v2_inbox.html, scheduler.py, payments.py). Require ONE merged artifact or hunk re-apply at ship + re-diff vs fresh live.
6. **Public write endpoints:** require a state gate (draft+Submitted+no invoice), uniform 403, item caps, idempotency, exact-label maps (not substring), generic error text. Phone+sequential-id is weak proof alone.
7. **Money amounts:** never trust a client amount; derive from the invoice residual server-side; bind invoice<->SO before ANY write (incl. action_post); refuse cancelled; tip bounded.
8. **Shadow/telemetry on a public or live path:** bound the cost (cap days sampled, daemon thread, connect/statement timeouts), count real units (page HITS not day-checks), never write an exclude-filtered result to a shared cache.
9. **Dedup keys with no time component** permanently block a legit repeat once the ledger records them (queued-send fallback key) — scope by date.

Related: [[feedback_verify_collection_and_live_pipe]], [[feedback_reuse_function_follow_full_logic]], [[feedback_check_endpoint_map_first]].
