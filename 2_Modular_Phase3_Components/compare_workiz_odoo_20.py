"""
Compare the 20 non-Bev jobs: Workiz vs Odoo SO. Report any mismatches.
Run from 2_Modular_Phase3_Components.
"""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.workiz.get_job_details import get_job_details

UUIDS = [
    "YHDBIB", "5EMPGR", "OQ0S9A", "R1OA3W", "FLBUHG", "LZI230", "TJMC1S", "BX5XTJ",
    "478XAY", "ITXZ5K", "91EHYO", "4GT35W", "QX41IW", "RXNAI8", "NO8DS6", "53OCNO",
    "QTTR4J", "UIBSKK", "L7SF9F", "UD8Z45",
]


def get_odoo_so(workiz_uuid):
    """Fetch SO by Workiz UUID with all comparable fields."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order",
                "search_read",
                [[["x_studio_x_studio_workiz_uuid", "=", workiz_uuid]]],
                {
                    "fields": [
                        "id", "name",
                        "partner_id", "partner_shipping_id",
                        "x_studio_x_studio_workiz_status",
                        "x_studio_x_studio_x_studio_job_type",
                        "x_studio_x_studio_lead_source",
                        "x_studio_x_studio_workiz_tech",
                        "x_studio_x_gate_snapshot",
                        "x_studio_x_studio_pricing_snapshot",
                        "x_studio_x_studio_notes_snapshot1",
                        "amount_total",
                    ],
                    "limit": 1,
                },
            ],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=10)
    res = r.json().get("result", [])
    return res[0] if res else None


def norm(s):
    return str(s or "").strip()


def workiz_team_str(team):
    if not team:
        return ""
    if isinstance(team, list):
        names = []
        for m in team:
            if isinstance(m, dict):
                names.append((m.get("Name") or m.get("name") or "").strip())
            elif m:
                names.append(str(m).strip())
        return ", ".join(n for n in names if n)
    return str(team).strip() if team else ""


def workiz_line_total(line_items):
    total = 0
    for item in (line_items or []):
        if isinstance(item, dict):
            qty = float(item.get("Quantity", 1))
            price = float(item.get("Price", 0))
            total += qty * price
    return round(total, 2)


def compare_one(uuid, w, o):
    diffs = []
    # Customer
    w_cust = norm((w.get("FirstName") or "") + " " + (w.get("LastName") or ""))
    o_cust = (o.get("partner_id") or [None, ""])[1] if isinstance(o.get("partner_id"), list) else (o.get("partner_id") or "")
    if norm(str(o_cust)) != w_cust:
        diffs.append(("Customer", w_cust, o_cust))
    # Address (property) - Odoo shipping is often display name
    w_addr = norm(w.get("Address") or "")
    o_ship = o.get("partner_shipping_id")
    o_addr = (o_ship[1] if isinstance(o_ship, list) else str(o_ship or "")) or ""
    if norm(o_addr) != w_addr:
        diffs.append(("Address", w_addr[:50], (o_addr or "")[:50]))
    # Order name (SerialId)
    w_name = norm(w.get("SerialId") or "")
    o_name = norm(o.get("name") or "")
    if o_name and w_name and o_name != w_name:
        diffs.append(("Order name", w_name, o_name))
    # Status
    w_status = norm(w.get("SubStatus") or w.get("Status") or "")
    o_status = norm(o.get("x_studio_x_studio_workiz_status") or "")
    if o_status != w_status:
        diffs.append(("Status", w_status, o_status))
    # Job type
    w_type = norm(w.get("JobType") or w.get("Type") or "")
    o_type = norm(o.get("x_studio_x_studio_x_studio_job_type") or "")
    if o_type != w_type:
        diffs.append(("Job type", w_type, o_type))
    # Lead source
    w_src = norm(w.get("JobSource") or "")
    o_src = norm(o.get("x_studio_x_studio_lead_source") or "")
    if o_src != w_src:
        diffs.append(("Lead source", w_src, o_src))
    # Tech
    w_tech = workiz_team_str(w.get("Team") or w.get("team"))
    o_tech = norm(o.get("x_studio_x_studio_workiz_tech") or "")
    if o_tech != w_tech:
        diffs.append(("Tech", w_tech, o_tech))
    # Gate
    w_gate = norm(str(w.get("gate_code") or w.get("GateCode") or ""))
    o_gate = norm(o.get("x_studio_x_gate_snapshot") or "")
    if o_gate != w_gate:
        diffs.append(("Gate", w_gate, o_gate))
    # Pricing
    w_pr = norm(str(w.get("pricing") or w.get("Pricing") or ""))
    o_pr = norm(o.get("x_studio_x_studio_pricing_snapshot") or "")
    if o_pr != w_pr:
        diffs.append(("Pricing", w_pr[:60], (o_pr or "")[:60]))
    # Notes (first 80 chars)
    w_notes = norm((w.get("JobNotes") or "") + " " + (w.get("Comments") or ""))[:80]
    o_notes = norm(o.get("x_studio_x_studio_notes_snapshot1") or "")[:80]
    if o_notes != w_notes:
        diffs.append(("Notes (snippet)", w_notes, o_notes))
    # Amount: Workiz line total vs Odoo amount_total
    w_total = workiz_line_total(w.get("LineItems") or [])
    o_total = float(o.get("amount_total") or 0)
    if w_total and abs(round(o_total, 2) - w_total) > 0.01:
        diffs.append(("Amount total", str(w_total), str(o_total)))
    return diffs


def main():
    print("Comparing 20 non-Bev jobs: Workiz vs Odoo SO\n")
    all_ok = 0
    any_diff = 0
    for i, uuid in enumerate(UUIDS, 1):
        w = get_job_details(uuid)
        if not w:
            print(f"{i:2}. {uuid}  SKIP (Workiz fetch failed)")
            if i < len(UUIDS):
                time.sleep(2)
            continue
        o = get_odoo_so(uuid)
        if not o:
            print(f"{i:2}. {uuid}  MISMATCH: No SO in Odoo for this UUID")
            any_diff += 1
            if i < len(UUIDS):
                time.sleep(2)
            continue
        diffs = compare_one(uuid, w, o)
        cust = norm((w.get("FirstName") or "") + " " + (w.get("LastName") or ""))
        if not diffs:
            print(f"{i:2}. {uuid}  {cust}  OK (mirrored)")
            all_ok += 1
        else:
            print(f"{i:2}. {uuid}  {cust}  DIFFS:")
            for field, w_val, o_val in diffs:
                print(f"      {field}: Workiz={w_val!r}  Odoo={o_val!r}")
            any_diff += 1
        if i < len(UUIDS):
            time.sleep(2)
    print("\n" + "="*60)
    print(f"Summary: {all_ok} fully mirrored, {any_diff} with diffs or missing")


if __name__ == "__main__":
    main()
