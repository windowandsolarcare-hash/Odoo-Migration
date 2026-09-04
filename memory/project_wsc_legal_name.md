---
name: project_wsc_legal_name
description: The registered entity is "Window & Solar Care, LLC" WITH a comma (CA SOS B20260293155). Twilio's profile omits it — Twilio is the outlier, not the authority.
metadata:
  type: project
---

**The legal name is `Window & Solar Care, LLC` — WITH the comma.** Source of truth: the
California Secretary of State filing, entity **B20260293155**, Active, agent Daniel Saunders,
32569 San Miguelito Drive, Thousand Palms CA 92276.

**★ The trap:** Twilio's A2P Trust Hub Customer Profile records it as `Window & Solar Care LLC`
— **no comma**. On 2026-09-03 that was briefly treated as authoritative and the website was
changed to match, then reversed the same day when Lead pulled the SOS record with DJ. **Twilio
is the outlier. The SOS filing wins.** Don't "fix" the site to match Twilio again.

- **Legal name** (`Window & Solar Care, LLC`) belongs in: footer copyright, Terms & Conditions,
  Privacy Policy, any "operated by" line, and JSON-LD `legalName`.
- **Trade name** (`Window & Solar Care`, no LLC) stays in headlines, nav and marketing copy,
  and is the JSON-LD `name`. Never append LLC to hero copy.
- **Footer** (DJ 2026-09-03): **no year** — a hardcoded one is wrong every January and nobody
  bumps it. **No period after LLC.** Live form: `© Window & Solar Care, LLC · All rights
  reserved` — a middot separates the halves, since dropping the period outright would leave
  `LLC All rights reserved` as a run-on.
- EIN 42-3461012 (from the Twilio registration; see [[project_twilio_a2p_registration_facts]]).

**Why:** two records disagree on one character, and the wrong one was nearly baked in. Anyone
auditing name consistency across Twilio / GBP / the website will hit this again.

**How to apply:** before changing the legal name anywhere, check the SOS filing, not Twilio or
GBP. See [[project_wsc_domain_cutover]] for the site the name appears on.
