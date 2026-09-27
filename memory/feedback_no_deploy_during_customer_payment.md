---
name: feedback_no_deploy_during_customer_payment
description: "★ RETIRED 2026-09-27 (DJ): the pre-deploy PAYMENT-WINDOW hold is ELIMINATED — moot under numInstances=2 ROLLING deploys (one instance serves while the other restarts → no full-down window → in-flight payments aren't dropped). Only deploy gate now = Lead QC. Do NOT re-apply a deploy-timing payment check. Money-WRITE gates (DRY/review-then-fire/confirm-before-send) are a DIFFERENT concern and STAY."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-27T23:18:44.928Z
---

**★ RETIRED 2026-09-27 — do not apply this rule anymore.** DJ killed the pre-deploy payment-window deploy-hold. **Why it's moot:** it existed because a single-instance Render redeploy took the app fully down ~60-90s, so an in-flight customer Pay fetch could land in that window and fail. With **numInstances=2 rolling deploys**, one instance keeps serving while the other restarts — there is no full-down window, so in-flight payments aren't dropped. DJ's words: it was "the door that never opens," and the 2nd instance makes its whole premise moot.

**What this changes:** the ONLY deploy gate is **Lead QC**. Do NOT hold deploys for "a customer might be mid-payment," and do NOT re-derive that rule from the old Bob Lis incident below.

**★ Distinction — what did NOT change (still fully in force):** this retirement drops only the deploy-*TIMING* check. Every gate that guards an actual money/customer **WRITE stays** — DEFAULT-DRY on money mutations, review-then-fire (Credit RUNS the charge), HUD confirm-before-send, payment recording via Operator+app not raw. Those are about not firing an action unreviewed — a different concern from deploy timing. See [[feedback_reuse_function_follow_full_logic]], [[feedback_no_inventing_customer_lines_hud_confirm]].

**Historical (why the rule once existed — 2026-09-18, Bob Lis, $200 solar):** right after an authz fix, Bob tapped Pay and got "Network error." Not a code bug — root cause was 4 deploys in ~5 min, each a ~60-90s single-instance restart; his fetch hit one. That single-instance restart-window risk is what rolling deploys eliminate. Related: [[feedback_deploy_cadence]] (continuous deploy), [[feedback_regression_guard_pushes]].
