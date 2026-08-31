---
name: project_gmail_inbox_organization
description: "2026-08-30 inbox cleanup of windowandsolarcare@gmail.com via 11 imported Gmail filters. Four addresses funnel into one mailbox (3 forwarded). Noise gets labeled+archived+read; business mail is routed by original to: address; Money/Payments is NEVER archived (Paywatch reads INBOX). First sweep filed 5,075 threads, inbox 37,503 -> 32,454."
metadata:
  node_type: memory
  type: project
---

**Built and deployed 2026-08-30 (cloud Lead + DJ).** DJ: *"move emails - organized."* Chose
**label + archive everything** (nothing deleted, ever) with a going-forward + ~90-day backfill.

## The mailbox topology — FOUR addresses, ONE inbox

`windowandsolarcare@gmail.com` is the only real mailbox DJ reads. Three other addresses **forward
into it**:

| Address | Belongs to | Forwarded in? |
|---|---|---|
| `windowandsolarcare@gmail.com` | W&SC — the actual Gmail account | — (it IS the mailbox) |
| `dj@mirrokoat.com` | W&SC | yes |
| `dan@scenicartprint.com` | Saunders Printing | yes |
| `cheryl@scenicartprint.com` | Cheryl Johnson REALTOR® | yes |

**This is why business routing must filter on the original `to:` address, not the sender.** A
forwarded message keeps its original `To:` header, so `to:dan@scenicartprint.com` still matches
inside the Gmail account. Routing by sender would need an unbounded, ever-growing sender list;
routing by recipient is 3 rules that never need maintenance.

**★ `dan@scenicartprint.com` is ALSO a live IMAP mailbox that two watchers log into directly**
(upstream of the forward). Never filter it. Full rule: [[project_mail_watchers_two_mailboxes]].

## What was built

**`4_Reference_Data/wsc-gmail-filters.xml`** — 11 filters, imported by DJ via
Settings → Filters and Blocked Addresses → **Import filters**. Three groups:

1. **Money (2 filters)** — label only, `shouldNeverSpam`, **never archived**. Paywatch's two senders
   (`venmo@venmo.com`, `no.reply.alerts@chase.com`) are deliberately split into their own filter so
   nobody can casually add `shouldArchive` to the broader money rule and blind the payment loop.
2. **Noise (4 filters)** — Nextdoor / Facebook+Reddit / shopping+promos / news digests →
   label + `shouldArchive` + `shouldMarkAsRead`. Nothing deleted; all recoverable by label.
3. **Business routing (5 filters)** — by original `to:` address (WSC / Saunders / Cheryl), plus
   named-source labels for listing platforms and NBHOF+Zoo. **Label only, never archived.** Each
   routing rule carries a `-from:(...)` exclusion of the known noise senders so Nextdoor doesn't
   pollute a business label.

## First-sweep results (verified via `list_labels`, ~75 min after import)

- **Inbox 37,503 → 32,454 threads**
- Noise/Shopping 2,243 · Noise/Neighborhood 1,311 · Noise/Social 1,044 · Noise/News 477
  = **5,075 threads filed, all 0 unread**
- WSC 30,868 · Saunders 960 · Cheryl 129 · Money 605 · Money/Payments 672 ·
  Saunders/NBHOF 53 · WSC/Listings 29

## Gmail mechanics learned (these cost time — don't relearn them)

- **Filters vs labels:** a *label* is a tag on a message (a folder that allows multiple). A *filter*
  is a rule that ACTS (label / archive / mark read / never-spam). Labels are inert; filters are the
  automation. Creating a label does nothing on its own.
- **Import is desktop-web only.** Settings → *Filters and Blocked Addresses* → "Import filters" at
  the very bottom. It does **not** exist in the Gmail mobile app — DJ hit this. Filters, once
  imported, apply everywhere including mobile.
- **★ "Also apply to matching conversations" is retroactive and HEAVILY THROTTLED — hours, not
  minutes.** It ran at roughly **9 threads/min** against a 37k inbox. It looks frozen. It is not.
  DJ reported "its stuck" — it was working the whole time. Verify by re-reading label counts a few
  minutes apart, never by watching the UI.
- **`resultCountEstimate` from the search API is unreliable** — it pinned at "201" regardless of the
  real count. Use `list_labels` thread/message counts for anything quantitative.
- **Archive = removing the INBOX label.** There is no separate "archived" flag. This is exactly why
  archiving is dangerous for any sender an IMAP watcher reads via `select('INBOX')`.

## How to verify a sweep didn't break a watcher

The single check that matters — search for the protected label **outside** the inbox:

```
label:Money/Payments -in:inbox
```

**Empty result = safe** (nothing was archived). Run 2026-08-30: returned zero, confirming all 672
payment threads stayed in the inbox and Paywatch was never blinded. Do this after ANY future filter
change touching money senders.

## Open / next

- **Round-two filters not yet written.** Sample the inbox residue once the first sweep finishes and
  add rules for whatever still dominates. WSC at 30,868 is the bulk and is not yet subdivided.
- **A future session may be able to skip the XML dance entirely:** `create_filter` / `list_filters`
  are real Gmail-connector tools; they were simply not loaded in the 2026-08-30 cloud session. Check
  for them before hand-writing XML again. See [[feedback_verify_limits_before_declaring]].
- The email specialist (#8) is specced separately in `3_Documentation/EMAIL_SPECIALIST_BRIEF.md` —
  its highest-leverage output is proposing NEW FILTERS, not labeling mail one at a time.

## Related

- [[project_mail_watchers_two_mailboxes]] — ★ the safety constraints. Read before touching any filter.
- [[project_paywatch_specialist]] — what breaks if payment mail leaves the inbox.
