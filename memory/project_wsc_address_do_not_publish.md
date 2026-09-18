---
name: project_wsc_address_do_not_publish
description: "★ The Palm Desert mailbox on Odoo res.company/invoices is DELIBERATE (privacy) — do NOT 'fix' it. Two distinct addresses: the invoice MAILBOX (private, by design) and the hidden-SAB HOME/registered address (Thousand Palms) — neither goes on any PUBLIC listing (GBP/website/Yelp/directories)."
metadata: 
  node_type: memory
  type: project
  originSessionId: a6200401-4a1b-4492-894c-629c161de653
  modified: 2026-09-18T18:35:42.681Z
---

**DJ 2026-09-18 (via Lead), correcting a Web verification pass that had flagged the Odoo company
address as stale:** the Palm Desert address on the invoices is **intentional — leave it alone.**

**Two different W&SC addresses, do not conflate:**
1. **Invoice / company MAILBOX** = `41995 Boardwalk Ste. J, Palm Desert CA 92211` — DJ's still-active
   mailbox, stored on **Odoo `res.company` id1** and printed on invoices **ON PURPOSE for privacy**
   (he does not want customers seeing his home address). Invoices are **private correspondence, NOT
   a public Google-indexed NAP citation**, so this address there is correct and must **NOT** be
   "cleaned up" to the Thousand Palms address. This is a recurring "fix" trap — a session sees
   Palm Desert on the company record, assumes it's the same stale-NAP problem that got the GBP
   suspended, and tries to change it. **Don't.**
2. **Registered / operated-from HOME address** = `32569 San Miguelito Dr, Thousand Palms CA 92276`
   (CA SOS B20260293155, Twilio). This is a **hidden Service-Area-Business (SAB) home address** —
   it is what the GBP-reinstatement docs (registration + utility bill) must MATCH, but it is
   **also not published** on the public profile (SAB = service area shown, street hidden).

**The rule (unchanged by this correction):**
- **PUBLIC listings** (Google Business Profile, the website, Yelp, MapQuest, Angi, all directories):
  show name **Window & Solar Care** + phone **760-334-5355** + service area — **no street address**
  (neither the Palm Desert mailbox nor the Thousand Palms home). A published street was part of what
  got the profile flagged.
- **Invoices / private correspondence** (Odoo res.company): the Palm Desert mailbox is fine and
  intended. Do not flag it, do not route it to Operator as a fix.

**Why:** without this note, every NAP-audit session re-flags the invoice address as "stale/wrong"
and burns a cycle (and risks an unwanted Operator write to a money-touching record). It is a
deliberate privacy design, not drift.

**How to apply:** when auditing NAP, separate PUBLIC surfaces (must be clean/streetless) from the
PRIVATE invoice record (Palm Desert mailbox = by design). See [[project_gbp_suspension_appeal]],
[[project_wsc_legal_name]], [[feedback_assistant_use_app_workflow_not_raw_api]].
