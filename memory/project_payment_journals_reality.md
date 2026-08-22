---
name: project_payment_journals_reality
description: ALL app payments book into Chase Checking (journal 6); method buckets come from the MEMO via _detect_payment_method, NOT the journal. Method journals (17/18/19/29) are empty.
metadata:
  type: project
---

Verified 2026-07-21 (Charon Smith unwind follow-up): 310 of 311 account.payment records live in Chase Checking (journal 6); Check Payments (17), Cash (18), Zelle (19), Venmo (29) have ZERO payments; Credit Card (20) has 1. The payment flow writes the method into the MEMO (e.g. "Cash: Zelle") and reports resolve the bucket with _detect_payment_method (dashboard.py ~6555): payment_method_line -> else memo text contains zelle/venmo -> else cash.

**Why:** Zelle/cash/check money all physically deposits into Chase, so booking every payment straight into the Chase journal keeps the Odoo Chase ledger matching the real bank statement 1:1. The per-method journals were created (2026-06-07 constants table) but never wired into the payment flow. DJ confirmed Zelle money ultimately lives in Chase — this is the intended, correct setup.

**How to apply:** never "fix" a payment by moving it to journal 19/29 etc — reports don't read the journal. To make a payment count as Zelle/Venmo/Cash, the MEMO text is what matters. The CLAUDE.md journal->bucket table describes intent, not behavior — bucket detection is memo-based.
