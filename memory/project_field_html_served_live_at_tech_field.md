---
name: field-html-served-live-at-tech-field
description: "static/owner/field.html is the LIVE tech field screen served at /tech/field; the /owner/field route is retired — corrects CLAUDE.md rule 10's stale reachability claim."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-22T16:25:57.229Z
---

`static/owner/field.html` (V1) is NOT vestigial — it is served LIVE to field techs at **`/tech/field`** (`routers/tech/jobs.py:16-18` `tech_field()` does `open("static/owner/field.html")`; registered at `main.py:1127` `include_router(tech_jobs.router, prefix="/tech")`). Firsthand-confirmed 2026-10-22.

The legacy OWNER route `/owner/field` was reversibly RETIRED 2026-09-27 (`dashboard.py:9669`) and has zero live client links (only `static/owner/_archive_v1/*` + "instead of legacy" comments). So CLAUDE.md **rule 10's** claim that "V1 field.html is reached ONLY via `ql_panel.js:576 → /owner/field`" is **STALE** — the real reachability is `/tech/field`.

**Why:** field.html can't be treated as dead and can't be retired — the crew uses it daily at /tech/field. Tech-facing fixes to the field/job screen must land IN `field.html` (the live tech twin), not only the v2 owner panel. This is the same field.html↔panel twin trap as [[project_field_deeplink_return_latch]]: a fix often has to land in BOTH the v2 owner path (`v2_field.html` / `_job_detail_panel.js`) AND `field.html`@/tech/field.

**How to apply:** when touching the field/job screen, treat it as dual-surfaced — owner (v2_field.html / _job_detail_panel.js) AND tech (field.html served at /tech/field). Check both; don't trust rule 10's reachability line. Example (2026-10-22 nav fix): the owner so_history fix flowed nav_addr to /tech/field automatically because field.html:4676 calls /owner/api/so_history, but field.html's openJobById still needed its own client-side nav_addr passthrough. Related: [[nav-addr-canonical-source]], [[project_two_quote_pages_two_launchers]].
