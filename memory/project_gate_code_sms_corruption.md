---
name: project_gate_code_sms_corruption
description: "One-off data fix — a property's master gate-code field held a reactivation SMS; how the customer-brain Gate Code field is sourced and how to sweep for this."
metadata: 
  node_type: memory
  type: project
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

**2026-06-24:** DJ flagged the Customers-tab (customer brain) property card showing the full reactivation SMS text in the **"Gate Code"** row for 348 Casper Dr.

**The display is correct — the data was bad.** The customer-brain card is built by `GET /owner/api/customer_jobs` (in `dashboard.py`, ~L6779) which maps property fields: `('x_studio_x_gate_code', 'Gate Code')`, pricing/frequency/type-of-service/alternating/service-area, etc. So "Gate Code" faithfully renders `res.partner.x_studio_x_gate_code`. Property **#25408** (348 Casper Dr, parent = Dennis Gladu #23388) had the 546-char reactivation SMS sitting in that field.

**Scope check (do this before assuming systemic):** read all 904 Property records' `x_studio_x_gate_code`; only **1** was actually corrupted. 13 others are >25 chars but **legitimate** gate notes ("Front gate code is 0064 open", "Look up Pearson on directory"). So it was a one-off, not systemic. Also checked the customer's SOs — none had the SMS in `x_studio_x_gate_snapshot` or `x_studio_manual_sms_override`, so the field-Sync rollup (SA 955, which copies SO gate snapshot → property gate code) would NOT re-corrupt it. Cleared #25408's gate code to `False`.

**Root cause = unknown one-off** — nothing in the Render code writes the SMS to a gate field (only `new_job.py` writes `x_studio_x_gate_code`, legitimately from the gate_code input). Likely a one-time reactivation server-action/Zapier glitch or a manual paste long ago.

**Why:** so a future "gate code looks wrong" report is diagnosed as data, not a display bug. **How to apply:** customer-brain Gate Code = `res.partner.x_studio_x_gate_code`. To sweep: read all Property records, flag gate codes that contain `opt out` / `Window & Solar Care` / `schedule` (SMS tells) — those are corrupt; long-but-plain ones are real notes. XML-RPC gotchas this session: domain must be passed with the right bracket depth (`execute_kw(...,'search_read',[domain],{'fields':...})` where domain=`[['f','=',v]]`); Odoo 19 Domain rejects explicit `'&'` prefix in some shapes — use implicit-AND list; `write` = `execute_kw(...,'write',[[ids],vals])` (vals INSIDE args, positional). Run Odoo scripts from a clean dir (NOT C:\Users\dj — local `calendar.py` shadows stdlib `imaplib`/`calendar`).
