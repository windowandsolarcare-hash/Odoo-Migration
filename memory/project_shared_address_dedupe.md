---
name: project_shared_address_dedupe
description: "shared/addresses.py is the ONE canonical place \"same address\" is decided — normalize_street / address_key / group_by_address. Display-only dedupe of Workiz duplicate properties; never merge the Odoo records."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-20T14:24:35.647Z
---

**`shared/addresses.py`** (created 2026-08-20 by Portal, commit d9cdd364) — the single canonical
implementation of "is this the same physical address?". Lead locked it as canonical the same day.

**API:** `normalize_street(street)` · `address_key(rec)` (street + city + 5-digit zip) ·
`group_by_address(records, rank=…)` → `[{key, primary, records, ids}]`.

**Why it exists:** the Workiz migration left MULTIPLE property records per physical address
("44835 Guadalupe Dr" vs "…Drive" — Ed Dismukes, partner 23185, has three), each holding its own
last-visit/price/gate. Any screen listing a customer's properties showed the same house repeatedly
with its history split across the copies.

**★ DISPLAY-ONLY. Never merge the underlying Odoo records** — they carry invoice/accounting links;
DJ ruled a real merge out (2026-08-20). Group at render time and ACT on the group's `primary`.
`primary` = freshest visit, then has-gate, then has-service — the copy with the truest picture.

**Deliberate non-merges (don't "improve" these):** unit markers are preserved, so `#1` and `#2`
never collapse; a leading direction is NOT dropped, so `228 E Newport Rd` ≠ `228 Newport Rd`.
Only a TRAILING street-type word is folded, so a street named "Drive" mid-address survives.

**How it was validated — reuse this method for any normalizer:** swept **all 1,539 W&SC records
with a street**, grouped within-parent, and inspected every group collapsing on anything beyond a
pure suffix synonym. 635 groups collapse; exactly **6** differ by more, all direction synonyms
(`w`↔`west` etc.), all genuine pairs → **zero false merges**. A normalizer that silently merges two
real houses fails invisibly, so whole-dataset validation before shipping is the bar, not spot checks.

**How to apply:** anything resolving/listing properties (Customer Brain, property pickers, booking)
**imports this module** — do not write a second normalizer. If it misses a case, extend it HERE and
everyone benefits. Used today by `routers/owner/portal.py` (`account()` groups; `remembered()` rolls
up freshest visit + price and takes each remembered detail from the first copy that has it).

Related: [[project_customer_portal]], [[feedback_reuse_canonical_endpoint]]
