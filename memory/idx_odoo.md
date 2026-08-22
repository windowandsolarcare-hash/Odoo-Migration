# Odoo quirks & fields — memory index

- [project_money_decision_allowlist.md](project_money_decision_allowlist.md) — Any "does customer owe?" / Pay-now / auto-charge decision MUST allowlist owed states (`payment_state IN ('not_paid','partial') AND residual>0`), never denylist — a denylist fails OPEN and billed already-paid Blair. Same shape as the company_id fail-open.

- [project_shared_address_dedupe.md](project_shared_address_dedupe.md) — shared/addresses.py = the ONE place "same address" is decided (Workiz dup properties). DISPLAY-only, never merge Odoo records. Validated on all 1,539 records: zero false merges.

- [project_company_guard_enforce_at_resolver.md](project_company_guard_enforce_at_resolver.md) — Enforce company_id in [1,False] at the RESOLVER, not per-caller: a bare partner_id path rendered a Saunders customer a full W&SC portal. company_id FAILS OPEN (W&SC is mostly False).

- [project_res_partner_no_mobile_field.md](project_res_partner_no_mobile_field.md) — res.partner has NO `mobile` field in Odoo 19; one bad name in a `fields` list fails the WHOLE read, so a real record looks 'not found'. Use `phone`.

- [project_x_odoo_contact_id_is_integer.md](project_x_odoo_contact_id_is_integer.md) — crm.lead x_odoo_contact_id is an INTEGER field (bare partner id), NOT a many2one — never subscript it `[0]`. Fixed reactivation/book 'int not subscriptable' crash 2026-08-13.

- [project_confirmed_so_line_edit.md](project_confirmed_so_line_edit.md) — Editing order_line on a CONFIRMED SO: Odoo FORBIDS removing lines (no (5,0,0)/(2,)/(3,)) → update in place + zero leftovers; AND writing qty without price_unit recomputes price → always send price_unit. Fixed /api/job/lines 2026-08-05.

- [project_quote_line_note_and_quotes_shadow.md](project_quote_line_note_and_quotes_shadow.md) — Quote SO = clean product-name priced line + a display_type='line_note' line holding the [Render Quote Tool]+__QUOTE_JSON__ blob (detection/round-trip). quotes.py is DEAD — shadowed by dashboard.py (included first); edit quote logic in dashboard.py ONLY.

- [project_odoo19_no_mobile_field.md](project_odoo19_no_mobile_field.md) — res.partner has NO `mobile` field in Odoo 19 (merged into `phone`). Reading it raises "Invalid field 'mobile'" and fails the WHOLE read() call, not just that field.

- [project_frequency_service_architecture.md](project_frequency_service_architecture.md) — Frequency+Type-of-Service live on SO / property / contact. WORKIZ=master; property+SO mirror down (Phase 4). Property=reliable value; SA955 rolls SO→property. Display now falls back SO→property (so_full 4069bbb) so header never shows false "Unknown". res.partner has NO 'mobile' field.

