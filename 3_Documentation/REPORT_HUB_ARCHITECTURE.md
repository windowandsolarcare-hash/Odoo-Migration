# Report Hub + Brain — Architecture & Redesign Plan
**Status:** DRAFT for review (DJ + Claude) · **Created:** 2026-06-21
**Scope:** owner app in `saunders-render-app` (`routers/owner/*.py`, `static/owner/*.html`)
**Goal:** turn ~58 bolted-on report screens into ONE designed system: a report hub, one result format, and one place to *solve* what a report surfaces (the Brain).

---

## 1. Why we're doing this (DJ's words)

> "It's starting to feel like a bunch of add-ons rather than a well-thought-out app. All reports should come from the same report screen — maybe a pill you press, maybe a card — but the result should look formatted exactly the same as any other report, just different data. And the results should be drillable or editable. Too often I find something in a report and it doesn't give me the ability to solve it right there. That's why I wanted everything in the Brain."

Three principles fall out of that:

1. **One way to see a report.** Every report is selected the same way and renders in the same format. Different data, identical frame.
2. **One way to solve.** Any row, from any report, opens the same detail+action surface (the Brain). You fix it where you found it.
3. **Reports are lenses, not pages.** A report is a saved query that returns standard rows — not a hand-built screen.

---

## 2. Current state (from the 2026-06-21 code survey)

- **~58 report/list surfaces** across 30 router files + 27 HTML pages. No "reports home."
- **No shared UI.** 5 distinct color palettes; the same "status pill" coded 6 different ways; 5–7 different "result row" treatments (analytics=table+modal, stale=cards+pills, maintenance=cards+slots, reengage=cards+log, reactivation=two-view, hemet=cards+dot); 4 header/back patterns. Each page reinvents its CSS.
- **Dead-ends everywhere.** Most lists are read-only or link out to Odoo/Workiz. Worst: **Stale SOs** (0 in-place fixes), the **Brain SO-detail** (view-only wall), **Pre-Deposit** (row → another list). Proof in-place works: Maintenance "pick a slot", Reactivation "book".
- **Structural rot.** `dashboard.py` = **12,393 lines / 243 functions / ~15 domains** (43% of backend) and holds **dozens of duplicate routes that silently shadow the real routers** (confirmed: `/api/scheduled_sos`, `/api/reactivation/candidates`, `/api/planner/*`, plus todos/payroll/stale). Editing the "right" file often does nothing — this is the fragility.

---

## 3. Target architecture

```
        ┌─────────────────────────────────────────────────────┐
        │  REPORT HUB  /owner/reports                          │
        │  grid of report CARDS (live counts)                  │
        │  [Overdue 21] [Stale 8] [Reactivate 156] [Unpaid $X] │
        └───────────────┬─────────────────────────────────────┘
                        │ tap a card
                        ▼
        ┌─────────────────────────────────────────────────────┐
        │  REPORT VIEW (full screen)                           │
        │  PILL row to hop between related reports:            │
        │   (Overdue) Stale  Reactivate  Lapsed                │
        │  ── filters (optional) ───────────────────────────── │
        │  UNIFIED RESULT COMPONENT  (same format every time)  │
        │   row · row · row · row  ──── tap any row ────┐      │
        └───────────────────────────────────────────────┼──────┘
                                                         │
                                                         ▼
        ┌─────────────────────────────────────────────────────┐
        │  THE BRAIN  (universal detail + action sheet)        │
        │  full record + actions: Open WZ/Odoo · Sync ·        │
        │  Reschedule · Mark Paid · Send SMS · Edit · Book ·    │
        │  Add Note · Delete · Next job                         │
        └─────────────────────────────────────────────────────┘
```

**Selector model (DJ chose "cards → pills"):**
- The **Hub** shows report **cards** with live counts for discovery ("Overdue 21").
- Opening a card drops you into the **Report View**; a **pill row** at the top lets you hop between related reports without going back to the hub.

**Two shared components replace dozens of pages:**
- **Result component** — renders any report's rows identically.
- **Brain sheet** — the one detail+action surface every row opens.

---

## 4. Component contracts (the important part)

### 4.1 Standard row — what every report's data function returns
```ts
ReportRow = {
  key:       string,            // stable id, e.g. "so:15815"
  entity:    'job'|'customer'|'invoice'|'task',   // what the Brain opens
  entity_id: number,            // so_id / partner_id / move_id / task_id
  title:     string,            // primary line (customer name)
  subtitle:  string,            // address / service
  meta:      string,            // "Outside Windows · Submitted · 👷 Dan"
  amount:    number|null,
  date:      string|null,       // ISO; component formats it
  badges:    Badge[],           // [{label:'176d overdue', tone:'danger'}]
  actions:   ActionKey[],       // ['sync','reschedule','sms','pay','book','delete']
  links:     { workiz?:string, odoo?:string, property?:string }
}
Badge    = { label:string, tone:'ok'|'warn'|'danger'|'info'|'muted' }
ActionKey= 'open'|'sync'|'reschedule'|'pay'|'sms'|'book'|'edit'|'note'|'delete'|'nextjob'
```
The result component knows NOTHING about the report — it just renders rows + the actions each row declares. Same code, every report.

