---
name: project_nbhof_postcard_c_numbers
description: "NBHOF photo-postcard \"C number\" item-number sequence and how to find the next one"
metadata: 
  node_type: memory
  type: project
  originSessionId: 95c7bd46-9fa1-4224-a3d6-1a584f8d6e6b
---

NBHOF (Saunders Printing customer, Odoo partner id 26947, company 3) photo postcards each get a sequential item number formatted `C#####`. Contact = **Ben Hatton**, bhatton@baseballhall.org (signs "Ben Hatton"; DJ voice often transcribes as "Ben"/"band").

**How to find the next number:** read the line items of the most recent NBHOF invoice (`account.move`, partner_id=26947, move_type=out_invoice, order by invoice_date desc). Each card line name is like `C38677 — WRIGLEY FIELD — Photo Postcard`. Take the max C number across the lines, add 1. Lines are reachable via `invoice_line_ids` → `account.move.line.read` (cross-company search_read by move_id returns 0 — see [[project_saunders_invoice_send_view]]).

**Sequence state (2026-06-30):** Last 21-card batch (invoice 200239, PO 044167) ended at **C38681**. 2026 inductee cards then assigned:
- C38682 Jeff Kent
- C38683 Carlos Beltran
- C38684 Andruw Jones
- C38685 Carlos Beltran (Spanish)

So **next available = C38686**.

**Why:** DJ periodically asks "what's the next C number" when NBHOF adds postcards; the number is just last-used + 1 across the latest invoice's card lines.

**How to apply:** When emailing Ben new numbers, present them as "the next item numbers" — do NOT mention they continue from a prior order (he doesn't track the internal sequence). Draft emails for DJ to send himself, never auto-send — see [[feedback_email_draft_first_always]].
