---
name: project_v1v2_retirement_plan
description: "Plan to retire legacy V1 owner pages that have a V2 twin, via archive+redirect (reversible). Audit done 2026-07-30. BLOCKED on DJ's 4 decisions + the 'every V2 is Preview' parity question. Method + must-keeps + full map below."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
  modified: 2026-07-31T06:20:50.423Z
---

# V1 → V2 page retirement plan (audit 2026-07-30, NOT yet executed)

DJ asked to clean up the V1/V2 duplication (after an Edit-prices link landed on the wrong quote
twin — see [[project_two_quote_pages_two_launchers]]). CLAUDE.md now has the standing "V2 files
only" rule. This memory holds the retirement plan; **nothing has been changed yet** — waiting on DJ.

**Map artifact (DJ reviews on phone):** https://claude.ai/code/artifact/d304e227-ea9e-4c0f-8e6e-ae0f45e1bd17

**Key architecture finding:** V2 pages are served by the static mount (`/static/owner/v2_*.html`),
NO python route. So "retire a V1 page" = redirect its `/owner/<route>` GET → `/static/owner/v2_<name>.html`
AND **keep that router's API sub-routes** (the V2 page calls them) — never delete a whole router.
Root `/` already redirects to v2_home. **Every v2 page is still `<title>… — Preview`** = not
certified at parity; "safe to redirect" = reference-graph-safe, NOT parity-certified.

**Reversible method (DJ's guardrails):** (1) move each V1 .html to an archive folder (still in
git history too); (2) point old `/owner/<route>` at the V2 page so old links/bookmarks/launcher
don't error; (3) keep API sub-routes + all `/tech/*` routes; (4) one-flip undo per page.

**~30 READY to retire (redirect):** activities, ai, analytics, calendar, hemet, hr, inbox, inputs,
myday, new_job, new_order, outreach, planner, pre_deposit, quick, quote (owner route only — keep
/tech/quote), reactivation, reeng_review (orphan), reengage, shift_review, stale_sos, timeclock
(owner only — keep /tech), vault, voicemails, waiting, weekly_reports, booking_requests,
deleted_jobs, submitted_jobs. (maintenance.html already dead — its route is shadowed.)

**5 MUST KEEP:** `field.html` (core tech app + /tech/field; v2_field is partial preview),
`hiring.html` (v2_hiring links back to it as "Full cockpit"), `quote_rates.html` (no v2 twin;
v2_quote's Edit-prices points here), `library.html` (no twin), `index_classic.html` (/owner/classic
escape hatch).

**✅ DONE 2026-07-30 — V2 declared LIVE, "Preview" labeling removed:** stripped `— Preview` /
`(Preview)` from all v2 `<title>`s and the "Preview build · …" prefix from all `.foot` footers
(kept the useful footer tails), + "This preview is owner-only" → "This page is owner-only" on
v2_timeclock. 39 files in ONE atomic Git-Trees commit (268ff878) = single Render rebuild. Guards:
functional preview UNtouched (Reactivation "Preview & Launch", Vault openPreview/previewable,
`/api/…/preview` endpoints) — verified by token-count asserts + diff-only-touches-preview-lines
assert. Dead `.preview-ribbon` CSS left in place (no rendered element uses it). DJ: "just worry
about V2 being live not preview. deal with others later."

**✅✅ RETIREMENT EXECUTED 2026-07-30 (DJ decisions: command-center=v2_command; v2_schedule=retire→v2_command; price editor stays its own page; home pages retire, NO fallback).**

Two commits:
- **A (8646efa)** — 32 legacy pages retired via **redirect stub**: `static/owner/<name>.html` replaced
  with a tiny page that `location.replace()`es (preserving query+hash) to `/static/owner/v2_<name>.html`,
  meta-refresh fallback + manual link. Originals copied to **`static/owner/_archive_v1/<name>.html`**
  (openable + in git history). Covers: activities, ai, analytics, calendar, hemet, hr, inbox, inputs,
  myday, new_job, new_order, outreach, planner, pre_deposit, quick, reactivation, reeng_review,
  reengage, shift_review, stale_sos, vault, voicemails, waiting, weekly_reports, booking_requests,
  deleted_jobs, submitted_jobs, maintenance, schedule_hub, index, index_classic, v2_schedule.
- **B (820b144)** — dashboard.py: `/owner/quote` + `/owner/timeclock` → `RedirectResponse(307)` to their
  V2 pages (these two files are DUAL-served to techs, so NOT stubbed — the file stays live; only the
  owner route redirects). Added `RedirectResponse` to the top import.

**Techs untouched:** `/tech/quote`, `/tech/timeclock`, `/tech/field` still serve the real V1 files
(verified 200, not stubs). **field.html NOT retired** (core tech app, kept).

**Reverse any page:** restore its file from git history / `_archive_v1/` (stubs), or revert the
`/owner/quote|timeclock` handler (routes). All reversible.

**Still standalone (kept, per DJ):** quote_rates.html (price editor), library.html, and the two V1
home files are archived-and-stubbed (no fallback). ql_panel.js (old launcher) now only loads on the
archived copies; live app uses v2 WSCLauncher.

**Two launchers to unwind too:** old `ql_panel.js` (loaded by all ~33 V1 pages) vs v2 `v2_apps.js`
WSCLauncher (★Favorites/All). Retiring V1 pages removes ql_panel usage.

**How to apply:** when DJ answers the 4 + says "V2 is live, proceed", execute in one reversible
batch (archive + redirect the ~30), test each loads, leave the 5 keeps + all /tech routes + all API
sub-routes untouched.
