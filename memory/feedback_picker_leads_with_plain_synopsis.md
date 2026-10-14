---
name: feedback_picker_leads_with_plain_synopsis
description: "Every picker/question put to DJ must LEAD with a 2-3 line plain-English synopsis BEFORE the options: (1) what DJ originally complained about or asked, in his own words; (2) what we changed to fix it; (3) what happens if he taps each option. No lingo, no codes, no branch/commit jargon."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-14T03:03:20.247Z
---

DJ rule, effective 2026-10-13 (relayed by Dispatcher, all roles). **Why:** DJ said he taps **Deploy without knowing what he's approving** — the pickers were showing options + technical labels (branch names, commit shas, "gateway-retry", "§15") with no plain statement of what the thing even is. A deploy tap IS the authorization ([[feedback_dj_deploy_control_stage_and_trigger]], [[feedback_deploy_tap_reaches_executor_not_relayed]]); if DJ can't tell what he's authorizing from the picker, the authorization is hollow and a wrong tap is our fault, not his.

**The rule — every AskUserQuestion / picker to DJ opens with a 2-3 line plain synopsis, THEN the options:**
1. **What he asked for / complained about** — in HIS words ("cards won't clear when I press the check", "I keep getting that 502 when I confirm Patty"), not our internal name for the fix.
2. **What we changed** to fix it — one plain sentence, no file/branch/commit/§ jargon ("the check now clears the card for good"; "texts auto-retry so the hiccup is invisible").
3. **What each option does if tapped** — "Deploy now = it goes live on your phone in ~2 min"; "Not yet = nothing changes, it waits."

**How to apply:** this is the FIRST thing in the question body, above the options, on every picker — deploy pickers especially, but all of them (design calls, scope calls, blocked-build calls). It extends, does not replace, the existing picker rules: still use the AskUserQuestion picker for blocked/ready/unfinished ([[feedback_ready_and_unfinished_ask_picker]], [[feedback_blocked_build_ask_with_options.md]]), still keep replies plain-spoken and jargon-free ([[feedback_plain_english_no_jargon_dropchatter]], [[feedback_spoken_friendly_responses]]), still carry the tappable link + OVER line. The synopsis is the NEW mandatory lead-in. A picker that jumps straight to options with no plain "here's what this is and what each tap does" now FAILS the bar.

**Related, same date (tracked, NOT yet in force — Dispatcher owns, DJ deciding):** DJ is considering letting VERIFIED deploys go live WITHOUT a tap, asking him only when there's a problem. Dispatcher is putting that to DJ as a picker; nothing changes until DJ answers. If DJ approves it, it materially amends [[feedback_deploy_tap_reaches_executor_not_relayed]] (the tap-is-authorization model) — so that memory must be updated at that point, not before. Also tracked: DJ wants the **App Building / "ship system"** revived as the permanent record of problem→fix→result (Dispatcher scoping with DJ).
