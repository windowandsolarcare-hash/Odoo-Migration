---
name: Apr 29-30 evening session — PO infrastructure + Render Claude write tools + quote workflow finalized + project.task fix
description: Big session. Built end-to-end vendor PO flow (Active Window Products imported with 33 frame products, draft PO P00002, custom fiscal position + email template + aliases). Added 4 Render Claude write tools (create_purchase_order, send_purchase_order, convert_quote_to_job, push_quote_to_workiz). Locked the quote workflow architecture (don't touch Phase 3/4; watermarks distinguish quotes; manual Workiz handoff at acceptance). Fixed two bugs: /api/todos missed project.task records (50+ Phase 5 follow-ups invisible) + 30-row limit hid far-future tasks (Bud Piraino 2027-04-25).
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---

## Big strokes

### Vendor PO infrastructure — Active Window Products end-to-end

Built fresh tonight. Active Window Products is now a fully configured vendor in Odoo:

- Vendor `res.partner` 26936, `ref='55145'` (AWP Customer ID), `supplier_rank=1`
- Address: 5431 San Fernando Road West, Los Angeles, CA 90039
- **Tax-exempt** via custom `account.fiscal.position` "Resale - Tax Exempt" (id 5) — auto-applied to all POs from AWP
- Email field is comma-separated → `j.gutierrez@activewindowproducts.com, v.campos@activewindowproducts.com` so Odoo's "Send by Email" auto-sends to both
- Two child contacts: Jaime Gutierrez (id 26937, Sales/Order) + Valerie Campos (id 26938, Customer Service Manager)
- 33 frame products imported (5/16 Screen + Lip + 1×5/16 + 3/8 Slider variants × all colors) with `product.supplierinfo` linking back to AWP — naming pattern `AWP-{sku}` (e.g. AWP-1017AL = 5/16 Almond Screen Frame)
- Foot UOM (id 20) used as `uom_id` on frame products
- Two custom fields on `res.partner`:
  - `x_default_po_template_id` — points to the vendor's preferred PO email template (AWP → template 49 "AWP Order Request")
  - `x_aliases` — comma-separated short names DJ uses (`Active, AWP, Active Window, Active Window Products`)
- Custom mail.template id 49 "AWP Order Request" with DJ's preferred Part No / Qty / Est. Price layout, customer ID 55145, Tax Exempt note, Window & Solar Care signature
- Both PDFs (Sec 1 components + Sec 11 doors) attached to vendor record as Odoo `ir.attachment` (also surface in Odoo Documents app since that module is installed)

PO sequence renumbered: next PO = **P00101** (was P00003).

Sample PO `P00002` exists (100 ft of 1017AL @ $1.017/ft = $101.70, draft, tax cleared).

See `project_awp_vendor_setup.md` for the full reference + memory rules.

### Render Claude write tools — 4 new ones

Wired into `Saunders Render App/routers/owner/dashboard.py`. All preview-first via the existing WRITE_TOOLS confirmation pattern.

| Tool | Voice triggers | What it does |
|---|---|---|
| `create_purchase_order` | "PO with Active for 100 ft 5/16 almond" / "order from AWP" | Resolves vendor by name+aliases, resolves products by SKU OR natural language ("5/16 almond" — restricted to vendor's catalog), creates draft PO. Returns CLARIFY message when ambiguous (e.g. "5/16 almond" matches Screen + Lip — DJ specifies). |
| `send_purchase_order` | "send PO P00101" | Reads vendor's `x_default_po_template_id` (or default), sends email via that template. AWP gets the custom format with Jaime+Valerie on TO. |
| `convert_quote_to_job` | "convert quote S00107" / "wrap up the Flegel quote" | Clears QUOTE ONLY watermarks (client_order_ref + tag), sets job_type from quote-line product (141→In&Out variant, 103→Outside Windows and Screens). Drops SO off the Saved Quotes list. |
| `push_quote_to_workiz` | "customer approved", "they accepted", "Bud's a go", "go ahead with Flegel's quote", "push the X quote to Workiz" | Reads quote SO + lines, prepends a [Render] block to Workiz JobNotes with priced line items, suggested JobType swap, scheduling reminder, status-change reminder. Only works when SO has a Workiz UUID. |

All four are in `WRITE_TOOLS` set so they get the confirmation flow. Each has a `describe_write_tool` preview block.

### Quote workflow architecture — locked

After deep discussion, settled on this design:

1. **Workiz job creation** with JobType=Quote, status=Submitted → Phase 3 creates draft SO in Odoo (current behavior — keep)
2. **DJ schedules the quote visit in Workiz** (status → trigger value with date) → Phase 4 fires, confirms SO normally, creates a regular `project.task` on schedule
3. **Quote visit task looks/behaves like every other job task** — same code path. Distinguishing signal is the watermarks (job_type=Quote + client_order_ref="🔶 QUOTE ONLY" + QUOTE ONLY tag), NOT the SO state
4. **At customer site, DJ uses Render Quote Tool** → "Pick from scheduled jobs" finds the SO (now visible because /api/upcoming includes draft+sale states) → enters line items → save (zeroes existing, adds quote line)
5. **Customer accepts** → DJ taps "📲 Approve & Push to Workiz" on success card OR voice-says "customer approved" → `push_quote_to_workiz` fires → Workiz JobNotes gets [Render] block with line items + 4-step checklist (add line items, change JobType, set date, change status)
6. **DJ does the manual Workiz updates** following the checklist
7. **Phase 4 fires on status change** → syncs new line items + date_order, confirms SO if not yet confirmed
8. **(Optional) DJ runs `convert_quote_to_job`** to clear watermarks → SO drops off Saved Quotes list

**Why this architecture (not gap A/B):** DJ was concerned about modifying Phase 4 — load-bearing pipeline, risk to normal jobs. By using the watermarks instead of SO state to distinguish quotes, we avoid touching Phase 3/4 entirely. Tasks for quote visits use the SAME code path as all other jobs (same look, same allocated times, same titles).

**One Workiz config DJ owes himself:** disable customer auto-text when JobType=Quote so the customer doesn't get "we'll arrive to clean your windows..." on a quote visit. JobType filter in the Workiz automation rule.

### Critical bug fix — /api/todos missed project.task records

DJ reported: 3 follow-ups for Mark & Sarah Fredricksen show in Odoo /odoo/to-do but not in Render Activities. Root cause:

- Render's `/api/todos` was only reading `mail.activity`
- Render's `create_todo` tool writes to `project.task` (because Odoo's "To-do" app uses that model with `project_id=False`)
- Phase 5's "On Demand" path also writes to `project.task` (despite an outdated docstring claiming `mail.activity`)
- So 50+ project.task to-dos were invisible in Render

Fix (commit 668d619f):
- `/api/todos` now reads BOTH models, returns merged list with a `source` field (`'activity'` or `'task'`)
- `/api/todos/snooze` and `/api/followup/markdone` accept `source` param to know which model to write to
- Frontend caches `source` per todo and passes it back on Mark Done / Snooze
- `isFollowupTodo()` returns false for `source='task'` — task records can't use the SMS follow-up flow yet (depends on `x_followup_workiz_uuid` field on mail.activity)

See `project_todo_models_in_odoo.md` for the full breakdown.

### Second bug — 30-row limit hid far-future tasks

DJ invoiced Bud Piraino (12-month "On Request" frequency). Phase 5 created task #334 due 2027-04-25. DJ couldn't find it in Render. Root cause: my `/api/todos` query had `limit=30` per source; Bud's deadline was past position 50 in date-asc order.

Fix (commit c9f64d11): limit raised 30 → 250 per source. At DJ's current ~50 todos, no perceptible load impact (~200-500ms extra at most, ~100KB more over the wire).

### Phase 5 docstring lie — fixed

Phase 5's top docstring claimed "ON DEMAND: Creates follow-up reminder in Odoo (mail.activity only)" but the actual code at line 591 uses `project.task`. Fixed (commit 85129602 in Odoo-Migration repo).

The 30 historical "Follow-up: <Name>" mail.activity records appear to be from an older Phase 5 version (before it switched to project.task). Decision: leave them in mail.activity for now — they have access to the SMS Follow-Up flow which depends on `x_followup_workiz_uuid` storage. Once we extend that flow to project.task (task #25), we can convert them safely.

### Custom Studio fields added to Odoo

- `res.partner.x_default_po_template_id` (many2one to mail.template) — vendor's default PO email template
- `res.partner.x_aliases` (char) — comma-separated alternate names for natural-language matching

Pattern is reusable for any future vendor.

### Quote tool /api/upcoming surfaces drafts now

`/api/upcoming` previously filtered `state in ['sale', 'done']`. Now filters `state in ['draft', 'sale', 'done']` so Workiz-linked draft Quote SOs appear in the Quote Tool's "Pick from scheduled jobs" picker. Each job carries a `state` field so frontend can style/badge differently.

## Files touched tonight

- `Saunders Render App/routers/owner/dashboard.py` — many edits (4 new tools, 4 new endpoints, /api/todos extended, /api/upcoming includes drafts, helpers for vendor + product resolution)
- `Saunders Render App/static/owner/quote.html` — Approve & Push button on success card; opens Workiz in new tab on success
- `Saunders Render App/static/owner/activities.html` — pass `source` through to backend; suppress follow-up modal on task-source records
- `windowandsolarcare-hash/Odoo-Migration/1_Production_Code/zapier_phase5_FLATTENED_FINAL.py` — docstring fix (project.task, not mail.activity)

## Activities on DJ's todo list — actionable status

- **Activity #66** — Verify preselect coverage post-accounting-migration (due 2026-05-13). Self-contained runbook in note.
- **Activity #68** — Set up Workiz "Quote" substatus + automation webhook (DJ-blocked — DJ creates substatus in Workiz, then ping for Render endpoint). Spec'd in task #17.
- **Activity #70** — Order screen material (due 2026-05-01).
- **Activity #71** — Pay Younger Felix the balance (due 2026-04-30).

Activity #67 (Phase 4 auto-clear) and #69 (Push to Workiz button) — both COMPLETED tonight (closed in Odoo with feedback note).

## Open future tasks (parked, ready to execute when DJ green-lights)

- **Task #17** — Workiz Quote substatus + webhook for instant sync (DJ-blocked on Workiz substatus + automation creation)
- **Task #25** — Extend SMS Follow-Up flow to project.task records (then convert the 30 historical mail.activity follow-ups to project.task for unified model)

Both have spec-grade descriptions — files, functions, acceptance criteria, blocker breakdown.

## DJ-blocked items still waiting

1. **Workiz "Quote" SubStatus + automation webhook** — DJ creates substatus + automation in Workiz UI, then I wire the endpoint
2. **Workiz auto-text rule for JobType=Quote** — DJ filters the existing customer-confirmation auto-text so it doesn't fire on quote visits
3. **Active Window Products** — actual production use of the new PO flow (verify Bud's frame color tomorrow before sending P00102, etc.)

## Memory files added/touched tonight

- `session_apr30_summary.md` — this file (covers full session)
- `project_awp_vendor_setup.md` — extended with x_default_po_template_id, x_aliases, custom fiscal position, all 33 products, AWP Order Request template id 49, comma-separated email rule
- `project_todo_models_in_odoo.md` — NEW: explains mail.activity vs project.task, why create_todo writes to project.task, the bug-fix pattern
- `project_quote_tool.md` — Saved Quotes filter narrowed to client_order_ref watermark (was too broad with job_type='Quote')
- `feedback_activity_notes_self_contained.md` — extended with the "always real `<a href>` for URLs" rule
- `reference_supplier_pricing.md` — extended with Sec 1 PDF + 33 imported products
- `reference_google_cloud_apis.md` — Google Cloud project + API key registry
- `feedback_github_deploy_python_fallback.md` — fallback for the bash+powershell base64 issue
