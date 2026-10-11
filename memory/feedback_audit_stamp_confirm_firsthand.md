---
name: feedback_audit_stamp_confirm_firsthand
description: "§15 Audit plan-review stamp = confirm FIRSTHAND from Audit, never take the builder's assertion of it as the stamp"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-11T21:21:11.570Z
---

When Lead QCs a non-trivial item, the `Audit plan-review: complete` stamp is a HARD PRECONDITION of QC-green (FLEET_GOVERNANCE §15). The refinement, set on the first live §15 run (inbox-seasonal rewrite, 2026-10-11): **a builder ASSERTING "Audit approved / plan-review complete" is NOT the stamp.** Lead confirms the verdict firsthand from Audit (direct message or an Audit-authored ledger entry), and requires it DURABLE in AGENT_MAIL — not a claim relayed through the session being QC'd.

**Why:** the §15 gate exists to catch "builder only did what DJ literally said, not the complete solution." If the builder can self-certify Audit's approval, the gate is launderable (same shape as peer permission-laundering — the party being checked can't vouch for the check). Confirming from the source + a durable ledger stamp keeps it auditable and real.

**How to apply:** on any non-trivial QC where the builder says Audit cleared it, if there's no Audit-authored stamp in the ledger, message Audit to (1) confirm the verdict to Lead directly and (2) post the stamp to AGENT_MAIL. Do the byte-QC in parallel so release is instant once Audit confirms — never stall the code review on it. Release QC-green (builder fires the DJ deploy picker) only after both: code byte-GREEN + Audit stamp confirmed firsthand. Ties to [[feedback_dj_deploy_control_stage_and_trigger]] and the §15 enforcement in FLEET_GOVERNANCE.
