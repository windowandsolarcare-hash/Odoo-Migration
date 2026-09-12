---
name: project_field_deeplink_return_latch
description: "The field \"wrong location, needs relog\" bug = a write-once in-memory nav-intent global (_backToCC in field.html, _fromDeep in v2_field.html) latched true on a deep-link arrival and NEVER cleared, so every later close/return blindly history.back()s to stale history. Fixed 2026-09-12 by making them one-shot. Also: v2_field.html IS field.html's V2 twin (CLAUDE.md's \"no v2 twin\" is stale)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T16:33:31.696Z
---

**Fixed 2026-09-12.** DJ's recurring "a field/job screen drops me in the wrong place and I have to log out/in" bug.

## Root cause — write-once in-memory nav-intent global (a rule-12 class)
Both field screens set a window global when opened via a deep-link (`?from=cc` / `?open_so=`) so the ‹ Back/close returns to the SENDER via `history.back()`:
- **field.html (V1):** `window._backToCC` (set once at ~line 2010 from `?from=cc`).
- **v2_field.html (V2):** `window._fromDeep` (set at ~1110 and ~3979 when a deep-link opens with history.length>1).

These are long-lived SPAs (jobs open/close + "Next Job" swap with NO page reload). The flag was set once and **never cleared**, so after ONE deep-link arrival, EVERY subsequent close/return (`apBack`, `_returnToOrigin`, record-payment, delete, snooze…) blindly called `history.back()` — popping to whatever stale/blank entry was in the browser/bfcache history instead of the current job/schedule. Only a full reload (= log out/in) cleared the window global → "needs relog."

**Fix — field.html (V1):** made `_backToCC` ONE-SHOT — clear it before the `history.back()` (read sites ~2826/3543).

**Fix — v2_field.html (V2, the LIVE screen) — SUPERSEDED the one-shot with a DURABLE return target (DJ 2026-09-12):** the one-shot `_fromDeep` was still in-memory, so a webview background→restore / bfcache pageshow / reload left it undefined → close fell THROUGH to v2_field's OWN day-view schedule (narrow cards = DJ's "old schedule") instead of returning to the Command Center — his exact recurring symptom, relog to fix. New fix: at load, WHEN `?open_so` is present, capture `sessionStorage.setItem('v2field_return', document.referrer || '/static/owner/v2_command.html')` **BEFORE** the replaceState that strips `open_so` (the strip removes the only signal we were deep-linked, so capture must precede it). The close/‹Back handler (formerly the `_fromDeep` sites ~1467/1985) now reads that key → `location.href = <target>` + clears it — deterministic, survives reload/bfcache. A DIRECT open of v2_field (no `open_so`) clears `v2field_return` (boot's else) so close correctly reveals the day view (its home). `_fromDeep` removed entirely. Capture is in BOTH open_so blocks (boot ~3979 + the loadField-tail block ~1110); boot runs first (entry at ~4017, before loadField), so it's the real consumer.

## Secondary: `_openSoDone` in-memory flag (NOT changed — noted)
Both screens guard the `?open_so` deep-link re-open with in-memory `window._openSoDone` + a `history.replaceState` that strips `open_so` from the URL. Within a page load this prevents the 5-min `setInterval(loadField)` from re-opening the job (the 2026-07-07 "back on the last job / roof-photos" bug). A webview **resurrection that restores the original (unstripped) URL** could re-open it (flag reset + open_so back). **Do NOT "fix" this with a sticky durable (localStorage/sessionStorage by so_id) guard** — each legitimate re-navigation to the same job is a FRESH page load that correctly resets the in-memory flag, and a sticky guard would wrongly BLOCK re-opening the same job in the same session. The replaceState strip + DJ's Reset-app button cover the edge. Left as-is on purpose.

## ★ V1/V2 field divergence (CLAUDE.md correction)
CLAUDE.md says "field.html is a V1 holdout with NO V2 twin." **That is now STALE.** `static/owner/v2_field.html` ("Field Day", ~4052 lines) IS the V2 twin and is the LIVE field/job-detail screen — virtually every v2 page links to `v2_field.html?open_so=` (command, maint_advance, myday, calendar, analytics, customers, outreach, callcard…). `field.html` (V1, ~7041 lines) is now reached mainly via the legacy `ql_panel.js:576` (`/owner/field?tab=customers&ret=1`) on legacy pages. The two DUPLICATE the deep-link/return logic (so bugs must be fixed in BOTH — this one was). Retiring V1 field.html / repointing ql_panel is a separate DJ/Lead design call.

Related: [[feedback_never_remove_working_code]], [[project_two_quote_pages_two_launchers]], [[project_v2_launcher_duplicated_stale]].
