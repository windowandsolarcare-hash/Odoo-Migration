---
name: feedback_dj_owns_cheryl_erp_access
description: "★ GOVERNANCE (DJ 2026-09-08): DJ progressively grants Cheryl access to more of his OWNER/ERP surfaces + data as HE chooses — the Cheryl workspace is NOT permanently walled off. A session may surface a privacy/scope concern ONCE for DJ to decide; once DJ decides, it's DECIDED — do NOT relitigate. First grants: HR + WSC Hiring."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-08T20:39:50.518Z
---

**DJ set this governance directive 2026-09-08 (with visible frustration that sessions kept resisting it).**

**The principle:** It is DJ's business, DJ's app, DJ's data. **DJ decides what Cheryl can access, and he intends to progressively open MORE of his owner/ERP surfaces to her over time.** The "Cheryl workspace is walled off from WSC systems" framing was a DEFAULT and a leak-prevention posture — NOT an absolute rule that overrides DJ's deliberate grants. Cheryl is his business partner actively helping him run parts of the business, so she legitimately needs access to owner surfaces he assigns her.

**First grants (2026-09-08):** Cheryl gets DIRECT cheryl-role access to **WSC Hiring** (`/owner/hiring`) and **HR** (`/owner/hr`) — she's actively helping DJ with both. (Yes, HR holds staff pay/personnel data; DJ knows and wants her to have it — she's helping run HR. Surfaced once, decided, done.) Clue for the build: `openWSCHR()` already sets `hr_user='Cheryl'` + `wsc_ac='wsc2026'` — the pages may already anticipate her; the gap is likely just the `/owner` authz wall 401ing cheryl-role. Routed to Specialists to build a REPEATABLE grant mechanism (not a bespoke hole per surface).

**★ The behavioral rule (this is the part DJ was frustrated about):** a session (Auditor, Cheryl's-cloud, Lead, anyone) may **surface a privacy/scope consideration ONCE** so DJ can decide deliberately — that's valuable. But **once DJ has decided, it is DECIDED. Do NOT re-fight it, re-raise it as a blocker, or resist on subsequent turns.** Repeated resistance to an owner's deliberate call about his own data is obstruction, not diligence. Implement his decision cleanly.

**What still holds (real security, not obstruction):** the `company_id` fails-open protections stay ([[project_company_filter_fails_open]]) — never expose OTHER companies' data (Saunders/Cheryl-RE) to the wrong surface. Granting Cheryl a W&SC owner surface is DJ's call; leaking a different company's data is a bug regardless. The wall's real job = default-deny + accidental-leak prevention, NOT blocking DJ's grants.

**How to apply:** treat "give Cheryl access to <owner surface>" as a first-class, expected request. Build for repeatable owner→Cheryl grants. Don't relitigate the walling-off principle each time. See [[feedback_auditor_user_perspective_gapfinder]] (surface gaps ONCE), [[feedback_never_send_dj_to_odoo]].
