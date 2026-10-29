---
name: project_inbox_thread_partner_stamp_fragility
description: "Inbox list-merge groups by STORED conv.partner_id (sms.py ~2591-2604) while OPENING a thread re-derives members from the partner's ODOO phone numbers (_merge_partner_thread 2763 → _partner_norms 2680). The two can disagree, and _resolve_partner_by_phone returns hits[0] ARBITRARILY among partners sharing a number (719-751) + inbound overwrites conv.partner_id (~1976). Real LATENT fragility (shared-number case) — but PARKED hardening, not shipped off the 2026-10-29 'pole' incident, which was a WRONG-RECIPIENT user send, not a mis-stamp."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-29T22:42:03.146Z
---

**2026-10-29 — DJ reported an outbound "I left my pole at your house…" text as mis-threaded (previewed under Bill Zwick's row, seemingly absent from the opened thread). Specialists + Lead root-caused a plausible code mechanism; then a Lead-gated LIVE READ (Operator) OVERTURNED the premise before anything shipped.**

**The live truth (Operator firsthand read):** the pole msg is CORRECTLY in Bill Zwick's thread, correctly stamped `partner_id=27310`; `5152493840` is genuinely Bill's OWN Odoo number (Bill 27310 + his property child 27311), with NO Jeff record on it. Jeff Oberman is a SEPARATE contact `26931` on a DIFFERENT number `6127029988` (his thread has today's on-my-way/photos/Zelle). So DJ sent the pole note to Bill while meaning Jeff = **a wrong-RECIPIENT user send, not a code mis-stamp.** The "missing from the opened thread" symptom did NOT reproduce in live data (it's present) → at most a transient display/refresh artifact. **Do NOT re-chase this incident as a bug.**

**★ THE REAL LATENT FRAGILITY (verified firsthand in code, worth hardening SOMEDAY — PARKED, DJ to prioritize, do NOT rush/ship off a non-reproducing incident):**
- **List vs open disagree.** The inbox LIST collapses rows by STORED `conv.partner_id` (`sms.py` ~2591-2604, the 2026-09-21 split-number merge). OPENING a partner thread re-derives its member convs from the partner's ODOO phone numbers (`_merge_partner_thread` 2763 → `_partner_norms` 2680, which reads res.partner `phone`/`x_studio_x_studio_second_phone` + parent, company-guarded 1/False). If a conv's stored `partner_id` is NOT one of that partner's Odoo numbers, the conv folds under them in the LIST but is EXCLUDED when the thread is OPENED.
- **Arbitrary resolve on shared numbers.** `_resolve_partner_by_phone(norm)` (719-751) matches on last-10 digits and returns `hits[0]` — ARBITRARY when multiple W&SC partners share a number (a real scenario here — see the Sally Walsh dup-partner note in `clear_needs_reply_for_so`). The inbound path (~1976) then OVERWRITES `conv['partner_id']` with that arbitrary pick (it does NOT overwrite when unresolved — "never downgrade to Unknown").

**Designed fix IF/WHEN DJ wants the hardening (Lead-approved direction, not yet built):**
1. On an AUTO stamp, verify the partner actually owns the conv's number before stamping; outbound should stamp the partner resolved FROM THE DESTINATION number, never a carried-over context pid.
2. For the ambiguous shared-number case, reuse the EXISTING precedent `_resolve_partners_by_phone` (plural, ~776) that already detects "ambiguous multi-contact — do not guess/merge": on ambiguity, keep the existing link / leave as-is, never arbitrary `hits[0]`.
3. Optionally make list-merge consistent with thread-open — but SECONDARY/defensive only; alone it just makes a wrong grouping consistent, so it is NOT the root fix.
**★ REGRESSION CAVEAT (must hold):** the guard must target AUTO mis-stamps only — never un-stamp/override a HUMAN-set link, and never break the legit new-customer-texts-from-an-unknown-number case (an unstamped standalone conv is CORRECT there).

**Process lesson:** verify the DATA PREMISE of a reported bug against live data BEFORE root-causing/fixing the code. The code analysis was sound, but this specific incident was not an instance of it — and the Lead "live-read before staging" gate is exactly what prevented shipping a guard (with real regression surface) for a non-bug. See [[feedback_reconcile_approval_scope_to_live_data]], [[feedback_cant_headlessly_seed_is_security_feature]], [[feedback_root_cause_not_just_instance]].
