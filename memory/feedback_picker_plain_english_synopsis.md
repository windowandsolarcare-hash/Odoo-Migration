---
name: feedback_picker_plain_english_synopsis
description: Every AskUserQuestion picker to DJ opens with a 2-3 line plain-English synopsis before the options.
metadata:
  node_type: memory
  type: feedback
  originSessionId: 967bdc43-a1eb-42bc-82ff-a4be56f896dc
  modified: 2026-10-14T03:09:37.604Z
---

Effective 2026-10-13 (DJ rule, relayed via Lead): **every deploy/decision picker fired to DJ must LEAD with a 2–3 line plain-English synopsis** — (1) what he asked for, (2) what we changed, (3) what each tap does — BEFORE the options. No jargon, no codes, no commit SHAs, no endpoint names in the synopsis.

**Why:** DJ reads pickers on a phone, often in the field; terse lingo/branch-name pickers make him guess what he's approving. Plain English up front = he taps with full understanding.

**How to apply:** In the AskUserQuestion `question` field, write the synopsis as plain sentences first, then the options. Keep technical detail (SHAs, file paths, route names) for my own reply/ledger, not the picker DJ sees. Ties to [[feedback_plain_english_no_jargon_dropchatter]], [[feedback_spoken_friendly_responses]], [[feedback_dj_deploy_control_stage_and_trigger]].

Related (same relay, NOT yet active): DJ is moving toward AUTO-DEPLOY — code passing Lead byte-QC + Audit §15 ships without a Deploy tap, asked only on a problem (keep Lead QC, post-deploy verify, ~15s spacing; customer sends stay DJ-reviewed). **Pending — current DJ-tap authorization path stands until Lead confirms the flip firsthand with DJ.** Do not ship code without a tap until that confirmation lands.
