---
name: project_gate_code_on_schedule
description: "Command Center schedule cards show the gate code (🔑) per job; calendar_jobs now returns gate. Gate values are free-text."
metadata:
  node_type: memory
  type: project
  originSessionId: 6f63b0d4-dd6a-4dd1-aac3-e533a99e7526
---

**Built 2026-07-09 (DJ: "Gate Code should appear on this schedule list").** The Command Center schedule (`static/owner/schedule_hub.html`, served at `/owner/command-center`) now shows a 🔑 gate line on each job card that has one.

## Backend
`/api/calendar_jobs` (the LIVE copy is in **dashboard.py**, not calendar.py — dashboard router registers first in main.py so it wins the duplicate route) now returns `gate` per job:
`gate = so['x_studio_x_gate_snapshot'] or property['x_studio_x_gate_code'] or ''` — the SO's gate snapshot first, else the shipping (property) partner's master gate code. Added `x_studio_x_gate_snapshot` to the SO field list and `x_studio_x_gate_code` to the ship_map read.

## Frontend
schedule_hub.html adds `extra:(j.gate?('🔑 '+j.gate):'')` to the on-schedule rows (`loadOn`) AND the calendar-day rows. WSCKit.renderResult (report_kit.js) renders `r.extra` as a `<div class="r-extra">` line.

## ★ Gotcha — gate values are FREE TEXT, often already containing "Gate"
The stored gate values are full phrases, e.g. `"Gate code is 1159"`, `"00909 enter"`, `"testing 1234"` — NOT bare codes. So prefix with just the 🔑 icon, NOT "🔑 Gate ", or you get "Gate Gate code is 1159". Verified: Barry Matthews (SO 004713) shows "🔑 Gate code is 1159"; Chuck McBride (no gate) shows nothing. 258 SOs have a gate_snapshot, 80 partners have a gate_code.
