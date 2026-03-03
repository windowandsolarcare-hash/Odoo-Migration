# AGENTS.md: Window & Solar Care - Odoo/Workiz Master Protocol

## 1. MISSION DIRECTIVE
To migrate 6 years of historical data from Workiz to Odoo and establish a bi-directional "Mirror" integration. Build a "Dormant Client Reactivation Engine" in Odoo while maintaining the "One Number Strategy."

## 2. THE 5 CRITICAL COMMANDMENTS
1. **ONE NUMBER STRATEGY**: Customers NEVER receive SMS from Odoo. Odoo triggers -> Zapier transports -> Workiz sends.
2. **PROPERTY IS THE BRAIN**: Service data (Gate Codes, Frequency, Last Service) belongs to the PROPERTY/ADDRESS record (`partner_shipping_id`), NOT the billing contact.
3. **INTEGERS, NOT STRINGS**: All record IDs passed to Odoo via Zapier/API must be INTEGERS. String IDs will fail silently.
4. **ODOO SANDBOX RULES**: Server Actions are sandboxed. `import` statements are FORBIDDEN. Use `record["field"]` syntax, not `record.field`.
5. **THE LEVER PULL**: To send SMS via Workiz, POST to `/job/create/` without status, then immediately POST to `/job/update/` to set the status/sub-status.

## 3. TECHNICAL SPECIFICATIONS
- **Odoo Search Domains**: Must be triple-wrapped: `[[["field", "=", "value"]]]`.
- **Workiz Auth**: Dual methods required. API Key in URL + `auth_secret` as the FIRST key in the JSON body for POST.
- **Related Records**: Create child records (like CRM Logs) by writing to the parent using the `[0, 0, {...}]` magic command.
- **External IDs**: Follow Mirror V31.11: `external_id = workiz_[id]`.

## 4. AGENT WORKFLOW & EXECUTION
- **Role**: Software Architect / Builder.
- **The /plan Command**: Before any execution, use `/plan` to analyze existing documentation in the repository.
- **Visual Verification**: Before generating or changing code, provide a Markdown table (5-10 rows) comparing Source (Odoo) vs. Destination (Workiz) logic for approval.
- **Zero-Edit Scripting**: Generate single, complete Python scripts. 
- **Pathing Rule**: Hardcode exact filenames provided in documentation. Assume all input/output files are located in the same directory as the script.

## 5. GIT WORKFLOW
- When the user approves code changes, push them directly to the `main` branch.
- No pull requests, no feature branches — commit and push directly to `main`.
