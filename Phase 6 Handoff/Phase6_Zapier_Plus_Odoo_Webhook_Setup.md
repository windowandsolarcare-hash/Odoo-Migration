# Phase 6: Zapier (Catch a Hook) + Odoo (Send Webhook)

This is a **new Zap**: trigger = **Webhooks by Zapier – Catch a Hook** (Odoo-originated), so no Odoo polling. When an invoice is marked paid in Odoo, **Odoo** sends a webhook to Zapier; Zapier runs the Phase 6 code and calls Workiz.

---

## Part 1: Set up the Zap in Zapier

Do this first so you have the webhook URL to give Odoo.

### Step 1 – Trigger: Webhooks by Zapier (Catch a Hook)

1. In Zapier: **Create Zap** (or **Create a new Zap**).
2. **Trigger:** Search for **Webhooks by Zapier** → choose **Catch Hook**.
3. Click **Continue**. Zapier shows a **webhook URL** (e.g. `https://hooks.zapier.com/hooks/catch/12345/abcdef/`).
4. **Copy that URL** — you will paste it into Odoo in Part 2.
5. Click **Continue**. Zapier will say “Trigger by Zap” / “Waiting for a test” — that’s normal. You’ll send a test from Odoo (or a manual POST) later.
6. **Optional test now:** In another tab, use Postman or a similar tool to send a **POST** to that URL with body `{"id": 123}` (or `{"invoice_id": 123}`). Then in Zapier click “Test trigger”; you should see the body. That confirms the Zap receives data. Use the same key in Odoo (see Part 2).

### Step 2 – Action: Code by Zapier (Run Python)

1. **Action:** Search for **Code by Zapier** → choose **Run Python**.
2. **Input Data:** Add **one** input:
   - **Key:** `invoice_id`
   - **Value:** From the trigger, pick the field that has the **invoice id**.  
     - If Odoo sends `{"id": 123}`, the trigger will expose something like `id` — map that to `invoice_id` (e.g. `{{trigger.id}}` or whatever Zapier shows for the webhook body).
   - So: **invoice_id** = the number that identifies the paid invoice in Odoo (the `account.move` id).
3. **Code:** Open `2_Modular_Phase3_Components/zapier_phase6_FLATTENED_FINAL.py` from your repo. Copy the **entire** file and paste it into the Code box.  
   - The script expects `input_data.get("invoice_id")` and uses the same Odoo/Workiz credentials as your other phases (set at the top of the file). No need to pass credentials via Input Data unless you prefer to.
4. Save the step and **Continue**.

### Step 3 – Turn the Zap On

1. Name the Zap (e.g. “Phase 6 – Invoice paid → Workiz”).
2. **Turn the Zap ON.**

You’re done in Zapier. The only thing Odoo needs is the **webhook URL** from Step 1.

---

## Part 2: Set up Odoo to send the webhook when an invoice is paid

Odoo will **POST** to the Zapier URL when a customer invoice is **paid** (so when payment is registered and the invoice shows paid / zero amount due). We use Odoo’s **Send Webhook Notification** action (no Python, no “Execute Code”).

### 1. Open Automations

- **Odoo Studio** → **Automations** → **New**  
  (or **Settings** → **Automation** → **Automated Actions** → **Create**, depending on your Odoo version and apps).

### 2. Basic settings

- **Name:** e.g. “Phase 6: Notify Zapier when invoice paid”.
- **Model:** **Invoice** (`account.move`).  
  - If you don’t see it: enable **Developer Mode**, then pick the **Invoice** / **account.move** model.

### 3. Trigger

- **Trigger:** **Values Updated** (or **On create and edit** / **When a record is created or updated**).
- So the automation runs when an invoice record is updated (e.g. when payment is registered).

### 4. When to run (Apply on / domain)

We only want to run when the invoice is a **customer invoice** and **paid**:

- **Apply on** (or “After update” domain): add conditions so the record has:
  - **Move Type** = **Customer Invoice** (`out_invoice`), and  
  - **Payment Status** = **Paid** (`paid`).

So: only when the updated record is a customer invoice that is paid. (If your Odoo uses “Before / After” domains, use the one that means “after the update, the record must match these conditions.”)

### 5. Action: Send Webhook Notification

- **Action:** **Send Webhook Notification** (or **Webhook**).
- **URL:** Paste the **Zapier webhook URL** from Part 1 (the Catch a Hook URL).
- **Fields to send:** Include at least the **invoice id** so Zapier can use it as `invoice_id`:
  - Add the field **Id** (the record id; technical name is usually `id`).  
  - Odoo will send a JSON body with that field; Zapier will expose it (e.g. as `id` or `Id`). In Part 1 you mapped that to **invoice_id** in the Code step.

If Odoo lets you add more fields (e.g. `name`, `invoice_origin`), you can, but the Code step only needs the invoice **id**.

### 6. Save

- **Save** the automation and leave it active.

---

## End-to-end flow

1. In Odoo you **post** the invoice and **register the payment** (e.g. Pay button) so the invoice is **Paid**.
2. Odoo’s automation runs (trigger: values updated; condition: customer invoice + paid).
3. Odoo sends a **POST** to the Zapier Catch a Hook URL with the invoice **id** (and any other fields you chose).
4. Zapier runs the Zap: Code by Zapier gets **invoice_id** from the webhook body and runs the Phase 6 script.
5. The script reads the invoice and SO in Odoo, gets the Workiz job UUID, adds the payment in Workiz, and marks the job **Done**.

No polling, no your PC — only Odoo, Zapier, and Workiz.

---

## If the field name from Odoo isn’t `id`

When you test, look at what Zapier receives (Test trigger in the Zap). If Odoo sends the id under another key (e.g. `invoice_id`, `res_id`, or a custom name), in the Code step’s **Input Data** set **invoice_id** to that key (e.g. `{{trigger.invoice_id}}` or whatever Zapier shows). The Python code only needs `input_data.get("invoice_id")` to be the numeric invoice id.

---

## Files to use

| What | Where |
|------|--------|
| Zapier Code step (paste into Run Python) | `2_Modular_Phase3_Components/zapier_phase6_FLATTENED_FINAL.py` |
| Older webhook-only doc | `Zapier_Phase6_Webhook_Setup.md` (same Zap structure; this doc adds Odoo setup) |
