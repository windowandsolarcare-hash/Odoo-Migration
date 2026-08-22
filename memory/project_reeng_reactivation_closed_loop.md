---
name: project_reeng_reactivation_closed_loop
description: "The closed-loop lifecycle for re-engagement + reactivation: Launch=snooze (don't die), send recorded on customer, and the on-SO-confirm Odoo automation that closes the task/lead when they book."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce472468-5c4c-4b62-be96-a95fc1c75f1b
---

DJ's "full circle" so a re-engagement/reactivation never dies AND never double-contacts after they book. Built 2026-06-25.

**1. SEND IS RECORDED (already existed):** `/api/followup/launch` posts "📨 Text sent" to the customer chatter + writes `x_studio_last_followup_sent = today` (re-engagement; 45-day cooldown anchor). The 🔍 Check (My Day editor + reeng_review page) now surfaces "📨 Last re-engagement text sent: {date}" from that field so DJ references it without digging.

**2. LAUNCH NO LONGER KILLS THE TASK:** the My Day editor's `tkLaunchSend` used to call `/api/myday/done` after sending → task died → a non-responder was lost forever. Changed to **`/api/myday/snooze {days:60}`** — task stays open, cycles back in ~2 months if they never booked. (Skip = snooze 7 days; Launch = snooze 60 days; neither marks done. See [[project_reeng_launch_review_page]].) reengage.py auto-pilot + the standalone reeng_review.html still markdone — align them later if needed.

**3. CLOSE-ON-BOOKING (the keystone) — Odoo automation `base.automation` id=9 / server action id=1364.** Trigger = `on_state_set` on sale.order, `trg_selection_field_id=2123` (state → 'sale' = CONFIRMED). DJ's key insight: re-engagement/reactivation trigger jobs sync into Odoo as **DRAFT** SOs and never confirm, so confirming is the natural gate — only a REAL booking (DJ sets date/tech/line items → confirm) fires it; no JobType gating needed. On confirm, for that customer (commercial partner + child properties, company_id==1):
- open `project.task` (name 'Re-engagement:', state 01_in_progress) → `1_done`
- open `crm.lead` (name ilike 'Reactivation Campaign', stage not in [4 Won, 6 Lost]) → stage **4 (Won)** [just mark Won, leave Workiz alone — DJ's call]
- posts a reconcile note on the SO chatter.
Code source-of-truth: `1_Production_Code/reconcile_on_confirm.py` (Odoo-Migration). **Two-step rule: edit BOTH that file AND SA 1364.** crm.lead reactivation campaigns = named "Reactivation Campaign - {name} - {date}", partner_id=customer, stage 5="Attempt 1 - Sent"; CRM stages: 1 New/2 Qualified/3 Proposition/**4 Won**/5 Attempt 1-Sent/**6 Lost**. sale.order model_id=670, state selection ids: draft=2121/sent=2122/sale=2123/cancel=2124. **TESTED 2026-06-25** w/ throwaway data: draft did NOT fire, confirm closed task+lead. ✅

**4. REACTIVATION CANDIDATES now exclude the recently RE-ENGAGED (2026-06-26).** `api_reactivation_candidates` (reactivation.py L40 domain) only checked `x_studio_last_reactivation_sent` vs the 12-mo cooldown — it ignored re-engagement sends, so a customer we just re-engaged still showed as a reactivation candidate (Richard Blee: re-engaged 2026-06-25 but reactivation date 2019 → wrongly listed). Added the same OR-cooldown clause on **`x_studio_last_followup_sent`** (the re-engagement send-date field — DJ's "last time we communicated"). Now a candidate must be cold on BOTH reactivation AND re-engagement within the cooldown window. Verified Richard dropped off (82 candidates). Both send-date fields are the "did we reach out?" signal; no single unified "last communicated" field exists — use both.

**Responder path full circle:** customer replies → DJ books (New Order or any path) → SO confirms → automation closes the open re-eng task + reactivation lead → the new job's normal Phase-5 cycle creates the next ~6-month follow-up. Non-responder: task re-surfaces in 2 months for another attempt. **POST-WORKIZ:** when Workiz leaves (delayed by number-port kickback), this stays Odoo-native and gets simpler. See [[project_reengagement_vs_reactivation]], [[project_reeng_duedate_audit_and_declutter]].
