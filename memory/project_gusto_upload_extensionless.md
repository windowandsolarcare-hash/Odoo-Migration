---
name: project_gusto_upload_extensionless
description: "Gusto's exported payroll reports download from S3 with NO file extension → any accept-filter hides them in Android picker. Payroll out-files input uses accept=\"*/*\"."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-10T18:33:37.350Z
---

**Symptom (DJ, 2026-08-10):** On the payroll page (v2_timeclock.html "Payroll Output — PDF + CSV from Gusto" upload), the two documents downloaded from Gusto would NOT appear in the Android file picker — greyed out / invisible.

**Root cause:** Gusto's report exports download from `gusto-zp-reports-production-us-west-2.s3.amazonaws.com` with **no file extension** (names are opaque hashes like `vljoc5h7rvr5jgqln16ctlh9se7d`, generic gray icon). Android's document picker greys out any file that doesn't match the `<input accept=...>` filter, and an extensionless file matches NO extension/MIME-based accept. The old `accept=".pdf,.csv,application/pdf,text/csv"` hid them.

**Fix (commit d7f54ca):** `#out-files` input → `accept="*/*"` (allow all). The `#in-files` input (our own generated `gusto_timesheet_*.csv`, which HAS an extension) left as `.csv,text/csv` — it works fine.

**Server side is already tolerant:** `/api/payroll/upload_docs` (dashboard.py) sets mimetype = `f.content_type or (pdf if name endswith .pdf else text/csv)` and never rejects by extension — so extensionless files save to Odoo Documents fine (Payroll → Output folder). They land under their hash name with the browser-provided content_type, so Odoo can still preview them.

**General rule:** any file that originates as a third-party S3/signed-URL download may arrive extensionless — use `accept="*/*"` on those upload inputs, don't extension-filter.
