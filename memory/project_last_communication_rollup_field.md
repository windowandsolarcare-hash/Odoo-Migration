---
name: project_last_communication_rollup_field
description: "res.partner x_last_communication = rollup (max) of all outreach send-date fields, kept current by automation id 10. The SAFE rollup pattern (plain field + automation, NOT a Studio computed field which crashes SaaS)."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce472468-5c4c-4b62-be96-a95fc1c75f1b
---

**`res.partner.x_last_communication`** (date, field id 21336, plain STORED field — `compute: False`) = the **latest of all outreach send-date fields**, so "have we reached out to this customer recently (any channel)?" is a single filterable field. Built 2026-06-26 (DJ's ask: stop every filter checking N separate comm fields).

**Currently rolls up:** `x_studio_last_followup_sent` (re-engagement) + `x_studio_last_reactivation_sent` (reactivation). **To add a new communication channel later:** add its date field to the `comm_fields` list in server action **1365** (automation id **10** "Roll up Last Communication") — ONE edit, every filter that uses x_last_communication auto-benefits.

**TEXT-HISTORY BACKFILL (2026-06-26):** one-time scan of imported [workiz-history] transcripts bumped x_last_communication for **139** customers to a genuine off-program contact date. SAFE logic (don't blindly use "last text" — it's full of routine job comms): count a message ONLY if it's a **customer reply** (speaker not Dan/business = active conversation) OR a **Dan outreach** message (matches outreach phrases: checking in / hope all is well / we last cleaned-serviced / due for a cleaning / bring back the sparkle / peak performance / get you on the schedule / your windows-solar panels are due …), AND it's **>14 days after the last completed job** (skips the post-job payment/thanks/confirmation cluster), AND the customer has **no future job** (next_job_date False — others are excluded from campaigns anyway). Caught the manual OLD-template re-engagement texts DJ sent outside the program (the gap he wanted). Excluded the 2026-06-23 mass "Greetings {name} — below is your next service appointment" confirmation blast. Rollback: `C:\Users\dj\lastcomm_texthistory_ROLLBACK.json`. This is a SNAPSHOT backfill (history up to ~2026-06-25 export); keeping it live going forward = the post-Twilio "log new inbound/outbound texts" piece.

**Never-lower:** the automation includes the CURRENT x_last_communication in the max(), so it's a high-water mark — a later program send with an OLDER date can't wipe a text-history-derived value (tested). 

**Kept current by base.automation id 10** (res.partner, `on_create_or_write`, trigger_field_ids = the source comm fields only [20151, 13842] so writing x_last_communication doesn't re-fire). Server action 1365 code: for each rec, `new_val = max(non-false source dates)`; writes only if changed (recursion guard). Backfilled all 515 contacts that had a send date. Verified: Richard Blee → 2026-06-25; automation fires on write (test passed).

**★ SAFE-PATTERN LESSON (DJ once crashed the instance with Studio + needed support):** that crash was a **computed field** (runs a formula on every READ → can wedge a SaaS instance). NEVER use a Studio computed field for rollups here. The proven pattern (mirrors automation id 2 "Sync Property Visit Date to Parent" → x_studio_last_visit_all_properties) = a **plain stored field written by an automation** on write. All the existing rollup/visit/send fields are plain stored (compute:False), updated by automations/code. Use this pattern for any future rollup.

**★ POST-TWILIO PLAN (DJ's design call 2026-06-26) — maintain at the SEND LAYER, not per-campaign.** Once SMS sending moves off Workiz to DJ's own Twilio ([[project_twilio_port_from_workiz]]), the SINGLE "send SMS" wrapper must stamp `x_last_communication = today` on the recipient on every successful send, AND the inbound Twilio webhook stamps it on every reply. Then ANY future campaign (re-engagement, reactivation, review requests, blasts, one-offs) auto-updates the field for free — campaigns never need to know the field exists. The per-channel fields + rollup automation + text-history backfill were the BRIDGE while Workiz still owns sending; at the Twilio cutover, move the stamp into the send function. RULE: every outbound text must route through that one send function (chokepoint, like the booking reconciler) — no side-channel sends, or the field goes stale. Keep the never-lower guard.

**Consumers:** reactivation candidate filter (`api_reactivation_candidates`, reactivation.py) now uses ONE clause `x_last_communication < cooldown_cutoff OR False` instead of per-channel checks (replaced the 2026-06-26 two-field version). See [[project_reeng_reactivation_closed_loop]], [[project_reengagement_vs_reactivation]]. res.partner ir.model id = 90.
