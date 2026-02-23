# Phase 6: Scope and Agreements (What’s Not Elsewhere)

**Purpose:** Single place for Phase 6 intent and development agreements. Written so the new chat has everything that was agreed or assumed but wasn’t already in the other handoff docs.  
**Date:** February 9, 2026

---

## 1. Which “Phase 6” This Is

In **this handoff**, **Phase 6 = Invoice Automation** (sync invoices from Workiz, payment tracking, QuickBooks/accounting integration). That’s what’s in PROJECT_COMPLETE_SUMMARY and Zapier_Architecture_Complete.

**Naming note:** In `BUSINESS_OVERVIEW_For_Partners.md`, “Phase 6” is used for **Route Optimization** (group jobs by neighborhood, optimal days, minimize drive time). In the **technical** docs and this folder, Route Optimization is **Phase 5C** or a later enhancement. So for development:

- **Phase 6 = Invoice Automation** (this doc and the next chat).
- Route Optimization = Phase 5C / future phase; not part of Phase 6 scope here.

---

## 2. What’s Already in the Phase 6 Handoff Docs

Already in this folder (no need to duplicate):

- **PROJECT_COMPLETE_SUMMARY.md** — Phase 6 bullets: “Sync invoices from Workiz”, “Payment tracking”, “QuickBooks integration”.
- **Zapier_Architecture_Complete.md** — “Phase 6: Invoice Automation (Potential)” — sync Workiz → Odoo, payment tracking, accounting integration.
- **START_HERE_First_Prompt.md** — States Phase 6 = Invoice Automation (future), not yet implemented.

So the **high-level scope** is documented; what was missing was **agreements and implementation context** (below).

---

## 3. Agreements and Conventions to Carry Forward (Develop Phase 6 With These)

These match how Phases 3–5 were built and should apply to Phase 6 unless you explicitly change them with the user.

### 3.1 Architecture and integration

- **Zapier “Code by Zapier” hybrid:** Build and test logic in Python (e.g. in this repo), then deploy a **flattened** (no `import` statements) script into Zapier. Same pattern as Phase 3/4/5.
- **Workiz as source of truth for operational data:** Jobs and status live in Workiz; Odoo mirrors. For Phase 6, **invoice/payment data** is assumed to originate in Workiz (or whatever system actually issues invoices today); Odoo is the “brain” for reporting/analytics and optionally accounting.
- **Sync direction:** Workiz → Odoo for invoice/payment data (mirror, not the other way around), unless the user explicitly asks for bi-directional or Odoo→Workiz.
- **One Number Strategy:** Customer-facing communications (SMS, etc.) go through Workiz, not Odoo. Phase 6 is about **invoices and payments**, not sending messages; no change to that rule unless the user says otherwise.

### 3.2 IDs and hierarchy

- **Mirror V31.11 logic:** Use `external_id = workiz_[id]` for any Workiz entity we mirror in Odoo. If we create Odoo invoice/accounting records from Workiz invoices, link them the same way (e.g. `workiz_invoice_[id]` or as agreed).
- **Hierarchy:** Client → Property → Job is established. Phase 6 adds **Invoice/Payment**; these should tie back to the same hierarchy (e.g. invoice linked to job/SO or to contact, depending on Odoo’s model and user preference).
- **Reference data:** Keep using `Workiz_6Year_Done_History_Master.csv` and existing refs for history and consistency.

### 3.3 Technical constraints (from existing handoff)

- **Odoo Server Actions:** No `import` in Odoo sandbox; use built-ins and `env[...]`. If Phase 6 uses Server Actions, same rules apply.
- **Zapier:** Flattened Python only (no imports). Record IDs as **integers** when calling Odoo.
- **Odoo search domains:** Double-wrap: `[[["field", "=", "value"]]]`.
- **Workiz API:** Dual auth (API key in path + `auth_secret` first in JSON body for POST).

---

## 4. What Was Not in the Docs (Decisions to Confirm With User)

These were **not** written down in the repo; the next chat should confirm before implementing.

### 4.1 Scope and data source

- **Workiz invoice API:** Does Workiz expose invoices (and payments) via API? If not, is the source QuickBooks, manual export, or something else?
- **Which invoices to sync:** All invoices, or only those tied to jobs that reached “Done” (or another status)? Any date range or “go-live” cutoff?
- **Payment tracking:** Does “payment tracking” mean status (paid/unpaid) only, or full payment transactions (amount, date, method)? Where does that data live today?

### 4.2 Odoo side

- **Odoo model:** Use Odoo **Invoicing** (`account.move` / customer invoices) or only custom fields on existing SOs (e.g. “invoice number”, “paid date”)? Depends on whether the user wants full accounting in Odoo or just visibility.
- **QuickBooks vs Odoo accounting:** Is the goal (a) sync Workiz → Odoo for visibility and use Odoo for accounting, (b) sync Workiz → QuickBooks and optionally mirror to Odoo, or (c) replace QuickBooks with Odoo accounting over time? This drives whether we build a Zap to Odoo, to QuickBooks, or both.

### 4.3 Trigger and frequency

- **Trigger:** Workiz webhook when invoice is created/updated/paid (if available), or scheduled polling (e.g. Zapier polling)? Same “webhook if available, else poll” pattern as other phases.
- **Idempotency:** Use a stable external_id (e.g. `workiz_invoice_[id]`) so re-runs don’t create duplicates.

### 4.4 Priority and phasing

- **MVP:** Agree with user on “Phase 6 MVP”: e.g. “sync invoice headers and paid status from Workiz to Odoo” first, then payment details, then QuickBooks if needed.
- **Route Optimization:** Explicitly out of Phase 6 scope here; can be Phase 5C or Phase 7 depending on user preference.

---

## 5. Summary for the New Chat

- **Phase 6 in this handoff = Invoice Automation** (sync invoices, payment tracking, QuickBooks/accounting). Route Optimization is a different (later) phase.
- **Apply the same patterns:** Mirror V31.11, hierarchy, Zapier hybrid, Workiz as source of truth for invoice data, One Number Strategy unchanged.
- **Confirm with user:** Workiz invoice API, which invoices to sync, Odoo vs QuickBooks role, trigger (webhook vs poll), and MVP scope before building.
- **This doc** is the place for Phase 6 scope and agreements; the rest of the folder is Phases 1–5 and general project context.
