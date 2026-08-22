---
name: project_categorize_bank_line_mechanic
description: How to categorize/reconcile a Chase bank-feed line in Odoo 19 via API — repoint its suspense move line to the target account. Proven reversible 2026-06-07.
metadata: 
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

**To categorize a bank-feed statement line in Odoo 19 (clear it out of Bank Suspense):**

Each `account.bank.statement.line` has a posted `account.move` (move_type=`entry`) with exactly 2 lines:
- bank line on `101401` Chase Checking (account id **100**) — the real money side
- suspense line on `101402` Bank Suspense (account id **101**) — the uncategorized counterpart

**Categorize = write the SUSPENSE line's `account_id` to the target account.** Odoo then auto-flips `is_reconciled` to True on the statement line. No draft/repost needed — works on the posted move directly.

```python
# ids and vals as SEPARATE positional args (this is the gotcha that bit us first)
models.execute_kw(DB,UID,KEY,'account.move.line','write',[<suspense_line_id>],{'account_id':<target_acct_id>})
```

**Proven 2026-06-07** on stmt line 2286 (Panera $18.38): suspense(101402) → 671000 Meals flipped is_reconciled False→True; reverting account_id back to 101 flipped it False again. Fully reversible.

**Find the suspense line of a statement line:** read `account.bank.statement.line.move_id` → read move `line_ids` → the line whose `account_id` code == `101402` is the suspense line.

**CALL CONVENTION (xmlrpc helper):** `call(model,method,*a,**k)` → `execute_kw(...,model,method,list(a),k)`. For `write` you MUST pass `call('m','write',[ids],{vals})` — ids and vals as two separate args. Passing `[[ids],{vals}]` as one arg → "write() missing 1 required positional argument: 'vals'". See [[feedback_odoo_rpc_write_pattern]].

Related: [[project_bank_feed_qb_double_booking]] (the cleanup this enables). account_id 85 = 671000 Meals & Entertainment.

---

**RETIRING a QB duplicate (feed wins) — reverse via `account.move.reversal` wizard:**
```python
wiz=call('account.move.reversal','create',{'move_ids':[(6,0,[qb_move_id])],'date':<ORIGINAL_QB_DATE>,'journal_id':<misc_ops_jid>,'reason':'...'})
call('account.move.reversal','reverse_moves',[wiz])  # creates+posts reversal, links reversed_entry_id
```
Net per matched pair after (categorize feed→cat) + (reverse QB): Chase single outflow, category single expense, suspense 0. Verified 2026-06-07.

**🔴 CRITICAL DATE GOTCHA (cost a rework 2026-06-07):** The reversal's `date` MUST equal the ORIGINAL QB move's date, NOT a constant/cutoff date. I batched 795 reversals all dated `2024-11-25` (the cutoff) → the expense offsets landed in Nov 2024 while 2025/2026 stayed DOUBLED. All-time total was right but per-YEAR P&L was wrong (tax-year matters). Fix: per-move reversal date.

**To FIX a posted move's date:** `account.move.write([id],{'date':...})` — this silently RESETS the move to `draft` (state goes posted→draft on date edit). Must `account.move.action_post([ids])` after. Reconciliation with the original may drop but P&L (amounts+dates) is what matters. Batch pattern: group by target date → bulk write date → `action_post` in chunks of 100.
