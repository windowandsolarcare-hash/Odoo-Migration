# Phase 6 Design — As It Looks Right Now

**Purpose:** Single snapshot of what Phase 6 is and how it’s designed today (no implementation yet).  
**Date:** February 2026

---

## 1. What Phase 6 Is (Agreed Scope)

In this handoff, **Phase 6 = Invoice Automation**.

- **Sync invoices** from Workiz (or the system that issues them) into Odoo.
- **Payment tracking** (paid/unpaid and optionally full payment transactions).
- **QuickBooks / accounting integration** (role TBD: mirror only, or Odoo as accounting).

**Out of scope for Phase 6 here:** Route Optimization (group jobs by neighborhood, optimal days). That’s Phase 5C or a later phase.

---

## 2. Two Flows That Show Up in the Docs

Phase 6 appears in two related but different ways in the handoff:

| Flow | Direction | Where it’s described | Status |
|------|-----------|----------------------|--------|
| **Invoice Automation** | Workiz → Odoo | Phase_6_Scope_and_Agreements, PROJECT_COMPLETE_SUMMARY, Zapier_Architecture_Complete | Agreed intent; not built |
| **Payment sync (Odoo first)** | Odoo → Workiz | Phase_3_4_5_Reference_Summary | Agreed design; not built |

### 2.1 Invoice Automation (Workiz → Odoo)

- **Source of truth:** Workiz (or current invoice system).
- **Target:** Odoo (mirror invoices/payment status for reporting/analytics and optionally accounting).
- **Conventions:** Same as Phases 3–5: mirror logic, hierarchy Client → Property → Job, external_id pattern (e.g. `workiz_invoice_[id]`).
- **Details:** What to sync (headers only vs lines vs payments), which invoices (e.g. only Done jobs), and trigger (webhook vs poll) are **to be confirmed with you** (see Phase_6_Scope_and_Agreements §4).

### 2.2 Payment Sync (Odoo → Workiz)

Described in **Phase_3_4_5_Reference_Summary** as “Phase 6”:

- **Flow:** Payment received at door → recorded in Odoo → Phase 6 runs (webhook or poll) → syncs payment to Workiz via `POST /job/addPayment/{UUID}/` → if balance = 0, mark job “Done” in Workiz → Phase 4 (and then Phase 5) run as today.
- **Conflict fix with Phase 4:** Phase 6 sets an Odoo SO field (e.g. `x_studio_payment_synced_from_odoo` datetime). Phase 4 checks this flag before reading payment from Workiz: if set, skip payment read; if not set, keep current behavior (read from Workiz as fallback).
- **Requires:** New Odoo custom field, Phase 4 logic change, Phase 6 script.

So **right now**, Phase 6 design includes:

1. **Invoice Automation** (Workiz → Odoo) — main scope in Scope & Agreements.
2. **Payment sync (Odoo → Workiz)** — designed in Phase 3/4/5 reference; can be part of Phase 6 or a separate first slice.

---

## 3. Agreements That Apply to Phase 6

(From Phase_6_Scope_and_Agreements; same as Phases 3–5 unless you change them.)

- **Zapier “Code by Zapier” hybrid:** Build and test in Python (e.g. in repo), deploy **flattened** (no `import`) script in Zapier.
- **Workiz as source of truth** for operational data; for Invoice Automation, invoice/payment data is assumed to originate in Workiz (or current system); Odoo mirrors.
- **Sync direction for invoices:** Workiz → Odoo (mirror), unless you ask for bi-directional or Odoo→Workiz.
- **One Number Strategy:** Customer comms (SMS, etc.) stay in Workiz; Phase 6 is invoices/payments only.
- **IDs:** Use `external_id = workiz_[id]` (or e.g. `workiz_invoice_[id]`) for mirrored entities.
- **Hierarchy:** Invoice/Payment ties back to Client → Property → Job (e.g. link to SO or contact per Odoo model and your preference).
- **Technical:** Odoo double-wrap search domains; Zapier flattened Python, integer IDs for Odoo; Workiz dual auth (API key in path + `auth_secret` in body).

---

## 4. What’s Not Decided Yet (Confirm Before Building)

(Summarized from Phase_6_Scope_and_Agreements §4.)

- **Workiz invoice API:** Does Workiz expose invoices/payments via API? If not, source = QuickBooks, export, or other?
- **Which invoices:** All, or only for jobs that reached “Done” (or other status)? Date range or go-live cutoff?
- **Payment tracking:** Status only (paid/unpaid) or full transactions (amount, date, method)? Where does that data live today?
- **Odoo side:** Use Odoo Invoicing (`account.move`) or only custom fields on SO (e.g. invoice number, paid date)?
- **QuickBooks vs Odoo:** (a) Workiz → Odoo for visibility, Odoo for accounting, (b) Workiz → QuickBooks and optionally mirror to Odoo, or (c) move to Odoo accounting over time?
- **Trigger:** Workiz webhook (if available) vs scheduled polling (e.g. Zapier).
- **MVP:** Agree Phase 6 MVP, e.g. “invoice headers + paid status from Workiz to Odoo” first, then payment details, then QuickBooks if needed.
- **Payment sync (Odoo → Workiz):** Confirm whether this is part of Phase 6 MVP or a separate first deliverable.

---

## 5. What Exists Today (No Phase 6 Code Yet)

- **Design and agreements:** In Phase_6_Scope_and_Agreements and Phase_3_4_5_Reference_Summary.
- **Architecture mentions:** PROJECT_COMPLETE_SUMMARY, Zapier_Architecture_Complete, START_HERE_First_Prompt.
- **No Phase 6 scripts, Zaps, or Odoo custom fields** for invoice/payment sync yet.
- **Phase 4** does not yet check `x_studio_payment_synced_from_odoo`; that change is part of the agreed Phase 6 (or payment-sync) work.

---

## 6. One-Sentence Summary

**Phase 6 right now:** Agreed as **Invoice Automation** (Workiz → Odoo sync, payment tracking, QuickBooks/accounting), with a **related Odoo→Workiz payment flow** (record in Odoo, push to Workiz, mark Done, Phase 4 flag) designed but not built; MVP, data source, and exact scope are still to be confirmed with you before implementation.
