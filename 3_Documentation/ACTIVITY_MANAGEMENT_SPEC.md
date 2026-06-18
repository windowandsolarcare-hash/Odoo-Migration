# Activity Management — Canonical Spec
**Status:** living document · **Owner:** DJ Sanders · **Last updated:** 2026-06-17
**Part of:** the comprehensive CRM (see SHARED_MEMORY "★ NORTH STAR"). This is **one pillar** — the action-item / task / follow-up layer. Not the whole CRM.

---

## 1. Purpose
Give DJ a single, phone-friendly **command center** for everything he has to *do* — separate from the *work* (jobs). One model, several views, all tied to the customer. Built on Odoo's `project.task` engine with a friendly Render UI on top (the proven pattern).

## 2. The Model — two entities only
Everything that happens in DJ's day is either a **Job** or an **Action Item**.

### 2a. Job — `sale.order`
Scheduled, paid work for a customer. **Always** has a date/time. Unchanged by this pillar. (Created via Workiz→Phase 3, New Job, online booking, reactivation.)

### 2b. Action Item — `project.task` (`project_id = False`, `user_ids ∋ 2`)
*Everything else DJ needs to do.* One record type, with these attributes:

| Concept | Odoo field | Notes |
|---|---|---|
| **Type** | `x_myday_type` (char, id **20879**) | `'task'` \| `'followup'`. **Reactivation = a Follow-up** (reason, not a separate type). API key = `kind`. |
| Title | `name` | |
| **Due date** (optional) | `date_deadline` (datetime) | Tasks & follow-ups may or may not have one. Carries an exact time. |
| **Customer** (optional) | `partner_id` | The contact (or a property). Powers the circle-back. A follow-up is ~always tied to a person; a task may be. |
| Priority | `x_myday_priority` (id **20869**) | 3 High / 2 Med / 1 Low / 0 None. |
| Categories | `tag_ids` → `project.tags` | Free-form, My-Day-managed subset via param `myday.tags`. |
| Repeat | `x_myday_recur` (char, id **20875**) | daily/weekdays/weekly/biweekly/monthly. On done → spawns next occurrence. |
| **Subtasks** | `child_ids` (native) | NOT yet surfaced in UI — future. |
| Done | `state` | `'1_done'` = done, `'1_canceled'` = cancelled. |

`project.task` model id = **856**. Activities (`mail.activity`) also appear in the action stream today (legacy) and are treated as **Follow-ups** (`kind='followup'`) — Step 4 migrates them onto `project.task`.

## 3. The Views — one data set, several lenses
| View | Where | Shows |
|---|---|---|
| **Now / needs attention** | My Day screen (`/owner/myday`); calendar Undated + Past Due sections | undated + overdue, by priority |
| **Upcoming (advance look)** | Calendar `🔜 Upcoming` (next 21d, day-grouped) | all dated items forward |
| **By customer (circle-back)** | Customer brain (field.html) `☀️ Action Items` | a customer's open tasks + follow-ups |
| **Calendar** | `/owner/calendar` month/day | jobs + dated action items + Google, future & history |
| **By type / priority / category / date** | My Day grouping segments | filter/group the list |
| **Morning digest** | web push 7am | named overdue/High items |

## 4. What's built (2026-06-17)
- **0 ✅ Planner removed** — habits were just tasks; toggle commented out (reversible), data kept.
- **1 ✅ Type field** — `x_myday_type` created + backfilled 203 items (35 task / 168 followup, derived from name). myday.py add/update/list/recur-spawn handle it; output `kind`. myday.html: Type select in Add+Edit, kind chip on cards (✅/📞), **Type grouping** segment.
- **2 ✅ Customer circle-back** — `/api/customer_jobs` (dashboard.py) returns `actions` (open project.task by `partner_id` + mail.activity on the contact/properties, each with `kind`/date/priority). field.html customer brain renders `☀️ Action Items (N)` between property header and Jobs. Display-only.
- **3 ✅ Upcoming advance-look** — calendar.html `🔜 Upcoming` (next 21d). `loadUpcoming()` fetches `/api/calendar_jobs?start=&end=` (range mode, **lives in dashboard.py — calendar.py copy is shadowed**) → `upcomingJobs`, merged with `actsByDate` + gcal. Respects Jobs/My Day toggles; excludes done. Also earlier this session: recurring-to-do projection (`expandRecurring`) + completed-history (done items on past days) on the calendar.

