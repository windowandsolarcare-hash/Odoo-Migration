---
name: project_feed_badge_int_crash
description: "The HUD feed 500'd (whole 'what needs you' list blank) because a feed card had badge='REPLY' (a string) and the counts rollup did int(badge) OUTSIDE api_feed_list's try/except — one bad card takes down the entire feed. Coerce non-numeric badge to 0."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-07T01:09:28.745Z
---

**Root cause (2026-09-06, DJ's HUD fully down in the field):** `routers/owner/feed.py` `api_feed_list` (and its twin `api_feed_live_list`) build a `counts` rollup AFTER the `try/except` that wraps `list_items`. One line was `'badge': sum(int(x['item'].get('badge') or 0) for x in live)`. A feed card produced by the customer-reply notifier had **`badge: 'REPLY'`** (a label, not a count) — card id `operator:reply:16952`, "Clark Argeris - reply: got it, windows only". `int('REPLY')` → `ValueError: invalid literal for int() with base 10: 'REPLY'`. Because that genexpr sits OUTSIDE the try/except, the exception escaped as an **uncaught 500** and blanked the ENTIRE HUD feed ("Couldn't load the feed — check signal"). ONE malformed card kills the whole list.

**Fix (shipped, verified 200 live):** added `_badge_int(v)` helper (try `int(v or 0)` / except `(TypeError, ValueError)` → 0) and used it in BOTH badge sums (feed.py ~398 list + ~436 live_list). A badge that isn't a clean int now counts as 0 instead of 500ing. Commit `becd7505`.

**Upstream (Specialists' deeper fix):** the reply-card producer should not put a non-numeric string in `badge` (a numeric-count field). 'REPLY' belongs in a label/pill field, not `badge`. The guard makes any bad badge harmless, but the producer's schema misuse is the real defect — routed to Specialists.

**Verification-insufficiency trap I fell into:** the FIRST error I found in the logs was a `project.task(999999999) MissingError` at 16:26 UTC — a SEPARATE, older, unrelated error. I nearly diagnosed the outage from it. The LIVE failure (reproduced by curling `/owner/api/feed/list` with an owner cookie → HTTP 500, then reading the FULL traceback to its deepest frame `ValueError: invalid literal for int() with base 10: 'REPLY'`) was the true cause. **Lesson: reproduce the failure NOW and read the traceback to its final "ValueError:/…Error:" line — don't diagnose a live outage from the first stale error in the log window.** Also: HTTP 200 on the app ROOT ≠ the failing endpoint is fine; test the SPECIFIC endpoint. Related: [[project_odoo_200_not_success]], [[project_401_not_route_exists]], [[project_writeback_not_proof_computed_field]].

**General rule this reinforces:** any per-item computation in a count/rollup that runs OUTSIDE the endpoint's try/except is a whole-feature-killer — one malformed stored item 500s everything. Coerce defensively (never raw `int()`/`float()` on stored JSON values) OR move the rollup inside the guard. The feed store (`ir.config_parameter wsc.feed.items`) is producer-written JSON; treat every field as possibly-malformed at read time.
