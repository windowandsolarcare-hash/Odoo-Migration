---
name: project_employee_referral_program
description: "Employee referral program — client text, incentive structure, full blast architecture with frontend picker"
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## Employee Referral Program

**Status:** Fully designed, NOT YET BUILT (2026-05-28)
**Prerequisite:** Zapier → Render migration must happen first ([[project_zapier_to_render_migration]])

---

## Incentive Structure

- $250 total credit toward future services (discounts, not cash)
- First service after hire: up to $150 off
- Second service: $100 off
- Capped at actual job cost per visit
- Only pays out if referred person is hired and sticks

---

## Referral Text Message (from Dan)

> Hey [Name], it's Dan from Window & Solar Care. I'm looking to bring someone on to help with residential window cleaning here in the Coachella Valley. If you know anyone reliable who might be interested, send them my way — if I hire them, I'll give you up to $250 toward your future services as a thank you. Feel free to pass along my number. Thanks!

---

## Sending Architecture

**One-number concept:** SMS must go through Workiz phone number. No direct Twilio or other sender.

**Flow:**
1. DJ opens frontend picker, selects which clients to include (checkboxes)
2. Render loads referral message into Workiz job field for each selected job
3. Render sets `blast.active = "referral"` flag + initializes tracking map
4. Render loops through selected jobs, flips SubStatus to "Referral Employee" (new SubStatus to create in Workiz)
5. Workiz automation fires → sends SMS from Workiz number
6. 2–3 second delay between flips; pause 15 seconds every 30 jobs (Workiz rate limit ~30 calls)
7. After all flips: loop back through snapshot, restore each job to original SubStatus
8. Webhooks come back → tracked against map → flag clears when all accounted for

**Workiz setup required:**
- Create "Referral Employee" SubStatus in Workiz
- Create Workiz automation: when SubStatus = "Referral Employee" → send SMS (the message field)

---

## Blast Flag System (permanent infrastructure — reusable for future blasts)

Stored in Odoo `ir.config_parameter`:
- `blast.active` — blast type name e.g. `"referral"`, `"promotion"`, or `"false"` when idle
- `blast.expected` — total webhooks expected (jobs × 2)
- `blast.received` — running counter of webhooks received during blast
- `blast.snapshot` — JSON map of all jobs: `[{"uuid": "...", "original_substatus": "Scheduled", "got_flip": false, "got_restore": false, "message_verified": null}]`

**Webhook handler behavior during blast:**
- Match incoming webhook UUID to snapshot map
- If new SubStatus = "Referral Employee" → mark `got_flip = true`
- If new SubStatus = original value → mark `got_restore = true`
- Compare message field in payload against sent message → log mismatch as warning (non-blocking). Note: test first whether Workiz truncates long text fields — if so, compare first N characters only
- Increment `blast.received` counter
- When all jobs have both `got_flip` and `got_restore` → clear flag, generate report

**End-of-blast report:**
- Jobs completed cleanly
- Jobs missing one or both webhooks
- Jobs with message mismatch warnings

**Timeout safety net:** After 30 minutes, Render auto-clears the flag regardless. Any incomplete jobs are flagged in the report for manual follow-up.

**Normal operations:** Flag reads `"false"` → webhook handler bypasses blast logic entirely in milliseconds. Zero impact on day-to-day.

---

## Frontend Picker (to build in Render app)

DJ does not want to blast all clients — needs to pick and choose per send.

**UI:**
- Page in Render owner app (e.g. `/owner/blast` or inside a marketing section)
- Loads all active non-DNC contacts from Odoo
- Checkbox list — client name, last service date, phone number visible
- Select all / deselect all toggle
- Preview of the message at the top
- "Send to selected (N)" button
- Confirmation step before firing

**How to apply:** Build frontend picker + blast endpoint together as one feature. Picker sends selected UUIDs to Render blast endpoint. Blast endpoint runs the full flow above.
