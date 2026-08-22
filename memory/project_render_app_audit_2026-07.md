---
name: project_render_app_audit_2026-07
description: "2026-07-15 full-codebase audit of saunders-render-app — 59 findings (6 critical), + a redesign plan. Report artifact + fix backlog."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

2026-07-15: DJ asked for a full audit (bugs/security/perf/anti-patterns) + a UX redesign, "don't change original code, duplicate it." Ran 6 parallel read-only auditors over a fresh tarball checkout of `saunders-render-app` @ main 3a5d27a6 (no code touched). Delivered as an artifact report: https://claude.ai/code/artifact/48119877-c280-488f-8d95-11804b03d628 (source: scratchpad/render_app_audit.html). DJ chose "audit report first" then redesign later on **parallel preview routes (/owner/v2/…)** in the same app, so nothing live changes.

**6 CRITICALS (fix first, none fixed yet):**
1. No auth on any endpoint — see [[project_render_app_no_auth_layer]].
2. `/ask` AI agent (field.py:2970) has unauth `odoo_write` (any model/method) + `github_push_file` to prod → RCE/full-DB.
3. Live Odoo/Workiz keys hardcoded (main.py:57, printing/watcher.py:24, hemet.py, submitted_jobs.py, provenance.py) → rotate.
4. ✅ FIXED 2026-07-16 (commit 3258de95). Field payment double-charge. Live path is field.html doPayment/psDoPayment/sfDoPayment → POST /owner/api/payment → `_execute_payment` in **dashboard.py:4273** (NOT field.py — that copy is unused). Root cause: it only searched for a DRAFT invoice; on a lost-response retap the first invoice is now POSTED, so it minted a 2nd invoice+payment. Fix = surgical additive idempotency guard: if the SO already has a POSTED out_invoice with payment_state in ('paid','in_payment') → return success, create nothing; if posted-but-unpaid → register against that invoice (skip create+re-post). Verified read-only on real data: paid Done SOs (004904/004903/004619/004329) all payment_state='paid' → guard blocks dup; to-invoice SOs → guard doesn't trigger, normal flow. Client button already disables in-flight; server guard is the real protection (a retap after error is now idempotent). NOT yet added: client-side 30s fetch timeout (optional UX; server fix makes retap safe). Full throwaway end-to-end (create SO→double-pay→assert single) NOT run to avoid mutating production accounting — detection verified instead.
5. `cron.py` calls undefined `_find_open_att`/`_att_date_range_utc` (lines 296/366/409) → Tasker GPS clock-in/out + nightly Hemet flag NameError every call. Fix: import from timeclock.
6. Dead shadowed routers — see [[project_dead_shadowed_routers]].

**Recurring HIGH themes:** company_id=1 / [1,False] missing on several sales+customer queries (field.py:25 api_stats_month, dashboard.py sales tools, reactivation candidates) = other-company money in W&SC totals; async handlers block the event loop on sync odoo_rpc (the 502 root cause — myday.py already fixed, rest not); payments default to UTC date.today() not today_pt() (day-late dating); Twilio webhooks unsigned; booking token forgeable (truncated HMAC + default secret); field payments hardcode journal_id 6 → Zelle/cash misreported as Check.

**✅ Pinch-zoom fixed 2026-07-16 (commit 1e1362c5):** 39 static HTML pages had `maximum-scale`/`user-scalable=no` blocking zoom (worst a11y miss for DJ's limited vision). Replaced each viewport content with `width=device-width, initial-scale=1` in ONE atomic git commit (git Trees/Commits API — not 39 contents pushes → 1 deploy, not 39). Each file asserted single-line diff before commit. All static/owner/* + login/booking/printing/tech/cheryl/chores. **GPS clock-in fix (C5) DECLINED by DJ 2026-07-16** — he keeps clock-in manual, doesn't want auto location-based clock-in re-enabled.

**Pattern for bulk same-edit across many repo files:** use the git Data API (get ref→base commit→base tree; per file: get blob, edit, create blob; create tree with base_tree + changed items; create commit; PATCH ref) = one atomic commit + one Render deploy. Far better than N contents-API pushes. See scratchpad for the script shape.

**UX/design:** 3 competing "brand blues" (real accent #1e5aa8 in only 2 files), 31/34 pages duplicate their own tokens, 320 hex values, body text mostly 12–15px (below the 16–19 standard — sunlight-readability gap), pinch-zoom disabled on several pages, flat-gray-box + emoji-only look. Redesign plan (sequenced): one token file + one brand blue → 16px floor + restore zoom → two-tier card system → hierarchy+icons → reskin clock-bar+FAB → consolidate components. Keep: clockin-bar.js cache-then-refresh pattern, the pill/badge shapes.

**How to apply:** this is the open fix backlog for the app. When DJ greenlights fixes, do them in a controlled pass finding-by-finding (criticals first), and build the redesign on preview routes. Full detail lives in the artifact.