- [project_accounting_master_plan.md](project_accounting_master_plan.md) — READ FIRST for any accounting work. Strategy (QB accurate thru 2024 → Odoo forward, opening balance bridges to reality).
- [project_awp_vendor_setup.md](project_awp_vendor_setup.md) — Active Window Products in Odoo: vendor 26936, Customer ID 55145, Resale tax-exempt fiscal position, 33 frame products imported, AWP Order…
- [project_awp_vendor_setup.md](project_awp_vendor_setup.md) — Active Window Products in Odoo: vendor 26936, Customer ID 55145, Resale tax-exempt, 33 frame products imported, order emails go to BOTH Jaime +…
- [project_categorize_bank_line_mechanic.md](project_categorize_bank_line_mechanic.md) — How-to mechanics: categorize bank line (re-point suspense line), retire dup (reverse w/ ORIGINAL date — date-bug!), re-point payment (doesn't…
- [project_hiring_video_interview.md](project_hiring_video_interview.md) — Hiring VIDEO interview cockpit (2026-06-17): live during call.
- [project_odoo_accounting_migration.md](project_odoo_accounting_migration.md) — FULL accounting migration plan: revenue from Odoo SOs + Workiz payment CSVs, expenses from QB CSV, opening balances from real accounts.
- [project_odoo_action_confirm_resets_date_order.md](project_odoo_action_confirm_resets_date_order.md) — Odoo action_confirm() resets date_order to now() — must write correct date back after confirming
- [project_so_numbering_post_workiz.md](project_so_numbering_post_workiz.md) — ★ DECIDED post-Workiz SO name = YY(service-year)+climbing 6-digit count (264935), set at create, sorts by year then counter. Old = Workiz SerialId zfill(6). ~38 stranded S00xxx maint jobs to clean up.
- [project_odoo_name_typos.md](project_odoo_name_typos.md) — Real example: "Jon Hamm" stored as "John Ham" in Odoo. Search must fuzzy-handle.
- [project_odoo_no_fuzzy_operator.md](project_odoo_no_fuzzy_operator.md) — Odoo has no fuzzy/similar operator. Just like/ilike substring.
- [project_odoo_so_name_format.md](project_odoo_so_name_format.md) — Odoo SO names are 6-digit zero-padded numbers, NO S prefix.
- [project_odoo_upsell_activity.md](project_odoo_upsell_activity.md) — Odoo native "Upsell" To-Do auto-created when timer hours > ordered qty.
- [project_owntracks_home_detection.md](project_owntracks_home_detection.md) — Ping-based home clock-out (reliable vs flaky geofence events).
- [project_personal_time_direct_odoo.md](project_personal_time_direct_odoo.md) — Create "Personal Time" calendar blocks directly in Odoo (skip Workiz): partner 24177, job_type "Personal Time", date_order=UTC start, write…
- [project_pricing_quote_strategy.md](project_pricing_quote_strategy.md) — Quote tool = quote.html (/owner/quote), per-pane model LINE_ITEMS (~L456): Reg/Over/2nd-Story panes $7/8/9, Reg/Over/Triple sliders $25/30/35 ×…
- [project_quote_tool.md](project_quote_tool.md) — READ FIRST when editing /owner/quote, /tech/quote, or /api/quote/*.
- [project_so_lines_zero_means_deleted.md](project_so_lines_zero_means_deleted.md) — Odoo blocks hard-delete of sale.order.line on confirmed SOs.
- [project_so_unlink_needs_cancel.md](project_so_unlink_needs_cancel.md) — 2026-04-27: Odoo blocks unlink on confirmed sale.order — must action_cancel first.
- [project_todo_models_in_odoo.md](project_todo_models_in_odoo.md) — READ FIRST when editing /api/todos or any to-do code. Two models act like to-dos: mail.activity (chatter reminders) + project.task with…
- [user_accounting_knowledge.md](user_accounting_knowledge.md) — DJ is comfortable with P&L, less so with balance sheet, not an accountant.
- [project_payment_journals_reality.md](project_payment_journals_reality.md) — all payments book into Chase journal 6; method bucket = MEMO text (_detect_payment_method), method journals are empty.
- [project_paid_without_payment_record.md](project_paid_without_payment_record.md) — migration-era invoices are paid with NO account.payment record; paid checks must trust invoice payment_state.
- [project_respartner_no_mobile_field.md](project_respartner_no_mobile_field.md) — res.partner has NO `mobile` field (only `phone`); reading mobile crashes. Phone lives on PERSON not PROPERTY → job/property screens need parent_id.phone fallback.
- [project_property_dedup.md](project_property_dedup.md) — Duplicate PROPERTY cleanup: use Odoo NATIVE base.partner.merge (moves posted invoices; manual write cant; cap 3/merge; deletes dupes). ~58 excess. Barry test DONE.
- [SO partner_id is the PROPERTY](project_so_partner_id_is_property.md) — ★ a job/SO partner_id is the property child (record_category=Property), NOT the person; person = parent_id. activeJob.partner_id is the property. intake endpoint now walks property→person.
