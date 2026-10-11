---
name: feedback_ready_and_unfinished_ask_picker
description: "When a build is staged + READY, or ANY work won't be finished for whatever reason, bring it to DJ as an AskUserQuestion PICKER (tappable options) — never wait for him to type, never silently stall/skip/decide. Belongs in every role boot pack."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 71d8a955-480c-46cd-92bf-c963ba9d5a16
  modified: 2026-10-11T17:38:02.687Z
---

DJ 2026-10-11 (verbatim intent): he shouldn't have to keep typing "deploy" (or keep guessing whether a session is ready). When a builder's work is **staged + QC-GREEN + ready to ship**, the builder **proactively asks DJ with the `AskUserQuestion` picker** so he just **taps a button** instead of typing. The picker does double duty: (1) it signals "I'm ready for you," and (2) it lets him trigger the action with a tap, not a typed word.

Deploy picker shape (recommended first): **"Deploy now (Recommended)"** · **"Deploy part of it"** (only if it splits sensibly) · **"Park it — don't deploy yet."** Tapping "Deploy now" IS DJ's own deploy trigger — exactly equivalent to him typing "deploy" (a real in-chat user action, not permission laundering; the stage-and-DJ-triggers model [[feedback_dj_deploy_control_stage_and_trigger]] is unchanged — only the trigger UI changes from typed word → tapped button).

**Broader rule (the governing one):** ANYTHING that is **not going to be finished — for whatever reason** (blocked, needs a decision, out of scope, waiting on input, a judgment call, a nice-to-have) — must be **brought to DJ as an AskUserQuestion with options**, asking how he wants to handle it. The three standard options:
- **Continue** — keep going / do the fuller version.
- **Give me the info** — hand DJ what's needed so he can decide/act.
- **Park it** — hold it, don't drop it (parked ≠ dropped; it gets re-surfaced, never silently abandoned).

Never silently stall, skip, defer-with-a-vague-timeframe, or unilaterally decide on DJ's behalf. A tap is nearly free for him; a silent stall or a wrong unilateral call is expensive.

**Why:** DJ is often on a phone in the field. Typing is friction; a button tap is one touch. And he wants a reliable signal that a session is ready for him, plus certainty that nothing unfinished gets quietly dropped.

**How to apply:**
- Ready-to-ship → fire the deploy picker (don't wait to be asked, don't make him type "deploy").
- Any unfinished/blocked/decision item → fire an options picker (Continue / Give info / Park), recommendation first.
- **This belongs in EVERY role's boot pack** — Dispatcher owns propagating it fleet-wide (many live sessions predate this rule and won't have it until re-briefed or rebooted). Relayed to Dispatcher 2026-10-11.

Extends [[feedback_blocked_build_ask_with_options]] (picker + concrete options when I can't/won't continue) and [[feedback_alert_dj_when_input_needed.md]] / [[feedback_escalate_to_dj_sparingly]]. Ties to [[feedback_dj_deploy_control_stage_and_trigger]] and [[feedback_next_not_later_ai_blindspots]] (deferring-with-a-timeframe = never).
