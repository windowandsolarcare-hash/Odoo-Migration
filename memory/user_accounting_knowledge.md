---
name: DJ Accounting Knowledge & Preferences
description: DJ's accounting background, comfort level, and how Claude should handle accounting tasks for him
type: user
originSessionId: d77fc6bd-119f-4192-b2c8-a8592257d2b6
---
DJ likes accounting conceptually but is not an accountant. Specific comfort levels:

- **P&L** — comfortable. Understands income, expenses, categories, what drives profit.
- **Balance sheet** — less confident. Understands it exists and roughly what's on it but not comfortable managing it himself.
- **Double-entry accounting** — does not want to deal with it at all. Never had an accountant to ask. Has made do in QB but found journal entries and reconciliation tedious and confusing.

**How Claude should handle accounting for DJ:**

- DJ describes financial events in plain English ("I sold the truck for $7,000", "a customer got a refund", "I paid off the loan")
- Claude translates to correct accounting treatment and executes all transactions in Odoo directly
- Claude never makes DJ think about debits, credits, or which accounts to touch
- If Claude needs a factual answer DJ would know (e.g. "what did you originally pay for that truck?") Claude asks — otherwise just handles it
- Claude should briefly explain what it did and why in plain English after doing it, so DJ builds understanding over time without being overwhelmed

**DJ wants Claude to be his on-call accountant** — available any time, handles anything from simple categorization questions to complex asset disposal or loan payoff journal entries.

**Specific scenarios DJ mentioned:**
- Customer refund — doesn't do these but wouldn't know how to handle one if it happened
- Selling a vehicle — removing asset from books, recognizing gain/loss
- Loan payoff — zeroing out liability
- Owner draws — moving money from business to personal

All of these: DJ describes it, Claude handles it completely in Odoo.