## 5. Step 4 — CONSOLIDATION (the deep cleanup, NOT YET BUILT)
**Goal:** one Action-Item model. Today action items are split across `project.task` AND `mail.activity`, and the reactivation/followup automation auto-creates a noisy mix. Unify onto `project.task` typed `Follow-up`.

### The current mess
- **`mail.activity`** — used as lightweight reminders (Phase 5 "Follow-up" type 15 on SOs; reactivation reminders on contacts). They archive on done; they're a parallel system.
- **Auto `project.task`** — reengage flow creates `Re-engagement: <name>` tasks; followup creates `[Render] Follow-up: <name>`. These dominate the list (157 of ~172 open items are follow-ups, mostly auto).

### Target
- All action reminders = `project.task`, `x_myday_type='followup'`, `partner_id`=the customer, with an optional **reason** (reactivation / re-engagement / general) — likely a tag or a small char field `x_myday_followup_reason`.
- `mail.activity` retired for DJ's action stream (kept only where Odoo natively needs it).

### What this touches (audit before building)
- `reengage.py` — creates the re-engagement project.tasks + reads them (find_due, scan_and_notify).
- `phase5` (zapier) — creates the Follow-up `mail.activity` (type 15) on submitted-job SOs; Phase 4 auto-closes them.
- `reactivation.py` / SA 563 — reactivation campaign + the followup/launch path (markdone archives the mail.activity).
- The calendar + My Day + customer-brain readers already handle both `source='task'` and `source='activity'` — they'll keep working through the migration.

### Migration approach (proposed, confirm before doing)
1. **New creators first** — change anything that creates a follow-up `mail.activity` to create a typed `project.task` Follow-up instead (with partner_id + reason). Verify downstream (markdone, auto-close) still works.
2. **Backfill** — optionally convert existing open `mail.activity` → `project.task` Follow-ups (or let them age out; they're mostly near-term).
3. **Retire** the `mail.activity` path once nothing creates them.
4. **De-noise** — with everything typed + reasoned, the auto reactivation/followup items can be filtered/collapsed in the UI (DJ wanted to "streamline old code into something comprehensive").

### Risk
Medium-high — it's the automation that drives reactivation/followups (real customer texts). Do it incrementally, one creator at a time, verifying the SMS-send path each time. **Don't big-bang it.**

## 6. Future (beyond Step 4)
- **Subtasks UI** — surface `project.task` child_ids (DJ: "tasks may have subtasks").
- **Tap-to-edit from the customer page** (circle-back is display-only now).
- **Follow-up reason** field (reactivation vs general) + a reason filter.
- **From an action → open the customer** (My Day card → field customer brain).

## 7. Field reference (verified 2026-06-17)
`project.task` (model id 856), all `state='manual'` custom fields:
- `x_myday_type` (20879, char) — task|followup
- `x_myday_priority` (20869) — 3/2/1/0
- `x_myday_recur` (20875, char) — daily/weekdays/weekly/biweekly/monthly
- native: `partner_id`, `date_deadline` (datetime), `tag_ids`, `child_ids`, `state`, `sequence`
- registry param `myday.tags` = the tag subset My Day manages.

## 8. Key endpoints
- `/owner/api/myday` (+ /add /update /done /snooze /history /reorder /tags…) — My Day CRUD (myday.py)
- `/owner/api/todos?include_done=1` — calendar's action feed (dashboard.py; returns kind, recur, done)
- `/owner/api/customer_jobs` — returns `actions` for the circle-back (dashboard.py)
- `/owner/api/calendar_jobs?start=&end=` — range jobs for Upcoming (**dashboard.py copy is live; calendar.py shadowed**)
