---
name: project_careers_hud_applicants
description: "Careers-page job applicants → HUD 'New applications' card. Locked Odoo IDs (Web, 2026-10-08): utm.source 'Careers Page' = id 15; new applicants land stage_id=1 ('New', seq 0, the initial/unreviewed stage); hr.job id 1 = 'Window Cleaner' (the ONLY hr.job). HUD section filters /api/hiring/applicants on source_id==15 AND stage_id==1."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-08T21:24:55.520Z
---

**Feature (DJ-directed via Web, routed by Lead 2026-10-08):** surface NEW careers-page applications in DJ's HUD "Hiring" area as a "📥 New applications (N)" section, above the interview-roster card, live-derived, DJ-only, self-hide at 0.

**Data path (reuse, don't raw-query):** `GET /api/hiring/applicants?passed=false` in `routers/owner/hiring.py` (`list_applicants` ~ln 331, formatted by `_fmt_applicant` ~ln 290). Returns a JSON ARRAY (not {ok}-wrapped) of `{id,name,email,phone,stage_id,stage_label,priority,source_id,source_label,notes_raw,created,active,indeed_url,has_audio}`. Domain = `job_id==1` AND `active==true`.

**Locked Odoo IDs (Web verified + created 2026-10-08):**
- **utm.source "Careers Page" = id 15.** Web's `/careers` Odoo-website form stamps `source_id=15` on every careers applicant. **HUD filters `source_id==15`** (robust — survives a job rename). Add `15:'Careers Page'` to `hiring.py` `SOURCE_LABELS` (today: 14 Indeed, 4 Facebook, 9 Craigslist, 10 Referral — no website source existed before 15).
- **stage_id=1 = "New"** (sequence 0, the initial/unreviewed stage). Careers applicants land here. HUD treats `stage_id==1` as "new/unreviewed" so a row auto-drops off the glance once DJ advances it. (NB: `hiring.py` `STAGE_LABELS` labels stage 1 as 'Reviewing' — same stage, app's own label. Stages: 1 Reviewing/New, 2 Phone Screen, 3 Interview, 5 Offer, 6 Hired.)
- **hr.job id 1 = "Window Cleaner"** — the ONLY hr.job; the applicants pipeline filters on it. Web sets `job_id=1`.
- Resume attaches as `ir.attachment` on the hr.applicant (form flips `website_form_access=True`). Surface a resume link in the drill-in when present.

**Build sequencing (Lead-approved):** this section lives in the SAME `static/owner/v2_hud.html` as the interview-roster "Hiring" card (see [[feedback_hud_cards_live_not_inbox]]). Keep them SEPARATE deploys — do NOT bundle (bundling holds the green card hostage to this Web-source blocker + un-QC'd code). Order: (1) interview-roster card deploys first (after Portal's `portal/hiring-confirm-polish` merges, on DJ "deploy"); (2) THIS applications section = **deploy #2, built ON the live/deployed v2_hud.html** — RE-FETCH live at build time, apply the diff, re-diff before push; never build on the green-staged copy ([[feedback_staged_mirror_stale_base_refetch]]).

**Perf:** applicants fetch hits Odoo (`hr.applicant` search_read) each HUD render vs the roster's PG read — one extra Odoo call per render, acceptable since HUD_EXTRAS-gated (DJ-only, not Cheryl) and rides loadFeed. Only if Odoo 429 shows: add a short server-side cache (~30–60s) on the applicants list — do NOT pre-optimize (Lead).

**Ownership:** Web owns the intake (Odoo-website form → native hr.applicant; no app endpoint/CORS). Specialists owns the HUD section + the `SOURCE_LABELS` add. Verify end-to-end when Web pings that real careers applicants are landing.
