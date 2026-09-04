---
name: project_endpoint_map_generator
description: "The ENDPOINT_MAP.md AST generator is now COMMITTED at saunders-render-app 3_Documentation/gen_endpoint_map.py — regen is one command; Audit is the cadence-backstop, shipping session regenerates on push."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-09-04T23:06:39.877Z
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

**Process ownership (Lead's call, 2026-09-04):** the SHIPPING session regenerates as a push-checklist step (regen > hand-patch); **Audit (this role) re-runs on a cadence as the backstop.** NOT a boot/deploy hook.

**As-of 2026-09-04 regen:** 787 route registrations / 64 files / 690 live / 97 dead / 96 colliding paths. Known live doubled-prefix typo (payments.py decorates `/owner/api/...` → mounts at `/owner/owner/api/...`; dashboard's correct twin is LIVE) — documented in the map, left as-is (those payments.py routes are shadowed/dead anyway). Related: Operator's `project_endpoint_map` (the map is a snapshot — verify very-recent routes against live). See [[feedback_windows_python_path_and_append_guard]] for the push-guard pattern used.
