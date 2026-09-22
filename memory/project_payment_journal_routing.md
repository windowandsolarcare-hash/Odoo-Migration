---
name: project_payment_journal_routing
description: How the app books payments to account.journals. VENMO → journal 29 (+ inbound line 46); everything else (check/cash/zelle/credit) → Chase (journal 6). There are MULTIPLE payment-register sites + _execute_payment copies — a future payment change must cover ALL live ones. payment_method_line_id is JOURNAL-SPECIFIC.
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T00:52:06.709Z
---

**Venmo journal routing (2026-09-21, commit 641bc664, DJ-approved + Lead-QC'd).** Fixed: every payment method was hardcoded to `journal_id: 6` (Chase Checking) + memo. DJ: Venmo funds sit in a SEPARATE Venmo account, so a Venmo payment must book to the **VENMO journal (29)**; he manually transfers Venmo→Chase as his own bank entry.

## The rule (per-method journal)
- **VENMO → journal 29** (name "Venmo", code VENMO, bank, company 1) + journal-29's **inbound Manual-Payment line 46** + memo "Venmo".
- **check / cash / zelle / credit → journal 6 (Chase Checking)**, UNCHANGED. DJ confirmed **Zelle drops straight into Chase — NO separate Zelle journal** (do NOT use journal 19, even though the CLAUDE.md constants table historically listed 19=Zelle — that line was wrong for the payment flow; Lead corrected the bible).
- **★ `payment_method_line_id` is JOURNAL-SPECIFIC** — journal 6's inbound lines are 41/51; journal 29's inbound Manual-Payment is **46**. So venmo must pair (journal 29 + pml 46); reusing a journal-6 pml with journal 29 is invalid. Verify pmls live: `account.payment.method.line` where `journal_id=<id>`, `payment_type='inbound'`.

## The pattern (default-preserving) — BELT-AND-SUSPENDERS (commit ef95551e, live 2026-09-22)
The first fix (641bc664) keyed only on the `method` arg (`_method_journal.get(method,(6,None))`). Lead caught the gap: **2 legacy callers pass `method='cash', memo='Venmo'`** (the `/api/record_venmo_payment` path via `_stale_so_payment` in dashboard.py:10624 + payments.py:1194) → still misrouted to journal 6. So the register sites are now **memo-aware**:
```
_is_venmo = (raw_method == 'venmo') or ('venmo' in str(memo or '').lower())
if _is_venmo:
    _journal_id, pml = 29, 46
else:
    _journal_id = 6   # existing pml unchanged
# ...register.create: 'journal_id': _journal_id, 'payment_method_line_id': pml
```
AND the 2 gap callers were changed from `('cash','Venmo')` → `('venmo','Venmo')` (canon). Verified routing table offline: venmo* + cash/Venmo → 29; cash/Cash, cash/Zelle, zelle, check, credit → 6 (byte-identical). Non-venmo path untouched.

**★ BEHAVIOR NOTE (flagged to Lead):** changing the 2 callers to canon `'venmo'` means the manual venmo path now sends the `finalize_payment` "Funds Received" thank-you text (REMOTE-method behavior, idem-deduped — consistent with paywatch). If unwanted, revert JUST the caller args to `'cash'` — the memo-aware belt alone still fixes the journal. Left as-is pending Lead's call.

## ★ ALL payment-register sites (a future payment change MUST cover every LIVE one)
LIVE venmo-reachable (all fixed with the pattern):
1. `dashboard._execute_payment` (~4850) — the SHARED recorder: paywatch email-payment Approve, the stale-SO page, check/credit endpoints (via `_stale_so_payment`→here), payments.py `_stale_so_payment`→here, AND the tech app→here. Fix ONE = many paths.
2. `dashboard.record_check_payment` (~2256) — the voice-assistant AI payment tool (its own register).
3. `dashboard.api_process_payment_with_sync` (~11793) — LIVE `/owner/api/process_payment_with_sync` (its own register).
4. `tech/payments.py` `_METHODS` — the technician app: it maps tech method→(canon, memo) and was converting **venmo→canon 'cash'** (→ j6); now venmo→`('venmo','Venmo')` so it reaches _execute_payment's venmo branch → j29.
DEAD / not-venmo (correctly untouched): `payments.py api_process_payment_with_sync` (~1931 — DEAD doubled-prefix `/owner/owner/…`, shadowed by dashboard); `field.py _execute_payment`/`execute_write_tool` (DEAD — field is included AFTER dashboard in main.py → shadowed; no direct importer); Stripe card recorders `dashboard`(~6191, j7) + `payments._stripe_record_and_close`(~728, j6, via carddoor) — venmo can't reach them.

## P&L report bucket (cron.py)
`_JNL_BUCKET[29]='Venmo'`; added `elif 'venmo' in memo: bucket='Venmo'` (BEFORE the zelle check); 'Venmo' added to the bucket set + display labels. So Venmo income reports as "Venmo", not "Check".

## Verify-before-real-money gate (Lead's rule for a never-posted journal/pml pairing)
Push → fetch-diff confirm → a **$1 THROWAWAY** venmo record via the app → odoo-read the resulting `account.payment` has `journal_id=29` + `payment_method_line_id=46` → delete → ONLY THEN a real venmo payment.

★ RULE-9 FOLLOW-UP (durable): there are ≥3 `_execute_payment`-style recorders + ≥5 scattered method→journal/pml maps across dashboard/field/payments/tech. The dead ones still hold `venmo→6` and are landmines for a future refactor. The durable fix = ONE shared `payment_journal_and_pml(method)` helper in shared.py that every register site imports. Not done (scope); flagged. See [[feedback_question_when_big_picture_wrong]], [[feedback_reuse_canonical_endpoint]], and CLAUDE.md SYSTEM CONSTANTS (account.journal ids).
