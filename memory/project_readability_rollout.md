---
name: project_readability_rollout
description: "App-wide readability rollout (DJ 2026-06-24): bigger fonts + darker day gray + add day mode to dark-only screens, across ALL ~30 owner screens. Multi-batch, DJ spot-checks."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**DJ wants the Command Center readability treatment applied to EVERY owner screen** (he said "the new job, the activities, the my day, everything everything"). Standing requirement — see [[feedback_field_readability_sunlight]] (limited vision + bright sun).

## The catch
Owner screens do NOT share CSS — each `.html` has its own `<style>` block + its own color tokens. Only `common.css` is shared, and just by the Command Center (`schedule_hub.html`) + reports_demo. So this is a per-screen sweep, ~30 files. `field.html` alone = 318KB / 315 font-size rules (the risky giant).

## DJ's decisions (2026-06-24)
1. **Add a day mode** to the 3 dark-only screens too: **My Day, New Order, Maintenance** (single dark `:root`, no light theme → unreadable in sun even after font bump). Screens WITH a day theme already: field, activities, calendar, hr, planner, stale_sos, etc.
2. **Pace = batch through; DJ spot-checks** (not one-at-a-time sign-off).

## ★ NEW MINIMUM FONT FLOOR — RAISE TO 16px (DJ 2026-06-29)
DJ: the 15px floor from the 06-24 sweep is STILL too small — he wants the **minimum default font size bigger**. New standard = **16px floor** for body/content text (was 15). So the sweep recipe floor moves up one notch (see below) and `common.css` content classes go 15→16. Reason = limited vision + bright sun ([[feedback_field_readability_sunlight]]) — bias BIGGER, this is a recurring "still too small" so don't be timid. Card customer name (`.r-title`) 18→19, amount (`.r-amt`) 16→17 to keep the hierarchy above the 16 floor. Started on Command Center (`common.css` + `schedule_hub.html`) as the calibration sample — CONFIRM the size with DJ, then re-sweep the other ~30 screens to the 16 floor. NOTE: small UPPERCASE labels (day headers, section heads) can stay ~14px — "minimum" = readable content text, not micro-labels.

## The recipe (consistent target = matches common.css bump)
- **2026-06-29 floor is now 16:** `…→16` — i.e. raise `8/9/10/11/12/13/14/15 → 16` for content text (was the 15 floor); leave uppercase micro-labels at ~14 and anything 16px+ alone.
- **Font size — raise the floor (layout-safe, single-pass callback so values don't cascade):** `8→12, 10→13, 11→13, 12→14, 13→14, 14→15`; leave 15px+ alone. regex `font-size(\s*:\s*)(\d+)px`. Verify diff has ZERO non-font-size lines before pushing.
- **Contrast:** darken the day-mode muted/dim token where too light (e.g. activities/calendar light `--text-muted:#64748b` → ~`#3d4f5a`). field light token already dark (#1f2937 = fine). Color-only = no layout risk.
- **common.css (already done, commit ced89a0):** body 14→15, titles 16→18, amounts/buttons→16, day `--dim #5b6f7c→#3d4f5a`.

## Progress
- ✅ Command Center / common.css (commits ced89a0, f4121f1)
- ✅ **Batch 1 font-size sweep** (2026-06-24): new_order (e261e74), new_job (fe78d39), activities (916f561), myday (b524ede)
- ✅ **Batch 2 long-tail font sweep** (2026-06-24): 24 files swept + verified font-size-only + pushed — analytics, booking_requests, calendar, deleted_jobs, hemet, hiring, hr, inbox, index, index_classic, jd_window_cleaning_assistant, notes, planner, pre_deposit, quick, quote, reactivation, reengage, reference, shift_review, stale_sos, submitted_jobs, timeclock, weekly_reports. (Render coalesces rapid pushes into one deploy.)
- ✅ **field.html** (commit 9b64653): already mostly 15/16px — only 47 bumps (46× 14→15 + 1× 12→14, no ≤11px). Fetched LIVE, swept, diff verified font-size-only, pushed; live stayed 5866 lines (no regression). **FONT SWEEP NOW COMPLETE ACROSS ALL OWNER SCREENS.**
- ✅ **My Day day mode** (commit 9df47ca): grafted hr.html pattern — `<html data-theme="dark">`, no-flash head script (`myday_theme` localStorage), `html[data-theme=dark|light]` token blocks, ☀️/🌙 `#tog` button in header, applyTheme/toggleTheme JS. Light tokens: primary #0077b3, bg #eef2f7, card #fff, dim #475d6b. **Reusable recipe for adding day mode to any dark-only screen.**
- ✅ **New Order day mode** (commit 7a04903, key `neworder_theme`) + **Maintenance day mode** (commit 3116b74, key `maint_theme`, kept plum #5e4766 header in both). All 3 dark-only screens now have the ☀️/🌙 toggle. No more dark-only owner screens.
- 🔴 TODO: darken day-mode gray on activities/calendar (#64748b) + any other light-token-too-light screen
- ✅ **Dashboard (owner hub) = `static/owner/index.html`** (served by dashboard.py `/` route L7410) — already font-swept in Batch 2; it HAS a day mode but via a **`body.light` class** (line 26), NOT `data-theme` (so a `data-theme` grep finds nothing — don't conclude it's dark-only). index_classic.html same.
- ✅ **9px gap fix** (commits 724bb4d/82dbb87/e71a8a8/871929/bb9d3b9): the font map skipped 9px → tiny labels survived on index, index_classic, booking_requests, maintenance, planner (.ql-app-label, .slot .sg badge, .hm-lbl). Bumped 9→12. NOTE: map covers 8,10,11,12,13,14 — **9 (and <8) were the blind spots**; if re-running the sweep add 9→12.
- ✅ **dashboard.py inline customer pages** (commit 0c910ec): DJ said bump those too. 9 surgical edits to the payment/tip page + navigate snippet + email body — font floor-raise (12/13/14→14/15) + darkened grays (#aaa/#888/#bbb/#94a3b8 → #777/#5b6b7f/#6b7785). Line count unchanged (12484), compiles. The OK/error confirmation pages (L5050/5094) already use default 16px — left as-is.
- 🔴 Optional follow-up: titles bump per page (recipe leaves 15px+ alone; if DJ wants bigger headers, do targeted per-page title bump)

GH push gotcha that bit twice this session: NEVER `open(p,'wb').write(open(p,'rb').read()...)` in one expression — wb truncates before the read → empty file. Read into a var first, write separately. Always guard `[ ${#b64} -lt 1000 ] && abort`. See [[feedback_gh_push_empty_file_guard]], [[project_owner_page_nostore_stale]].
