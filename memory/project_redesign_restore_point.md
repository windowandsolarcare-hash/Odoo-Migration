---
name: project_redesign_restore_point
description: Pre-redesign safety snapshot (2026-06-21) + the working discipline that keeps the existing app intact while the ERP redesign proceeds
metadata: 
  node_type: memory
  type: project
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

Before the ERP redesign (see [[project_report_hub_redesign]]) goes past Phase 0, DJ asked to guarantee everything built prior stays intact in case the redesign takes a while.

**Restore points created 2026-06-21 (both repos):**
- `saunders-render-app`: tag **`stable-2026-06-21`** + branch **`backup-2026-06-21-pre-redesign`** → commit `56c55a6a11b8da9dd7011c0564b61b1964ab7972`
- `Odoo-Migration`: tag **`stable-2026-06-21`** + branch **`backup-2026-06-21-pre-redesign`** → commit `592cfafc83165ea1a8bb4a13c0e3e074c598935d`

**To restore a single file to the known-good state:** `gh api repos/<repo>/contents/<path>?ref=stable-2026-06-21 --jq '.content' | base64 -d`. To roll the app back wholesale, redeploy from the backup branch / reset main to the tag sha (only with DJ's OK).

**Working discipline for the redesign (keeps the live app safe — Render auto-deploys `main`, no staging):**
1. Redesign work is **additive**: new files (`common.css`, `report_kit.js`, demo/new pages) and new routes only. Phase 0 shipped this way — zero existing screens touched.
2. **Never modify a working screen in place** for the redesign until its replacement is built, proven, and DJ approves the swap (CLAUDE rule 10 + the gh-push line-regression gates still apply).
3. New versions live behind **new URLs/routes** (e.g. `/static/owner/reports_demo.html`, a future `/owner/reports`) so the old screen keeps serving until parity.
4. The redesign is **frontend/Render-app only** — Odoo server actions, Zapier phase scripts, and the sync engine are NOT being changed, so production job/payment/sync logic is unaffected.

Phase 0 status: `common.css` + `report_kit.js` + `reports_demo.html` live at `/static/owner/reports_demo.html` (day/night, cards→pills, unified result, Brain stub). Awaiting DJ's feedback on the look before Phase 1 (schedule as command center).
