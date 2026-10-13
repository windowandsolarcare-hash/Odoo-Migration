---
name: project_render_static_deploy_propagation_window
description: "After a gh-api deploy of a static owner asset, Render's zero-downtime swap serves OLD bytes for ~60-90s (healthz stays 200 on the old instance) — don't conclude 'my change didn't ship' from one read; poll the served file until the token/last-modified flips."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-13T20:23:45.683Z
---

Observed firsthand 2026-10-13 (next-job schedule-load deploy, branch specialists/nextjob-schedule-load), independently by BOTH Lead and Audit — a recurrence signal, so it's documented.

**Fact:** a `gh api` Contents-PUT deploy of a static owner asset (`static/owner/v2_*.html`, `*.js`) triggers a Render **zero-downtime swap**: the OLD instance keeps serving until the NEW build passes its health check. For roughly **60–90s** after the push (observed ~80s), a live `curl` of the served file returns the **OLD bytes** even though `/healthz` is 200 (`ok/ready`, `warm` may be true=old instance) and the Render dashboard shows the deploy "live." During the window a loaded page can have NEW already-fetched JS while the HTML is still OLD (or vice versa).

**No lasting stale-cache trap:** owner static serves with `Cache-Control: no-cache, must-revalidate` (verified in the response headers) — once the new instance swaps in, the next load gets fresh bytes; there's no CDN/browser persistence beyond the swap. `last-modified` bumps when the new bytes land.

**How to apply (post-live verify of a static deploy):** do NOT conclude "the deploy failed / didn't include my change" from a single read ~1 min post-deploy — that's the swap window, not a defect. Confirm the path is real first (a stable marker present in both old+new + HTTP 200 + no-cache headers), then **poll the served file** for a functional token (or watch `last-modified`) until it flips, THEN call the verify. A background poll loop (~20s interval, ~4 min cap, exit when the token appears) closes it without sleep-polling. `healthz` 200 during the window reflects the still-serving OLD instance, so healthz-green alone is NOT propagation proof. Ties [[feedback_verify_collection_and_live_pipe]] (green deploy ≠ serving the new bytes — verify the live-served file) and [[feedback_odoo_verify_content_not_status]] (verify by content, not status).
