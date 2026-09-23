---
name: project_static_gates_miss_semantic_placement
description: "Static deploy gates (drift-clean diff, py_compile, node --check, AST 'add-only') pass on a change that is syntactically valid but SEMANTICALLY misplaced — e.g. an allowlist entry added to the WRONG collection. A new endpoint's LIVE end-to-end test is the only gate that catches it; and HTTP 200 can carry an error body, so verify the READ by content too."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-23T15:42:22.073Z
---

# Static deploy gates can't catch WRONG-COLLECTION placement — a live end-to-end test can

**2026-09-23, telemetry deploy (ef330e11 → fix 28508ad9 → serializer batched).** Two bugs shipped past a full battery of static gates and were caught only by exercising the live pipe end-to-end. Both are instances of "verify real behavior, not a proxy," worth a concrete note.

## Bug 1: an allowlist entry added to the WRONG collection
The new telemetry beacon/rate routes were meant to go in `authz.py`'s `PUBLIC_EXACT` (cookieless-exempt). They were mis-anchored and landed in `TECH_GRANTED_OWNER` instead (the editor anchored to a nearby tech-granted route's closing `)`). ALL static gates PASSED and none could have caught it:
- `py_compile` / `node --check` — the code was syntactically valid.
- drift-diff — it WAS add-only.
- AST "add-only" check — it correctly added lines.
None of these check WHICH collection the lines joined. So the cookieless sendBeacon got 401'd by the owner middleware (never actually exempt). **Only the post-deploy LIVE beacon test** (fire a real cookieless beacon → expect 204) exposed it. Fix moved both entries into `PUBLIC_EXACT` (AST-verified `in PUBLIC_EXACT`, not `in TECH_GRANTED_OWNER`).

## Bug 2: HTTP 200 with an error body (the read view)
`GET /rate` with the right secret returned **200** — but the body was `{"ok":false,"error":"Object of type datetime is not JSON serializable"}` (psycopg returns ts/first_seen/last_seen as datetimes; plain `JSONResponse` can't serialize them). Reading the log STATUS LINE (200) read as "works"; reading the BODY showed the read view was broken. The Lead mis-called it "works" from the 200 before Specialists read the body. Fix: `Response(json.dumps(rate(sm), default=str), media_type='application/json')`. (The beacon+INSERT were fine — only the read rendering broke, so no data lost; the fix was batched to avoid a restart while DJ was in the field.) This is [[feedback_odoo_verify_content_not_status]] applied to our OWN endpoints, not just Odoo.

## How to apply
- **Every new/changed ENDPOINT gets a live end-to-end test before it's called done** — for an auth-exempt or auth-gated route, actually hit it in each mode (exempt → 204/200; gated → 401 without creds, 200 with) and read the BODY, not the status line. Static gates (compile/lint/drift/AST) prove syntax and diff shape, NEVER semantic correctness (right collection, right serialization, right data).
- **Prove the pipe end-to-end, never trust an empty/200 view.** Fire one known input, confirm it appears on the read side by CONTENT. This is also why an unset telemetry DB env would have been a false all-clear (see the MEMORY_DB_URL fallback + loud no-DB boot warning).
- The live pipe caught what every static gate missed **twice** in one deploy — budget for the live e2e test, don't skip it because "compile + drift passed." Ties to [[feedback_no_conclusion_from_single_test_sporadic]] and [[project_logs_healthy_but_user_broken_is_client_side]]. MIRROR to Odoo-Migration/memory/ pending (held during the deploy freeze).
