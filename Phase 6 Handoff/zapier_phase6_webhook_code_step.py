"""
Phase 6: Zapier — Webhook trigger + single Code step (Odoo → Workiz)
=====================================================================
Use in Zapier: Trigger = Webhooks by Zapier (Catch a Hook). Step 2 = Code by Zapier (Python).
Put this entire file (flattened, no external imports beyond requests) in the Code step.

Webhook payload expected (POST JSON):
  { "invoice_id": 123 }   (Odoo account.move id for the customer invoice that was paid)

Or from Zapier Odoo trigger (if you use "Odoo - Updated Record" instead of webhook):
  Map the Odoo record "Id" to invoice_id in the Code step input.

Credentials: Set in Zapier Code step input or use Zapier Storage / env.
  ODOO_URL, ODOO_DB, ODOO_UID, ODOO_API_KEY, WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
"""

# --- Paste below into Zapier Code by Zapier (Python), input_data = webhook body or previous step ---

def main(input_data):
    import requests

    invoice_id = input_data.get("invoice_id")
    if not invoice_id:
        return {"success": False, "error": "Missing invoice_id"}

    # Credentials - replace with your Zapier env or Storage
    ODOO_URL = input_data.get("ODOO_URL") or "https://window-solar-care.odoo.com/jsonrpc"
    ODOO_DB = input_data.get("ODOO_DB") or "window-solar-care"
    ODOO_UID = int(input_data.get("ODOO_USER_ID", 2))
    ODOO_API_KEY = input_data.get("ODOO_API_KEY") or ""
    WORKIZ_BASE_URL = input_data.get("WORKIZ_BASE_URL") or "https://api.workiz.com/api/v1/api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
    WORKIZ_AUTH_SECRET = input_data.get("WORKIZ_AUTH_SECRET") or ""

    if not ODOO_API_KEY or not WORKIZ_AUTH_SECRET:
        return {"success": False, "error": "Missing ODOO_API_KEY or WORKIZ_AUTH_SECRET"}

    def odoo_call(model, method, args, kwargs=None):
        params = [ODOO_DB, ODOO_UID, ODOO_API_KEY, model, method, args]
        if kwargs is not None:
            params.append(kwargs)
        r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}}, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        return data.get("result")

    # 1) Get invoice and check paid
    invs = odoo_call("account.move", "read", [[invoice_id]], {"fields": ["invoice_origin", "payment_state", "amount_total", "name"]})
    if not invs:
        return {"success": False, "error": "Invoice not found"}
    inv = invs[0]
    if inv.get("payment_state") != "paid":
        return {"success": False, "error": "Invoice not paid", "payment_state": inv.get("payment_state")}

    origin = inv.get("invoice_origin")
    if not origin:
        return {"success": False, "error": "Invoice has no sale order origin"}

    # 2) Get SO and Workiz job UUID
    sos = odoo_call("sale.order", "search_read", [[["name", "=", origin]]], {"fields": ["id", "name", "x_studio_x_studio_workiz_uuid"], "limit": 1})
    if not sos:
        return {"success": False, "error": "Sale order not found for origin " + str(origin)}
    so = sos[0]
    job_uuid = so.get("x_studio_x_studio_workiz_uuid")
    if not job_uuid:
        return {"success": False, "error": "Sale order has no Workiz UUID"}

    # 3) Get payment(s) for this invoice (amount, date, method, ref)
    amount_total = float(inv.get("amount_total", 0))
    payment_date = None
    payment_type_raw = "manual"
    payment_ref = ""

    try:
        payments = odoo_call("account.payment", "search_read", [[["reconciled_invoice_ids", "in", [invoice_id]]]], {"fields": ["amount", "date", "ref", "payment_method_line_id"], "limit": 5})
    except Exception:
        payments = []

    if payments:
        p = payments[0]
        amount_total = float(p.get("amount", amount_total))
        payment_date = p.get("date")
        payment_ref = (p.get("ref") or "").strip()
        mid = p.get("payment_method_line_id")
        if isinstance(mid, (list, tuple)) and len(mid) >= 2:
            try:
                pm = odoo_call("account.payment.method.line", "read", [[mid[0]]], {"fields": ["name"]})
                if pm:
                    payment_type_raw = (pm[0].get("name") or "").lower()
            except Exception:
                pass
        elif isinstance(mid, dict):
            payment_type_raw = (mid.get("name") or "manual").lower()
    if not payment_date:
        try:
            from datetime import date
            payment_date = str(date.today())
        except Exception:
            payment_date = inv.get("date") or ""

    # ISO date-time for Workiz (API: date-time e.g. 2016-08-29T09:12:33.001Z)
    if payment_date and "T" not in str(payment_date):
        payment_date = str(payment_date) + "T12:00:00.000Z"

    # Map Odoo payment method -> Workiz type (cash, credit, check, + UI types if API accepts)
    type_map = {"check": "check", "checks": "check", "cash": "cash", "credit": "credit", "manual": "cash", "manual payment": "cash",
                "zelle": "zelle", "venmo": "venmo", "cash app": "cash app", "consumer financing": "consumer financing",
                "bank transfer": "bank transfer (offline)", "debit offline": "debit offline", "credit offline": "credit offline", "credit charge": "credit"}
    workiz_type = "cash"
    payment_type_lower = (payment_type_raw or "").lower()
    for k, v in type_map.items():
        if k in payment_type_lower:
            workiz_type = v
            break

    # 4) Workiz: add payment (addPaymentBody: auth_secret, uuid, amount, type, date, reference optional). API accepts only cash, credit, check.
    if workiz_type not in ("cash", "credit", "check"):
        workiz_type = "cash"  # API rejects zelle/venmo etc.; map to cash
    # Put real method (e.g. Zelle) in reference so Workiz has a record
    ref_parts = []
    if payment_type_raw and payment_type_raw.lower() not in ("cash", "credit", "check", "manual", "manual payment"):
        ref_parts.append(payment_type_raw.strip())
    if payment_ref:
        ref_parts.append(payment_ref)
    workiz_reference = " - ".join(ref_parts) if ref_parts else None
    add_pay_url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/addPayment/{job_uuid}/"
    add_pay_body = {"auth_secret": WORKIZ_AUTH_SECRET, "uuid": str(job_uuid), "amount": round(amount_total, 2), "type": workiz_type, "date": payment_date}
    if workiz_reference:
        add_pay_body["reference"] = workiz_reference[:255]
    try:
        resp = requests.post(add_pay_url, json=add_pay_body, timeout=15)
        if resp.status_code not in (200, 201, 204):
            return {"success": False, "error": "Workiz addPayment failed", "status": resp.status_code, "body": resp.text[:500]}
    except Exception as e:
        return {"success": False, "error": "Workiz addPayment error: " + str(e)}

    # 5) Workiz: mark job Done (status only; no SubStatus for Done)
    update_url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/update/"
    update_body = {"auth_secret": WORKIZ_AUTH_SECRET, "UUID": job_uuid, "Status": "Done"}
    try:
        resp2 = requests.post(update_url, json=update_body, timeout=15)
        if resp2.status_code not in (200, 201, 204):
            return {"success": True, "add_payment": "ok", "mark_done": "failed", "status": resp2.status_code, "body": resp2.text[:500]}
    except Exception as e:
        return {"success": True, "add_payment": "ok", "mark_done": "error: " + str(e)}

    return {"success": True, "invoice_id": invoice_id, "job_uuid": job_uuid, "amount": amount_total, "workiz_type": workiz_type, "payment_date": payment_date}
