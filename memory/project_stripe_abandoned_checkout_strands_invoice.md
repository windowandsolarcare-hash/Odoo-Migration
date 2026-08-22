---
name: project_stripe_abandoned_checkout_strands_invoice
description: "The Stripe \"Charge Card at Door\" / payment-link flow POSTS the invoice before the card is paid. If the customer never completes checkout, you're left with a posted, unpaid invoice that blocks line-item sync and re-invoicing. OPEN ISSUE to fix."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

# Stripe abandoned-checkout leaves a stranded posted invoice (found 2026-06-09)

**What happens:** The Stripe flow in `routers/owner/payments.py`:
- `/api/stripe/payment_link` → creates the invoice from the SO (`sale.advance.payment.inv`, delivered).
- `/api/stripe/create_checkout` → **posts** the invoice (`account.move action_post`) THEN opens the Stripe checkout.
- Payment is only recorded by `/api/stripe/success` IF the customer actually pays.

So if the customer **never completes the card payment**, the invoice is left **posted + unpaid, with no `account.payment`** and no SO chatter. That posted invoice then:
- **Blocks the Sync button** — server action 955 skips line-item sync when any linked invoice is posted ("Line items differ but invoice posted — line sync skipped (safe)").
- Blocks clean re-invoicing until it's cancelled.

**Real incident:** 2026-06-06 ~6:34 PM PT, DJ was *testing Stripe* and used Steve Bluestein's account (job SO 003789 / INV/2026/02446, $515.50), never completed it. It sat posted/unpaid for 3 days and blocked a $0.50 line-item sync. **Fixed 2026-06-09** by draft→cancel of the invoice (no payments attached). Cleanup mechanics: `account.move` `button_draft` then `button_cancel`. ⚠ XML-RPC chokes marshalling the `None` return of these action methods ("cannot marshal None") even though the action runs — use **JSON-RPC** (`/jsonrpc`) for button_draft/button_cancel, or just re-read state after.

**✅ FIXED #1 — 2026-06-09 (commit 8c2e4a0c):** The invoice is now kept in **DRAFT** through `/api/stripe/create_checkout` (removed the `action_post` there) and is **posted only in `/api/stripe/success`** once Stripe confirms `payment_status=='paid'` (post → then `account.payment.register`). So an abandoned checkout now leaves at most a *draft* invoice (deletable, does NOT block sync — action 955 only blocks on POSTED invoices; a draft also doesn't flip SO invoice_status off "to invoice"). `check_payment` still works (returns paid only when posted+paid).

**✅ FIXED #2 — 2026-06-09 (commits 67291194 payments.py + 6f2522fc cron.py):** Abandon now = nothing left + a debug trail.
- **Marker:** `payment_link` sets the draft invoice's `narration='STRIPE_PENDING'` and posts SO chatter `💳 Stripe payment link generated — $X to {customer}...`.
- **Explicit cancel:** `cancel_url` now carries `?invoice_id&so_id`; `/api/stripe/cancel` deletes the draft (if still draft) + posts SO chatter `⚪ Stripe checkout cancelled...`.
- **Success:** clears the `narration` marker when posting, posts SO chatter `✅ Stripe payment received — $X...`.
- **Tab-close (cancel URL never hit):** `_run_daily_sync` (cron.py, ~4:17am) deletes draft `out_invoice` with `narration ilike STRIPE_PENDING` and `create_date` > 36h old (past Stripe's 24h session expiry, so safe). So a closed-tab abandonment clears within a day.
- SO chatter is the **debug trail** DJ asked for (every attempt logged: generated / paid / cancelled).

**STILL OPEN:**
- **#3 test mode** — testing Stripe still creates a real (now draft) invoice on the real customer (it'll auto-clean in ≤36h, but a test path that creates nothing would be cleaner). DJ deferred this. [[project_invoice_qty_delivered_gate]] [[project_field_sync_button_repaint]]
