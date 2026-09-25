---
name: feedback_lazy_on_demand_not_prefetch
description: Don't speculatively prefetch data for a possible tap; load only when DJ opens/expands it, and cache-first (last-known instant + bg refresh) only where the on-tap wait is unacceptable
metadata:
  type: feedback
---

DJ's governing UI-data principle (2026-09-25): NEVER load data in preparation for a tap that may or may not happen. Load ONLY when DJ opens/expands the thing. If the on-demand wait bothers him, THEN make that one thing cache-first — paint the last-known copy instantly + refresh in the background while he looks — but don't blanket-prefetch.

**Why:** the schedule open was firing ~12 Odoo calls at once (including a 90-day skipped-reschedule pull he rarely opens, and 5-week/3-month calendar ranges for a tab he hadn't tapped) → ~9s load. DJ: "let's not be loading stuff up that I'm not asking for in preparation of me asking… wait until I ask, then do it. And if I have a problem with the speed, then we'll cache it and give me that at least, and work in the background while I'm looking at the cache."

**How to apply:** collapsed sections (e.g. the 90-day skipped list) fetch on EXPAND, never on parent open. Secondary tabs (calendar ranges, offers) fetch on tab-tap. Pre-warm/SWR is only for the FIRST-paint essentials the user sees immediately, not for speculative secondary data. Cache-first (SWR + localStorage, offline-capable) is the fallback for the few things whose on-tap wait is unacceptable. Before building: AUDIT the existing code — much of this (cache-first, lazy sections) may already exist; close gaps, don't rebuild. See [[feedback_hud_cards_live_not_inbox]].
