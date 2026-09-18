---
name: project_gbp_suspension_appeal
description: "Google Business Profile SUSPENDED (deceptive content / NAP mismatch). Full history + what was fixed + the appeal open-items. As of 2026-09-09: NOT filed, no action since Sep 4. Appeal linchpin = ONE provable address matching listing + registration + utility bill."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-10T00:06:16.864Z
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

**★ DECISIONS LOCKED (DJ 2026-09-09):**
- **Canonical address = DJ's HOME: `32569 San Miguelito Dr, Thousand Palms, CA 92276`** (home-based business). This matches the CA SOS Articles of Organization AND the federal EIN letter.
- **Appeal docs to upload = (1) federal EIN letter + (2) CA Articles of Organization** — BOTH show the Thousand Palms address. Google's form asks for a utility bill, but DJ has **no utilities in the business name** (home-based; LLC only ~2 months old, approved ~2026-07, so no time to set up business utilities). The EIN + Articles (two official gov docs bearing the same address) are the substitute, agreed with an earlier Lead. Explain the home-based/new-LLC rationale in the appeal notes.
- **DJ approved the fleet doing the external directory cleanup + MapQuest dupe deletions via computer-use** (he'll provide logins on request).

**OPEN ITEMS — prioritized for the appeal (2026-09-09):**
- ★ **MUST before submit (appeal-critical):** (1) DECIDE THE ONE ADDRESS — real, operated-from, that you have a utility bill for in the business name, and that your registration shows; (2) make the GBP LISTING show that SAME address; (3) upload registration + utility bill BOTH showing that name+address (they must match the listing); (4) clean external directories still showing the OLD 855 / wrong city (Yelp, Thumbtack=Palm Desert, homeyou, Nextdoor=Hemet) + DELETE the two MapQuest duplicates (`430179537`, `467659337`) — Google reads the search index, not just the site.
- **Can wait (not submit-blockers):** brand tagline "Serving Hemet & the Coachella Valley"; LocalBusiness JSON-LD `legalName`; the durable decision-log feature (WSC-DECISION-LOG-SPEC — a "what does this touch" surface-list that would have caught the original suspension).
- **Resolved:** account owner = windowandsolarcare@gmail.com (from the form).

**Durable-fix proposal:** company decision log with a "surfaces this touches" field + `checked_on` date, surfaced via briefing.py, monthly stale-check — "precisely what would have caught the Google suspension."

Sources: cheryl-workspace `WSC-NAP-CHECKLIST.md` / `MEMORY-AUDIT.md` / `AGENT-MAIL-OUT.md` (2026-09-04); app-repo AGENT_MAIL.md; memories [[project_wsc_domain_cutover]], [[project_wsc_legal_name]], [[project_localbusiness_schema_todo]], [[project_ai_growth_seo_website]].

---

## ★ VERIFIED LIVE 2026-09-18 (Web — browser sweep on DJ's Chrome + Odoo RPC). Reconciles the record to reality; DJ's hunch was that more was done — for some items it's the OPPOSITE (they were NOT done):

**DONE / clean:**
- **Website /reviews — "Cheryl J." testimonial was STILL LIVE** (DJ believed it removed 5×). Root cause: his edits never reached the SOURCE view `wsc.reviews` (ir.ui.view id 3841, website 1) — the only reviews page — so every re-render/rebuild restored it. **Web removed the exact `<div class="quote">…Cheryl J.…</div>` block from view 3841 (validated XML) and verified live-gone** (curl /reviews: 0 Cheryl hits, other reviewers intact, renders clean). This one is now truly done.
- **Website phone** = 760-334-5355 site-wide, zero 855/2273 (re-verified live). **JSON-LD** legalName="Window & Solar Care, LLC" (comma, correct per SOS). Good.
- **Bing** — no distinct W&SC listing surfaced (Bing web + Bing Maps show only competitors). No NAP conflict to fix (optionally an unclaimed-listing opportunity).
- **Houzz** — no W&SC listing found (not indexed).
- **MapQuest dupe #467659337** = GONE (404). One of the two known dupes is deleted.

**STILL OPEN / WORSE than recorded:**
- **Odoo `res.company` id1 = STILL OLD** — `41995 Boardwalk Ste. J, Palm Desert CA 92211`, phone **951-972-6946** (a THIRD wrong number, not even the 855 or 760-334-5350). This prints on INVOICES. Money-touching accounting record → Operator/DJ to fix, not Web. Should be the registered Thousand Palms address + 760-334-5355.
- **Yelp** — phone STILL old **(855) 245-2273** (biz page "Updated August 2026"). Service-area shows "Thousand Palms" (no street). PHONE must be corrected on Yelp.
- **MapQuest** — dupe **#430179537 STILL LIVE** (Thousand Palms 92276, Yelp-fed). AND a SEPARATE MapQuest listing indexed at **Rancho Mirage, CA 92270** (city conflict). So MapQuest has ≥2 live entries with different cities — more than the "2 dupes" recorded, and the appeal-relevant city inconsistency (Thousand Palms vs Rancho Mirage) is LIVE. Both non-Thousand-Palms/duplicate entries should be removed/merged.
- **Angi / HomeAdvisor** (Angi-owned) — W&SC listed as a SERVICE-AREA pro, 4.9 (17), across Rancho Mirage/Desert Hot Springs/Indio/Cathedral City/Bermuda Dunes/Hemet — no fixed street (NAP-safe on address). PHONE not shown in public snippet → verify on the claimed profile (DJ login).
- **Nextdoor** — DJ's OWN business page is not publicly indexed (public search returns only an UNRELATED "FM Window & Solar Care" in Pasadena). The "still Hemet?" question can only be answered from **DJ's logged-in Nextdoor** — OPEN, needs DJ.
- **Facebook / Instagram / X** — no public W&SC business page surfaced; current address/phone can't be verified without **DJ's logged-in sessions** — OPEN, needs DJ.
- **Apple Maps** — no headless web surface; verify/correct via **Apple Business Connect** (Apple device / DJ login) — OPEN, needs DJ.

**Net:** the "deceptive content" /reviews item is now genuinely fixed at the source. The remaining NAP drift is concentrated in Odoo-invoices (951 + Palm Desert), Yelp (855), and MapQuest (live dupes + Thousand-Palms-vs-Rancho-Mirage city conflict). The login/app-walled directories (Nextdoor/FB/IG/X/Apple) still need DJ's own sessions to verify — not reachable headlessly.
