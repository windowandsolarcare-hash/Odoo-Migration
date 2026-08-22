---
name: project_customer_card_no_gate_code
description: "'NO GATE CODE' shows when a job/property has no gate — on BOTH the Command Center schedule cards (v2_command.html) and the Customer Brain card (v2_customers.html)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-23T06:29:58.093Z
---

## ★ Which screen is "Command Center" / "the customer card" (2026-07-22)
When DJ says **"Command Center"** he means the LIVE page **`static/owner/v2_command.html`** (direct link `https://wsc-field-assistant.onrender.com/static/owner/v2_command.html`, served straight off the `/static` mount in main.py — NO custom route). This is the schedule screen with job cards (name → address → chips → time). **NOT** `schedule_hub.html` (whose memory [[project_gate_code_on_schedule]] said `/owner/command-center`). The **"customer card"** DJ pointed at = these v2_command.html **job cards**. Verified by dropping a temp "Dan Saunders" marker between name and address in `jobCard()` (~L696) — he confirmed seeing it there. First-attempt mistake this session: I edited v2_customers.html (Customer Brain) instead — wrong screen.

## Command Center schedule cards (v2_command.html) — the real target
Two card builders — `loadOn()` (~L667, "On the schedule") and `calDayTap()` (~L935, "Calendar day") — set `extra:(j.gate?('🔑 '+j.gate):'🔑 NO GATE CODE')`. Renderer `jobCard()` shows `r.extra` as `<span class="mchip gate">` only when it starts with 🔑, so keep the 🔑 prefix. `j.gate` from `/api/calendar_jobs` = SO `x_studio_x_gate_snapshot` or property `x_studio_x_gate_code`.

## Customer Brain card (v2_customers.html)
**2026-07-22.** The Customer Brain card (`static/owner/v2_customers.html`, dossier fetched from `/owner/api/customer_jobs`) also ALWAYS shows a **Gate Code** row per property.

## Where
Backend `/owner/api/customer_jobs` in **dashboard.py** (~L7160, the `for f, lbl in PROP_FIELDS` loop). Previously every empty property field was skipped (`if v in (False,'',None): continue`) so a blank gate code made the row vanish. Now special-cased: when `f == 'x_studio_x_gate_code'` and the value is empty, append `{'label':'Gate Code','value':'NO GATE CODE'}` instead of skipping. All OTHER empty fields still hide. Frontend needed no change — `v2_customers.html` renders whatever `p.fields` the endpoint returns as generic label/value rows.

## ★ Do NOT re-hide this row
If a future session "cleans up" the PROP_FIELDS empty-skip, keep the gate-code exception. DJ wants the explicit words so a blank isn't read as "not loaded".

## Source nuance
Reads the PROPERTY master `res.partner.x_studio_x_gate_code` only — NO SO-snapshot fallback (DJ didn't ask for it). So "NO GATE CODE" means the property master field is empty, even if a job's `x_studio_x_gate_snapshot` has one. The [[project_gate_code_on_schedule]] schedule card DOES fall back to the SO snapshot; the customer card does not. Only ~80 property records have a master gate code vs 258 SOs with a snapshot, so most customers will show NO GATE CODE. See [[project_gate_code_sms_corruption]] for how the Gate Code row is sourced.
