---
name: feedback_money_adjacent_staging_risk_calibrated
description: Money-adjacent ships are risk-calibrated — SEND/MOVE-money → dual-GREEN BEFORE merge; inert/reversible price-write → may ride auto-deploy-on-QC if QC is prompt.
metadata:
  node_type: memory
  type: feedback
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-11-04T21:03:21.915Z
---

Lead's ruling (2026-11-04, ratified after the accept-to-job agreed-price override shipped to main BEFORE Audit's §15 byte-gate completed): the "money-adjacent → stage for dual-GREEN before merge" convention is **risk-calibrated, not blanket**.

- **Stage for dual-GREEN (Audit + Lead) BEFORE merge** when the change would **SEND to a customer** (any message/email/SMS primitive in the path) or **MOVE money on its own** (records a payment, transfers, charges, auto-confirms a bill).
- **May ride auto-deploy-on-QC** (merge to main, then byte-gate promptly — minutes, not hours) when the change is **inert until a confirm-gated action**, **additive**, and **reversible** — e.g. an accept-to-job price-write that only rewrites an SO line, has NO send primitive, and does nothing until DJ taps a confirm-gated prompt.

**Why:** a post-merge byte-gate on an inert/reversible price-write has near-zero blast radius (worst case = a price on a draft/confirmed SO DJ is accepting anyway, read-back-verified; no customer contact, no money movement), so blocking its merge buys little. But anything that reaches a customer or moves money has irreversible blast radius the instant it runs, so it must clear dual-GREEN first.

**How to apply:** when a peer stages or ships money-adjacent code, first classify the PATH (grep for send/pay/charge/transfer primitives — "no customer-send in the path" is a firsthand check, not a claim to accept). SEND/MOVE → expect it staged on a branch/review-folder, and byte-gate before promote. Inert/reversible price-write → acceptable already-on-main; still byte-gate promptly and surface the base posture factually (I flagged "these 3 commits are already live on main" — Lead called raising it the right move even though the ruling was "acceptable"). A finding on an already-merged inert change is **fix-forward**, not block-merge. Refuses/guards must be HONORED (return the error, never advertise a price/amount that wasn't actually set). See [[feedback_picker_plain_english_synopsis]] (auto-deploy-on-QC model), [[feedback_audit_stamp_confirm_firsthand]] (§15 stamp = firsthand + durable), [[feedback_dj_deploy_control_stage_and_trigger]], [[feedback_data_location_odoo_vs_postgres]].
