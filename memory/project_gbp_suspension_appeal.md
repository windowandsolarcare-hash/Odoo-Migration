---
name: project_gbp_suspension_appeal
description: "✅ RESOLVED — Google Business Profile REINSTATED 2026-09-28 (appeal case 9-2903000041323; DO NOT re-file). Suspension reason was 'flagged for suspicious activity'; NAP mismatch the driver. Appeal won on Articles+EIN showing the Thousand Palms home address + phone 760-334-5355. ★ ONE OPEN DJ ACTION: a separate still-unread 2026-09-28 'Further verification required' email — DJ must complete Get-verified (business.google.com/n/13507549370210966/profile/verify) before his listing EDITS publish to customers. Full history + lesson [[reference_platform_appeal_file_once]] kept."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-10-06T04:41:52.471Z
---


> ## ✅ RESOLVED — PROFILE REINSTATED. Google confirmed reinstatement **2026-09-28** (DJ re-confirmed live 2026-10-05). Appeal case **[9-2903000041323]**. **DO NOT RE-FILE** — the appeal succeeded; any further filing only risks the account. History below kept for the record.
>
> **★ ONE OPEN DJ ACTION (NOT the appeal — a separate ownership-verification step):** a SECOND Google email the same day (2026-09-28, subject *"Further account verification is required for Window & Solar Care"*, **still UNREAD** in the inbox as of 2026-10-05) says: *"You must successfully verify your profile so your edits can be visible to customers."* So the profile is LIVE/reinstated, but until DJ completes **"Get verified"** (→ `https://business.google.com/n/13507549370210966/profile/verify`), any edits he makes to the listing will NOT publish to customers. The reinstatement email's "no further action to verify at this time" refers to the APPEAL; this manage/edit verification is a distinct Google step and is login-walled (DJ-only — his identity). **Until DJ finishes Get-verified, treat the listing as read-only to customers.**
>
> **Exact reinstatement wording (googlebusinessprofile-support@google.com, 2026-09-28 06:21 UTC):** *"I'm happy to confirm that we were able to reinstate the Business Profile for you. No further action is required on your part to verify at this time. After the profile is live again, it may take a few days for it to start appearing on Google."* Appeal docs accepted = `Articles.Windowandsolarcare.pdf` + `EIN.Windowandsolarcare.pdf` (both Thousand Palms address), phone `(760) 334-5355`, framed as home-based service-area business.

**Window & Solar Care's Google Business Profile is SUSPENDED — CONFIRMED reason = "flagged for suspicious activity"** (★ CORRECTED 2026-09-26 via Lead/Dispatcher: DJ read the ORIGINAL Google suspension email verbatim; primary source now in WSC-NAP-CHECKLIST.md §G. The earlier "deceptive content" label was our INFERENCE, not what Google said — do not repeat it.) The underlying driver is still a NAP (Name/Address/Phone) mismatch across the places Google can see — primarily an inconsistent PHONE, compounded by an inconsistent ADDRESS. ★ **APPEAL SUBMITTED 2026-09-27** (DJ filed it — a long time coming). Status: FILED, awaiting Google's response. DO NOT re-file (see file-once caution). Investigation/fix work was 2026-09-03/04.

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
- "Cheryl J." testimonial pulled from /reviews (a review from someone connected to the business — still worth removing for authenticity/NAP hygiene, though NOT "the exact suspension reason": reason is "suspicious activity", see correction above). ⚠️ if Cheryl J = Cheryl Johnson (partner), NEVER ask her for a Google review. DJ to confirm identity.

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
- ~~Odoo `res.company` id1 address~~ — **CORRECTED 2026-09-18 (DJ via Lead): this is INTENTIONAL, do NOT flag or "fix" it.** The `41995 Boardwalk Ste. J, Palm Desert CA 92211` on res.company id1 is DJ's still-active MAILBOX, kept ON invoices ON PURPOSE for privacy (he doesn't want customers seeing his hidden-SAB home address). Invoices are private correspondence, NOT a public Google-indexed NAP citation, so a "wrong" address there is fine. See [[project_wsc_address_do_not_publish]]. (NB: the ADDRESS is the only intentional part — the same record's phone 951-972-6946 IS a real fix → should be 760-334-5355; Lead routed it to Operator 2026-09-18.) The NAP rule is unchanged: the mailbox and the hidden home address must be OFF every PUBLIC listing; on invoices is by design.
- **Yelp** — phone was old **(855) 245-2273** at the 2026-09-18 sweep; ★ CORRECTED to **760-334-5355 (DONE)** per Lead/Dispatcher 2026-09-26. Service-area shows "Thousand Palms" (no street).
- **MapQuest** — dupe **#430179537 STILL LIVE** (Thousand Palms 92276, Yelp-fed). AND a SEPARATE MapQuest listing indexed at **Rancho Mirage, CA 92270** (city conflict). So MapQuest has ≥2 live entries with different cities — more than the "2 dupes" recorded, and the appeal-relevant city inconsistency (Thousand Palms vs Rancho Mirage) is LIVE. Both non-Thousand-Palms/duplicate entries should be removed/merged.
- **Angi / HomeAdvisor** (Angi-owned) — W&SC listed as a SERVICE-AREA pro, 4.9 (17), across Rancho Mirage/Desert Hot Springs/Indio/Cathedral City/Bermuda Dunes/Hemet — no fixed street (NAP-safe on address). PHONE not shown in public snippet → verify on the claimed profile (DJ login).
- **Nextdoor** — DJ's OWN business page is not publicly indexed (public search returns only an UNRELATED "FM Window & Solar Care" in Pasadena). The "still Hemet?" question can only be answered from **DJ's logged-in Nextdoor** — OPEN, needs DJ.
- **Facebook / Instagram / X** — no public W&SC business page surfaced; current address/phone can't be verified without **DJ's logged-in sessions** — OPEN, needs DJ.
- **Apple Maps** — no headless web surface; verify/correct via **Apple Business Connect** (Apple device / DJ login) — OPEN, needs DJ.

**Net:** the /reviews "Cheryl J." item is fixed at the source; Yelp phone now 760 (done). Remaining PUBLIC NAP drift is the res.company PHONE on invoices (951→760, routed to Operator; the ADDRESS there is intentional — see [[project_wsc_address_do_not_publish]]) and MapQuest (live dupes + Thousand-Palms-vs-Rancho-Mirage city conflict). The login/app-walled directories (Nextdoor/FB/IG/X/Apple) still need DJ's own sessions to verify — not reachable headlessly.

---

## ★ CONFIRMED REASON + FILE-ONCE CAUTION (2026-09-26, via Lead/Dispatcher; DJ has read it — no new DJ decision needed):
- **Suspension reason = "flagged for suspicious activity"** (Google's own words, DJ read the original email; primary source WSC-NAP-CHECKLIST.md §G). NOT "deceptive content" and NOT "no reason given" — those were earlier inferences. Fold this exact reason into the reinstatement/appeal narrative.
- **★ FILE THE REINSTATEMENT ONCE, CLEAN.** A repeat or sloppy appeal risks the WHOLE `windowandsolarcare@gmail.com` Google account (not just the profile). So: get the NAP + evidence airtight FIRST, then submit a single clean appeal — do not fire off attempts iteratively.
- Appeal package otherwise unchanged + correct (address linchpin: one provable address matching listing + registration + utility bill). Yelp phone → 760 is DONE.
