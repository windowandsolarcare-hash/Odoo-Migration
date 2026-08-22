---
name: project_paywatch_auto_tip
description: "PayWatch \"paid\" card auto-handles tips — when more money lands than the job costs, one Approve adds a Tip line so the invoice matches exactly, records it, marks Done, creates the next maintenance visit. Split shown on the card face."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-14T13:59:43.131Z
---

**DJ's ask (2026-08-13):** when a Zelle/Venmo payment comes in HIGHER than the job total (customer added a tip), the paywatch approval card should show the split and, on Approve, automatically create the tip line + record + close — no floating credit, no manual steps.

**Built (specialist_paywatch.py, commits 314b30d + ff29c60):**
- `_tip_product_id()` — find-or-create a **"Tip"** service product (`default_code='WSC-TIP'`, type service, invoice_policy 'order', no taxes). Booked as a real invoice line = tip is income, not an unapplied credit.
- `api_paywatch_record` (the Approve target): before `_execute_payment`, if `amount - SO.amount_total >= 0.50` AND no posted invoice yet, it **adds a Tip line** for the overage, posts chatter, then records the FULL amount. The freshly-created invoice now equals the amount paid → matches exactly → paid in full → mark Done + `create_next_maintenance_so`. Partial/exact payments unchanged.
- `_submit_card`: reads live SO total, computes the tip, and puts the split **on the bold title face** — `"<name> paid $250 via Zelle · $220 job + $30 tip"` — plus explains what Approve does. Also `delete_item('zelle_engaged:<so_id>')` so posting the paid card clears the stale "is paying — tapped Copy" engagement card (that producer never removed its own card).

**Verified live (Norman Woodel, SO 004652, 2026-08-13):** he Zelle'd $250 on a $220 job. One Approve tap → lines became Windows $115 + Solar $105 + **Tip $30**; INV/2026/02531 = **$250 posted, paid**; job **Done**; next maintenance SO 264947 created for **Nov 11**. Clean, no credit.

**Funds-received thank-you (DJ 2026-08-14, commits paywatch 5fbfb18 / payments 29f2ca4):** watcher-approve now also texts the customer "{first}, Funds Received, thank you!" (matching the field-app manual path the lead added). Dedupe across both Zelle paths = **shared `idem='funds_received:%d' % so_id`** on both `messaging.send` calls (messaging dedupes on idem) — a payment recorded via BOTH paths only texts once. Fires for zelle AND venmo in paywatch. I added the same idem to the lead's `payments.py` funds_received (1 line). Manual path already disarms paywatch via settle(), so both-fire is an edge case; idem is belt-and-suspenders. See [[project_sms_send_paths_quiet_hours]].

**Notes:** the stale-card-clear here is a one-off patch of the exact symptom the HUD live-projection redesign ([[project_command_conf_pills_cached]] era / HUD_REALTIME_BRIEF) fixes wholesale. The zelle_engaged card is created elsewhere (payments.py api_zelle_track) and had no self-clear. Related: [[project_so_activity_breadcrumb]] (the opened/tapped-Copy breadcrumbs), [[project_mark_done_refuses_workiz_uuid]] (paid-in-full closeout).
