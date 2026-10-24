---
name: spam-voicemail-segregation
description: "Spam voicemails auto-segregate into a reversible 'Spam' bucket in the Inbox (Option 2, shipped 2026-10-24 commit a451e8e3). Classifier _vm_spam_reason (sms.py): customer-bypass FIRST via _resolve_partner_by_phone; then learned list / phrase / silent(empty+short). NO toll-free trigger, NO auto-learn (tap-only). conv['spam'] flag must be wired through the SUMMARY projection, not just the conv."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-24T05:29:31.308Z
---

**Shipped 2026-10-24 (commit a451e8e3, atomic 4-file Git-Data-API commit; Audit + Lead dual byte-QC GREEN; DJ approved Option 2). Fast-follow d3484685 = toggleSpam disable-on-tap.**

**What it does:** an inbound Twilio voicemail that's confidently spam is auto-filed to a collapsed, reversible **Spam bucket** in the Inbox; it NEVER touches a real customer's VM. Nothing is deleted.

**Classifier `_vm_spam_reason(norm, text, duration_s)` (sms.py, near _summaries_for).** Returns a reason to auto-file, or None. Order (precision-first; Lead-adjudicated):
1. **Known-customer BYPASS first** — FRESH `_resolve_partner_by_phone(norm)` (company_id in [1,False]); a customer is NEVER spam; resolve error → fail-safe None (never misfile on an Odoo hiccup). ★ Use this, NOT `_find_customer` (sms.py:693, no company filter + suffix-ilike misses formatted numbers).
2. **learned** — `_is_vm_spam_num(norm)` (list `wsc.vm.spam.numbers`, built ONLY from DJ's Mark-spam taps — NEVER auto-added).
3. **phrase** — DJ-editable `wsc.vm.spam.phrases` (seed incl. 'vehicle warranty','press 1','to an agent'; 'solar leads' NOT 'solar').
4. **silent** — empty transcript (≤3 chars) AND short (`duration_s` present AND ≤8s); MISSING RecordingDuration FAILS toward NOT-spam.
5. else None (unknown + no content signal stays in the inbox). ★ TOLL-FREE/8xx is NOT a trigger (Lead decision 3 — content-gate rail + HR hiring 8xx callbacks would misfile).

**Learning is TAP-ONLY (Lead decision 2):** auto-detect files only THIS VM (reversible), does NOT persist the number; only DJ's explicit "Mark spam" `_vm_spam_add`s → one false auto-detect never becomes a permanent rule.

**Hooks (voice.py):** `voice_recording_done` (:329, pre-transcript) = learned-number fast-path (if `_is_vm_spam_num` → conv['spam']=True, quiet). `voice_transcription` (:361) = content classify in BOTH the empty-text branch (silent) and the non-lead branch (phrase); mirrors the existing `_is_lead_call` quiet-branch pattern. Every spam branch CLEARS the needs_reply+unread that recording_done set.

**★ THE INERT-BUG WIRING (the load-bearing bit — [[feedback_field_whitelist_strip_silent_inert]]):** `inbox_list` iterates SUMMARIES (`_summaries_for`), not convs, and `_summary_from_conv` (sms.py:406) is a field WHITELIST. So conv['spam'] must be wired through 5 spots or it ships INERT: (a) `_summary_from_conv` return +`'spam'`; (b) `_counts` +spam count & `continue`; (c/e) the EXCLUSION is in the POST-CACHE pass (NOT the status-filter loop — excluding there empties the cache the spam view reads): `if view=='spam': out=[only spam] else: out=[not spam]; if view: _vmatch`; (d) out-row +`'spam'`. Every spam-SET routes through `_conv_set` (the chokepoint, sms.py:432) so the summary projection refreshes. Spam is a VIEW (`view=spam`), default views + the 'all'/no-view path all exclude spam.

**Endpoints (owner-authed by inclusion, like inbox_status):** `POST /owner/api/inbox/mark_spam {c}` → conv['spam']=True + `_vm_spam_add`; `POST /owner/api/inbox/not_spam {c}` → conv['spam']=False + `_vm_spam_remove` (FULL reverse: clear flag AND un-learn).

**UI (v2_inbox.html):** a "🚫 Spam (N)" pill (setFilter('spam') → VIEW='spam'); a thread-header toggle `spamBtn` (🚫 mark / ✓ not-spam, disabled in-flight). `/api/inbox/thread` returns the merged conv (carries 'spam') so the icon state is correct.

**Tuning (editable, non-blocking):** the phrase list + the silent ≤8s threshold. Related: [[project_inbox_twilio_voicemail_storage]], [[project_owner_api_auth_enforced]].
