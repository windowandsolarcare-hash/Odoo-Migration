---
name: project_calendly_offzapier_odoo_webhook
description: TABLED plan — move Calendly booking off Zapier to an Odoo webhook (capture-first) for reliability. Includes Calendly webhook retry facts.
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

UN-TABLED + STARTED 2026-06-14. Part of the bigger "drop Zapier" goal ([[project_zapier_to_render_migration]]).

## BUILD STATE (2026-06-14)
**Capture webhook = DONE + smoke-tested.** Calendly webhooks have NO dashboard URL field — they're API-only via a Personal Access Token (DJ confirmed paid plan; Integrations & apps → API and webhooks = Connected). Odoo webhook mechanism = `base.automation` rule (`trigger=on_webhook`, model res.partner/90) + a code `ir.actions.server`; URL = `/web/hook/<uuid>`; inside the action `payload` is the dict, `json`/`requests`/`datetime`(module) available, returns `{"status":"ok"}` 200 automatically.
- **Capture SA = 1340 "Calendly Booking Capture"; automation rule = 8; URL = `https://window-solar-care.odoo.com/web/hook/d319ad6f-571b-402a-b706-4646f3aa89a7`.** Source in repo `1_Production_Code/odoo_calendly_capture_webhook.py` (commit a535a55).
- **Queue scheme (ir.config_parameter):** `calendly.queue` = JSON list of unprocessed keys; `calendly.raw.<key>` = raw payload JSON per booking; `calendly.done.<key>` = processed flag; `calendly.last_raw`/`calendly.last_received` = debug. Dedupe key = Calendly invitee `uri` (fallback email|start_time). Smoke test passed (HTTP 200, queued, deduped) then cleared.
- Existing webhooks for reference: STOP handler SA 954 / automation 6 (`/web/hook/f64d0bc1…`); "Test Hook" SA 944 / automation 5. Creating an automation via API: create ir.actions.server (state=code, usage='ir_actions_server', model_id=90) then base.automation (trigger on_webhook, action_server_ids=[[6,0,[sa_id]]], record_getter="model.env['res.partner'].browse(1)", log_webhook_calls=True).

**NEXT (blocked on DJ's PAT):** (1) DJ generates a Calendly Personal Access Token (Integrations & apps → API and webhooks → Settings → generate). (2) I register a webhook subscription to the capture URL via `POST https://api.calendly.com/webhook_subscriptions` (events `invitee.created`; org/user URI from `/users/me`) — keep ALONGSIDE Zapier, don't remove yet. (3) One real test booking → capture real payload from `calendly.raw.*`. (4) Build the **processor cron** (ir.cron, ~1 min): read `calendly.queue`, port the 6-phase booking from `zapier_calendly_booking_FLATTENED_FINAL.py` to NATIVE env ORM (Workiz still via requests), idempotent (remove from queue + set done flag), attempt cap. (5) Test end-to-end, THEN remove the Zapier Calendly subscription.
**PORTING NOTES (from inspecting zapier_calendly_booking_FLATTENED_FINAL.py, 1193 lines):** 6 phases — 3A property/contact by `street ilike` (strip SPC/APT/unit) → parent_id contact; 3B crm.lead w/ `x_workiz_graveyard_uuid`; 3C **update existing graveyard Workiz job in place** (date/time UTC→PT, job type, notes) — does NOT create; 3D action_set_won; 3E create+confirm SO (write date_order back), update property gate/pricing; 3D2 create activity card + set_tasks_to_planned; 3F write contact email. Raw Calendly `invitee.created` is NESTED (`payload.scheduled_event.start_time`, `payload.email`, `payload.name`, `payload.questions_and_answers[]`) — must map Q&A by question text (needs real sample). `re` module may NOT be available in server action — rewrite address-strip as plain string ops or verify.

**DJ's concern:** Calendly booking reliability — "it only fires once." 

**CALENDLY WEBHOOK FACTS (verified 2026-06-14):** Calendly DOES retry — up to ~25 attempts with exponential backoff over **24 hours** on any non-2xx response OR timeout. Needs a **2xx within 10 seconds**. After 24h of failed delivery it **DISABLES the webhook subscription** → all future bookings silently stop until re-enabled. Source: Calendly community FAQ "how does a webhook become disabled".

**WHY IT'S EFFECTIVELY "FIRES ONCE" TODAY:** Zapier's catch-hook returns 2xx to Calendly INSTANTLY (before the zap processes). So Calendly marks it delivered and never retries — if the zap's downstream processing then fails, the booking is LOST. So the current Zapier path is the real single-point-of-failure.

**ROBUST TARGET DESIGN:** Calendly → **Odoo webhook directly** (Odoo always up; already does webhooks — STOP handler at `window-solar-care.odoo.com/web/hook/…`). Pattern = **durably STORE the raw payload first → return 2xx → process from the store** (idempotent, re-runnable). Then Calendly's retries guarantee capture, and a processing hiccup can't lose the booking. Guardrails: keep the webhook action <10s (store + return; heavy work via cron/queue), make processing idempotent (retries must not double-book/double-SO), and MONITOR for subscription disablement.

**SETUP NEEDS:** (1) Calendly webhook config access (Professional+/API) to point the booking event at the Odoo URL — confirm whether managed via Calendly API/dashboard vs the Zapier Calendly trigger today. (2) A real Calendly payload sample so the Odoo parser matches.

**RELATION TO SHARED CLONER:** this reinforces putting the canonical Workiz cloner in Odoo (always up), not Render — see [[project_shared_workiz_clone]] (Odoo server action CAN return data to a JSON-RPC caller via `action = {...}` — verified). Calendly itself UPDATES the graveyard job (doesn't create), so the cloner is more relevant to Phase 5 / reactivation-create / duplicate; but the Odoo-native direction is the same.
