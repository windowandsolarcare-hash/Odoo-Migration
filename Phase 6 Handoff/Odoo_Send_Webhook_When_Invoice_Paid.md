# Odoo: Send Webhook When Invoice Is Paid (Phase 6)

Use this to have Odoo **POST to your Zapier Catch Hook** when a customer invoice is paid (or when a payment is entered), so the Phase 6 Zap runs automatically.

You can trigger on **Invoice** (account.move) or **Payment** (account.payment). If the Invoice model is hard to find in your UI, use **Payment** (see Option B below).

---

## Option A: Trigger on Invoice (when invoice becomes Paid)

---

## 1. Open Automations

- **Option A:** In the main app switcher (top left), open **Studio** → **Automations** → **New**.
- **Option B:** **Settings** → **Automation** → **Automated Actions** → **Create**.

(If you don’t see **Automations** or **Automated Actions**, you may need the **Automation** or **Studio** app installed.)

---

## 2. Name and model

- **Name:** e.g. `Phase 6: Notify Zapier when invoice paid`
- **Model:** **Invoice** (or **Customer Invoices**).
  - If **Invoice** isn’t in the list: enable **Developer Mode** (Settings → General → Developer Tools → Developer mode), then create/edit the automation again and choose **Invoice** / **account.move**.

---

## 3. Trigger

- **Trigger:** **Values Updated** (or **On create and edit** / **When a record is created or updated**).
- So the automation runs when an invoice record is **saved after a change** (e.g. when payment is registered).

---

## 4. When to run (only for paid customer invoices)

Restrict the automation so it runs **only** when the updated invoice is a **customer invoice** that is **Paid**:

- Find the **Apply on** / **After update** / **Domain** (or **Add condition**) section.
- Add **two** conditions (exact labels depend on your Odoo version):
  1. **Move Type** = **Customer Invoice** (or **out_invoice**).
  2. **Payment Status** = **Paid** (or **paid**).

So: run only when the record is a customer invoice and its payment status is Paid.

---

## 5. Action: Send Webhook Notification

- Click **Add an action** (or **Actions To Do** → **Add**).
- **Action type:** **Send Webhook Notification** (or **Webhook**).
- **URL:** paste your Zapier Catch Hook URL:

  ```
  https://hooks.zapier.com/hooks/catch/9761276/uegifni/
  ```

- **Fields to send:** include the **invoice id** so Zapier can pass it to the Code step as `invoice_id`:
  - Click **Add field** (or **Fields**) and choose **Id** (the record’s database id).
  - If you see a list of fields, select **Id** only; that’s enough for Phase 6.

Odoo will send a **POST** request to that URL with a JSON body containing the chosen fields (e.g. `{"id": 45}`). Zapier will receive it; in your Zap you mapped that value to **invoice_id** in the Code step.

---

## 6. Save and turn on

- Click **Save** (or **Save & Close**).
- Ensure the automation is **active** (toggle or status = Active).

---

## Quick check

1. In Odoo, open a **customer invoice** that comes from a sale order (and that sale order has a Workiz UUID if you want Phase 6 to sync to Workiz).
2. **Confirm** the invoice (Post) if needed, then **register the payment** (e.g. **Pay** → enter payment → Validate).
3. When the invoice shows **Paid**, the automation should run and send the webhook.
4. In **Zapier** → your Phase 6 Zap → **Zap History**, you should see a new run with the invoice id. In **Workiz**, the related job should get the payment and be marked Done.

---

## If the automation doesn’t run

- Confirm **Move Type** = Customer Invoice and **Payment Status** = Paid in the conditions.
- In Odoo, check **Settings** → **Technical** → **Automation** (or **Automated Actions**) and open your rule: confirm it’s **Active** and the trigger/conditions look correct.
- If your Odoo uses **Studio**, the same rule may appear under **Studio** → **Automations**; edit there if needed.

---

## Option B: Trigger on Payment (when a payment is entered/confirmed)

Use this if the **Invoice** model is hard to find in the Model list. The **Payment** model is usually easy to find (e.g. **Payment** or **account.payment**).

1. **Automation Rules** → **New**.
2. **Name:** e.g. `Phase 6: Notify Zapier when payment recorded`
3. **Model:** **Payment** (or **Payments** / **account.payment** — the one that represents a single payment you register against an invoice).
4. **Trigger:** **Values updated** or **On create and edit** (so the rule runs when a payment is saved).
5. **Apply on:** **State** = **Paid** (or **Posted** / **Sent** — use the value your Odoo uses for “confirmed” payments; e.g. Draft / In Process / **Paid** → use **Paid**).  
   This limits the action to payments that are in the Paid (or Posted) state. In practice this gives the right set of records (e.g. only the payments that were just paid), whereas “State is set to Paid” as the trigger alone can run on *all* paid records (e.g. 15) every time.
6. **Optional — Before Update Domain:** To run only when a payment *becomes* Paid (not when an already-Paid record is edited), set **Before Update Domain** to e.g. **State** is not **Paid** (or State = Draft). Then the webhook runs only on the transition into Paid.
7. **Action:** **Send Webhook Notification**
   - **URL:** `https://hooks.zapier.com/hooks/catch/9761276/uegifni/`
   - **Fields:** **Id** (the payment id).
8. **Save** and leave the automation **Active**.

**In Zapier:** In the Code step’s **Input Data**, map the webhook body field that contains the payment id to **`id`** or **`payment_id`** (e.g. `{{trigger.id}}`). The Phase 6 code accepts either `invoice_id` or `payment_id`/`id`; when it receives a payment id, it looks up the payment’s reconciled invoice and runs Phase 6 for that invoice.

---

## Summary

**Option A (Invoice):**

| Setting        | Value |
|----------------|--------|
| **Model**      | Invoice (account.move) |
| **Trigger**    | Values Updated (or On create and edit) |
| **Conditions** | Move Type = Customer Invoice, Payment Status = Paid |
| **Action**     | Send Webhook Notification |
| **URL**        | `https://hooks.zapier.com/hooks/catch/9761276/uegifni/` |
| **Fields**     | Id |

**Option B (Payment):**

| Setting        | Value |
|----------------|--------|
| **Model**      | Payment (account.payment) |
| **Trigger**    | Values updated or On create and edit |
| **Apply on**   | State = Paid (or Posted; use what your Odoo shows) |
| **Optional**   | Before Update Domain: State ≠ Paid (so it runs only when a payment *becomes* Paid) |
| **Action**     | Send Webhook Notification |
| **URL**        | `https://hooks.zapier.com/hooks/catch/9761276/uegifni/` |
| **Fields**     | Id |
| **Zapier**     | Map trigger `id` to Code input `id` or `payment_id` |
