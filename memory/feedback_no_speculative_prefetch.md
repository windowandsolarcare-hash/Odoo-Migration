---
name: feedback_no_speculative_prefetch
description: "★ STANDING DESIGN RULE (DJ 2026-09-25, schedule + generally): NEVER speculatively prefetch data in preparation for a POSSIBLE tap. Load ONLY when DJ opens/expands the thing (lazy-load-on-open / on-expand / on-tab-tap). Cache-first (paint last-known instantly + bg-refresh) is the FALLBACK only for a section whose on-demand wait is unacceptable — never a blanket prefetch. Pre-warm ONLY first-paint essentials, not secondary on-demand sections. AND: audit what already exists before building — don't rebuild lazy/cache logic that's already there."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-25T18:57:03.099Z
---

# No speculative prefetch — load on open/expand; cache-first only as a fallback

**DJ directive, 2026-09-25** (locked during the ~9s schedule-open fix; applies generally). The default is **lazy**, not eager:

1. **NEVER speculatively prefetch** in preparation for a possible tap. Load a section's data ONLY when DJ actually opens/expands/taps it (lazy-load-on-open, on-expand, on-tab-tap).
2. **Cache-first is the FALLBACK, not the default.** If — and only if — the on-demand wait on a given section bothers DJ (his impatience threshold), THEN make that section cache-first: paint the last-known value instantly + background-refresh. Not before, and not as a blanket prefetch of everything.
3. **Pre-warm ONLY the first-paint essentials** — the handful of calls the default view needs to render on open. Do NOT pre-warm secondary/collapsed/on-demand sections (that's speculative prefetch by another name, and it grows the per-instance Odoo baseline).
4. **AUDIT before building.** Much of the lazy/cache-first machinery may already exist — read-only audit what's there vs the gaps, and close ONLY the gaps; don't rebuild working lazy/cache logic.

## Concrete applications (schedule-open, 2026-09-25)
- 90-day skipped-reschedule reach: KEEP the reach (DJ uses 90d when he looks), but it's a COLLAPSED section → fire its server call ONLY on EXPAND, never on schedule-open. (This is why the answer to "trim the 90d?" was "no — lazy-load-on-expand instead.")
- Calendar-tab ranges (5-week / 3-month calendar_jobs, offers/in_window): load on the calendar-TAB tap only, not on the default schedule open.
- First-paint essentials (today's calendar + scheduled_sos + sched/states) are the only things prewarmed / fetched on open.

## How to apply
When designing ANY screen with sections/tabs/heavy reads: default every non-first-paint section to lazy-load-on-open. Reach for cache-first only where DJ says the wait is unacceptable. Reach for pre-warm only for the first-paint essentials. Ties to [[feedback_hud_cards_live_not_inbox]] (live-derived, not stored) and the SWR/throttle work ([[project_broad_except_defeats_global_503_handler]]). MIRROR to Odoo-Migration/memory/.
