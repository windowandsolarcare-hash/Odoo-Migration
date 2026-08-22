---
name: Workiz type_of_service_2 field name
description: The Workiz API custom field for service type is type_of_service_2, NOT type_of_service — using the wrong name causes Phase 5 to create activities instead of new jobs
type: project
---

The Workiz API returns and accepts the service type custom field as `type_of_service_2`, not `type_of_service`.

**Why:** This caused Phase 5 to read the field as None, fall through to the "on demand" branch, and create an Odoo activity instead of a new Workiz maintenance job. Also caused new maintenance job creation to fail with "Could not find matching value for type_of_service - Maintenance". Fixed 2026-04-01.

**How to apply:** Always read with `workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')` and write with key `type_of_service_2`. Affects Phase 4 (3 read locations) and Phase 5 (read + write). The Odoo contact field that stores this value is `x_studio_x_type_of_service`.
