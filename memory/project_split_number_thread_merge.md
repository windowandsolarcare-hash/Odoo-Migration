---
name: project_split_number_thread_merge
description: "Inbox threads are keyed per-phone (wsc.sms.conv.<norm>), so a customer with a cell + a landline shows as TWO threads and a VM/text on the 2nd number is invisible where DJ replies. Fix = DISPLAY-TIME merge by shared partner_id>0 (_merge_partner_thread). Plus a tracked follow-up: convs missing from wsc.sms.index are invisible in the list."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-21T14:56:35.307Z
---

**(A) split-number merge (2026-09-21, commit eb41361c, Lead-QC'd):** conversations are keyed `wsc.sms.conv.<norm>` (norm = last-10-digits). A customer with a **cell (texts)** + a **landline (calls/VMs)** has TWO conv stores → two threads → an inbound on the 2nd number is invisible where DJ replies = a customer can be missed (Glenn Uhley, partner 23018: 6192443337 cell/34 msgs + 9514670287 second_phone/2 msgs incl the Sep-18 inbound).

## The fix — DISPLAY-TIME merge by partner_id (no data mutation)
- **`_partner_norms(partner_id)`** → the partner's numbers `[(norm, phone)]` from `res.partner` `phone` + `x_studio_x_studio_second_phone` (+ parent person), primary `phone` first, W&SC company-guarded (1/False).
- **`_merge_partner_thread(partner_id)`** → loads each number's conv, merges all msgs into ONE ts-sorted timeline (each tagged with source `num`), **clears unread on EVERY source conv** (so the badge can't reappear), returns the merged conv whose identity = the **primary**. **Primary (= reply target) = the main `phone` line** if it has a conv (DJ's rule: reply on the text number; the main-phone thread carries the real history) — NOT "most-recent inbound" (a stray recent text from a 2nd number must not hijack the reply target). Fallback: the conv with the most inbound texts, else first.
- **`inbox_thread(c)`** and **`inbox_thread_by_partner(partner_id)`** both return the merged thread when partner_id>0 (before, thread_by_partner resolved ONLY the primary `phone`, missing second_phone). So opening ANY of a customer's rows shows the full merged thread; reply goes to the primary/cell.
- **`inbox_list`** collapses rows sharing partner_id>0 into ONE (keep the first = most-urgent/most-recent by the existing sort; OR unread, max last_ts, `merged_count`). **`_counts` counts each CUSTOMER once** (per partner_id, most-urgent status) so the badge matches the rows shown.
- **HARD RULE:** group ONLY by an explicit shared **partner_id > 0**. partner_id 0/null convs stay STANDALONE — NEVER merge by phone-across-partners or fuzzy name (merging two different people is far worse than a split thread).
- **Server-side only** — the merged conv carries `norm`=primary + merged `msgs`, so the existing v2_inbox.html renders the full timeline and replies to the cell with no client change.
- Note: "landline VM" msgs may be stored as `source='text'` (Glenn's Sep-18 were) — the merge includes ALL msgs regardless of source, so it works either way. If the resolved primary is a non-text line, offer a call affordance (Lead note; not gold-plated).

## ★ TRACKED FOLLOW-UP (Lead flagged 2026-09-21) — NOT fixed here
Glenn's 34-msg CELL conv (6192443337) is **NOT in `wsc.sms.index`** (his 2-msg landline IS). `inbox_list` iterates the index → **a conv missing from the index is fully invisible in the list**. The merge-by-partner sidesteps it (opening the indexed row merges in the non-indexed sibling via partner resolution), BUT a customer whose ONLY conv is non-indexed would be **completely invisible** = a latent "invisible customer" risk. Investigate later: why a written 34-msg conv isn't in the index (index built from a different source? a rebuild dropped it? a write path that skips `_touch`?), and consider an index-reconcile (index = all wsc.sms.conv.* with msgs). See [[project_inbox_summary_readmodel_a5]] (inbox_list reads the index → summaries), [[feedback_never_send_dj_to_odoo]].
