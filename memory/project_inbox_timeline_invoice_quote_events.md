---
name: project_inbox_timeline_invoice_quote_events
description: "INBOX->TIMELINE (live 2026-10-26 main e27849c465, DJ option 'B'): when an invoice OR quote is SENT, the event ALSO threads into the UNIFIED INBOX (not just the SO chatter) as a labeled bubble. The taxonomy: a NEW dedicated inbox source token 'sent' (NOT 'system' which = customer-didn't-receive, NOT text/vm which force the default textvm view) + labels 'invoice'/'quote'. Covers why 'sent' exists, the dual-surface logging (sale.order chatter + res.partner/inbox), the no-HUD-card + honors-B guarantees, and the client<->server paired bucketing (bubbleView == _vmatch)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T05:32:05.817Z
---

**INBOX->TIMELINE for invoice/quote sends** (LIVE 2026-10-26 main `e27849c465`; §15 dual-GREEN Lead firsthand + Audit converge, auto-deploy, no customer send). When DJ SENDS an invoice or a quote, the send event now shows on TWO surfaces: (1) the **per-job timeline** (sale.order chatter, via `_log_invoice_sent`/`_log_quote_sent` message_post — the pre-existing half) AND (2) the **unified customer inbox** as a labeled bubble (the new half). DJ picked option **B**: they surface under 🗂 All + dedicated invoice/quote pills, but do NOT flip the default view (textvm stays default).

**THE KEY TAXONOMY DECISION — a NEW inbox source token `'sent'`:**
- The unified inbox classifies every message by `source` (`_INBOX_SOURCES`, sms.py:497) + optional `label` (`_INBOX_LABEL_TYPES`, sms.py:496). Added **`'sent'`** to sources and **`'invoice'`,`'quote'`** to labels.
- **Why NOT `source='system'`:** `metaExtras` (wsc_thread.js) tags EVERY `source='system'` bubble "📝 Note — not sent" (system := customer did NOT receive). An invoice/quote WAS received → 'system' is a semantic lie. **Why NOT `source='text'/'voicemail'`:** `bubbleView` buckets those into the DEFAULT textvm view → would violate B. So a dedicated `'sent'` (dir='out') was the only correct choice. (Lead rejected 'system'; Specialists owns the taxonomy → picked ONE shared token 'sent' for both; the LABEL invoice/quote distinguishes them.)

**WIRING (brain.py):** one shared helper `_inbox_timeline_event(so_id, label, body)` is called from BOTH `_log_invoice_sent` + `_log_quote_sent` AFTER their existing `message_post` (Rule 10 — adds, never replaces). It resolves the customer from the SO partner_id and calls `sms.append_inbox_event(body, source='sent', label='invoice'|'quote', partner_id=.., direction='out', so_id=.., index=True)`. Fully try/except-wrapped → a logging/inbox failure can NEVER break the send.

**INVARIANTS (all verified firsthand at QC):**
- **Honors B:** `has_textvm` (sms.py:413) counts only `source in ('text','voicemail')`, so a 'sent' event never sets it → excluded from the default textvm view. (A customer you also TEXTED still shows — it's a real conversation.) Server `_vmatch` (sms.py ~2618-2634) gains `invoice`/`quote` view buckets keyed on `last_label`, and EXCLUDES invoice/quote from the 'misc' fallthrough.
- **NO HUD action card:** `reminders._status_from_index` (reminders.py:1457) hard-filters the label-index to `('confirmed','reschedule','cancel')` — invoice/quote are ignored, so they never become actionable maint cards. Also a new event-born conv gets `status='answered', unread=False` (invoice/quote ∉ the reply-demanding set reschedule/cancel/question) → never nags.
- **NO double-post on the job timeline:** `append_inbox_event`->`_log_odoo` posts to **res.partner** chatter; the logger's own `message_post` posts to **sale.order** chatter — different records, so the per-job timeline (so_activity) shows it once.
- **No-phone customer:** `append_inbox_event` returns '' and skips threading gracefully (the SO-chatter record still happened); never raises.
- **PAIRED CHANGE (client<->server, keep in lockstep):** client `bubbleView` (wsc_thread.js) MUST bucket identically to server `_vmatch` (sms.py) — both lab-key `invoice->invoice`, `quote->quote`, exclude both from misc. Client renders a POSITIVE chip ("📄 Invoice sent"/"📝 Quote sent") keyed off LABEL, and maps `source='sent'`->📤 glyph. Changing one side's bucketing REQUIRES the other.

**Tracked LOW fast-follow (non-block):** the visible link TEXT in an inbox bubble shows a literal `&amp;` for an `&`-bearing URL (shared `bodyHtml` double-escapes the display string); the href/tap works. Pre-existing shared-renderer behavior, not new here.

**How to apply:** any future "also surface an outbound system-generated-but-customer-DELIVERED event in the inbox" → use `source='sent'` (NOT 'system'), dir='out', a descriptive label, and KEEP the existing chatter log. If you add a new inbox label/source, add it to `_INBOX_LABEL_TYPES`/`_INBOX_SOURCES` (else append_inbox_event's downgrade guards silently rewrite it → mislabeled) AND update BOTH `_vmatch` and `bubbleView`. See [[project_send_quote_and_branded_pages]], [[feedback_hud_cards_live_not_inbox]], [[feedback_field_whitelist_strip_silent_inert]].
