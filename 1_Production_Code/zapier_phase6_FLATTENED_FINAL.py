"""
ZAPIER PHASE 6 FLATTENED SCRIPT - FINAL
=======================================
Odoo payment recorded -> sync to Workiz (add payment + mark job Done).

Trigger: Webhooks by Zapier - Catch a Hook.
Step 2: Code by Zapier - Run Python.
  - Input Data: invoice_id OR id (payment id). If Odoo triggers on Payment model, map trigger "id" to input "id" or "payment_id".
  - Code: paste this entire file.

Same pattern as Phase 3/4/5: credentials at top, main(input_data), output = main(input_data).

Generated: 2026-02
"""

# VERSION: 2026-03-05-v2 (Force refresh - invoice_id fix for Phase 5 trigger)
import re
import json
import requests
from datetime import date

# ==============================================================================
# CONFIGURATION & CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

# Phase 5 webhook: when we mark job Done here, Workiz may not fire "Job Status Changed", so Phase 4/5 never run. We trigger Phase 5 ourselves so the follow-up activity (or next maintenance job) is still created.
PHASE5_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/9761276/ue4o0az/"


# ==============================================================================
# ODOO HELPER
# ==============================================================================

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


# ==============================================================================
# PHASE 6: PAYMENT SYNC TO WORKIZ
# ==============================================================================

