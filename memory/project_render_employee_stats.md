---
name: Render app employee stats — future design decision
description: Stats panel is owner-only on mobile; future employee stats will use a toggle button swap approach
type: project
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
Stats panel (`#office-panel`) is intentionally desktop/owner-only. Employees on a phone only see the schedule panel.

**When employee-facing stats are built:**
- Use a toggle button in the field panel header to swap the entire view to a fresh employee stats screen
- Start from a completely blank screen — do NOT modify or reuse the existing `#office-panel`
- This gives full design freedom for employee-appropriate metrics without touching owner layout

**Why:** DJ wants stats like revenue to remain owner-only. Employee stats (e.g. jobs completed, hours logged) may be added later as a separate view.

**How to apply:** When DJ says "add employee stats to the app", implement as option #2 (toggle/swap), not as tabs within the existing office panel.
