---
name: project_dj_return_today_20260805
description: "DJ's two hands-on tasks for when he returns 2026-08-05 — (1) kill Zapier, (2) clean-login + flip AUTH_ENFORCE. When he asks 'what do I need to do?', tell him these two."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-05T14:10:49.213Z
---

**When DJ returns today (2026-08-05) and asks "what are the things I need to do?", tell him these TWO:**

1. **Kill Zapier.** Turn off / disconnect the Zapier zaps (Workiz→Odoo sync is being retired; Workiz went dark ~Aug 3-4). DJ does this in his Zapier account. (This is his call/action, not mine — I don't have the Zapier off-switch; confirm which zaps if he wants a list.)

2. **Log in + flip the authorization.** His clean-cycle: **log in → sign out → log in again → stay logged in** (verified working — sign-out now POSTs /api/logout to clear the SERVER cookie, deployed + confirmed live 2026-08-05; 180-day sliding session, he stays logged in after the final login). THEN flip **`AUTH_ENFORCE=1`** to lock the app. He can set it himself on Render (wsc-field-assistant service → Environment tab → AUTH_ENFORCE=1 → save) OR say "flip it" and I do it via Render API (POST-per-var, never PUT the full env list — [[feedback_render_env_var_patch_not_put]]). Roll back = unset/0.
   - **Prereq before flip:** DJ + **Danny** + **Cheryl** should each log in once (mints their cookies) so they aren't locked out. If only DJ has logged in, Danny/Cheryl will be bounced until they log in.
   - Whitelist for machine callers already shipped ([[project_authz_block_b]]) so GPS/crons/Twilio/customer-pay won't break on flip. After flip: watch `/owner/api/authz/report` + app behavior; unset to roll back instantly.

Once both are done: Workiz is off AND the app is locked. Delete/retire this memory after DJ completes them.
