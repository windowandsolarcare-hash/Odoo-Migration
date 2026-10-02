---
name: project_hud_group_approve_strip
description: "A HUD card rollup/regroup that copies only {id,title,why_now,action,...} into a grouped member row SILENTLY drops draft/on_approve/kind — so an APPROVAL card folded into a group loses its Approve button entirely. Root cause of the paywatch 'paid, approve' money bug (Bruce 17698 / Linda 17464 / Geri 17727 stuck new, no invoice). QC gate: a regroup MUST preserve every member's actionable affordance."
metadata:
  node_type: memory
  type: project
  originSessionId: 8a97aa73-5f27-4f02-a0f6-64f2dd10d242
  modified: 2026-10-02T06:15:45.897Z
---

**Bug (2026-10-01, money-touching):** after the 2026-09-28 HUD-declutter change folded every `source=='billing'` card into one "Money" group, the paywatch "paid — record" approval cards had NO reachable Approve button. DJ literally couldn't approve → Bruce 17698 / Linda 17464 / Geri 17727 sat `new` with no invoice and jobs open; the "awaiting response" card also never cleared (its clear runs inside the approve flow that could never fire).

**Root cause (two layers, both from the regroup):**
1. SERVER `feed._group_hud_cards` folded a paywatch card (`id='paywatch:<so>'`, `kind='approval'`, `source='billing'`, with Approve in `draft.on_approve → POST /owner/api/paywatch/record`) into the Money group, but the grouped member row copied ONLY `{id,title,why_now,action,urgency,queued,queued_label}` — **dropping `draft`/`on_approve`/`kind`/`dollars`.**
2. CLIENT `v2_hud.html groupSummaryHtml` rendered each grouped member as a bare navigate link — no Approve, no `doApprove`. (The non-grouped `card()` renderer DID render Approve.)
The `/owner/api/paywatch/record` endpoint itself was fully intact and runs the FULL canonical flow (overpayment tip → `_execute_payment` → invoice/mark-Done/next-visit → `settle()` → delete card); it was simply never reachable once grouped.

**Fix shipped (option B, in the 2026-10-01 7-file deploy, commit 86170dab):** in the Money group ONLY, carry `kind/draft/on_approve/dollars` into member rows and render an inline `✅ Approve` wired to the EXISTING `doApprove`; group-A (navigate-only) rows stay navigate-only (double-gated). `/paywatch/record` unchanged.

**QC GATE (add to any rollup/regroup review):** a card rollup/regroup that drops `draft`/`on_approve` from an approval member silently removes its Approve action. **A regroup MUST preserve every member's actionable affordance** — for every grouped member that had `on_approve`, assert the grouped render still reaches that endpoint, OR exclude approval-kind cards from grouping entirely.

Related: [[feedback_reuse_function_follow_full_logic]], [[feedback_hud_cards_live_not_inbox]].
