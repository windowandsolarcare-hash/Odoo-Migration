---
name: feedback_root_cause_not_just_instance
description: "★ When handling ANY issue, don't just fix the one occurrence — dig into WHY it happened and whether it will recur, then fix the SYSTEMIC root cause. A fixable problem means it will happen again unless the cause is addressed."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 90c41229-811c-4085-801e-7475f63f81b9
  modified: 2026-09-27T21:16:36.418Z
---

DJ (2026-09-27): *"When I ask you to handle something, think beyond the exact occurrence. Think how it happened, because the fact that it needs fixing means it's going to happen again unless we dig deeper to find out why it happened."*

**The rule:** every "handle/fix X" request has two halves, and the fix is not done until BOTH are:
1. **Fix the immediate instance** (the one customer / job / record in front of you).
2. **Root-cause it** — ask *why did this happen?*, decide *is it systemic / will it recur?*, and **route or fix the underlying cause** so it can't happen to the next one.

**Why:** the fact that something NEEDED fixing is proof the system produced a bad state — so it will keep producing it until the cause is removed. A patched symptom that leaves the cause intact guarantees the problem returns (and DJ keeps hand-catching the same class of bug). Fixing the system is what makes the effort actually pay off.

**How to apply:** on any fix, before calling it done, answer out loud: *"Why did this happen? Is it a one-off or a class? What stops the next occurrence?"* If it's a class, surface/route the systemic fix (to Lead/owner) alongside the instance patch — and say clearly which half is the one-off and which half closes the recurrence (don't let a manual one-off be mistaken for the systemic fix). Good examples this session: the missing "✅ Confirmed" timeline entry (patched Bruce/Kay AND routed the set_confirmation systemic fix), the gate-code snapshot (hand-wrote it AND routed the editable-field + snapshot-sync fix), the confirm flags cleared by an "unknown clearer" (re-set them AND flagged the clearer-hunt). Ties to [[feedback_proactive_inefficiency_capture]], [[feedback_operator_followup_verify]], [[feedback_reuse_function_follow_full_logic]].
