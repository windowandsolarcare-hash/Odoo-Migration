---
name: feedback_cheryl_app_fix_not_add
description: "DJ 2026-09-09 — PAUSE new features on the Cheryl app; FIX + clean up what's already there. No new tiles until existing ones work or are removed."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-09T21:34:03.224Z
---

DJ 2026-09-09: **"Yes, pause new features and fix what Cheryl has."** (Ruled after Cheryl walked the app herself.)

**Why:** Cheryl (the actual user) walked her app and hit: (1) her **Plan showing SAMPLE/seed data, not her real data** (the real-data call is failing for her cheryl-role → the page falls back to the sample); (2) **"multiple interfaces"** — she faces 3+ front doors (the artifact launcher, the /cheryl/ home, the FAB) and **most tiles are dead** (coming-soon block + /owner tiles she's blocked from), so she concludes the app is broken and stops trying. A home screen where most tiles don't work teaches the user the app is broken. Verification gap exposed: the fleet confirmed deploys by byte-count/greps while the app served fake data to its real user — **nobody's check covered "does a REAL user see REAL data."**

**How to apply (standing until DJ lifts it):**
- **NO new tiles/features on the Cheryl app** — not until existing ones either WORK or are removed. (Memory + Meeting Recorder are already built + QC'd, so they stay; the rule is: stop ADDING.)
- **Fix backlog (fix-what's-there):** (a) her Plan must show her REAL data (fix the failing /cheryl/api/view/plan call for cheryl-role — QC it AS cheryl, not as owner); (b) **consolidate to ONE clear front door** + remove/grey the dead tiles (kill the "multiple interfaces" confusion); (c) her **login is weak** (first name + birth month/day) on an app exposing job/schedule/money data — change it.
- **★ QC RULE that falls out:** for any cheryl-facing surface, verify AS cheryl-role that a REAL user sees REAL data — byte-count/grep/deploy-confirm is NOT enough. (Extends [[feedback_odoo_verify_content_not_status]] + the Auditor user-walk rule [[feedback_auditor_user_perspective_gapfinder]].)
- The "end every reply with the full link table" habit may be compounding the multiple-interfaces confusion — DJ's call to lift.

Related: [[project_cheryl_home_groups]], [[project_cheryl_fab_launcher]], [[feedback_never_send_dj_to_odoo]] (a dead tile is the same class of "the UI failed the user").
