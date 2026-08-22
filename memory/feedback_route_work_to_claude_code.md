---
name: feedback_route_work_to_claude_code
description: Default ALL work to Claude Code (me, flat Max subscription = no marginal cost). Reserve Render Claude (API = real per-token $) for in-the-field phone access only.
metadata:
  node_type: memory
  type: feedback
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

**Route work to Claude Code by default; use Render Claude only when DJ is in the field and genuinely needs phone access.** (DJ, 2026-06-08.)

**Why (DJ's reasoning, confirmed correct):**
- **Render Claude = Anthropic API**, billed per-token to DJ's API account — every field-assistant query costs real marginal money.
- **Claude Code (me) = DJ's flat $100/mo Max subscription** — rate-limited, NOT per-token-billed. No marginal dollar cost; just draws on weekly allowance he's already paid for and is nowhere near exhausting (see [[feedback_use_sonnet_for_routine]] — heavy day = 10% of weekly limit).
- So anything that *can* be done in a Claude Code session should be, to avoid API charges.

**How to apply:**
- Default home for accounting/bookkeeping, analysis, code edits, planning → Claude Code (me).
- Render Claude → only when DJ is physically in the field and needs on-the-spot access on his phone.
- **Recurring weekly/monthly bookkeeping = Claude Code wake-up (me), NOT Render crons calling Render Claude** — keeps ongoing automation on the subscription, no marginal API cost. See [[project_recurring_bookkeeping_plan]].
- The cash-expense entry form in the Render field app is fine — it's a plain form writing to Odoo, not a Render Claude AI call, so it costs nothing per use.
