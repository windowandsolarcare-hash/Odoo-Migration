---
name: project_property_dedup
description: "Duplicate PROPERTY cleanup (Workiz made a new property per visit). Merge method = Odoo NATIVE base.partner.merge (handles posted invoices; manual write can't). ~48 same-addr clusters / ~58 excess. Barry Matthews test cluster DONE 2026-08-03."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-04T02:41:07.084Z
---

**Workiz duplicated PROPERTY records** (created a NEW res.partner Property per visit instead of reusing). DJ wants them consolidated to one record per real property. Scale (W&SC, company in [1,False], 2026-08-03): 920 properties, ~48 same-address clusters, **~58 excess/removable records**; ~862 real properties, ~620 real customers (NOT ~500 — DJ over-estimated the dupe rate). Contact-level dupes are tiny (~3-5 real; phone is a BAD dedupe key — DJ's own cell 951-972-6946 is stamped on test/system records "Fred Test"/"Holiday"/"Personal Time", and families share numbers).

## MERGE METHOD — use Odoo's NATIVE merge, NOT manual field reassignment
- **Manual `write` of partner_id FAILS on posted invoices:** `account.move` posted → `Fault 2: You cannot modify readonly fields on a posted move: partner_id`. So a hand-rolled reassign can move sale.order/project.task/mail.message but NOT posted invoices. Learned the hard way (half-merged Barry, recovered).
- **Correct tool: `base.partner.merge.automatic.wizard`** (core Odoo dedup, Contacts app). It reassigns ALL references incl. posted invoices/journal entries, then **DELETES** the merged dupes (not archive — more final; data is moved first so nothing lost).
  - API: `wiz=create({'dst_partner_id':SURVIVOR,'partner_ids':[(6,0,ids)],'state':'selection'})` then `action_merge([wiz])`. Private `_merge` is NOT RPC-callable.
  - ★ **SAFETY CAP: max 3 contacts per merge** (`Fault 2: cannot merge more than 3 contacts together`). Chunk: survivor + ≤2 dupes per call; repeat for clusters with more dupes.
- **Survivor rule:** prefer an ADDRESS-named record (skip the person-named artifact e.g. "Barry Matthews" property), with the most recent job (date_order). 
- To enumerate what's tied to a record (completeness proof): `ir.model.fields` where ttype in (many2one,many2many) and relation='res.partner' = 263 fields / 163 models; skip `*report*`/view models (auto-recompute). But with native merge you DON'T need to hand-reassign — it does it all.

## STATUS
- **Barry Matthews (902 Tierra Lane) — MERGED 2026-08-03.** 4 records → survivor 27126; both posted invoices ($220 INV/2026/02500, $150 INV/2026/02460) moved; 27081/27078/27073 deleted. Verified. This validated native merge as the batch method.
- **NEXT (pending DJ eyeball of Barry):** batch the remaining ~47 clusters via native merge (chunked ≤3), with a per-cluster log. Review each cluster's records first (survivor pick). Going-forward fix: new_job.py property creation should reuse existing property + stamp phone so dupes/blank-phones stop recurring. See [[project_respartner_no_mobile_field]], [[project_property_partner_naming_quirk]].
