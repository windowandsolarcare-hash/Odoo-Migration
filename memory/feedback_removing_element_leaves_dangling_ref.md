---
name: feedback_removing_element_leaves_dangling_ref
description: Removing an HTML element (e.g. a header button) without removing/guarding the JS that references it crashes page init — whole app gets stuck.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

2026-06-07: The field assistant (`static/owner/field.html`) went "haywire" — errors + a screen DJ couldn't get out of — after a header edit (from another Claude session) that removed the timeclock + mic buttons. Root cause: the edit deleted the element `id="clock-link"` but left the startup line `document.getElementById('clock-link').href = HUB_PREFIX + '/timeclock';`. `getElementById` returned null, `.href =` threw a TypeError, and that **halted the entire init block** — `boot()`, clock tick, tab setup, everything after it never ran. Server was fine (all pages 200); only the page's JS was dead. Fixed by null-guarding the line: `{ const _cl = document.getElementById('clock-link'); if (_cl) _cl.href = ...; }`.

**Why:** An uncaught exception during synchronous page-init JS stops everything below it. A single dangling getElementById after deleting an element bricks the whole app, not just that one feature.

**How to apply:**
- When removing ANY element from field.html / index.html / etc., grep the file for its `id` and remove or null-guard EVERY JS reference (`getElementById('X')`, querySelector, addEventListener) — especially ones in the init/boot path.
- Always `node --check` the extracted inline JS before pushing (see [[feedback_field_html_js_syntax_check]]) — but note syntax-check does NOT catch null-reference runtime crashes; you must also grep for dangling refs.
- Diagnosis pattern for "stuck/error screen, can't escape": server is usually fine (curl pages = 200); the break is a runtime JS error halting init. Pull the file, grep for refs to recently-removed element ids.
- **Multi-session hazard:** DJ edits this app from several Claude chats at once (Render Claude on phone + Claude Code). They step on each other — today's header edit + two "fix corrupt prefix" cleanups came from another session and left the dangling ref. Prefer driving field.html changes from one place. Related: [[feedback_local_vs_deployed_drift]], [[feedback_script_insertion_anchor]].
