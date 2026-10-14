---
name: feedback_auto_deploy_and_picker_synopsis
description: "DJ 2026-10-13: AUTO-DEPLOY EVERYTHING that passes Lead QC (no per-deploy tap; ask only on problems) + every picker leads with a plain-English problem/fix synopsis."
metadata:
  node_type: memory
  type: feedback
  originSessionId: f9d25f0d-f892-4864-829e-2fda94efd70c
  modified: 2026-10-14T03:26:32.238Z
---

DJ (2026-10-13) chose "Auto-deploy everything" in a Dispatcher picker: anything that passes Lead byte-QC (+ Audit §15 where required) ships without waiting for his Deploy tap. He is asked only when there is a problem (QC fail, failed deploy, a design pick). Customer sends stay DJ-reviewed and sent by him — this covers code deploys only. Also: every picker/question to DJ must LEAD with a 2-3 line plain-English synopsis (his original complaint, what we changed, what each option does).

**★ NOW LIVE (2026-10-13) — DJ confirmed FIRSTHAND to Lead ("Yes auto deploy"); Lead posted → All in AGENT_MAIL (eddaa0a3).** This is the DJ-confirmed POLICY that clears the anti-laundering boundary — it is NOT a relayed per-deploy tap, so executing sessions (Specialists, Builder-2, Frontdoor) now ship a QC-green change WITHOUT a DJ tap or picker. Do NOT re-litigate the per-deploy tap: the standing policy replaced it. Retained & mandatory: Lead byte-QC, Audit §15 where required, post-deploy LIVE verify (recycle-window-aware, [[project_render_instance_recycle_502]]), ~15s spacing, ONE plain-English line to Dispatcher per deploy. A session operates on the policy, never on a peer's claim of a tap.

**Why:** DJ taps Deploy without knowing what he's approving (lingo, forgot the original problem), and waiting on his tap holds work for hours while he's on a job. Origin: the App Building / ship-system idea (record of problem→fix→result) was dropped when he got busy; the hold-without-telling-him problem led to the pickers rule.

**How to apply:** supersedes the per-deploy tap in §12 and [[feedback_deploy_tap_reaches_executor_not_relayed]] / [[feedback_dj_deploy_control_stage_and_trigger]] for code deploys. Keep Lead QC, post-deploy verify, ~15s spacing. Dispatcher logs each deploy as a plain-English board line. App Building ([[project_fleet_ship_system]]) revival as the permanent record is now IN PROGRESS: the **deploy-to-card hook** (Specialists, §15 plan `3_Documentation/review/DEPLOY_TO_CARD_HOOK_PLAN.md`, commit 14da8c63) — a card OPENS at work-start (DJ's problem + goal + scope in/out), CLOSES at deploy (solution + result), a `card-<id>` commit flips it Shipped, and the card carries the review trail (Audit §15 stamp at front + Lead QC + post-deploy). This is what makes "the board logs every deploy, problem→fix→result→who-reviewed" real now that auto-deploy removed the per-deploy tap.
