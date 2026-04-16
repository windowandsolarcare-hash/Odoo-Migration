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
- action_timer_stop on project.task stops the timer AND commits the timesheet entry automatically. The wizard it returns is browser-only UI — do NOT call it via API. Calling the wizard with time_spent=0 overwrites the logged time with 0 hours and Odoo deletes the 0-hour entry. Just call action_timer_stop and done.

## WORKIZ API DEFAULTS (required to avoid validation errors)
- type_of_service_2: 'On Request'
- frequency: 'Unknown'
- confirmation_method: 'Cell Phone'
- JobSource: 'Referral'

## ODOO INVOICE + PAYMENT API PATTERN (reuse for QB migration)
# Creates invoice from SO, confirms it, registers payment, reconciles — Phase 6 fires automatically
# Journal: Bank (ID=6) | Check method line: ID=8 "Check (Bank)" | Memo = check number
# Payment method line IDs on Bank journal:
#   1=Manual Payment, 2=Batch Deposit, 3=Manual Payment, 4=Checks, 5=NACHA
#   6=Cash, 7=Credit, 8=Check (Bank)
#
# Step 1: Check for existing draft invoice, else create:
#   odoo_call('sale.order', 'action_create_invoices', [[so_id]])
#   so_data = odoo_call('sale.order', 'read', [[so_id]], {'fields': ['invoice_ids']})
#   draft_inv = odoo_call('account.move', 'search_read',
#       [[['id','in', so_data[0]['invoice_ids']], ['state','=','draft'], ['move_type','=','out_invoice']]],
#       {'fields': ['id','name','amount_total'], 'limit': 1})
#
# Step 2: Confirm invoice:
#   odoo_call('account.move', 'action_post', [[invoice_id]])
#
# Step 3: Register payment via wizard (handles reconciliation):
#   ctx = {'active_model':'account.move','active_ids':[invoice_id],'active_id':invoice_id}
#   wizard_id = odoo_call('account.payment.register', 'create',
#       [{'payment_date': today, 'amount': amount, 'communication': check_number,
#         'journal_id': 6, 'payment_method_line_id': 8}], {'context': ctx})
#   odoo_call('account.payment.register', 'action_create_payments', [[wizard_id]], {'context': ctx})
#
# For QB migration: same pattern but loop over historical payments, match SO by name/origin
# payment_method_line_id values: 8=Check, 6=Cash, 7=Credit, 1=Manual(bank transfer)

## RECENT DECISIONS / CONTEXT
- 2026-04-16: Migrated Render app from OpenAI to Claude native (no wrapper), added power tools (odoo_query, odoo_write, github_read_file, github_push_file), added shared memory system
- 2026-04-15: Migrated Render app from ChatGPT to Claude (Anthropic SDK)
- 2026-04-12: Added orphaned task restore, SO smart button, staggered task times, Sunday tag (508 SOs), Calendly Cathedral City, app.py timer tools
- 2026-04-02: Backfilled x_studio_next_job_date on 48 contacts
- Credit card at-door: JobAmountDue=0 + Status!=Done = CC taken. Invoice using "Credit" method → Phase 6 skips Workiz payment POST
