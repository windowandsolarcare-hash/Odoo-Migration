# Phase 6 Automation: Run When Invoice Is Paid

When an invoice is **posted as paid** (zero amount due) in Odoo, you can automatically sync that payment to Workiz and mark the job Done by calling a small webhook server. No manual run of `phase6_payment_sync_to_workiz.py` needed.

---

## How the Odoo Automation flow works (plain English)

There are **two different “servers”** in this setup. It’s easy to mix them up.

### 1. Odoo’s server (Odoo Online / window-solar-care.odoo.com)

- This is where your Odoo app lives. You don’t control this machine; Odoo does.
- When you create an **Automation** in Odoo, that automation runs **on Odoo’s server**.
- The only thing that automation does is run a **very small** bit of code: “When an invoice is updated and its payment status is Paid, send one HTTP request to a URL I give you, and put the invoice’s ID in that request.”
- So **Odoo does not run Phase 6**. Odoo only runs that tiny “notify a URL” step. It has no copy of your Phase 6 code and doesn’t talk to Workiz.

### 2. Your webhook server (your machine or a server you control)

- This is a **small program you run**: `phase6_webhook_server.py`. It runs on **your** PC or a server you rent (VPS), not on Odoo’s servers.
- That program does one job: **listen for incoming HTTP requests** at a specific address. That address is your **“webhook URL”** (e.g. `https://abc123.ngrok.io/sync-invoice`).
- When someone (Odoo or Zapier) **calls** that URL and sends the invoice ID in the body, your program:
  1. Receives the invoice ID.
  2. Runs the **Phase 6** logic (the same code as `phase6_payment_sync_to_workiz.py`): it uses your Odoo API and Workiz API to read the paid invoice, find the job, add the payment in Workiz, and mark the job Done.
- So **Phase 6 runs on your webhook server**, not on Odoo. Your server has your config (Odoo URL, Workiz keys) and your Phase 6 code.

### What “call your webhook URL” means

- **Webhook URL** = the full address where your webhook server is listening, for example:
  - `https://abc123.ngrok.io/sync-invoice` (if you use ngrok on your PC), or
  - `https://yourcompany.com/phase6/sync-invoice` (if you host the script on your own server).
- **“Call”** = Odoo (or Zapier) sends an HTTP **POST** request to that URL, with a JSON body like `{"invoice_id": 123}`. So “call your webhook URL” = “send that POST request to that URL.”
- Your webhook server receives that request, reads `invoice_id`, runs Phase 6 for that invoice, and replies with success or error.

### Step-by-step: what happens when you mark an invoice paid

1. **In Odoo:** You (or your process) post the invoice and register the payment. The invoice’s status becomes **Paid**, amount due = 0.
2. **Odoo’s server:** The automation you configured runs. It sees: “This record is an invoice, and its payment_state is paid.” So it runs the Python snippet you entered. That snippet does **only** this:  
   `POST to WEBHOOK_URL with body {"invoice_id": record.id}`.  
   So Odoo sends one request **out** to the internet (or your network) to the URL you put in `WEBHOOK_URL`.
3. **Your webhook server:** The request lands on the machine where `phase6_webhook_server.py` is running. The script receives the invoice ID (e.g. 123).
4. **Your server runs Phase 6:** The script calls the same logic as `phase6_payment_sync_to_workiz.run(123)`: it talks to **Odoo’s API** (to read the invoice and the related sale order) and to **Workiz’s API** (to add the payment and mark the job Done). All of that runs on **your** server; Odoo is only being asked for data and is not “running Phase 6” itself.
5. **Done:** Workiz now has the payment and the job is marked Done. Your webhook server sends back a success (or error) response to whoever called it (Odoo doesn’t usually do anything with that response; it just triggered the call).

### Summary

| Where        | What runs there |
|-------------|------------------|
| **Odoo’s server** | Only the automation: “when invoice is paid, POST invoice_id to this URL.” No Phase 6 code. |
| **Your webhook server** | The program that listens at the webhook URL and runs **Phase 6** (Odoo API + Workiz API) when it receives an invoice_id. |

So: **Odoo tells your server “this invoice was paid (id=123).” Your server then does the real work (Phase 6) and talks to both Odoo and Workiz.**

---

## 1. Run the webhook server

On a machine that has the Phase 6 code and can reach Odoo + Workiz (your PC or a small server):

