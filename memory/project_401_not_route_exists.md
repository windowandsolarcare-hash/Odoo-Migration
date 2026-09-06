---
name: project_401_not_route_exists
description: "On the Render app under AUTH_ENFORCE=1, a 401 does NOT prove a route exists — the auth middleware answers BEFORE routing, so a nonexistent /owner or /cheryl path 401s just like a real one. Verify a route is built by CONTENT with a real cookie, never by status."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-06T08:18:05.341Z
---

**On the Saunders Render app with AUTH_ENFORCE=1, a 401 tells you NOTHING about whether a route exists.** The auth gate (Block B / authz.py) runs as middleware BEFORE routing, so ANY path under a protected prefix returns `401 {"error":"auth required"}` to a no-cookie caller — including a made-up path. Proven 2026-09-06 by Cheryl's cloud: `GET /cheryl/nonexistent-route-xyz` (no cookie) → 401, identical to `/cheryl/hud` → 401.

**The trap (both Lead and Cheryl's cloud fell for it, 2026-09-06):** inferring "`/cheryl/library` returns 401, not 404, therefore the route is built." INVALID. The 401 is the wall answering, not the router. Lead had told DJ "/cheryl/library is built" on that basis — it wasn't independently confirmed.

**How to actually verify a route is built under enforcement:** mint a cookie for a role allowed on that prefix (e.g. `POST /api/login` for a cheryl-role contact), then GET the path WITH the cookie and check the **CONTENT** — real page bytes + expected content-type (the way /cheryl/hud was verified: 200 + 40,785 real bytes with a cheryl cookie). A route that 404s or errors BEHIND the cookie is not built; a 401 with the cookie means the role isn't allowed there; only real content proves "built."

**Why:** direct sibling of [[project_odoo_200_not_success]] and [[feedback_odoo_verify_content_not_status]]. That rule says 200 ≠ success (denied Odoo attachments serve placeholder.png 200). This adds the enforcement-era corollary: **401 ≠ route-absent AND 401 ≠ route-present** — status codes from behind an auth wall are about auth, not routing. Verify deployment claims by content with the right cookie, never by bare status from outside. Applies to any external smoke-test of `/owner/*` or `/cheryl/*` under AUTH_ENFORCE=1.
