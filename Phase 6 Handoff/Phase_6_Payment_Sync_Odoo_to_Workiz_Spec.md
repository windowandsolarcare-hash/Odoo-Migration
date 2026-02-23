# Phase 6: Payment Sync (Odoo → Workiz) — Implementation Spec

**Purpose:** Single spec for “record payment in Odoo → sync to Workiz → mark job Done.”  
**Date:** February 2026

---

## 1. Agreed User Flow (Manual, No Change)

1. Create invoice from SO (if not already created).
2. **Draft** → review/edit (e.g. add line) → **Confirm** (manual).
3. **Pay** (top button) → enter Journal, Method, Amount, Date, Memo → **Submit**.
4. Invoice shows **Paid**.
5. **Trigger:** After payment is recorded (invoice Paid), run Phase 6 sync.

---

## 2. What Phase 6 Must Do

| Step | Action | Notes |
|------|--------|------|
| 1 | **Trigger** when invoice becomes Paid (or payment posted + reconciled). | See §5 below. |
| 2 | Get **job UUID** for this invoice. | Invoice → Sale Order → `x_studio_x_studio_workiz_uuid`. |
| 3 | Get payment data from Odoo. | Amount, payment type, memo/reference, payment date. |
| 4 | **Add payment in Workiz** | `POST /job/addPayment/{UUID}/` (see §4). |
| 5 | **Mark job Done in Workiz** | `POST /job/update/` with `Status: "Done"` (and correct SubStatus). |
| 6 | Workiz status change runs existing automations (Phase 4, Phase 5, etc.). | No Phase 6 change needed. |

---

## 3. Data to Send to Workiz

| Workiz need | Odoo source | Notes |
|-------------|-------------|--------|
| **Amount** | Payment amount (or invoice amount paid) | Dollar amount. |
| **Payment type** | Odoo payment method | Map to Workiz: **check** / **cash** / **credit**. |
| **Confirmation / reference** | Payment **Memo** or **Reference** | What user enters in Pay wizard or on payment. |
| **Paid-on date** | Payment **Date** in Odoo | The date user records payment (e.g. today). |
| **Job identifier** | Job **UUID** | From SO `x_studio_x_studio_workiz_uuid`. |

**Payment type mapping (Odoo → Workiz):**

- Odoo “Check” / “Checks” → Workiz `type`: **check**
- Odoo “Cash” / “Manual” (if used for cash) → **cash**
- Odoo “Credit” / “Manual” (if used for card) → **credit**  
Exact Odoo method names to confirm in your DB; Workiz expects one of: `cash`, `credit`, `check`.

---

## 4. Workiz API (Add Payment + Mark Done)

### 4.1 Add payment

- **Endpoint:** `POST /job/addPayment/{UUID}/`  
  (Replace `{UUID}` with the job UUID; same base URL and auth as existing Workiz calls.)
- **Auth:** Same as other Workiz POSTs: API key in URL path, `auth_secret` in JSON body (first key).
- **Body (addPaymentBody):**  
  - `auth_secret` (required)  
  - `amount` (number)  
  - `type`: `"cash"` | `"credit"` | `"check"`  
  - `date`: paid-on date (format TBD from Workiz docs; likely ISO date or `YYYY-MM-DD`)  
  - Optional: confirmation/reference (field name per Workiz API docs; often `reference` or `confirmationCode`).

Confirm exact field names (e.g. `reference`, `confirmationCode`, `memo`) in [Workiz Developer API](https://developer.workiz.com/) or by testing.

### 4.2 Mark job Done

- **Endpoint:** `POST /job/update/` (already used in Phase 3/4/5).
- **Body:** `auth_secret`, `UUID`, `Status`: `"Done"`, and appropriate `SubStatus` for Done (match what Phase 4 expects so automations run correctly).

---

## 5. Where the Job UUID Comes From (Already Captured)

- **Sales Order** has custom field: `x_studio_x_studio_workiz_uuid` (Workiz job UUID).
- Invoice is created **from** the SO; in Odoo the link is:
  - Invoice has `invoice_origin` = SO name (e.g. `S00123`), and/or
  - There is a relation from invoice to SO (e.g. `sale_order_id` or via `invoice_line_ids` → `sale_line_id` → `order_id`).
- **Phase 6 logic:** Given a paid invoice (or its payment), resolve the related SO, then read `x_studio_x_studio_workiz_uuid`. That is the job UUID for both addPayment and job/update.

So the UUID is captured **early** (when the SO is created from the job in Phase 3) and is available at payment time.

---

## 6. Trigger Options (To Decide)

| Option | How it works | Pros / cons |
|--------|-----------------------------|-------------|
| **A. Odoo automation** | On `account.payment` posted (or `account.move` state = Paid), run server action or automation that calls an external service. | Fires immediately; may need “Call Webhook” or small middleware to call Zapier/script. |
| **B. Odoo → Zapier webhook** | Same as A, but Odoo hits a Zapier “Webhooks by Zapier” catch URL with invoice/payment + job UUID; Zap runs Python. | Keeps logic in Zapier; Odoo only sends payload. |
| **C. Zapier polling** | Zapier (e.g. every 5–15 min) polls Odoo for invoices that became Paid since last run; for each, get SO → UUID, then call Workiz. | No Odoo change; delayed; need a “last synced” marker to avoid duplicates. |

Recommendation: **B** (Odoo automation or scheduled action that POSTs to a Zapier webhook with invoice id + payment details + job UUID) so the trigger is “right after payment” and logic stays in one place (Zapier Python or repo script invoked by Zapier).

---

## 7. One-Paragraph Summary

After you **Confirm** the invoice and use **Pay** → Submit, the invoice is **Paid**. Phase 6 should trigger then and: (1) get the job UUID from the invoice’s SO (`x_studio_x_studio_workiz_uuid`), (2) read from Odoo the payment amount, type (map to check/cash/credit), memo/reference, and date, (3) call Workiz `POST /job/addPayment/{UUID}/` with those, (4) call Workiz `POST /job/update/` to set the job to **Done**, so your existing phases (and Workiz automations) run. The UUID is already on the SO from job creation; the only decision left is how to trigger (Odoo automation → webhook vs Zapier polling).
