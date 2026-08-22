---
name: Chatter message formatting standard
description: All Odoo chatter messages must use pipe-separated plain text — no HTML tags
type: feedback
---

Use pipe-separated plain text for all `message_post` body values. Never use HTML tags (`<br/>`, `<p>`, `<strong>`, etc.).

**Why:** Odoo escapes HTML tags in chatter in two scenarios: (1) external JSON-RPC calls from Zapier always escape HTML; (2) Odoo 17+ server actions also escape HTML unless you use `Markup`, which requires an import that safe_eval blocks. Plain text with `|` separators looks clean and works everywhere.

**How to apply:**
```python
# CORRECT — works from both server actions and Zapier JSON-RPC
record.message_post(body='[2026-04-02 07:58:13] Synced from Workiz: Job Type: Maintenance | Tech: Dan Saunders | Workiz Status: Pending / Scheduled')

# WRONG — tags show as literal text
record.message_post(body='<p><strong>Synced</strong></p><br/>Job Type: Maintenance')
```

Format pattern: `[YYYY-MM-DD HH:MM:SS] Action label: Field: Value | Field: Value | Field: Value`

**Unicode emoji DOES work in chatter** — only HTML tags are escaped, not Unicode characters. Use emoji for status indicators:
```python
record.message_post(body='✅ COMPLETE: https://...')   # green checkmark
record.message_post(body='🔔 Follow-Up Activity Created | ...')
record.message_post(body='⚠️ WARNING: ...')
record.message_post(body='❌ FAILED: ...')
```
DJ prefers `✅` for completion messages. Use it on all success/completion `message_post` calls.
