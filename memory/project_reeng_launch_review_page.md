---
name: project_reeng_launch_review_page
description: Re-engagement Launch Review page /owner/reeng-review — pre-text safety check (last-comm flag) + inline Launch/Skip. Plus the new-router deploy-ordering lesson.
metadata: 
  node_type: memory
  type: project
  originSessionId: ce472468-5c4c-4b62-be96-a95fc1c75f1b
---

**Re-engagement Launch Review = `/owner/reeng-review`** (built 2026-06-25, DJ's ask). Pre-flight check before texting a re-engagement customer: never re-engage without knowing the LAST communication. Lists all open "Re-engagement:" project.tasks; for each, compares the customer's last text (imported `[workiz-history]` transcript) against their last visit (last Done job date) and flags:
- 🔴 **customer-replied** since visit (the dangerous one — "told me to hold off", opt-out, deceased, already-talking)
- ❓ **no-history** (can't verify — check phone)
- 🟡 **you-messaged** since visit (you already reached out)
- 🟢 **auto-only** (only an automated re-engage text went out)
- ✅ **clean** (no contact since visit)
Also shows 🛑 if contact is phone_blacklisted / Do-Not-Contact. Tap a row → reads the post-visit messages inline + 📜 Full history (reuses `/owner/api/text_history`) + **🚀 Launch** (preview→edit→send) + **⏭ Skip**. Launch/Skip REUSE the existing reactivation.py endpoints (same safety gates): `POST /api/followup/preview {partner_id}`→`{sms_text,cooldown_warning}`, `POST /api/followup/launch {partner_id,sms_text}` (re-validates STOP/DNC/45-day cooldown server-side), `POST /api/followup/markdone {activity_id:task_id,source:'task'}` (state→1_done). Sorted due-now first, then worst flag.

**PRIMARY SURFACE = My Day editor 🔍 button (2026-06-25, DJ preferred this over the bulk page).** The bulk `/owner/reeng-review` list pulls all 150 transcripts at once → ~2 min spinner (kept but secondary/slow). The fast path: `GET /api/reeng_review/one?partner_id=` = single-customer check, ~2.5s. Wired into the **My Day task editor** (`static/owner/myday.html`): a **🔍 Check last contact** button sits in `tkLaunchWrap` just above 🚀 Launch (shown for Follow-up / "Re-engagement:" tasks with a customer); `tkCheckContact()` calls the one-endpoint and renders the flag banner + post-visit message bubbles inline (`tkRenderCheck`/`TKFLAG`), so DJ reviews THEN launches in the same sheet. Same flag logic as the list. ALSO FIXED in that editor: the sticky header (`#tkTitle`) showed generic "Reminder" so the task name vanished when the body scrolled / keyboard up — now `openTask` sets `tkTitle` to the task name + `tkName` oninput keeps it synced, and `.fu-title` truncates with ellipsis (DJ screenshot 2026-06-25). See [[project_foldable_mobile_modal_fixes]].

**My Day editor re-engagement block actions (final 2026-06-25):** 🔍 Check last contact → flag + post-visit texts inline; 📜 View full text chain (`tkFullHistory` → modal `#thm`, fetches `/api/text_history`); 🚀 Launch; **⏭ Skip for now = SNOOZE 7 days, NOT mark-done** (`tkSkipReeng` → `/api/myday/snooze {days:7}`, no confirm for fast triage). DJ explicitly wanted Skip to DEFER (task stays open, cycles back in a week to decide together), not complete. `/api/myday/snooze` re-bases overdue → today+N (myday.py L478). Interval is a one-line change if DJ wants different/spread-out.

**Files:** `routers/owner/reeng_review.py` (router + `GET /api/reeng_review/list` bulk + `GET /api/reeng_review/one?partner_id=` fast single), `static/owner/reeng_review.html` (common.css, WSCTheme day mode), `static/owner/myday.html` (the 🔍 button), registered in main.py. Detector/flag logic ports `scratchpad/reeng_lastcomm.py`. **Catch (real, 2026-06-25):** Sharon Odenbaugh family replied "passed away 4-22-2026"; LD Fowler replied "Stop" — both must NOT be re-engaged. Exactly why DJ wanted this. NOTE: an OLDER re-engage template exists in history ("Hi X, I hope all is well. It's Window & Solar Care. We last serviced your home on…") distinct from current `_build_followup_sms` ([[project_reengagement_sms_template_detector]]) — so the auto-only detector under-counts old sends (they show as you-messaged). Fine for this purpose.

**DEPLOY LESSONS (both burned me this build):**
1. **New router → push the router FILE first, main.py LAST.** I pushed main.py (which `import`s the new router) before the router file's push succeeded → `ImportError: cannot import name 'reeng_review' from 'routers.owner'` → whole app crash-looped (deploy `update_failed`, served stale). Order matters because each push triggers a deploy. Verify the route 200s after the final deploy via `mcp__render__list_deploys` + curl; check boot errors with `mcp__render__list_logs` (select workspace tea-d78l9fqdbo4c7388n9og first).
2. **gh contents push via heredoc-JSON intermittently 400s "Problems parsing JSON"** (hit on the 2 new files; main.py via same heredoc worked — non-deterministic). RELIABLE FIX = build the payload with **Python json.dumps**: read file bytes → `.replace(b'\r\n',b'\n')` → base64 → `json.dump({'message','content','branch',('sha' if existing)})` → `gh api ... --input`. Same as the reference.py note. Prefer this for any new-file push.
