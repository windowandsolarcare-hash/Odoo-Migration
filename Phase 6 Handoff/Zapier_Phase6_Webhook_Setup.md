# Phase 6 Zapier: Webhook + Code by Zapier (same pattern as Phase 3, 4, 5)

Same setup as your other Zaps: **Step 1 = Webhooks by Zapier (Catch a Hook)**. **Step 2 = Code by Zapier — Run Python** with **Input Data** and **Code** box.

---

## Zap structure

1. **Trigger: Webhooks by Zapier — Catch a Hook**
   - Use your webhook URL (e.g. `https://hooks.zapier.com/hooks/catch/9761276/uegifni/`).
   - When you POST to this URL with body `{"invoice_id": 123}` (Odoo customer invoice id that was paid), the Zap runs.

2. **Step 2: Code by Zapier — Run Python**
   - **Input Data:** Add one variable and map it from Step 1 (Webhook):
     - **invoice_id** ← map from the Webhook trigger (the request body field `invoice_id`). Same idea as mapping `job_uuid` from the trigger in Phase 3/4.
   - **Code:** Paste the **entire** contents of `2_Modular_Phase3_Components/zapier_phase6_FLATTENED_FINAL.py` into the code box. Credentials are at the top (same as Phase 3/4/5); no extra input_data for credentials.
   - **Output:** The step returns `output` (the dict from `main`: `success`, `error`, or `job_uuid`, `amount`, etc.).

---

## Credentials

Credentials are in the script at the top (ODOO_*, WORKIZ_*), same as Phase 3/4/5. No need to pass them via Input Data.

---

## What the Code step does

1. Reads the invoice in Odoo; if not paid, exits.
2. Gets the sale order from `invoice_origin` and reads `x_studio_x_studio_workiz_uuid` (job UUID).
3. Gets payment amount, date, method, and ref (from payment if available, else from invoice).
4. Maps payment method to Workiz type (cash / credit / check).
5. Calls Workiz `POST /job/addPayment/{UUID}/` with auth_secret, uuid, amount, type, date, reference.
6. Calls Workiz `POST /job/update/` to set the job **Status = Done** (no SubStatus).

**Payment types:** API accepts only `cash`, `credit`, `check`. The script maps Odoo methods to those three and puts the **real method name** (e.g. Zelle, Venmo) in the **reference** field so Workiz has a record (e.g. "Zelle - 12345").

---

## Where to go from here

1. **Create the Zap:** Step 1 = Webhooks by Zapier (Catch a Hook) — your URL. Step 2 = Code by Zapier — Input Data: `invoice_id` from webhook body; Code: paste `zapier_phase6_FLATTENED_FINAL.py` (in `2_Modular_Phase3_Components/`).
2. **Trigger the Zap:** POST to the webhook URL with `{"invoice_id": <odoo_invoice_id>}` when that invoice has been paid (same way you trigger other webhook Zaps).
3. **Add payment methods in Odoo** (Zelle, Venmo, etc.) if you want; the script sends cash/credit/check to Workiz and puts the real method name in the reference field.
4. **Test:** Pay an invoice (SO with Workiz UUID), POST the invoice id to the webhook, confirm in Workiz: payment added, job Done.

**Future test jobs:** `create_test_job_and_test_zelle.py` to create; `cleanup_test_job_workiz.py` with `TEST_JOB_UUID` to cancel (`2_Modular_Phase3_Components/`).
