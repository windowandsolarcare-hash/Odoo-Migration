---
name: project_app_repo_push_redeploys
description: "★ Pushing ANY file outside 3_Documentation/** to windowandsolarcare-hash/saunders-render-app redeploys the LIVE money app (wsc-field-assistant restart blip). The fleet's review/ mirror convention has been silently redeploying it — mirror to 3_Documentation/review/ instead."
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-22T21:44:40.440Z
---

**wsc-field-assistant (srv-d78le0fkijhs738dsli0) autoDeploys on EVERY commit to `windowandsolarcare-hash/saunders-render-app` whose changed paths are NOT ALL under the buildFilter `ignoredPaths` — which is ONLY `["3_Documentation/**"]`.** So a push to `review/…`, `routers/…`, a root file, ANYTHING outside `3_Documentation/**` → a full app rebuild + redeploy = a single-instance restart blip (the 502 risk the zero-downtime work targets).

**Why this matters (found 2026-09-22, Builder-2):** the fleet's standing convention "mirror code to `review/momscare/` (and `review/zero_downtime/`) in the APP repo for Cheryl's review" was silently redeploying the money app on EVERY mirror — dozens of restart blips across a session, on a day that already had a payment 502. Confirmed in the deploy log: `review/zero_downtime/worker.py` push → dep-dapebl4s728c73ei7j40 (built+deployed), `requirements.txt` → dep-dapeblhc3rtc73d86q30. The commit message literally said "HELD — not deployed" but the PUSH itself redeployed the whole app (the mirror file is inert; the redeploy is the harm).

**How to apply:**
- **Mirror review copies UNDER `3_Documentation/` (build-ignored)** — e.g. `3_Documentation/review/momscare/…`, `3_Documentation/review/zero_downtime/…`. Cheryl/Lead still read them via `gh api` Contents; they NEVER redeploy. (Alternative: add `review/**` to the service buildFilter ignoredPaths — but that's a Render dashboard/service-config change; the path move is fleet-controllable via gh api.)
- **Any real code push to this repo IS a deploy** → treat it as one: only in a coordinated QUIET window, never while DJ transacts (see [[feedback_no_deploy_during_customer_payment]]). "It's just a doc/mirror" is false unless it's under `3_Documentation/**`.
- Memory/AGENT_MAIL/SHARED_MEMORY mirrors to the `Odoo-Migration` repo are safe (that repo feeds Zapier, no Render deploy). It's specifically `saunders-render-app` pushes that redeploy the money app.
- Verify a repo's deploy-trigger before treating a push as harmless: `get_service` → `serviceDetails.buildFilter.ignoredPaths`. Related: [[project_zero_downtime_worker]] (the fix for the underlying restart-blip class).
