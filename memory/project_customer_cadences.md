---
name: project_customer_cadences
description: "Per-service maintenance cadences for multi-service customers (each service its own interval). Until the cadence-engine ships, hand-correct these customers' next jobs each cycle. DJ 2026-09-06."
metadata: 
  node_type: memory
  type: project
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-06T08:51:56.768Z
---

Some customers run DIFFERENT frequencies for DIFFERENT services, so the single-frequency next-job generator mis-dates them (wrong date + wrong service mix). Until the per-service cadence engine ships ([[project_operator_playbook]] blueprint → Lead 2026-09-06), hand-correct each cycle using the maint set_time endpoint (+ /api/job/lines for the service, + job_type). Anchor dates to CITY_WEEKDAYS.

**Nick Conway** (partner 22986; property 24108 = 76201 Vía Mariposa, Indian Wells; Indian Wells anchor = Wed/Thu):
- Solar Panel Cleaning: every **2 months**.
- Windows Inside & Outside Plus Screens: every **4 months**.
- So: a COMBINATION job (windows + solar) every 4 months, and a SOLAR-ONLY job at the in-between 2-month mark. Fixed 2026-09-06: his Sep-10 combo is correct; his solar was mis-dated Oct 14 (1mo later) → moved to Nov 11 (2mo after the combo, Indian Wells Wed).

**Norman Woodel** (SO context 17563; 3586 Date Palm Trail, Palm Springs; PS anchor = Fri):
- Outside Windows: every **month**.
- Solar Panels: every **3 months**.
- So: every 3rd monthly job = windows + panels; the other two = windows-only. Fixed 2026-09-06: his job was "Combination" monthly → stripped to Outside Windows only ($115), panels only on the every-3rd.

**Engine status:** blueprint accepted, Specialists building (opt-in per customer via wsc.cadence.<partner_id> JSON, last-done derived from history, throwaway-QC by Operator before touching real customers). The actual wsc.cadence config seed is deferred to the engine build (or DJ's explicit OK) — Operator does NOT raw-write it. Related: [[project_operator_playbook]], [[project_lessons_referral_scheduling]].
