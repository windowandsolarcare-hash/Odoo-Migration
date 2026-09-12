---
name: project_endpoint_map_generator
description: "The ENDPOINT_MAP.md AST generator is now COMMITTED at saunders-render-app 3_Documentation/gen_endpoint_map.py — regen is one command; Audit is the cadence-backstop, shipping session regenerates on push."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-09-12T19:50:36.893Z
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

**★ SHARED GENERATOR (2026-09-12) — the logic now lives in ONE importable module.** `endpoint_map_gen.py` at the **repo ROOT** exposes `build_map(root, old_map_text='') -> (markdown, stats)` — a pure function (no file I/O / no argv). `3_Documentation/gen_endpoint_map.py` is now a **thin CLI wrapper** that imports it (adds root to sys.path, reads OLD_MAP from disk, writes the file). This kills CLI-vs-server drift: the CLI and the durable server job call the SAME code. (Refactor was proven byte-identical to the old monolithic script before shipping.)

**Process ownership (Lead's call; upgraded 2026-09-12 to a DURABLE server job per DJ's durable-watcher-first principle):** TWO layers.
- **Primary = the SHIPPING session regenerates on every push** — a CLAUDE.md pre-push gate (gate 3). Regen > hand-patch.
- **★ Second-line net = a DURABLE Render server job (replaced Audit's session-cron 2026-09-12).** `main.py` `_scheduled_endpoint_map` (APScheduler, hourly at **minute :47**) sweeps the **ACTUALLY-DEPLOYED** code in-process (this service's own main.py + routers/**, more accurate than a clone) via `build_map`, and **CAS-pushes ONLY when the route set changed**: GET the live map (content for auth-merge + compare, blob sha for CAS) → build → compare with the `**Auto-generated <date>**` line ignored → PUT with the sha (409 = a shipping session won, yields). Zero Claude tokens, **survives session death, never expires** — the fix for the old Audit session-cron which died on exit + expired in 7 days. Uses env `GITHUB_TOKEN`/`GITHUB_REPO` (same push creds as the app's github_push_file). Logs `[endpoint-map] no change (...)` / `PUSHED` / `409 conflict` to Render stdout. **Verified live 2026-09-12 19:47:02Z** (fired on schedule, swept 847 routes, correctly no-change/no-push). Audit's old `audit_endpoint_map_backstop.sh` STEP-0c is being retired (told Audit to drop it; the doc-path is build-filter-ignored so the push never triggers a redeploy loop).

**As-of 2026-09-12 regen:** 852 route registrations / 72 files / 755 live / 97 dead / 96 colliding paths (was 787/64/690 on 2026-09-04 — +65 routes: full Thumbtack flow, Cheryl assistant `routers/cheryl/assistant.py`, printing + myday/todos churn).

**As-of 2026-09-04 regen:** 787 route registrations / 64 files / 690 live / 97 dead / 96 colliding paths. Known live doubled-prefix typo (payments.py decorates `/owner/api/...` → mounts at `/owner/owner/api/...`; dashboard's correct twin is LIVE) — documented in the map, left as-is (those payments.py routes are shadowed/dead anyway). Related: Operator's `project_endpoint_map` (the map is a snapshot — verify very-recent routes against live). See [[feedback_windows_python_path_and_append_guard]] for the push-guard pattern used.
