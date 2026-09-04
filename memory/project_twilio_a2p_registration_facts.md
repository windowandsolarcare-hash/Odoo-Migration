---
name: project_twilio_a2p_registration_facts
description: "Twilio A2P 10DLC full registration state (verified live 2026-09-03): brand/campaign/customer-profile all Verified/Approved, number 760-334-5355 attached, registered entity 'Window & Solar Care LLC' EIN 42-3461012 — and it's cutover-safe, do NOT edit (re-vetting risk)."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-04T01:47:40.387Z
---

**Verified live in the Twilio console 2026-09-03** (Lead drove it; DJ logged in, session carried over). Account: "My first Twilio account" (Account SID is the `AC…` string on the Twilio console dashboard — not repeated here; GitHub secret-scanning blocks the literal).

**A2P 10DLC is FULLY HEALTHY — every layer green:**
- **Customer Profile (Trust Hub)** `BUd18bb9a6d9aeddf24981a3a1de1d9afb` — ✅ Twilio Approved.
- **Brand** `BN43bb88d2d4aa6c4798f57541145e5c1a` ("WSC A2P Messaging Profile") — 🟢 Registered, Low Volume Standard. Trust Hub A2P bundle `BUb1834d3032086cc3c8ea1a730dd60d72`. External Brand ID BM65NM4.
- **Campaign** `CM2f33d239cdb8c27bc597cb5495c12465` — 🟢 **Verified**, use case **Customer Care**, External Campaign ID C47FUAT. Linked Messaging Service `MG9d920513cc6e7f7963a4334a818fbf05`.
- **Number attached to campaign:** `+17603345355` = **760-334-5355** (the CORRECT public number), status Registered, phone SID `PN5cf4cce2134594e3e9d31437982eb1d5`.

**Registered business identity (from the Trust Hub profile):**
- Legal entity: **Window & Solar Care LLC** (Limited Liability Corporation), Industry PROFESSIONAL_SERVICES.
- **EIN: 42-3461012**.
- Address: 32569 San Miguelito Drive, Thousand Palms, CA 92276, US.
- Authorized rep / "people to contact": **Daniel Saunders, windowandsolarcare@gmail.com, +1 951-972-6946**.
- Registered website: `https://windowandsolarcare.com` (domain only, no path).

**★ Cutover-safe — nothing in Twilio breaks when windowandsolarcare.com flips to the Odoo site.** The only URLs on file are (a) the domain-level website (domain unchanged) and (b) the opt-in flow citing `/free-quote/` which **301s cleanly to `/quote`**. There is **NO `/terms` URL registered** here (Web's defensive checklist assumed one; it doesn't exist), so the "terms URL breaks post-cutover" concern does NOT apply to Twilio.

**★ RULE: do NOT edit the A2P brand/campaign or the Trust Hub profile without a deliberate reason.** They're Verified/Approved; editing can trigger **re-vetting** (lose Verified status, possible re-vet fee). Nothing here needs changing for the cutover.

**NAP note:** the owner-contact phone in the profile is **951-972-6946** — a THIRD number vs the old 855 toll-free and the correct 760-334-5355. It's the rep's *verification* contact, NOT public-facing, so it does NOT feed the GBP/website NAP consistency issue that suspended the [[project_localbusiness_schema_todo]] / GBP profile. Leave it.

**Open item DJ raised (separate decision):** DJ asked about "the Comm LLC" — Twilio is currently on "Window & Solar Care LLC" (EIN 42-3461012). Swapping the registered entity is the ONLY thing that'd justify touching this, and it forces a full re-vet. Not done; needs DJ's explicit call. See [[feedback_ported_means_twilio]].
