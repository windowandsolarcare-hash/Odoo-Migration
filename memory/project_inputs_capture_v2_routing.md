---
name: project_inputs_capture_v2_routing
description: Inputs/quick-capture (/owner/api/capture in myday.py) now routes override chips to v2 pages carrying the typed text; v2 Vault/Customers accept prefill params.
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-24T13:48:10.096Z
---

**2026-07-24 (DJ: override to Notes dropped his text + old vault showed 'Hub' not Back).** The Inputs quick-capture flow (`POST /owner/api/capture` in `routers/owner/myday.py`, ~L420) was pointing every destination + alt chip at the OLD v1 pages (`/owner/vault`, `/owner/myday`, `/owner/field`, `/owner/planner`) — and the document/vault link carried NO text. Repointed ALL to v2 pages, each carrying the extracted text (commit 28628e6):

| capture type | v2 destination | text param |
|---|---|---|
| task | `/static/owner/v2_myday.html?add=1&title=<t>&due=<iso>` | title (v2_myday already had `add/title/due` — L1271 `openAdd`) |
| customer_note | `/static/owner/v2_customers.html?cust_q=<cust>&prefill_note=<note>` | prefill_note (NEW handler) |
| document | `/static/owner/v2_vault.html?compose=<text>` | compose (NEW) — was `/owner/vault` with NO text |
| plan | `/static/owner/v2_planner.html` | none |
| search | `/static/owner/v2_vault.html?q=<query>` | q (NEW handler) |

## Frontend param handlers added
- **v2_vault.html** (commit 25a8a8b): init reads `?compose=<text>` → prefills the always-on home composer `#cap-text` (opens a new note ready to edit+save, DJ's choice) + `autoGrow` + scroll/focus; `?q=<query>` → sets `#q` + `runSearch()`. Cleans the params from the URL after (history.replaceState) so a refresh doesn't re-trigger. Verified live.
- **v2_customers.html** (commit 5bf4556): init reads `?prefill_note=<text>` → `window._prefillNote`; `openNote(pid)` injects it one-shot into `#note-text`. If `cust_pid` also present, auto-opens the note sheet ~900ms after `doSearch`. Strips prefill_note from URL.

## Broader v2 cross-link audit (2026-07-24) — DJ's fear: v2 screens linking to OLD v1 pages
Static-scanned all 38 v2_*.html for NAVIGATIONS (location.href / href= / window.open, excluding fetch/API) pointing to old `/owner/*` routes or non-v2 .html. Scanner: `scratchpad/audit_v2_links.py`; report `C:\Users\dj\v2_link_audit.txt`. Found 9 pages / ~20 nav targets off-v2.
**FIXED (repointed to v2, commits 6daade7/ace7f63/8331371/4f6f5bd):** v2_schedule (Overdue/To-schedule→v2_maintenance, ＋FAB→v2_new_order), v2_new_order (reactivation book_lead/book_reengage→v2_reactivation which already reads them, booking_requests→v2_booking), v2_inputs (static fallback chips fb-task/doc/plan/find→v2_myday?add=1/v2_vault/v2_planner), v2_maintenance (🧠 Customer Brain was →/owner/field, now →v2_customers.html?cust_q=&cust_pid=).
**FIXED (2026-07-24, commits 20e6832/2b46039) — turned out the v2 targets ALREADY parse the deep-link params, so it was just a repoint, no handler to build:**
- v2_voicemails "Open task" → now `/static/owner/v2_myday.html?open=<id>`. v2_myday's init already does `ITEMS.filter(x=>x.id===open)[0]` → `openEditor(it)` (~L1273).
- v2_customers review → now `/static/owner/v2_outreach.html?review=<pid>` (L905). v2_outreach already has `// deep link: ?review=<pid>&name=&task=` → `openReview(...)` (~L421). ★ Lesson: before concluding "need to add a handler," grep the target page's init for the exact param — my first pass missed both because I searched the wrong pattern.
**JUDGMENT CALLS (may be intentional old pages — ask DJ):** v2_hiring "Full cockpit"→/owner/hiring (richer old page?); v2_new_job "View full schedule"→/owner/calendar (new tab); v2_activities dynamic back `/owner/'+FROM` (likely superseded by the standardized Back button).

## Why / how to apply
DJ wants an override tap to land PREFILLED, never retype. The v2 pages (not the old /owner/* ones) also give the standardized "‹ Back" button (via [[project_v2_launcher_duplicated_stale]] v2_apps.js). If adding a new capture type, point it at the v2 page and pass the text as a param the page reads on init. Note: the OLD `/owner/vault` (vault.html, served by routers/owner/vault.py) still exists with its 'Hub' button — the Inputs flow no longer links to it, but other old-page links might.
