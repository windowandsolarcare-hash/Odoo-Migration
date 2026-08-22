---
name: Pending Discussion — Auto-sync Workiz before Payment button
description: REMIND DJ to discuss running the Workiz sync server action automatically (with small lag) before the payment button fires, so SO data is fresh
type: project
originSessionId: 200f31b4-0c58-455f-b0db-ae50a45f5d8f
---
# Pending Discussion — Run Workiz Sync Before Payment Button

**Raised:** 2026-04-20 (DJ, mid-field)

**The idea:** Before the Payment button in the Field Assistant triggers Phase 6 / invoice flow, auto-run the existing "Sync with Workiz" server action against that SO so the Odoo data (tech assignment, amounts, any Workiz-side edits) is guaranteed fresh. A slight lag / brief spinner may be needed to let the sync complete before the invoice step kicks off.

**Why it matters:** Today's Jose Merelies case (SO 17113, 2026-04-20) hit the Phase 6 tech gate — no tech assigned on the SO, Workiz had none either. DJ had to manually assign tech in Workiz, sync the SO, then re-invoice. An auto-sync before payment would have caught the blank-tech state (and potentially fixed it if Workiz was updated on his phone before tapping Payment), or at least failed with a clearer message before an invoice was already created.

**Open questions for the discussion:**
- Where does the sync hook in — Render app side (before calling the Odoo payment endpoint) or Odoo side (as a pre-step inside Phase 6 / server action)?
- How much lag is acceptable? Workiz API calls can 429; need to rate-limit.
- Do we always sync, or only when the SO hasn't been synced in the last N minutes?
- What do we do if sync fails? Block the payment, or warn and proceed?

**How to apply:** When DJ says "let's talk about that sync thing" or similar, open this discussion. Don't build until we decide the where/how. Related memory: `project_phase6_tech_gate.md`.
