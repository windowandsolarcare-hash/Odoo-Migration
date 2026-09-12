---
name: project_endpoint_map_generator
description: "The ENDPOINT_MAP.md AST generator is now COMMITTED at saunders-render-app 3_Documentation/gen_endpoint_map.py — regen is one command; Audit is the cadence-backstop, shipping session regenerates on push."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-09-12T14:17:44.019Z
---

**ENDPOINT_MAP.md regen is now repeatable (2026-09-04).** The prior generator (`parse_routes.py`/`gen_doc.py`) was NEVER committed, so the Sep-3 map silently drifted (missing routes, a malformed `confirm_card` file:line cell). Fixed: committed a single self-contained AST sweep to **`3_Documentation/gen_endpoint_map.py`** in the `saunders-render-app` repo.

**Regen command** (from a synced app clone — `git reset --hard origin/main` first, never edit the clone):
`python 3_Documentation/gen_endpoint_map.py <repo_root>` → writes `3_Documentation/ENDPOINT_MAP.md` in place (override target with env `ENDPOINT_MAP_OUT`).

**What it does / why it's robust:**
- Reads `main.py` directly for BOTH `@app.<method>` app-level routes AND `include_router(...)` order+prefixes — **no INCLUDE list to hand-maintain** (the old generator needed one).
- Line-orders the whole registration stream so shadow resolution matches FastAPI (first-registered under a prefix wins; e.g. `GET /owner/` LIVE = main.py, dashboard `hub()` = DEAD twin).
- AST-parses every included router's `@router.<method>` decorators; groups by INCLUDE prefix (root app-level / root no-prefix / /book / /owner / /tech / /cheryl / /printing).
- **Auth column is MERGED from the prior map** (regex-parses old rows) so hand/heuristic-tuned auth values persist; only genuinely new routes get best-effort auth (`access_code` param / `{token}` in path / `—`). The auth heuristic's original source was lost — merging is what prevents a noisy diff.
- Emits: shadow/collision table + Pattern paragraph, a Misplaced-decorator/required-query-param check, the grouped full table, totals footer.

**Process ownership (Lead's call, 2026-09-04; upgraded 2026-09-12 to keep the map LIVING per DJ):** TWO layers now.
- **Primary = the SHIPPING session regenerates on every push** — a CLAUDE.md pre-push gate (gate 3, added 2026-09-12 by Lead). Regen > hand-patch.
- **Second-line net = Audit's HOURLY tick auto-regens** (STEP 0c of the Audit watcher cron). Script `C:/Users/dj/audit_endpoint_map_backstop.sh`: git reset --hard origin/main → `gen_endpoint_map.py` → **CAS-push ONLY when the route set actually changed.** Two safeguards: (1) the compare IGNORES the daily `**Auto-generated <date>**` line so date churn never triggers a spurious push — only real route deltas do; (2) a 409 means a shipping session regenerated concurrently → theirs wins, no clobber. So the map is never >~1h stale even if a push-gate is missed. (Still NOT a boot/deploy hook — it's Audit-session-local; dies with the session, re-armed each start.)

**As-of 2026-09-12 regen:** 852 route registrations / 72 files / 755 live / 97 dead / 96 colliding paths (was 787/64/690 on 2026-09-04 — +65 routes: full Thumbtack flow, Cheryl assistant `routers/cheryl/assistant.py`, printing + myday/todos churn).

**As-of 2026-09-04 regen:** 787 route registrations / 64 files / 690 live / 97 dead / 96 colliding paths. Known live doubled-prefix typo (payments.py decorates `/owner/api/...` → mounts at `/owner/owner/api/...`; dashboard's correct twin is LIVE) — documented in the map, left as-is (those payments.py routes are shadowed/dead anyway). Related: Operator's `project_endpoint_map` (the map is a snapshot — verify very-recent routes against live). See [[feedback_windows_python_path_and_append_guard]] for the push-guard pattern used.
