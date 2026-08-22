---
name: duplicate_workiz_job tool fix — copies ServiceArea and sets last_date_cleaned
description: 2026-04-26 fix to Render Field Assistant's duplicate_workiz_job tool — was missing ServiceArea copy and last_date_cleaned set
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
The `duplicate_workiz_job` tool in `saunders-render-app/routers/owner/dashboard.py` (around line 1040) was missing two fields when constructing the Workiz job-create payload:

1. `ServiceArea` — never copied from the source job
2. `last_date_cleaned` — never set on the new job

Fixed 2026-04-26 (commit a6ae157):
- Copy `ServiceArea` from source: `payload['ServiceArea'] = str(job.get('ServiceArea') or job.get('service_area'))`
- Set `last_date_cleaned` on new job to source job's `JobDateTime[:10]` — when the source job ran, that was the customer's most recent cleaning, so the duplicate inherits that as the "last cleaned" date

The tool's description says "Copies all fields" — but the implementation didn't actually copy all fields. Render Claude trusted the description and produced jobs missing ServiceArea and last_date_cleaned.

**Why:** Tool descriptions are agent-facing contracts. If a tool says "copies all fields," its implementation MUST do that — agents can't be expected to re-verify every payload field, and adding "remember to also pass ServiceArea" instructions to the system prompt is a fragile workaround. Fix the tool, not the prompt.

**How to apply:** When auditing other "copy from source" tools (`create_workiz_job`, future variants), check that the payload actually copies every field promised by the description. The two known business-critical fields that often get forgotten: `ServiceArea` and `last_date_cleaned`. Workiz API uses `ServiceArea` (PascalCase, system field) and `last_date_cleaned` (snake_case, custom field) — different casing conventions.
