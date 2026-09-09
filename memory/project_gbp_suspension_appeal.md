---
name: project_gbp_suspension_appeal
description: "Google Business Profile SUSPENDED (deceptive content / NAP mismatch). Full history + what was fixed + the appeal open-items. As of 2026-09-09: NOT filed, no action since Sep 4. Appeal linchpin = ONE provable address matching listing + registration + utility bill."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-09T23:55:57.767Z
---

**Window & Solar Care's Google Business Profile is SUSPENDED for "deceptive content."** Driver = a NAP (Name/Address/Phone) mismatch across the places Google can see — primarily an inconsistent PHONE, compounded by an inconsistent ADDRESS. As of **2026-09-09 the appeal has NOT been filed; no action since 2026-09-04** (DJ confirmed). Investigation/fix work was 2026-09-03/04.

**★ Facts from the live Google appeal form (screenshot 2026-09-09, "Request review of suspended profile"):**
- **Business Profile ID: `13507549370210966`**
- **Official managing email: `windowandsolarcare@gmail.com`** → this RESOLVES the old "not sure DJ owns the account" open item — DJ's business email owns it.
- **Suspension date shown on form: `7/27/2022`** — ⚠️ FLAG: this predates the Aug-2026 phone change by 4 years. Either the profile has been suspended since 2022 (long-standing, and the phone/NAP mismatch is why it STAYS deniable), or the date field is wrong. DJ to confirm the real suspension date — it's a required field and reframes the narrative.
- **Required uploads:** (1) Business Registration/License showing business name + address that MATCHES the listing being appealed; (2) a Utility bill showing the SAME business name + address. "Avoid sending sensitive business documents." → **The appeal is won or lost on name+address consistency across listing ⇄ registration ⇄ utility bill.**

**Root cause (per MEMORY-AUDIT, 2026-09-04):** number changed 2026-08-14 from old toll-free **855-245-2273** → **760-334-5355** (in sms.py), recorded but never propagated everywhere; nothing tied "we changed our number" to "here's every surface it appears on." Re-derived from scratch in the 2026-09-03 DJ/Cheryl meeting. Three historical numbers: 855-245-2273 (old toll-free), 760-334-5350 (older), **760-334-5355 (correct)**.

**Address problem — FOUR cities for one business:** Rancho Mirage (GBP + website), Palm Desert (Thumbtack), Hemet (Nextdoor), **Thousand Palms** (CA SOS registration + Twilio: 32569 San Miguelito Dr, Thousand Palms CA 92276). Google ranks by proximity from the REGISTERED address, not the service-area list. ⚠️ Changing the GBP address on a SUSPENDED profile may trigger re-verification and reset the appeal clock.

**Legal entity:** `Window & Solar Care, LLC` (comma) — CA SOS **B20260293155**, agent Daniel Saunders, 32569 San Miguelito Dr, Thousand Palms CA 92276. Twilio has it WITHOUT the comma (outlier; SOS wins). Trade name = `Window & Solar Care`.

**ALREADY FIXED (2026-09-03/04):**
- GBP phone → 760-334-5355 (Sep 3 meeting).
- Website (Odoo) → 760-334-5355, verified live in 10 places, zero old numbers (wsc_shared.py PHONE_DISPLAY/PHONE_TEL + run_build.py/wsc_pages_b.py).
- App code purged of old 855 number: 22+ occurrences across 7 files (calfeed.py ×9, booking.py ×4 — both customer-facing — dashboard/specialist_billing/voice/hemet/specialist_booking), plus a 2nd-pass gap (hr.py ×2 letterhead, v2_dialer_numbers.html ×1). `sms.py:48` intentionally kept (idempotency matches both). "App is NAP-clean."
- A2P/SMS "HELP" (Twilio `HelpMessage`) verified CLEAN (Advanced Opt-Out; no number in it).
- "Cheryl J." testimonial pulled from /reviews (a review from someone connected to the business = the exact "deceptive content" category). ⚠️ if Cheryl J = Cheryl Johnson (partner), NEVER ask her for a Google review. DJ to confirm identity.

**OPEN ITEMS — prioritized for the appeal (2026-09-09):**
- ★ **MUST before submit (appeal-critical):** (1) DECIDE THE ONE ADDRESS — real, operated-from, that you have a utility bill for in the business name, and that your registration shows; (2) make the GBP LISTING show that SAME address; (3) upload registration + utility bill BOTH showing that name+address (they must match the listing); (4) clean external directories still showing the OLD 855 / wrong city (Yelp, Thumbtack=Palm Desert, homeyou, Nextdoor=Hemet) + DELETE the two MapQuest duplicates (`430179537`, `467659337`) — Google reads the search index, not just the site.
- **Can wait (not submit-blockers):** brand tagline "Serving Hemet & the Coachella Valley"; LocalBusiness JSON-LD `legalName`; the durable decision-log feature (WSC-DECISION-LOG-SPEC — a "what does this touch" surface-list that would have caught the original suspension).
- **Resolved:** account owner = windowandsolarcare@gmail.com (from the form).

**Durable-fix proposal:** company decision log with a "surfaces this touches" field + `checked_on` date, surfaced via briefing.py, monthly stale-check — "precisely what would have caught the Google suspension."

Sources: cheryl-workspace `WSC-NAP-CHECKLIST.md` / `MEMORY-AUDIT.md` / `AGENT-MAIL-OUT.md` (2026-09-04); app-repo AGENT_MAIL.md; memories [[project_wsc_domain_cutover]], [[project_wsc_legal_name]], [[project_localbusiness_schema_todo]], [[project_ai_growth_seo_website]].
