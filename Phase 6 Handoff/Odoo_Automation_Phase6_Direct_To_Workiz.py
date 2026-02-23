"""
Phase 6 entirely inside Odoo: when an invoice is marked paid, Odoo runs this Python
and calls Workiz directly (add payment + mark job Done). No Zapier, no your PC.

IMPORTANT: Odoo Online (SaaS) often restricts "import" and outbound HTTP in
automated actions. If you get an error like "forbidden opcode IMPORT_NAME" or
HTTP calls fail, you cannot do this 100% inside Odoo on that plan — use Zapier
instead (Odoo trigger → Zapier Code step that calls Workiz). Self-hosted Odoo or
some plans may allow it; try this first.

SETUP IN ODOO
-------------
1. Settings → Automation → Automated Actions → Create
2. Model: Invoice (account.move)
3. Trigger: On Update
4. Apply on: Update on records
5. Domain (optional but recommended so it only runs when invoice is paid):
   [('move_type','=','out_invoice'), ('payment_state','=','paid')]
6. Action: Execute Python Code
7. Paste the code below into the Python code field.

BEFORE PASTING: Replace the two placeholders with your Workiz credentials.
   WORKIZ_BASE_URL = "https://api.workiz.com/api/v1/YOUR_WORKIZ_API_TOKEN"
   WORKIZ_AUTH_SECRET = "sec_YOUR_AUTH_SECRET"

(Odoo Automation has access to 'record' = the invoice that triggered, and 'env' = Odoo ORM.
 We use only standard library urllib and json so it works on Odoo Online.)
"""

# ============ PASTE FROM HERE INTO ODOO AUTOMATION (Execute Python Code) ============
# Replace the next two lines with your real Workiz values (same as in your config / Zapier).
WORKIZ_BASE_URL = "https://api.workiz.com/api/v1/YOUR_WORKIZ_API_TOKEN"
WORKIZ_AUTH_SECRET = "sec_YOUR_AUTH_SECRET"

# --- 1) Get invoice and SO + Workiz UUID from Odoo (using record and env) ---
inv = record
if inv.payment_state != 'paid' or inv.move_type != 'out_invoice':
    raise UserError("Phase 6: Invoice is not a paid customer invoice.")
origin = inv.invoice_origin
if not origin:
    raise UserError("Phase 6: Invoice has no sale order origin.")
so = env['sale.order'].search([('name', '=', origin)], limit=1)
if not so:
    raise UserError("Phase 6: Sale order not found for origin %s" % origin)
job_uuid = (so.x_studio_x_studio_workiz_uuid or "").strip()
if not job_uuid:
    raise UserError("Phase 6: Sale order has no Workiz UUID.")

# --- 2) Payment amount, date, type, reference ---
amount_total = float(inv.amount_total)
payment_date = inv.date and str(inv.date) or ""
payment_type_raw = "manual"
payment_ref = ""

payments = env['account.payment'].search([('reconciled_invoice_ids', 'in', [inv.id])], limit=5)
if payments:
    p = payments[0]
    amount_total = float(p.amount)
    payment_date = p.date and str(p.date) or payment_date
    payment_ref = (p.ref or "").strip()
    if p.payment_method_line_id:
        payment_type_raw = (p.payment_method_line_id.name or "manual").lower()

if not payment_date:
    from datetime import date
    payment_date = str(date.today())
if "T" not in payment_date:
    payment_date = payment_date + "T12:00:00.000Z"

# Map Odoo payment method -> Workiz type (cash, credit, check)
type_map = {
    "check": "check", "checks": "check", "cash": "cash", "credit": "credit",
    "manual": "cash", "manual payment": "cash",
    "credit charge": "credit", "credit offline": "credit", "debit offline": "credit",
    "zelle": "cash", "venmo": "cash", "cash app": "cash", "consumer financing": "credit",
    "bank transfer": "check",
}
workiz_type = "cash"
for k, v in type_map.items():
    if k in (payment_type_raw or "").lower():
        workiz_type = v
        break

ref_parts = []
if payment_type_raw and payment_type_raw.lower() not in ("cash", "credit", "check", "manual", "manual payment"):
    ref_parts.append(payment_type_raw.strip())
if payment_ref:
    ref_parts.append(payment_ref)
workiz_reference = " - ".join(ref_parts) if ref_parts else payment_ref or None

# --- 3) Call Workiz: add payment (using urllib; no requests needed) ---
import json
import urllib.request

add_pay_url = (WORKIZ_BASE_URL.rstrip("/") + "/job/addPayment/%s/") % job_uuid
add_pay_body = {
    "auth_secret": WORKIZ_AUTH_SECRET,
    "uuid": job_uuid,
    "amount": round(amount_total, 2),
    "type": workiz_type,
    "date": payment_date,
}
if workiz_reference:
    add_pay_body["reference"] = str(workiz_reference)[:255]

req = urllib.request.Request(
    add_pay_url,
    data=json.dumps(add_pay_body).encode("utf-8"),
    method="POST",
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        pass  # 200/201/204 = success
except urllib.error.HTTPError as e:
    raise UserError("Phase 6 Workiz addPayment failed: HTTP %s - %s" % (e.code, e.read()[:200]))
except Exception as e:
    raise UserError("Phase 6 Workiz addPayment error: %s" % e)

# --- 4) Call Workiz: mark job Done ---
update_url = WORKIZ_BASE_URL.rstrip("/") + "/job/update/"
update_body = {
    "auth_secret": WORKIZ_AUTH_SECRET,
    "UUID": job_uuid,
    "Status": "Done",
}

req2 = urllib.request.Request(
    update_url,
    data=json.dumps(update_body).encode("utf-8"),
    method="POST",
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req2, timeout=15) as r:
        pass
except urllib.error.HTTPError as e:
    raise UserError("Phase 6 Workiz mark Done failed: HTTP %s - %s" % (e.code, e.read()[:200]))
except Exception as e:
    raise UserError("Phase 6 Workiz mark Done error: %s" % e)

# Optional: post to invoice chatter so you see it ran
inv.message_post(body="Phase 6: Payment synced to Workiz and job marked Done.")
# ============ END OF CODE TO PASTE ============
