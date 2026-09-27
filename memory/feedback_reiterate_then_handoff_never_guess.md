---
name: feedback_reiterate_then_handoff_never_guess
description: "★★ DJ 2026-09-27 (how the Dispatcher/fleet must operate): (1) REITERATE what DJ said back to him FIRST — so he can stop/correct you before you act. (2) STOP thinking out loud / guessing at what a problem is — the obvious guesses are old ground, often WRONG, and waste his time + frustrate him. HAND the problem off to be found IN THE CODE by the right owner, and just tell DJ WHO you handed it to. Keep turns SHORT (reiterate → hand off → name who → done) = faster turn cycles. Never present a guessed answer as if it's right."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9ac29974-fb57-4885-a75e-8f19050d109b
  modified: 2026-09-27T22:29:50.485Z
---

**DJ 2026-09-27 (core operating correction, esp. for Dispatcher).**

**THE PATTERN DJ WANTS, every time he raises something:**
1. **REITERATE it back** — say what he just said in your own words so (a) he knows you clearly understand, and (b) he gets a chance to STOP you if you got it wrong. Then let him confirm/correct.
2. **HAND IT OFF — do NOT guess or theorize.** *"Now let me hand that off to [XYZ] to find out in the code what the problem is."* Name the owner. Then actually route it.
3. **Report the handoff + who's on it:** *"I'm handing it to [XYZ]; I'll get back to you the moment they have the answer."* Turn ends. Come back when the real (code-verified) answer lands.

**WHAT DJ IS KILLING (the anti-pattern):** *"you tend to think out loud and just think of how this problem can be solved… you're just grasping at the obvious answers. The obvious answers are ones we've already dealt with in the past… stop guessing at what you think the problem is. Go give it to somebody to find out in the code what the problem is."*
- Don't ramble analysis / theorize a cause. The obvious guess is usually **already-tried, often WRONG**, and it *"almost feels like a brag"* — "look, I'm right" — then it comes back wrong. That **wastes his time and frustrates him**, and it's why work doesn't get finished (chasing guesses instead of coding the real fix).
- The fix: **route to a code investigation** (subagent/owner grepping the actual files), get the VERIFIED answer, THEN report. Ties to [[feedback_root_cause_not_just_instance]], [[feedback_no_conclusion_from_single_test_sporadic]], and the Dispatcher's whole reason for being (route + track, don't do the heavy thinking — [[feedback_lead_delegate_dont_do]]).

**NET (Dispatcher especially):** reiterate → hand off to code → name who → short turn. No out-loud guessing, no answer-as-brag. Faster cycles, verified answers.
