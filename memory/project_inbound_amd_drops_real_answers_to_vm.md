---
name: project_inbound_amd_drops_real_answers_to_vm
description: "Inbound calls to the 855/760 drop to the app voicemail the instant DJ answers — Twilio AMD false-flags his real 'hello' as a machine. The /voice/dj-bridge gate hangs up on anything that isn't exactly 'human' (so AMD 'unknown' drops a real pickup), aggravated by MachineDetectionTimeout=5s. The OUTBOUND /voice/outbound-bridge gate was already fixed to the correct lenient pattern; inbound was never brought in line."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-20T16:51:45.239Z
---

**Symptom (DJ 2026-10-20, via Dispatcher):** customers calling EITHER number (855 toll-free + 760) can't be answered — the call drops to the in-app voicemail the moment DJ picks up. Both numbers, identical failure.

**Root cause (proven on code; Specialists + Operator converged independently):** `routers/owner/voice.py` inbound flow. `/voice/incoming` holds the caller in a conference and rings DJ's cell via `_dial_dj` with Twilio **Answering-Machine Detection** (`MachineDetection: Enable`). Twilio classifies the answer and passes `AnsweredBy` to `/voice/dj-bridge`, whose gate (voice.py:263) was:
```
if answered_by and answered_by != 'human':
    return _xml('<Hangup/>')
```
This drops on **`unknown`** too. Twilio returns `unknown` when it can't classify in time — common for a quick/short "hello" in a noisy field/truck environment. Aggravated by **`MachineDetectionTimeout: '5'`** (voice.py:238; Twilio default is 30s) which gives AMD too little time → biases to `unknown`. So a real human answer → `unknown` → gate hangs up DJ's leg → `/voice/dj-status` sees no human → caller redirected to the in-app voicemail. Both numbers route through this one flow → both fail the same way.

**NOT:** a Twilio account/number setting (webhook already reached `/voice/incoming` — the greeting plays + DJ's phone rings); NOT a 502 (a 502 on the webhook errors/drops the call, it does NOT cleanly land the caller in our voicemail — different fingerprint); NOT a regression (this inbound gate has been unchanged since the 2026-06-27 AMD rebuild — real-world AMD outcomes on DJ's field answers are what surfaced the always-present fragility).

**The fix (2026-10-20, surgical, inbound only — SHIPPED, commit 9dec2817; Lead firsthand §15-confirmed at sha 3020d622 + byte-QC):**
1. voice.py:263 gate → `if answered_by.startswith('machine') or answered_by == 'fax':` → connect `human`/`unknown`/empty, hang up only a CONFIRMED machine. **This mirrors the already-shipped, proven OUTBOUND gate** `/voice/outbound-bridge` (voice.py:735, live since 2026-08-04 click-to-call AMD commit) — the inbound gate was simply never brought in line. `answered_by` is `(AnsweredBy or '').lower()`, so empty → connect.
2. voice.py:238 `MachineDetectionTimeout` `'5'` → `'15'` (< `RING_SECS`=20) so AMD can classify a human before timing out. Outbound dial (:709/:713) + outbound gate left untouched (not the reported bug; gate already correct).

**SIBLING FOLLOW-ON (commit 18d51f42, 2026-10-20 — Audit fresh-eyes found, Lead paced + confirmed firsthand):** the fix above made `unknown` CONNECT, which exposed a race in `/voice/dj-status` (the StatusCallback on DJ's leg): it kept the all-good branch on `if answered_by == 'human':` and redirected the caller to VM on anything else — so a connected `unknown` call would POST a VM-redirect onto the caller leg at DJ hangup (near-always a harmless no-op since the conference tears down first, but a race that could dump a real conversation into "leave a message"). FIX: redirect to VM ONLY on a confirmed miss — `answered_by.startswith('machine') or == 'fax'` OR `CallStatus in ('no-answer','busy','failed','canceled')`; `human`/`unknown`/empty-completed = DJ connected → no redirect. `CallStatus` is the Twilio status-callback param (always present; `AnsweredBy` also present with AMD). This closes the bug CLASS (both the dj-bridge gate AND the dj-status gate now treat unknown as a connected human), not just the one instance. [[feedback_root_cause_not_just_instance]].

**Risk tradeoff (named, accepted):** treating `unknown` as human means IF DJ's carrier voicemail answers AND AMD reads it `unknown` (rather than `machine_*`), a caller could reach his personal VM. Acceptable vs. dropping EVERY real answer — AMD classifies an actual voicemail greeting as `machine_*` reliably; `unknown` is overwhelmingly the "real human we couldn't finish reading" bucket. Same tradeoff the outbound gate already runs in prod. DJ's design intent was no-key-press (comment voice.py:4-13) — so AMD stays; a key-press-to-accept leg is the more-robust alternative only if AMD stays flaky after this.

**How to apply / verify:** Twilio call logs for DJ's leg on the failing calls show `AnsweredBy` = `unknown`/`machine*` (Operator/DJ can eyeball to 100%-confirm the trigger). Post-fix, a real inbound call to each number connects to DJ on answer. PLAN: saunders-render-app `3_Documentation/review/voice_amd_inbound_drop/PLAN.md`. See [[feedback_root_cause_not_just_instance]], [[feedback_reuse_canonical_endpoint]] (inbound should reuse the proven outbound gate pattern).
