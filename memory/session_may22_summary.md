---
name: session-may22-summary
description: "2026-05-22 session: delete_workiz_job tool, commands page overhaul, SO format fix, CLAUDE.md rules rewrite, OwnTracks quiet mode bug"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b173fd1-b5b7-43e3-ba55-7c216343fb45
---

## delete_workiz_job tool — full rebuild
- Now supports 3 paths: by customer name (lists all active jobs, DJ picks), by SO/Workiz number (direct lookup), by UUID (internal fallback)
- SO number normalization: strip S prefix, `zfill(6)` → exact match, ilike fallback
- When customer name given: Claude must list ALL active (non-Done, non-Canceled) SOs and ask DJ to pick — NEVER silently grab most recent
- New `/owner/api/search_so?q=357` endpoint: returns matching SOs with customer name, date, amount — powers live search in commands panel

## ql_panel.js commands page — Jobs tab
- Now has 2 delete cards: "Delete job — by customer" (field:'customer') + "Delete job — by SO / Workiz #" (field:'so_number')
- so_number field type: live autocomplete calls /api/search_so, shows SO name + customer + date + amount
- Create a job card added with customer search

## Odoo SO name format — CONFIRMED
- 6-digit zero-padded numbers, NO prefix: `003575`, `004659`
- Added to CLAUDE.md SYSTEM CONSTANTS table and SHARED_MEMORY.md
- CLAUDE.md Rule 1 expanded: covers format guessing, not just field names

## CLAUDE.md proactive save rules rewrite
- Removed: "every 10 responses" + "when DJ signs off" — count/time based rules don't work for LLMs
- Added: event-triggered only — after API call to verify unknown fact, after discovering new field/behavior, after bug fix revealing non-obvious behavior
- Reason: LLMs have no persistent counter; meta-tasks get squeezed out under task load

## OwnTracks quiet mode bug — FIXED 2026-05-21
- Bug: server was sending `monitoring: -1` (Quiet) on home arrival
- Quiet mode on Android kills ALL events including geofence — clock-out stopped working
- Fix: now sends `monitoring: 1` (Significant) — low battery but geofence still fires
- DJ manually had to set mode back to Significant to break out of stuck state
- See project_owntracks_setup.md for full monitoring mode reference
