---
name: project_ask_route_shadow_dashboard
description: "The LIVE field-voice /owner/ask is in dashboard.py, NOT field.py (field.py's /ask is a DEAD shadow — main.py includes dashboard first). Edit voice-assistant changes in dashboard.py. Plus: anthropic SDK pinned ==0.122.0; namespace late routes to avoid shadowing."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-19T21:41:44.730Z
---

**Route-shadow gotcha, confirmed 2026-08-19 (Specialists burned hours; Lead re-review confirmed).** `routers/owner/dashboard.py` AND `routers/owner/field.py` BOTH define `@router.post('/ask')` with their own TOOLS / SYSTEM_PROMPT / `_agent_loop`. `main.py` includes the dashboard router FIRST under `/owner` (FastAPI first-match-wins), so **dashboard.py serves `/owner/ask` and field.py's `/ask` is DEAD.** A whole voice text-draft tool + agentic-prompt fix + Think-hard deep mode were built in field.py with ZERO effect, then ported to dashboard.py (d4282e4) where they work. **Any field-voice-assistant change → dashboard.py.** (Same shadow pattern as dashboard→hemet in CLAUDE.md's paired-changes table.)

**Voice text-draft tool (LIVE, dashboard.py) — Lead fresh-eyes SAFE 2026-08-19:** `open_text_draft` schema ~L2966, `tool_open_text_draft` ~L3712, registered in `READ_TOOL_MAP` ~L3764 (NOT `WRITE_TOOLS`, so no send path). Hard company guard is IN CODE (refuses company≠1 unless False; re-checks parent's company on the `parent_id` walk) — not prompt-only. Deep-link href via `urllib.parse.quote`, written to `#reply.value` in v2_inbox (no innerHTML) → XSS-safe, draft-only.

**Two durable rules from this:**
1. **`anthropic` SDK stays pinned `==0.122.0`** in requirements.txt. 0.123/0.124 stamp `tool_use.toolset_name`, which the Anthropic API 400-rejects → breaks EVERY session's Claude calls. Leave it pinned.
2. **Namespace late-registered routes.** Shadow collisions only happen on GENERIC paths (`/ask`, `/api/job`, `/api/customers`). Feature-namespaced prefixes (`/portal/...`, `/p/...`, `/owner/api/portal/link`) can't collide by construction — portal.py (registered late at main.py:292) is collision-proof for this reason. When adding a route to a late router, prefix it with the feature name, and before editing OR reviewing any endpoint, grep the path across the repo to confirm which file actually SERVES it.

**Also (pending, flagged to Specialists):** dashboard.py's `/ask` is still the pre-Workiz-retirement version — live Workiz tools still registered (`update_workiz_field`/`create_workiz_job`/`duplicate_workiz_job`/`push_quote_to_workiz`/`delete_workiz_job`/`get_jobs_list`) under a "WORKIZ RETIRED" prompt override. Strip these at full cutover — but the Workiz cleanup must NOT strip the still-live `workiz_status` FIELD. See [[project_workiz_retirement]], [[project_company_filter_fails_open]], [[project_odoo_200_not_success]].
