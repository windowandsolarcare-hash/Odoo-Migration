---
name: project_company_filter_fails_open
description: "Cross-company res.partner leak class: company_id FAILS OPEN (W&SC customers are mostly False), so enforce company_id in [1,False] at the RESOLVER/chokepoint, never per-caller. Real portal leak 2026-08-19."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-19T15:09:17.828Z
---

**Incident 2026-08-19 (customer-facing leak, caught + fixed before distribution).** The customer portal `wscare.pro/p/<token>` rendered a full **Window & Solar Care** portal — greeting, street address, visit history — for **National Baseball Hall of Fame**, a **Saunders Printing (company 3)** customer. Cause: `/owner/api/portal/link?q=` carried the company filter but `?partner_id=` and `build()` did NOT. Fixed (portal.py 1e580d36): a hard `_is_wsc()` guard inside **`account()`** — the single chokepoint BOTH the link endpoint and the portal payload pass through. Verified live: Saunders token/partner_id → `{ok:false}`, real W&SC customers unaffected.

**Two durable rules (broadcast to all sessions) for any endpoint that resolves a `res.partner`:**
1. **Enforce at the RESOLVER / single chokepoint, not at each caller.** One guarded path + one unguarded path is exactly how this hides (Portal had `q=` guarded, `partner_id=` not). Put the guard where every path converges.
2. **`company_id` FAILS OPEN.** W&SC customers are almost all `company_id = False` (see CLAUDE.md rule 8) — so "no company" and "another company's customer" look identical unless you check explicitly. **Allow only `company_id in [1, False]`. Never a bare "≠ my company"** (that lets `False` = every unstamped Cheryl/Saunders contact through).

**Rule 3 — resolvers that WALK (Portal's second door, 2026-08-19):** guarding the resolver isn't enough when it climbs a relation. Portal company-checked the MATCHED record but RETURNED its unchecked `parent_id`; a job-number branch dereferenced SO→`partner_id` with no company leaf. **The record you CHECK must be the record you RETURN** — after a company filter, if you then climb a `parent_id` or dereference a many2one (property→parent, SO→partner, invoice→SO), re-check `company_id in [1,False]` on the record you actually return. A hop between check and return is a door. Fixed portal.py 399e3fca.

**Why:** res.partner is NOT auto-isolated by Odoo (DJ's user has all 3 companies), and the stamped-vs-unstamped reality means a naive filter passes foreign customers. This is the enforcement backing for CLAUDE.md rule 8. Same guard requested for the voice `open_text_draft` tool (field.py). When adding any new customer-resolving endpoint (Customer Brain, pickers, portal, voice tools), audit for a second unguarded door AND a filter-then-hop. See [[feedback_no_guessing_on_fields]].
