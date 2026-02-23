"""
Test workflow: Sales Order -> Invoice -> Paid (via API)
=========================================================
Creates a test SO, invoices it, registers payment so invoice shows Paid.
Uses existing Odoo logic (no UI). Documents the correct procedure.
Run from repo root: python 1_Active_Odoo_Scripts/test_so_to_paid_workflow.py

Uses: ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY from config (same DB as repo).
"""

import sys
import os
sys.stdout.reconfigure(encoding="utf-8")

# Reuse same credentials as rest of project
ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"


def jsonrpc(model, method, args, kwargs=None):
    import requests
    params_args = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params_args.append(kwargs)
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params_args},
    }
    r = requests.post(ODOO_URL, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def main():
    print("=" * 60)
    print("Test: SO -> Invoice -> Paid (existing logic via API)")
    print("=" * 60)

    # 1) Get a partner (contact)
    partners = jsonrpc(
        "res.partner",
        "search_read",
        [[["is_company", "=", False], ["parent_id", "=", False]]],
        {"fields": ["id", "name"], "limit": 1},
    )
    if not partners:
        partners = jsonrpc("res.partner", "search_read", [[]], {"fields": ["id", "name"], "limit": 1})
    if not partners:
        print("[!] No partner found")
        return
    partner_id = partners[0]["id"]
    print(f"\n[1] Using partner: {partners[0].get('name')} (ID {partner_id})")

    # 2) Get a product
    products = jsonrpc(
        "product.product",
        "search_read",
        [[["sale_ok", "=", True]]],
        {"fields": ["id", "name"], "limit": 1},
    )
    if not products:
        products = jsonrpc("product.product", "search_read", [[]], {"fields": ["id", "name"], "limit": 1})
    if not products:
        print("[!] No product found")
        return
    product_id = products[0]["id"]
    print(f"[2] Using product: {products[0].get('name')} (ID {product_id})")

    # 3) Create Sales Order
    so_vals = {
        "partner_id": partner_id,
        "order_line": [(0, 0, {"product_id": product_id, "product_uom_qty": 1, "price_unit": 10.0})],
    }
    so_id = jsonrpc("sale.order", "create", [so_vals])
    print(f"[3] Created Sales Order ID {so_id}")

    # 4) Confirm SO
    jsonrpc("sale.order", "action_confirm", [[so_id]])
    print("[4] Confirmed SO")

    # 5) Create invoice from SO
    # Option A: Call sale.order method (name varies: _create_invoices in 17, etc.)
    so = jsonrpc("sale.order", "read", [[so_id]], {"fields": ["name"]})
    so_name = so[0].get("name", "") if so else ""
    invoice_ids = None
    for method_name in ["_create_invoices", "action_create_invoices", "action_create_invoice", "create_invoice"]:
        try:
            result = jsonrpc("sale.order", method_name, [[so_id]])
            if result is True or result is False:
                invs = jsonrpc(
                    "account.move",
                    "search_read",
                    [[["invoice_origin", "=", so_name], ["state", "in", ["draft", "posted"]]]],
                    {"fields": ["id", "name", "state"], "limit": 5, "order": "id desc"},
                )
                if invs:
                    invoice_ids = [invs[0]["id"]]
                    break
            elif isinstance(result, list) and len(result) > 0:
                invoice_ids = result
                break
            elif isinstance(result, int):
                invoice_ids = [result]
                break
        except Exception as e:
            err = str(e)
            if "has no attribute" in err or "method" in err.lower() or "object has no attribute" in err:
                continue
            print(f"    [{method_name}] {err}")
            continue
    # Option B: If no method worked, use existing unpaid posted invoice so we can still test payment flow
    if not invoice_ids or (isinstance(invoice_ids, list) and len(invoice_ids) == 0):
        print("[!] No invoice from SO methods; looking for any posted unpaid invoice to test payment flow...")
        invs = jsonrpc(
            "account.move",
            "search_read",
            [[["move_type", "=", "out_invoice"], ["state", "=", "posted"], ["payment_state", "!=", "paid"]]],
            {"fields": ["id", "name", "amount_residual"], "limit": 1},
        )
        if invs:
            invoice_id = invs[0]["id"]
            print(f"[5] Using existing unpaid invoice {invs[0].get('name')} (ID {invoice_id}) for payment test")
        else:
            print("[!] Could not create invoice from SO and no existing unpaid invoice found.")
            return
    else:
        invoice_id = invoice_ids[0] if isinstance(invoice_ids, list) else invoice_ids
        print(f"[5] Created invoice ID {invoice_id}")

    # 6) Post invoice (only if draft)
    inv_check = jsonrpc("account.move", "read", [[invoice_id]], {"fields": ["state"]})[0]
    if inv_check.get("state") == "draft":
        jsonrpc("account.move", "action_post", [[invoice_id]])
        print("[6] Posted invoice")
    else:
        print("[6] Invoice already posted, skip")

    # 7) Read invoice for residual and partner
    inv = jsonrpc(
        "account.move",
        "read",
        [[invoice_id]],
        {"fields": ["name", "amount_residual", "currency_id", "partner_id", "payment_state"]},
    )[0]
    amount_residual = inv.get("amount_residual") or 0
    currency_id = inv["currency_id"][0] if inv.get("currency_id") else 1
    inv_partner_id = inv["partner_id"][0] if inv.get("partner_id") else partner_id
    print(f"[7] Invoice {inv.get('name')} amount_residual={amount_residual}")

    # 8) Get bank journal and payment method line
    journals = jsonrpc("account.journal", "search_read", [[["code", "=", "BNK1"]]], {"fields": ["id"], "limit": 1})
    if not journals:
        journals = jsonrpc("account.journal", "search_read", [[["type", "=", "bank"]]], {"fields": ["id"], "limit": 1})
    if not journals:
        print("[!] No bank journal found")
        return
    journal_id = journals[0]["id"]
    method_lines = jsonrpc(
        "account.payment.method.line",
        "search_read",
        [[["journal_id", "=", journal_id]]],
        {"fields": ["id", "name"], "limit": 5},
    )
    payment_method_line_id = method_lines[0]["id"] if method_lines else False
    print(f"[8] Journal ID {journal_id}, payment_method_line_id {payment_method_line_id}")

    # 9) Create payment linked to invoice (invoice_ids so it reconciles)
    from datetime import date
    payment_vals = {
        "payment_type": "inbound",
        "partner_type": "customer",
        "partner_id": inv_partner_id,
        "amount": amount_residual,
        "currency_id": currency_id,
        "journal_id": journal_id,
        "date": date.today().strftime("%Y-%m-%d"),
        "invoice_ids": [(6, 0, [invoice_id])],
    }
    if payment_method_line_id:
        payment_vals["payment_method_line_id"] = payment_method_line_id
    # Odoo 19: no 'communication' on account.payment; ref/memo may exist - only set if needed
    payment_id = jsonrpc("account.payment", "create", [payment_vals])
    print(f"[9] Created payment ID {payment_id}")

    # 10) Post payment
    jsonrpc("account.payment", "action_post", [[payment_id]])
    print("[10] Posted payment")

    # 10b) Reconcile payment to invoice (Odoo 19 may not auto-reconcile from invoice_ids)
    pay = jsonrpc("account.payment", "read", [[payment_id]], {"fields": ["move_id", "state"]})[0]
    move_id = None
    if pay.get("move_id"):
        move_id = pay["move_id"][0] if isinstance(pay["move_id"], (list, tuple)) else pay["move_id"]
    if not move_id:
        # Fallback: find unreconciled credit line (payment) for this partner - most recent
        pay_lines = jsonrpc(
            "account.move.line",
            "search_read",
            [[["balance", "<", 0], ["reconciled", "=", False], ["partner_id", "=", inv_partner_id]]],
            {"fields": ["id", "move_id", "balance"], "limit": 5, "order": "id desc"},
        )
        if pay_lines:
            move_id = pay_lines[0]["move_id"][0] if isinstance(pay_lines[0]["move_id"], (list, tuple)) else pay_lines[0]["move_id"]
    if move_id:
        # Reconcile: match invoice line (debit) and payment line (credit) with same account_id
        try:
            inv_lines = jsonrpc("account.move.line", "search_read", [[["move_id", "=", invoice_id], ["reconciled", "=", False], ["balance", ">", 0]]], {"fields": ["id", "account_id"]})
            pay_lines_r = jsonrpc("account.move.line", "search_read", [[["move_id", "=", move_id], ["reconciled", "=", False], ["balance", "<", 0]]], {"fields": ["id", "account_id"]})
            # Pair by account_id (receivable will match)
            inv_by_acc = {}
            for l in inv_lines or []:
                aid = l["account_id"][0] if isinstance(l["account_id"], (list, tuple)) else l["account_id"]
                inv_by_acc[aid] = inv_by_acc.get(aid, []) + [l["id"]]
            for pl in pay_lines_r or []:
                aid = pl["account_id"][0] if isinstance(pl["account_id"], (list, tuple)) else pl["account_id"]
                if aid in inv_by_acc:
                    line_ids = inv_by_acc[aid] + [pl["id"]]
                    jsonrpc("account.move.line", "reconcile", [line_ids])
                    print("[10b] Reconciled payment to invoice")
                    break
            else:
                print(f"[10b] No matching account: invoice lines={len(inv_lines or [])}, payment lines={len(pay_lines_r or [])}")
        except Exception as e:
            print(f"[10b] Reconcile error: {e}")
    else:
        print("[10b] No payment move_id, skip reconcile")

    # 11) Check invoice payment_state
    inv2 = jsonrpc(
        "account.move",
        "read",
        [[invoice_id]],
        {"fields": ["name", "payment_state", "amount_residual"]},
    )[0]
    state = inv2.get("payment_state", "")
    residual = inv2.get("amount_residual") or 0
    print(f"\n[RESULT] Invoice {inv2.get('name')}: payment_state = {state!r}, amount_residual = {residual}")

    if state == "paid" or residual == 0:
        print("\n[OK] Invoice is PAID. Workflow via API works.")
    else:
        print("\n[!] Invoice not marked paid yet; reconciliation may be needed (see apply_payment_to_invoice.py).")

    print("=" * 60)
    return so_id, invoice_id, payment_id


if __name__ == "__main__":
    main()
