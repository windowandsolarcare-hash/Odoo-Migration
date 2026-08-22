---
name: project_myday_save_slow_boot
description: "My Day saves felt slow because edSave calls a full boot() reload (/api/myday = 1.3-2.6s), not the save itself (0.38s). Fixed with optimistic in-place render on edit."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T04:20:05.973Z
---

**2026-07-24 (DJ: "saving tasks takes a long time").** Measured: the save (`/api/myday/update`) is **0.38s** — fast. The slowness is `edSave()` calling **`boot()`** afterward, which re-fetches the ENTIRE My Day via **`/api/myday` = 1.3–2.6s** (many Odoo round-trips: tasks + activities + crm leads + schedule blocks + attachments). So the row didn't update for ~1.5s → felt like a slow save.

**Fix (commit 962a54b, v2_myday.html edSave):** on an EDIT (ED set), optimistically merge the saved `body` fields into the matching `ITEMS` entry and call `render()` (client-side, instant) BEFORE the background `boot()`. The reload still runs to reconcile derived fields (customer name, tag names, checklist counts) — invisibly, since values already match. New-task ADD still relies on boot() (no local row yet) — could get the same treatment if needed.

**Why / how to apply:** the pattern for ANY v2 mutate-then-refresh where the refresh endpoint is heavy — update local state + render immediately, reconcile with the network in the background; don't block the UI on the full reload. The durable win (not done) is slimming `/api/myday` itself (fewer Odoo queries). The Goal Board's capacity strip adds a non-blocking `/api/goals/capacity` (~1.5s) to My Day boot but never blocks the list; the per-day fit check only runs during editing, not on save.
