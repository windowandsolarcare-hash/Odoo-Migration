---
name: project_reactivation_route_shadowed_in_dashboard
description: "The live reactivation app runs from saunders-render-app (NOT Odoo-Migration/5_Mobile_Interface), and /api/reactivation/candidates is shadowed — dashboard.py's copy wins over reactivation.py. Edit dashboard.py."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ce92b3e-6626-4807-9e45-23722f7fcba2
---

## ⚠ ALL `/api/planner/*` routes shadowed in dashboard.py (2026-06-17)
The Daily Planner routes — `/planner`, `/api/planner/template`, `/template/save`, `/history`, **`/checkin`**, `/stats` — are in BOTH `dashboard.py` (~L12153+, registered first → WINS) AND `planner.py` (DEAD). Adding the Planner↔My Day sync hook to planner.py's `/checkin` had ZERO effect (no debug logs at all = the tell that the hooked code never runs). The LIVE one is **dashboard.py `api_planner_checkin` ~L12198**. Fixed there. See [[project_planner_myday_sync]]. Same pattern as below.

## ⚠ ANOTHER shadowed route — `/api/calendar_jobs` (2026-06-17)
`/api/calendar_jobs` is defined in BOTH `dashboard.py` AND `calendar.py`. main.py registers `owner_dashboard` (line 10) BEFORE `owner_calendar` (line 21) → **dashboard.py's copy WINS; calendar.py's is dead.** Editing calendar.py's version (added a start/end date-range param) deployed "live" with ZERO effect; the fix had to go in dashboard.py (~line 7650). **Rule: before editing ANY `/api/*` route in calendar.py (or any router after dashboard), grep dashboard.py for the same path first — if it's there, edit dashboard.py.** General pattern below.

## ✅ SHADOWING RESOLVED 2026-06-14 — reactivation is now its OWN app (no more duplication)
DJ: "reactivation — break that out so an agent can work on it… set it up the same way as other apps." Done. The 9 duplicated `/api/reactivation/*` + `/api/followup/*` routes (candidates, open_by_partner, so_list, preview, mark_inactive, launch, followup/preview, followup/launch, followup/markdone) + the `/reactivation` page route were REMOVED from dashboard.py; `reactivation.py` now owns them all (absorbed the live dashboard versions verbatim + its unique sent/suggest/book/decline/mark_active = 14 API routes + page route). dashboard.py −896 lines. Commits: reactivation 9e9190f/3b95ef1, dashboard 1ce3644/27ab4ef. Verified live (open_by_partner freq=4 Months, Hemet candidates=35, page 200). **So: edit `reactivation.py` now, NOT dashboard.py.** The rest of this note is the historical 2026-06-11 trap (kept for context).

---
Two traps cost a multi-hour investigation on 2026-06-11 while adding `address` to reactivation candidate cards.

**1. The live Render app is `saunders-render-app`, NOT `Odoo-Migration/5_Mobile_Interface`.**
- Service `wsc-field-assistant` (srv-d78le0fkijhs738dsli0) deploys from repo `windowandsolarcare-hash/saunders-render-app`, branch main, entry `main:app`, rootDir "". Confirmed via Render `get_service`.
- The `Odoo-Migration/5_Mobile_Interface/app.py` monolith (and its `render.yaml` claiming `app:app`) is a **stale/dead parallel copy** — editing/pushing it changes NOTHING live. Don't touch it for Render-app work.
- Owner routes are mounted with `prefix="/owner"` in main.py, so the real URL is `https://wsc-field-assistant.onrender.com/owner/api/reactivation/candidates` (no `/owner` = 404, which a lazy `d.get('candidates',[])` parser silently reads as "0 candidates").

**2. `/api/reactivation/candidates` is DUPLICATED and the dashboard.py copy SHADOWS reactivation.py.**
- Both `routers/owner/dashboard.py` (route at ~line 11624) AND `routers/owner/reactivation.py` define `@router.get('/api/reactivation/candidates')`.
- main.py includes `owner_dashboard` (line 100) BEFORE `owner_reactivation` (line 104). FastAPI uses the FIRST registered match → **dashboard.py's copy serves; reactivation.py's copy is dead.** Same is likely true for other `/api/reactivation/*` routes (open_by_partner, so_list, preview, launch, mark_inactive) and the `/reactivation` page (dashboard.py line ~6913 reads static/owner/reactivation.html).
- Editing reactivation.py looked correct, deployed "live", and had ZERO effect — that's the shadow. **To change reactivation candidate behavior, edit dashboard.py.**
- GitHub code search (`gh api search/code`) MISSED dashboard.py here — it only returned reactivation.py. Don't trust code search to find all route defs; `grep` the actual fetched files (dashboard.py, field.py, activities.py, hemet.py — the routers registered before reactivation).

**Diagnostic that broke the paradox:** add a temp unique marker route to the suspect file, deploy, curl it. If it 404s, you're editing the wrong/shadowed file. The candidate-dict marker-key test also works.

**Render deploy mechanics that wasted time here:**
- Pushing to GitHub fires an autodeploy (`trigger:new_commit`). If you ALSO trigger a manual API deploy of the same commit, the autodeploy **cancels** your manual one (status `canceled`) — don't bother manually deploying right after a push; just watch the autodeploy.
- A manual `POST /v1/services/{id}/deploys` with `{"commitId":"<sha>"}` fails `"not found: service does not have a commit <sha>"` until Render's git mirror has synced that commit. A plain manual deploy (no commitId) redeploys Render's LAST-KNOWN HEAD, which can be stale — so it can rebuild an OLD commit. Safest: push, then watch the autodeploy by SHA.
- Right at the `update_in_progress → live` switchover, the OLD container still serves for a few seconds — a curl fired the instant status flips to `live` can return stale output (saw a removed route still 200 for ~10s, then 404). Re-curl after a beat before concluding the deploy didn't take.

**The address feature (shipped):** dashboard.py candidates builder now fetches property `street`+`city`, builds `prop_addr` = "street, city", emits `'address': _addr` (best property, fallback first property, fallback contact city). Frontend `static/owner/reactivation.html`: list card line ~809 and open-customer `prev-city` line ~827 both render `c.address || c.city`. See [[project_render_app_architecture]] [[project_reactivation_sent_book]].