def main(input_data):
    """
    Sync one paid Odoo invoice to Workiz: add payment + mark job Done.

    Expected input_data from Zapier (Webhook body):
    - invoice_id: 123   (Odoo account.move id for the paid customer invoice), OR
    - id / payment_id: 456  (Odoo account.payment id; we look up reconciled_invoice_ids and use the first invoice)
    """
    print("\n" + "="*70)
    print("PHASE 6: ODOO PAYMENT -> WORKIZ")
    print("="*70)

    def _extract_id(name, val):
        """
        Accept int, numeric string, or Odoo webhook payload string.
        Odoo sometimes sends e.g. '49{"_action": "...", "id": 49, ...}' — we extract 49.
        """
        if val is None:
            return None
        if isinstance(val, int):
            return val if val >= 0 else None
        s = str(val).strip()
        if not s:
            return None
        # Plain number
        try:
            return int(float(s))
        except (TypeError, ValueError):
            pass
        # Leading digits (e.g. "49{...}" from Odoo payload)
        m = re.match(r"^(\d+)", s)
        if m:
            return int(m.group(1))
        # JSON object with "id" or "_id"
        if "{" in s and ("id" in s or "_id" in s):
            try:
                # Find JSON object: from first { to last }
                start = s.index("{")
                end = s.rindex("}") + 1
                obj = json.loads(s[start:end])
                n = obj.get("id") or obj.get("_id")
                if n is not None:
                    return int(n)
            except (ValueError, TypeError, KeyError):
                pass
            # Fallback: regex for "id": 49 or "_id": 49
            for key in ('"id"', '"_id"'):
                match = re.search(r"%s\s*:\s*(\d+)" % key, s)
                if match:
                    return int(match.group(1))
        raise ValueError(f"{name} must be the numeric Odoo record Id (integer); got: {repr(val)[:200]}. In Zapier, map the webhook body field that contains the Payment/Invoice Id (number), not the request or hook id.")

    raw_invoice_id = input_data.get('invoice_id')
    raw_payment_id = input_data.get('payment_id') or input_data.get('id')
    triggered_by_payment = False
    this_payment = None  # when triggered by payment_id: the payment record we're syncing

    if not raw_invoice_id and raw_payment_id:
        try:
            payment_id = _extract_id("payment_id", raw_payment_id)
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        if payment_id is None:
            return {'success': False, 'error': 'No payment_id provided'}
        pays = odoo_call("account.payment", "read", [[payment_id]], {"fields": ["amount", "date", "memo", "payment_method_line_id", "reconciled_invoice_ids"]})
        if not pays or not pays[0].get("reconciled_invoice_ids"):
            return {'success': False, 'error': 'Payment not found or has no reconciled invoice'}
        this_payment = pays[0]
        invoice_id = this_payment["reconciled_invoice_ids"][0]
        triggered_by_payment = True
        print(f"\n[*] Payment ID: {payment_id} -> Invoice ID: {invoice_id} (split payments: will mark Done only when balance=0)")
    else:
        invoice_id = None
        if raw_invoice_id:
            try:
                invoice_id = _extract_id("invoice_id", raw_invoice_id)
            except ValueError as e:
                return {'success': False, 'error': str(e)}
        if invoice_id is None and not triggered_by_payment:
            return {'success': False, 'error': 'No invoice_id or payment_id provided. Map the webhook body field with the numeric Payment Id (or Invoice Id) in Zapier.'}

    print(f"\n[*] Invoice ID: {invoice_id}")

    # 1) Get invoice (and optionally require paid when not triggered by payment)
    try:
        invs = odoo_call("account.move", "read", [[invoice_id]], {"fields": ["invoice_origin", "payment_state", "amount_total", "amount_residual", "date", "name"]})
    except Exception as e:
        return {'success': False, 'error': 'Odoo read failed: ' + str(e)}

    if not invs:
        return {'success': False, 'error': 'Invoice not found'}
    inv = invs[0]
    if not triggered_by_payment and inv.get("payment_state") != "paid":
        return {'success': False, 'error': 'Invoice not paid', 'payment_state': inv.get("payment_state")}

    origin = inv.get("invoice_origin")
    if not origin:
        return {'success': False, 'error': 'Invoice has no sale order origin'}

    # 2) Get SO and Workiz job UUID
    sos = odoo_call("sale.order", "search_read", [[["name", "=", origin]]], {"fields": ["id", "name", "x_studio_x_studio_workiz_uuid"], "limit": 1})
    if not sos:
        return {'success': False, 'error': 'Sale order not found for origin ' + str(origin)}
    job_uuid = sos[0].get("x_studio_x_studio_workiz_uuid")
    if not job_uuid:
        return {'success': False, 'error': 'Sale order has no Workiz UUID'}

    print(f"[*] Job UUID: {job_uuid}")

    # 3) Amount, date, type, ref: use THIS payment when triggered by payment; else first payment on invoice or invoice total
    amount_total = float(inv.get("amount_total", 0))
    payment_date = inv.get("date") or ""
    payment_type_raw = "manual"
    payment_ref = ""

    if triggered_by_payment and this_payment:
        amount_total = float(this_payment.get("amount", 0))
        payment_date = this_payment.get("date") or payment_date
        payment_ref = (this_payment.get("memo") or "").strip()
        # DEBUG: Uncomment to troubleshoot payment data
        # print(f"[DEBUG] Payment fields available: {list(this_payment.keys())}")
        # print(f"[DEBUG] payment_ref from 'memo' field: '{payment_ref}'")
        mid = this_payment.get("payment_method_line_id")
        if isinstance(mid, (list, tuple)) and len(mid) >= 2:
            try:
                pm = odoo_call("account.payment.method.line", "read", [[mid[0]]], {"fields": ["name"]})
                if pm:
                    payment_type_raw = (pm[0].get("name") or "manual").strip()
            except Exception:
                pass
        elif isinstance(mid, dict):
            payment_type_raw = (mid.get("name") or "manual").strip()
    else:
        try:
            payments = odoo_call("account.payment", "search_read", [[["reconciled_invoice_ids", "in", [invoice_id]]]], {"fields": ["amount", "date", "memo", "payment_method_line_id"], "limit": 5})
            if payments:
                p = payments[0]
                amount_total = float(p.get("amount", amount_total))
                payment_date = p.get("date") or payment_date
                payment_ref = (p.get("memo") or "").strip()
                mid = p.get("payment_method_line_id")
                if isinstance(mid, (list, tuple)) and len(mid) >= 2:
                    try:
                        pm = odoo_call("account.payment.method.line", "read", [[mid[0]]], {"fields": ["name"]})
                        if pm:
                            payment_type_raw = (pm[0].get("name") or "manual").strip()
                    except Exception:
                        pass
                elif isinstance(mid, dict):
                    payment_type_raw = (mid.get("name") or "manual").strip()
        except Exception:
            pass

    if not payment_date:
        payment_date = str(date.today())
    if "T" not in str(payment_date):
        payment_date = str(payment_date) + "T12:00:00.000Z"

    # Map Odoo method -> Workiz type (API only accepts cash, credit, check)
    type_map = {
        "check": "check", "checks": "check", "cash": "cash", "credit": "credit",
        "manual": "cash", "manual payment": "cash",
        "credit charge": "credit", "credit offline": "credit", "debit offline": "credit",
        "zelle": "cash", "venmo": "cash", "cash app": "cash", "consumer financing": "credit",
        "bank transfer": "check",
    }
    payment_type_lower = (payment_type_raw or "").lower()
    workiz_type = "cash"
    for k, v in type_map.items():
        if k in payment_type_lower:
            workiz_type = v
            break

    # Reference: include real method (e.g. Zelle) so Workiz has a record
    ref_parts = []
    if payment_type_raw and payment_type_lower not in ("cash", "credit", "check", "manual", "manual payment"):
        ref_parts.append(payment_type_raw.strip())
    if payment_ref:
        ref_parts.append(payment_ref)
    workiz_reference = " - ".join(ref_parts) if ref_parts else None
    
    # DEBUG: Uncomment to troubleshoot reference building
    # print(f"[DEBUG] payment_type_raw='{payment_type_raw}', payment_type_lower='{payment_type_lower}'")
    # print(f"[DEBUG] payment_ref='{payment_ref}', workiz_reference='{workiz_reference}'")

    # 4) Workiz: add THIS payment — SKIP for Credit Card payments (already recorded in Workiz at door)
    if workiz_type == "credit":
        print("[*] Credit Card payment detected — skipping Workiz addPayment (already recorded at door)")
    else:
        add_pay_url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/addPayment/{job_uuid}/"
        add_pay_body = {
            "auth_secret": WORKIZ_AUTH_SECRET,
            "uuid": str(job_uuid),
            "amount": round(amount_total, 2),
            "type": workiz_type,
            "date": payment_date,
        }
        if workiz_reference:
            add_pay_body["reference"] = workiz_reference[:255]

        try:
            resp = requests.post(add_pay_url, json=add_pay_body, timeout=15)
            if resp.status_code not in (200, 201, 204):
                return {'success': False, 'error': 'Workiz addPayment failed', 'status': resp.status_code, 'body': resp.text[:500]}
        except Exception as e:
            return {'success': False, 'error': 'Workiz addPayment error: ' + str(e)}

        print("[OK] Payment added in Workiz")

    # 5) Mark job Done ONLY when invoice balance is zero (fully paid)
    invs2 = odoo_call("account.move", "read", [[invoice_id]], {"fields": ["payment_state", "amount_residual"]})
    is_fully_paid = invs2 and (invs2[0].get("payment_state") == "paid" or float(invs2[0].get("amount_residual", 1)) == 0)

    if not is_fully_paid:
        print("[OK] Invoice not fully paid yet; job NOT marked Done (balance > 0)")
        print("="*70)
        return {'success': True, 'invoice_id': invoice_id, 'job_uuid': job_uuid, 'amount': amount_total, 'workiz_type': workiz_type, 'payment_date': payment_date, 'mark_done': 'skipped', 'reason': 'invoice_balance_not_zero'}

    # Fetch job to verify technician is assigned — Workiz requires a tech to mark Done
    # If no tech: stop and return clear error. Every job must have a tech.
    team_ids = []
    try:
        get_url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
        get_resp = requests.get(get_url, timeout=15)
        if get_resp.status_code == 200:
            get_data = get_resp.json().get('data', {})
            job_rec = get_data[0] if isinstance(get_data, list) and get_data else get_data
            raw_team = job_rec.get('Team') or []
            team_ids = [t['id'] for t in raw_team if t.get('id')]
    except Exception as e:
        print(f"[!] Could not fetch job to check tech: {e}")

    if not team_ids:
        print(f"[!] BLOCKED: Job {job_uuid} has no technician assigned — cannot mark Done")
        return {'success': False, 'add_payment': 'ok', 'mark_done': 'blocked',
                'reason': f"Job {job_uuid} has no technician assigned. Assign a tech in Workiz first, then re-invoice to trigger Phase 6 again."}

    print(f"[*] Tech verified (TeamId: {team_ids}) — proceeding to mark Done")
    update_url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/update/"
    update_body = {"auth_secret": WORKIZ_AUTH_SECRET, "UUID": job_uuid, "Status": "Done", "TeamId": team_ids}
    try:
        resp2 = requests.post(update_url, json=update_body, timeout=15)
        if resp2.status_code not in (200, 201, 204):
            return {'success': True, 'add_payment': 'ok', 'mark_done': 'failed', 'status': resp2.status_code, 'body': resp2.text[:500]}
    except Exception as e:
        return {'success': True, 'add_payment': 'ok', 'mark_done': 'error: ' + str(e)}

    print("[OK] Job marked Done (invoice fully paid)")

    # 5b) Move linked tasks to Done stage
    try:
        so_id = sos[0]["id"]
        task_ids = odoo_call("project.task", "search", [[["sale_order_id", "=", so_id]]])
        if task_ids:
            odoo_call("project.task", "write", [task_ids, {"stage_id": 19}])
            print(f"[OK] {len(task_ids)} task(s) moved to Done")
    except Exception as e:
        print(f"[!] Could not close tasks: {e}")

    # 5c) Flip pricing_mismatch to green on the SO — clears yellow CC warning or any prior state
    try:
        so_id = sos[0]["id"]
        amt = float(inv.get("amount_total") or amount_total or 0)
        amt_str = '{:.2f}'.format(amt)
        green_html = '<span class="text-success"><b>OK - Workiz: $' + amt_str + ' | Odoo: $' + amt_str + '</b></span>'
        odoo_call("sale.order", "write", [[so_id], {"x_studio_pricing_mismatch": green_html}])
        print("[OK] Pricing check set to green")
    except Exception as e:
        print(f"[!] Could not update pricing_mismatch: {e}")

    # 6) Trigger Phase 5 so follow-up activity (or next maintenance job) is created. When we mark Done via API, Workiz often does not fire "Job Status Changed", so Phase 4/5 would never run otherwise.
    if PHASE5_WEBHOOK_URL:
        try:
            so_id = sos[0]["id"]
            so_read = odoo_call("sale.order", "read", [[so_id]], {"fields": ["partner_id"]})
            if so_read:
                # SO partner_id = Property (usually) or Contact. Contact = Property.parent_id. If partner is Contact (no Property), use partner as contact_id.
                partner_id_raw = so_read[0].get("partner_id")
                if partner_id_raw:
                    pid = partner_id_raw[0] if isinstance(partner_id_raw, (list, tuple)) else partner_id_raw
                    prop_read = odoo_call("res.partner", "read", [[pid]], {"fields": ["parent_id", "city", "x_studio_x_studio_record_category"]})
                    if prop_read:
                        rec = prop_read[0]
                        parent = rec.get("parent_id")
                        cid = parent[0] if isinstance(parent, (list, tuple)) else parent if parent else None
                        category = (rec.get("x_studio_x_studio_record_category") or "").strip()
                        # If partner is a Contact (e.g. SO 004096), no parent_id; use partner as contact_id and property_id so Phase 5 still runs
                        if not cid and category == "Contact":
                            cid = pid
                        customer_city_5 = (rec.get("city") or "") if prop_read else ""
                        if pid and cid:
                            phase5_data = {"job_uuid": job_uuid, "property_id": pid, "contact_id": cid, "customer_city": customer_city_5, "invoice_id": invoice_id}
                            r5 = requests.post(PHASE5_WEBHOOK_URL, json=phase5_data, timeout=15)
                            if r5.status_code == 200:
                                print("[OK] Phase 5 triggered (follow-up activity or next job)")
                            else:
                                print(f"[!] Phase 5 webhook returned {r5.status_code}")
                        else:
                            print("[!] Property missing parent_id (Contact) - Phase 5 not triggered")
                else:
                    print("[!] SO missing partner_id (Property) - Phase 5 not triggered")
            else:
                print("[!] Could not read SO for Phase 5")
        except Exception as e:
            print(f"[!] Phase 5 trigger failed: {e}")

    print("="*70)
    return {'success': True, 'invoice_id': invoice_id, 'job_uuid': job_uuid, 'amount': amount_total, 'workiz_type': workiz_type, 'payment_date': payment_date}


# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # For local testing
    test_input = {'invoice_id': 123}  # Replace with real paid invoice id
    result = main(test_input)
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print(result)
    print("="*70)
else:
    # For Zapier deployment
    output = main(input_data)
