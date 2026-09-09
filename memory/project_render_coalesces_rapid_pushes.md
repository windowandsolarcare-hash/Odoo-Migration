---
name: project_render_coalesces_rapid_pushes
description: "Render coalesces a burst of rapid Contents-API pushes and may NEVER deploy the TIP commit — verify the last/critical commit has a LIVE deploy (or trigger_deploy), don't trust healthz 200."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T14:33:22.670Z
---

**Render's autoDeploy coalesces a burst of rapid commits and can skip deploying the TIP.** Discovered 2026-09-09 building the Cheryl Tasks screen: I pushed 6 files in rapid succession via the GitHub Contents API (each a separate commit to main). Render deployed the 1st then jumped to the 5th (`33e29e7c`) as "latest," and **never created a deploy for the 6th/tip commit** (`dbe7c546`, the `main.py` router-include). Result: the live build was the pre-include one — the new router returned **404 with a valid cookie** even though the code was correct on main and **`/healthz` stayed 200 the whole time** (200 = the OLD build was up, not proof the new code is live).

**Why it bites:** when the LAST commit in a burst is the critical one (e.g. the `main.py` `include_router` line, or a `requirements.txt` bump), coalescing means the thing that wires everything up may never go live, while every earlier file IS live → confusing partial-deploy symptoms.

**How to apply:**
- After a multi-file push where the tip commit is load-bearing, **verify the tip commit actually has a LIVE deploy** — `mcp__render__list_deploys` (serviceId `srv-d78le0fkijhs738dsli0`, workspaceId `tea-d78l9fqdbo4c7388n9og`); the newest row's `commit.id` must equal your tip and `status` must be `live`. If the tip has no deploy, **`mcp__render__trigger_deploy`** it.
- **`/healthz` 200 does NOT prove your new code is live** — a failed/never-triggered new deploy leaves the prior build serving 200. Verify by the deploy record or by content, never status alone (cf. [[feedback_odoo_verify_content_not_status]]).
- Prefer to order pushes so the tip is the one you most want deployed, and/or pause between the burst and the final include-commit. Either way, confirm-the-tip.
- A later unrelated commit (another session's SESSION_ROSTER heartbeat) will eventually trigger a deploy that includes your tip — but don't rely on that timing; trigger it yourself.

See [[feedback_regression_guard_pushes]], [[feedback_push_compare_and_swap]].
