"""
Phase 6: Sync payment from Odoo to Workiz (uses atomic functions).
Run locally for testing. When approved, flatten for Zapier Code step (no imports).

Trigger: Webhook receives invoice_id. This script does:
  1. Get invoice from Odoo (must be paid)
  2. Get SO -> job UUID
  3. Get payment amount, date, type, reference
  4. add_payment(job_uuid, amount, type, date, reference)  # atomic
  5. mark_job_done(job_uuid)  # atomic, no SubStatus

Requires: Odoo credentials in config; Workiz in config.
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.workiz.add_payment import add_payment
from functions.workiz.mark_job_done import mark_job_done


def odoo_call(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}}, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def payment_type_odoo_to_workiz(payment_type_raw):
    """Map Odoo payment method name -> Workiz type. API accepts only cash, credit, check (zelle/venmo etc. mapped to cash)."""
    type_map = {
        "check": "check", "checks": "check", "cash": "cash", "credit": "credit",
        "manual": "cash", "manual payment": "cash",
        "credit charge": "credit", "credit offline": "credit", "debit offline": "credit",
        "zelle": "cash", "venmo": "cash", "cash app": "cash", "consumer financing": "credit",
        "bank transfer": "check",
    }
    lower = (payment_type_raw or "").lower()
    for k, v in type_map.items():
        if k in lower:
            return v
    return "cash"


def run(invoice_id):
    """
    Sync one paid invoice to Workiz: add payment + mark job Done.
    Returns dict with success, error, job_uuid, amount, workiz_type, payment_date.
    """
    invs = odoo_call("account.move", "read", [[invoice_id]], {"fields": ["invoice_origin", "payment_state", "amount_total", "date", "name"]})
    if not invs:
        return {"success": False, "error": "Invoice not found"}
    inv = invs[0]
    if inv.get("payment_state") != "paid":
        return {"success": False, "error": "Invoice not paid", "payment_state": inv.get("payment_state")}

    origin = inv.get("invoice_origin")
    if not origin:
        return {"success": False, "error": "Invoice has no sale order origin"}

    sos = odoo_call("sale.order", "search_read", [[["name", "=", origin]]], {"fields": ["id", "name", "x_studio_x_studio_workiz_uuid"], "limit": 1})
    if not sos:
        return {"success": False, "error": "Sale order not found for origin " + str(origin)}
    job_uuid = sos[0].get("x_studio_x_studio_workiz_uuid")
    if not job_uuid:
        return {"success": False, "error": "Sale order has no Workiz UUID"}

    amount_total = float(inv.get("amount_total", 0))
    payment_date = inv.get("date") or ""
    payment_type_raw = "manual"
    payment_ref = ""

    try:
        payments = odoo_call("account.payment", "search_read", [[["reconciled_invoice_ids", "in", [invoice_id]]]], {"fields": ["amount", "date", "ref", "payment_method_line_id"], "limit": 5})
    except Exception:
        payments = []

    if payments:
        p = payments[0]
        amount_total = float(p.get("amount", amount_total))
        payment_date = p.get("date") or payment_date
        payment_ref = (p.get("ref") or "").strip()
        mid = p.get("payment_method_line_id")
        if isinstance(mid, (list, tuple)) and len(mid) >= 2:
            try:
                pm = odoo_call("account.payment.method.line", "read", [[mid[0]]], {"fields": ["name"]})
                if pm:
                    payment_type_raw = (pm[0].get("name") or "manual").lower()
            except Exception:
                pass
        elif isinstance(mid, dict):
            payment_type_raw = (mid.get("name") or "manual").lower()

    if not payment_date:
        from datetime import date
        payment_date = str(date.today())
    if "T" not in str(payment_date):
        payment_date = str(payment_date) + "T12:00:00.000Z"

    workiz_type = payment_type_odoo_to_workiz(payment_type_raw)
    # Put real method (e.g. Zelle) in reference so Workiz has a record
    ref_parts = []
    if payment_type_raw and payment_type_raw.lower() not in ("cash", "credit", "check", "manual", "manual payment"):
        ref_parts.append(payment_type_raw.strip())
    if payment_ref:
        ref_parts.append(payment_ref)
    workiz_reference = " - ".join(ref_parts) if ref_parts else payment_ref or None

    out = add_payment(job_uuid, amount_total, workiz_type, payment_date, reference=workiz_reference)
    if not out.get("success"):
        return {"success": False, "error": "Workiz addPayment failed", "message": out.get("message"), "body": out.get("body")}

    out2 = mark_job_done(job_uuid)
    if not out2.get("success"):
        return {"success": True, "add_payment": "ok", "mark_done": "failed", "message": out2.get("message")}

    return {"success": True, "invoice_id": invoice_id, "job_uuid": job_uuid, "amount": amount_total, "workiz_type": workiz_type, "payment_date": payment_date}


if __name__ == "__main__":
    # Test: pass invoice_id as first arg or env INVOICE_ID
    invoice_id = int(os.environ.get("INVOICE_ID", sys.argv[1] if len(sys.argv) > 1 else 0))
    if not invoice_id:
        print("Usage: INVOICE_ID=123 python phase6_payment_sync_to_workiz.py   OR   python phase6_payment_sync_to_workiz.py 123")
        sys.exit(1)
    result = run(invoice_id)
    print(result)
