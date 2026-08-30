---
name: project_mail_watchers_two_mailboxes
description: "The three mail watchers read TWO DIFFERENT mailboxes. Paywatch = windowandsolarcare@gmail.com; NBHOF + Zoo watchers = dan@scenicartprint.com (the ORIGINAL, upstream of forwarding). All three read INBOX only, and the Zoo live watcher is UNSEEN-only. Never add an archive/mark-read filter to dan@scenicartprint.com."
metadata:
  node_type: memory
  type: project
---

**Verified 2026-08-30 by reading the code (not memory), while designing Gmail filters for DJ's inbox cleanup.**

## The mailbox split — this is the whole point

Three specialists read email over IMAP, and they do **not** all read the same account:

| Watcher | File | Mailbox | Credential |
|---|---|---|---|
| Paywatch (Venmo/Zelle) | `routers/owner/specialist_paywatch.py:44` | **windowandsolarcare@gmail.com** | `GMAIL_WSC_APP_PASSWORD` |
| NBHOF PO watcher | `routers/printing/watcher.py:21` | **dan@scenicartprint.com** | `GMAIL_SCENIC_APP_PASSWORD` |
| Zoo Printing watcher | `routers/printing/zoo_watcher.py:10` (imports `GMAIL_USER`/`GMAIL_PASS` from watcher.py) | **dan@scenicartprint.com** | `GMAIL_SCENIC_APP_PASSWORD` |

**Mail flow:** `dan@scenicartprint.com`, `cheryl@scenicartprint.com` and `dj@mirrokoat.com` all **forward into `windowandsolarcare@gmail.com`** (confirmed 2026-08-30: one message matches BOTH `deliveredto:dan@scenicartprint.com` and `deliveredto:windowandsolarcare@gmail.com` — two Delivered-To headers = forwarded). The Gmail account is the aggregate; the others are the originals.

**So NBHOF/Zoo watchers read the ORIGINAL mailbox, upstream of the forward.** Anything done to the forwarded COPY in `windowandsolarcare@gmail.com` — labels, archive, mark read — is invisible to them and completely safe.

## Why: three ways to silently blind a watcher

All three watchers call `mail.select('INBOX')`. **Archiving = removing the INBOX label = the watcher can no longer see the message.** There is no error, no log line, nothing fails loudly — the PO/estimate/payment simply never gets processed.

Additionally, **the LIVE Zoo watcher is UNSEEN-only**:
- `zoo_watcher.py:219` — `mail.search(None, '(UNSEEN FROM "contact@zooprinting.com")')`
- So **marking a Zoo email as read before the daily cron runs makes it permanently invisible** to `check_zoo_emails`. Recovery is only via `collect_zoo_emails_for_po()` (the "📧 Zoo Emails" button), which uses `X-GM-RAW` and CAN see already-read mail.
- The NBHOF watcher is NOT UNSEEN-gated (`watcher.py:293/376/467` search `FROM "baseballhall.org"` with SUBJECT/SINCE), so read-state is safe there — but INBOX-membership still is not.
- Paywatch is NOT UNSEEN-gated either (`specialist_paywatch.py:101` — `(FROM "%s" SINCE %s)`), so marking read is safe; archiving is not. It also only looks back **3 days** (`_fetch_payment_emails(days=3)`) — DJ confirmed 3 days is enough (2026-08-30).

## How to apply — the standing rules

1. **NEVER add a Gmail filter to `dan@scenicartprint.com` that archives ("skip the inbox") or marks as read.** One careless rule there costs a real NBHOF PO or a Zoo order. Realistically: do not filter that mailbox at all.
2. **Do all inbox organizing in `windowandsolarcare@gmail.com`**, on the forwarded copies. Safe by construction.
3. **In `windowandsolarcare@gmail.com`, never archive Paywatch's senders.** `_TRUSTED` (`specialist_paywatch.py:45`) is exactly two: `venmo@venmo.com` and `no.reply.alerts@chase.com`. Marking them read is fine; archiving blinds the payment loop.
4. **Customers Zelle to CHASE, not Ally** (DJ confirmed 2026-08-30). `email@transfers.ally.com` traffic is DJ's own self-transfers, so Ally deliberately does NOT belong in `_TRUSTED`. Do not "helpfully" add it.
5. Before changing ANY mail-touching automation, check WHICH mailbox it logs into. Assuming one shared inbox is the trap this note exists to prevent.

**Deliverable this came out of:** `wsc-gmail-filters.xml` (11 filters, given to DJ 2026-08-30 for Settings → Filters → Import). Noise senders get labeled + archived + marked read; Money/Payments senders are labeled and explicitly never archived; business routing is by original `to:` address, which survives forwarding. The Paywatch dependency is documented in a comment at the top of that file.
