# SHARED MEMORY — Window & Solar Care
# Synced between Claude Code (local) and Render Claude (field assistant)
# Last updated: 2026-04-16
# Format: key facts only — both Claudes read this on every session

## OWNER
- DJ Sanders — owner and sole technician, Window & Solar Care, Southern California
- Email: windowandsolarcare@gmail.com

## PLATFORMS
- Odoo: https://window-solar-care.odoo.com (DB: window-solar-care, User ID: 2)
- Workiz: job scheduling — IP-restricted, proxy through Odoo if calling from local machine
- GitHub: windowandsolarcare-hash/Odoo-Migration (main branch only)
- Render: mobile field assistant at https://[render-url] — always-on paid plan
- Zapier: Phases 3-6 automation — fetches code from GitHub main on every trigger

## AUTOMATION PHASES
- Phase 3: New job creation (Workiz webhook → Zapier → Odoo)
- Phase 4: Job status updates (Zapier polling every 5 min)
- Phase 5: Auto job scheduling (triggered by Phase 6)
- Phase 6: Payment sync (Odoo webhook → Zapier)
- Phase 2: Reactivation engine (Odoo Server Action, manual run)
- Phase 2B: STOP compliance (Workiz → Odoo webhook)

## KEY ODOO SERVER ACTION IDs
- LAUNCH (reactivation): 563

## CRITICAL FIELD NAMES
- Workiz UUID on SO: x_studio_x_studio_workiz_uuid
- Workiz custom service field: type_of_service_2 (NOT type_of_service)
- Property partners: x_studio_x_studio_record_category = "Property"
- Contact type of service: x_studio_x_type_of_service
- Gate code (contact): x_studio_x_gate_code
- Gate code (SO snapshot): x_studio_x_gate_snapshot
- Pricing (contact): x_studio_x_pricing
- Workiz client ID on contact: ref field

## KNOWN BUGS / RULES
- After action_confirm() on SO, write date_order back — Odoo resets it to now()
- date_order = Workiz JobDateTime (start time, UTC) — never use end time
- No imports in Odoo server action code
- No 'response' or 'result' variable names in Odoo 19 server actions (reserved)
- HTML in chatter gets escaped — use plain text with | separators, unicode emoji OK
- Workiz filter on SubStatus not Status
- Deleted Workiz job returns HTTP 204 not 404

## WORKIZ API DEFAULTS (required to avoid validation errors)
- type_of_service_2: 'On Request'
- frequency: 'Unknown'
- confirmation_method: 'Cell Phone'
- JobSource: 'Referral'

## RECENT DECISIONS / CONTEXT
- 2026-04-16: Migrated Render app from OpenAI to Claude native (no wrapper), added power tools (odoo_query, odoo_write, github_read_file, github_push_file), added shared memory system
- 2026-04-15: Migrated Render app from ChatGPT to Claude (Anthropic SDK)
- 2026-04-12: Added orphaned task restore, SO smart button, staggered task times, Sunday tag (508 SOs), Calendly Cathedral City, app.py timer tools
- 2026-04-02: Backfilled x_studio_next_job_date on 48 contacts
- Credit card at-door: JobAmountDue=0 + Status!=Done = CC taken. Invoice using "Credit" method → Phase 6 skips Workiz payment POST
