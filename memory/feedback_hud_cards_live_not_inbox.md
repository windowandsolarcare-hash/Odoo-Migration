---
name: feedback_hud_cards_live_not_inbox
description: "★ DJ design principle (2026-09-11): HUD/status cards must be LIVE-DERIVED from current data on every render (a dashboard), NEVER a stored 'inbox' that captures entries and lets them go stale. A done/rescheduled job must fall out on its own because the live query no longer returns it — don't rely on a clear-on-event. Root of the maint 'next service' stale-card bug."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-11T14:49:53.162Z
---

**DJ (2026-09-11), on the maintenance "Next service confirmed" HUD card showing stale rows:** *"it should be a dashboard where it's live data all the time, rather than an inbox where it gets stale."*

**The bug that prompted it:** the maint next-service card listed Jim Leal 9/9 (his job was already `workiz_status='Done'`; real next service was Dec 8) and Bill Winkill 9/11 (his SO had been rescheduled to 9/14). Both lingered with stale info because the card was a **stored list** (captured entries persist until explicitly cleared).

**Why:** a stored-inbox card inevitably drifts from reality — completed jobs, rescheduled jobs, cancelled jobs all keep showing with stale dates/status. DJ repeatedly wants surfaces that are **always-live / never-stale** (same principle as [[project_idea_board]] "decaying dashboard, NOT an inbox" and [[project_cheryl_workspace_hud_pattern]] "ALWAYS-live/never-stale HUD").

**How to apply — build feed/HUD/status cards LIVE-DERIVED, not inbox-stored:**
- **Compute the list from current Odoo state on every render** — e.g. the maint next-service card = query the *current* upcoming, not-yet-Done maintenance jobs with their *live* `date_order`. A job that goes `workiz_status='Done'` or gets rescheduled/cancelled then simply isn't in the query anymore → self-corrects, zero cleanup needed.
- **Persist only the STATUS, not the list.** Stored state that genuinely must survive (customer confirmed = wsc.maint.confirmed, sent-flags, snooze/dismiss) is **layered onto** the live-derived rows by joining on the SO/id — never the source of which rows exist.
- **Don't lean on "clear-on-event" as the primary correctness mechanism** (clear-on-Done, clear-on-reschedule). It's a patch on the inbox model and every missed event = a stale card. Live-derive so staleness is impossible by construction; clear-on-event becomes unnecessary.

Applies to the maint comms cards, and to any feed/HUD card going forward. Reduces bugs (no drift) AND aligns with the fleet's "verify by live content, not a cached snapshot" habit.
