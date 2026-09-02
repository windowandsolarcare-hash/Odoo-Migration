---
name: feedback_verify_limits_before_declaring
description: "Before telling DJ \"I can't do X\" (esp. a cloud session claiming it can't reach the app/Odoo), actually TEST the call first — don't declare a limit from a stale doc."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-02T22:10:56.768Z
---

Before any session tells DJ it CANNOT do something — reach a URL, smoke-test the app, query Odoo, run a tool — it must **spend the five seconds to actually test it first.** Do not declare a limitation from memory or a doc header.

**Why:** The CLAUDE.md claim "cloud outbound network is GitHub-only, cloud can't smoke-test / can't reach Odoo" was **false on the current cloud env** and got repeated to DJ THREE times before anyone tested it. The allowlist was opened ~2026-08-22; a cloud session CAN hit `wsc-field-assistant.onrender.com` and `window-solar-care.odoo.com`, verify by content, and query Odoo. Root cause of the repeat: sessions read the doc's header bullet, not its corrected body — so a wrong "I can't" propagated as fact.

**How to apply:**
- Cloud session about to say "I'm GitHub-only / can't reach the app or Odoo" → run one real request against the target FIRST. Only report the limit if the request actually fails.
- Corrected the CLAUDE.md cloud-network bullet in place on 2026-09-02 (put the correction IN the bullet, since sessions read headers not bodies). See [[feedback_odoo_verify_content_not_status]].
- General form: a claimed constraint you're about to hand DJ as a reason not to do something = verify it live before stating it.