```bash
cd "2_Modular_Phase3_Components"
python phase6_webhook_server.py
```

- Listens on **http://0.0.0.0:8765** (all interfaces).
- Optional: `--port 8766` to use another port.
- Optional: set env **PHASE6_WEBHOOK_TOKEN** to a secret; callers must send header **X-Webhook-Token: &lt;same-secret&gt;** (recommended if the URL is public).

To expose it so Odoo (or Zapier) can reach it:

- **Same network:** Use your machine’s LAN IP (e.g. `http://192.168.1.10:8765`) if Odoo/Zapier runs on the same network.
- **Internet:** Use **ngrok** (e.g. `ngrok http 8765`) and use the HTTPS URL ngrok gives you, or put the server on a VPS with a real domain.

Example with ngrok:

```bash
# Terminal 1
python phase6_webhook_server.py

# Terminal 2
ngrok http 8765
# Use the https://xxxx.ngrok.io URL as WEBHOOK_URL below
```

---

## 2. Trigger the webhook when the invoice is paid

You can trigger the webhook in either of these ways.

### Option A: Odoo Automation (direct API – recommended)

1. In Odoo: **Settings → Automation → Automated Actions** (or **Apps → Automation**).
2. **Create** a new automated action:
   - **Model:** `Invoice` (`account.move`).
   - **Trigger:** “On Update”.
   - **Apply on:** e.g. “Update on records” (when a record is updated).
   - **Domain:**  
     `[('move_type','=','out_invoice'), ('payment_state','=','paid')]`  
     So it only runs when the updated record is a customer invoice that is paid.
3. **Action:** “Execute Python Code”.
4. **Python code** (replace `WEBHOOK_URL` with your server URL, e.g. ngrok or your server):

```python
import json
import urllib.request

WEBHOOK_URL = "https://your-ngrok-or-server.example.com/sync-invoice"

# record = the invoice that was just updated (account.move)
invoice_id = record.id
data = json.dumps({"invoice_id": invoice_id}).encode("utf-8")
req = urllib.request.Request(
    WEBHOOK_URL,
    data=data,
    method="POST",
    headers={"Content-Type": "application/json"}
)
# Optional: if you set PHASE6_WEBHOOK_TOKEN, add:
# req.add_header("X-Webhook-Token", "your-secret")
urllib.request.urlopen(req, timeout=10)
```

- If you use **X-Webhook-Token**, add the line that sets the header (and keep the token in Odoo’s encrypted config or a server env, not in plain text if possible).
- This runs **when an invoice is updated and is paid**. So when the user posts the invoice and then registers the payment (Pay button → payment registered), the invoice’s `payment_state` becomes `paid` and the automation runs and calls your webhook.

**Note:** Some Odoo SaaS plans may restrict “Execute Python” or outbound HTTP. If that’s the case, use Option B (Zapier).

---

### Option B: Zapier

1. **Trigger:** “Odoo – Updated Record” (or “New or Updated Record”) for **Invoice**.
2. **Filter:** Only continue if `payment_state` is `paid` (and optionally `move_type` = customer invoice).
3. **Action:** “Webhooks by Zapier – POST”.
   - URL: your webhook URL (e.g. `https://your-ngrok-or-server.example.com/sync-invoice`).
   - Payload Type: JSON.
   - Data: `{"invoice_id": <Id from trigger>}` (map the Odoo invoice Id to `invoice_id`).

Zapier will POST to your server whenever an invoice is updated and paid; the server runs Phase 6 for that `invoice_id`.

---

## 3. What the webhook does

- Receives **POST /sync-invoice** (or **/phase6**) with JSON **{"invoice_id": &lt;id&gt;}**.
- Calls the same logic as **phase6_payment_sync_to_workiz.py**: reads the paid invoice and linked SO in Odoo, gets the Workiz job UUID, adds the payment in Workiz, marks the job Done.
- Returns JSON **{ "success": true, ... }** or **{ "success": false, "error": "..." }**.

So: **invoice posted as paid (zero amount due) → automation triggers → webhook called with that invoice id → Phase 6 runs → payment and Done in Workiz.**

---

## 4. Manual fallback

You can still run Phase 6 manually when needed:

```bash
python phase6_payment_sync_to_workiz.py <invoice_id>
```

Or use the “update OD” / “update 2OD” status flow you already use for manual one-by-one refresh; the webhook only automates the **payment → Workiz** step when the invoice is paid.