### 4.2 Report definition — registering a report (the registry)
```ts
ReportDef = {
  key:    string,                 // 'overdue_maint'
  name:   string,                 // 'Overdue Maintenance'
  group:  string,                 // 'Schedule' (which pill cluster)
  icon:   string,                 // '🔧'
  count:  () => number,           // for the card badge
  rows:   (filters) => ReportRow[],   // THE query
  filters?: FilterDef[],          // optional facets (city, year, status)
}
```
**Adding a report = write a `rows()` function + register it.** No new page, no new CSS. That is the whole point.

Backend: a single `GET /owner/api/reports/{key}?<filters>` returns `{rows, count, filters}` in the standard shape, dispatching to the registered report. The hub's card counts come from `GET /owner/api/reports` (the registry + counts).

### 4.3 The Brain — `openBrain(entity, entity_id)`
- Loads a standard detail payload for the entity (reuse `so_full` / `customer_jobs` / invoice read).
- Renders the full action set; each action is wired to an **endpoint that already exists** (sync_job_from_workiz, set_slot, record_*_payment, send SMS, write SO fields, duplicate/book, delete_job).
- Inline edit for the high-value fields (date/reschedule, amount/line items, gate, frequency, type of service, paid status).
- This is the convergence of "everything in the Brain" + "solve where you found it." The Customers-tab brain we already have is the seed; this generalizes it and makes it editable.

---

## 5. Design system (`common.css` + shared JS)

- **One palette, one set of components** in `static/owner/common.css`: `--bg/--surface/--card/--line/--text/--dim/--accent/--ok/--warn/--danger/--info` and component classes `.rpt-card .rpt-row .rpt-pill .badge .sheet .page-header`. Every page links it.
- **Shared renderers** in `static/owner/report_kit.js`: `renderResult(rows)`, `renderPill row`, `openBrain(entity,id)`, `badge()`. Pages stop hand-rolling render functions.
- **Emailed reports use the same tokens** (and the required gray separator lines for financials) so on-screen and emailed reports finally match.
- Reuse what already works: `ql_panel.js` (quick launch), `route_map.js` (maps) stay; they already inject self-contained CSS.

---

## 6. Phasing (incremental — never a big-bang rewrite)

> Guardrail: existing screens keep working until their replacement is at parity. Nothing is deleted without DJ's OK (CLAUDE rule 10).

- **Phase 0 — Foundation.** `common.css` + `report_kit.js` (result component, badge, pill, brain stub). No behavior change. Retrofit ONE existing screen to it as a smoke test.
- **Phase 1 — Hub + 3 flagship reports.** Build `/owner/reports` (cards→pills) + the report registry + `GET /api/reports[/{key}]`. Wire **Overdue Maintenance, Stale SOs, Reactivation Due** into the unified result. Old pages stay.
- **Phase 2 — The Brain (the big build).** Universal detail+action sheet with inline **reschedule / mark-paid / send-SMS / edit**, opened from every result row. This is where dead-ends die.
- **Phase 3 — Migrate the rest** (lapsed, unpaid, hemet, submitted, deleted, payroll views…) onto the hub; retire bespoke pages as each reaches parity.

**Parallel debt track (invisible, prevents recurring bugs):**
- Delete the shadow-route duplicates from `dashboard.py` so the real routers run (kills the class of bug we hit with `scheduled_sos`).
- Split `dashboard.py` by domain (agent / payments / payroll / quotes / sync / core). Behind the scenes, no UX change.

---

## 7. Reports to register (first pass, from the survey)

Schedule: Overdue Maintenance · Submitted-to-Schedule · Stale SOs · Booking Requests · Calendar gaps
Money: Unpaid / Pre-Deposit · Stale w/ payment match · MTD vs forecast · Weekly digest
Retention: Reactivation Due · Reactivation Candidates · Hemet fill · Lapsed customers
Customers: LTV leaderboard · Deciles/Pareto · Cohort retention · Leads
Team: Payroll stops · Shift hours · Gusto export
Audit: Recently deleted · Daily sync log

Each becomes one `rows()` function returning `ReportRow[]`.

---

## 8. Open decisions for DJ

1. **Hub home:** new top-level **Reports** module is the front door for all of these — agreed? (Existing module cards can deep-link into specific reports too.)
2. **Editability depth in the Brain:** which fields must be inline-editable first? (proposed: date/reschedule, line items/amount, paid status, gate, frequency, type-of-service.)
3. **Debt track appetite:** do the shadow-route cleanup + god-file split in parallel, or after the UX is proven?
4. **Naming:** "Reports", "Command Center", or "The Brain" as the label?

---

## 9. Non-goals / guardrails
- No new Odoo seats / custom models / second instance (hard limits).
- No big-bang rewrite; old screens live until parity.
- No deleting working code without explicit OK.
- Reuse existing endpoints for actions wherever they exist; don't re-implement payment/sync logic.
