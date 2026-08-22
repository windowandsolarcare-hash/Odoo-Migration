---
name: project_wscsnooze_shared_module
description: "WSCSnooze = the ONE shared snooze/move sheet (static/owner/v2_snooze.js): move-mode for My Day tasks + until-mode (2026-07-26) for hide-until-a-time (HUD feed). Capacity-aware Days-with-room. NEVER build a page-local snooze sheet."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T18:00:35.406Z
---

**2026-07-26 — UNTIL-MODE added (DJ's call: ONE snooze UI app-wide, after catching a page-local sheet in v2_hud).** `WSCSnooze.open({id,name,hours},{mode:'until',onPick:fn(iso)})` = hide-until-a-TIME variant: quick picks In 1 hour / This evening 6 PM / Tomorrow 7 AM + the same capacity Days-with-room + pick-a-date (day picks resolve to 7 AM local → UTC iso). The host page does its own POST inside onPick (v2_hud acks `/owner/api/feed/ack {op:'snooze',until:iso}`). Move-mode callers below untouched (opts.mode defaults to 'move'). **NEVER build a page-local snooze sheet again.**

**2026-07-25 (DJ: "anywhere we deal with my day tasks this should replace any old move logic").** After building the capacity-aware move menu inline on the calendar day-sheet, DJ wanted it EVERYWHERE My Day tasks are moved, as ONE shared thing (not N copies).

**Module: `static/owner/v2_snooze.js` → `window.WSCSnooze`.** Self-contained (injects its own bottom-sheet + CSS on first use, CSP-safe, theme-aware via `var(--brand)` etc. with hex fallbacks; z-index 9000 to sit above host sheets). API:
```
WSCSnooze.open(
  {id, source, date, hours, name},      // the item; source 'task'|'activity'; hours→capacity fit (default 0.5)
  {onMoved: fn, accessCode: AC}          // refresh callback + optional code
);
WSCSnooze.close();
```
Menu = **Quick** (Tomorrow/In 3 days/Next week) + **Days with room (fits Nh)** + **Pick a date**. Reuses backend ONLY: `GET /owner/api/goals/next_slots?duration=&after=&count=4&span=30` (capacity days) and moves via `POST /owner/api/myday/snooze {id,source,days}` (relative) / `POST /owner/api/myday/bulk-date {ids:[{id,source}],date}` (exact; handles task+activity). **Auth:** only sends `X-Access-Code` header when `accessCode` is passed — calendar/activities pass their `AC`; **v2_myday auths by COOKIE and passes none** (sending an empty header could be rejected, so the module omits it when AC is falsy).

**Rolled out to the 3 genuine My-Day-task move surfaces (each old move logic removed):**
- **v2_calendar.html** (day-sheet ☀️ My Day rows) — removed the inline openSnz/snz-bg/CSS I'd just added; `actsnooze` handler now calls `WSCSnooze.open(..., {accessCode:AC, onMoved:onTaskMoved})`. commit f45bd78.
- **v2_myday.html** — replaced the row ⏰ (was `snoozeIt(idx,1)`), the ⋯-menu's 1/3/7-day items, and the editor's "Snooze 1 day" — all now `openMove(it)` → `WSCSnooze.open(..., {onMoved:boot})`. Deleted dead `snoozeIt`/`menuSnooze`. Left the "⏭ Back in a week" quick-action + Add-to-schedule/Pin (not generic move logic). commit d8c493a.
- **v2_activities.html** — replaced the `+1/+3/+7/+30` chip row + `detailSnooze` (which used `/api/todos/snooze`) with one "⏰ Move / snooze…" button → `detailMove()` → `WSCSnooze.open(..., {accessCode:AC, onMoved})`. commit e951ce1.

**Deliberately NOT touched (different concept, not My Day tasks):** v2_field "Reschedule" = Workiz JOB / schedule-block move; v2_customers/outreach/waiting/inbox/home "snooze" = outreach CADENCE for leads (already uses its own shared `WSCPark` sheet); v2_command myday/blocks = schedule blocks.

**Verified live on all 3:** module loads, menu opens on a real item, `next_slots` returns real capacity days (e.g. Sun 1h / Mon 0.5h / Tue 2h / Wed 6h), sheet fits viewport. Move endpoints are byte-identical to what these pages already called, so the write path was proven — did not mutate real to-dos in testing. **To add elsewhere:** include `<script src="/static/owner/v2_snooze.js"></script>` and call `WSCSnooze.open`. See [[project_calendar_daysheet_snooze]], [[project_workhours_capacity_model]], [[feedback_reuse_canonical_endpoint]], [[project_capacity_overview_screen]].
