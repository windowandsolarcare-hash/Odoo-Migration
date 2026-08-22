---
name: project_hiring_applicant_shadow_partners
description: How job applicants are recorded — hr.applicant is the record of truth; the auto-created res.partner shadow is archived so candidates never pollute customer lists
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Decision (DJ delegated, 2026-07-11): job applicants live in `hr.applicant` (Odoo recruitment) — that is the record of truth** (stages, notes, interview audio, `partner_name`/`email_from`/`partner_phone`). The hiring app (hiring.py) already uses hr.applicant correctly.

**The pollution:** Odoo auto-creates a `res.partner` "shadow" for each applicant's email (hr.applicant.partner_id). Those shadows are `company_id=1`, `is_company=False`, **no Workiz ref, no property child, no SOs** — so they leaked into customer searches/pickers (Francisco Rodríguez was one; the New Order picker showed 2 of him).

**Fix = archive the shadow, don't delete/relabel:**
- Every customer view filters `active=True`, so archiving (`active=False`) removes shadows from ALL pickers at once — zero schema change, fully reversible, no effect on the hiring UI (which reads fields off hr.applicant, not the partner). `record_category` is a fixed selection (Contact/Property only) so couldn't tag them 'Applicant' without a Studio change — archiving is cleaner.
- **Backfilled 2026-07-11:** archived 64 applicant-linked shadows + 32 orphan `@indeedemail.com` strays (Indeed relay emails = candidates, unlinked to an applicant), after confirming NONE had a ref/child/SO (0 were also real customers).
- **Going forward (commit 5c263d9):** `create_applicant` reads the new hr.applicant's `partner_id` and archives it right after create.
- **Backstop:** `/api/intake/search` also filters `'|' ref!=False, child_ids!=False` (real customers only) — see [[project_api_search_company_filter]]. Home `/api/search` already required ref.

★ If a candidate is HIRED and converted to employee, Odoo may need that partner — just un-archive it (active=True). ★ There may be other Odoo-auto-created shadows from the recruitment email gateway; the archive-on-create + the customer-search filters keep customer lists clean regardless.
