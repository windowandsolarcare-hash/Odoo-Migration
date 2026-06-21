# ERP Architecture — Schedule (heart) + Customer (brain)
**Status:** DRAFT for review (DJ + Claude) · **Created:** 2026-06-21 · **Reframed:** 2026-06-21 (ERP, not reporting)
**Scope:** owner app in `saunders-render-app` (`routers/owner/*.py`, `static/owner/*.html`)
**Goal:** evolve the owner app into a cohesive **ERP** whose HEART is the schedule and whose BRAIN is the customer — turning ~58 bolted-on screens into modules that all feed those two. The unified result component + Brain action sheet are the *mechanism*; the schedule is the center.
*(Filename keeps "REPORT_HUB" for link stability — but the report hub is one feeder mechanism, not the center. See §1.)*

---

## 1. What we're building — an ERP, not a reporting tool

> DJ, 2026-06-21: "I'm creating an **ERP-like system, not a reporting system.** Customer is the brain, but the **schedule is the heart** — everything else complements the schedule and the business."

Two organs anchor the whole system:

- **The Schedule is the HEART.** The field schedule / calendar / dispatch is where the business actually runs: jobs land on it, get worked, get paid. A day in the field *is* the business. Everything the system does exists to keep the right work flowing onto the schedule and to run it smoothly.
- **The Customer is the BRAIN.** Each customer record holds everything — history, properties, pricing, cadence, comms, money — and is where you DECIDE and SOLVE.

Everything else is a **complement** to those two — nothing is a standalone destination:

| Role | Modules | Serves the heart by… |
|---|---|---|
| **FILL** the schedule | Reactivation, Maintenance-due/overdue, Booking requests, New orders, Quotes | putting the right jobs on the calendar at the right time |
| **RUN** the schedule | Field assistant, Route/GPS, Timer, Payments, Confirmations | executing the day |
| **MONEY** | Invoicing, Pre-deposit, Reconciliation | the financial result of the schedule |
| **TEAM** | Payroll, Timeclock, Hiring | the labor that executes it |
| **LEARN / STEER** | Analytics, Reports | reading the business to decide what to schedule & where to grow |
| **GROW** | Marketing, Reviews, SEO, Website | generating demand that becomes scheduled work |

**So where do "reports" fit?** They are *feeder lanes*, not the centerpiece. Almost every report answers one of two questions — *"what should go on the schedule next?"* or *"what's falling through that I need to fix?"* — and its rows resolve **into the schedule** (book it) or **into the brain** (solve it).

The original pain ("a bunch of add-ons… I find something in a report and can't solve it right there") is real, but the cure is not "a better reporting system." The cure is an ERP organized around the heart and brain, where the **unified result component + the Brain action sheet (below) are the *mechanism*** that lets every complement feed the schedule. They are plumbing, not the product.

Three operating principles:
1. **The schedule is the center of gravity.** Every feature is judged by how it gets the right work onto the schedule or runs it better.
2. **One way to solve.** Any row, from any list, opens the same Brain detail+action surface. You fix it where you found it — or you book it onto the schedule from there.
3. **Lenses, not pages.** A report/list is a saved query returning standard rows — not a hand-built screen.

---

## 2. Current state (from the 2026-06-21 code survey)

- **~58 report/list surfaces** across 30 router files + 27 HTML pages. No "reports home."
- **No shared UI.** 5 distinct color palettes; the same "status pill" coded 6 different ways; 5–7 different "result row" treatments (analytics=table+modal, stale=cards+pills, maintenance=cards+slots, reengage=cards+log, reactivation=two-view, hemet=cards+dot); 4 header/back patterns. Each page reinvents its CSS.
- **Dead-ends everywhere.** Most lists are read-only or link out to Odoo/Workiz. Worst: **Stale SOs** (0 in-place fixes), the **Brain SO-detail** (view-only wall), **Pre-Deposit** (row → another list). Proof in-place works: Maintenance "pick a slot", Reactivation "book".
- **Structural rot.** `dashboard.py` = **12,393 lines / 243 functions / ~15 domains** (43% of backend) and holds **dozens of duplicate routes that silently shadow the real routers** (confirmed: `/api/scheduled_sos`, `/api/reactivation/candidates`, `/api/planner/*`, plus todos/payroll/stale). Editing the "right" file often does nothing — this is the fragility.

---

## 3. Target architecture

### 3.0 The ERP, organized around the heart
```
                         ┌──────────────────────────┐
        FILL ──────────► │                          │ ◄────── RUN
   reactivation,         │     THE SCHEDULE         │   field assistant,
   maint-due, booking,   │      (the HEART)         │   route/GPS, timer,
   new orders, quotes    │  field sched · calendar  │   payments, confirms
                         │       · dispatch         │
        GROW ──────────► │                          │ ◄────── MONEY / TEAM
   marketing, reviews,   └────────────┬─────────────┘   invoicing, deposits,
   SEO, website                       │                 payroll, hiring
                                      │ every job ties to a customer
                                      ▼
                         ┌──────────────────────────┐
                         │   THE CUSTOMER (BRAIN)    │  know everything,
                         │  history·props·pricing·   │  DECIDE & SOLVE here
                         │   cadence·comms·money     │
                         └──────────────────────────┘
```
The Schedule is the center of gravity; the Customer is the knowledge/decision center. Every other module is an arrow pointing at one of them.

### 3.1 The feeder mechanism (how complements reach the heart/brain)
The hub/result/Brain pattern below is the *plumbing* that lets any list resolve into **book-it-on-the-schedule** or **solve-it-in-the-brain**. It is one mechanism serving the organs above — not the center of the app.
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
