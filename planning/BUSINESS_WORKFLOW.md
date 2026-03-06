# Window & Solar Care — Complete Business Workflow
**Owner:** DJ Sanders  
**Date:** 2026-03-04  
**Purpose:** Full operational workflow document for Odoo migration gap analysis

---

## OVERVIEW
Window & Solar Care operates primarily through Workiz for job management, 
scheduling, and customer communication. The goal is to migrate all operations 
to Odoo with AI-driven automation, replacing Workiz entirely and improving 
on every workflow currently done manually.

---

## 1. LEAD INTAKE

### Current State (Workiz)
- Lead sources: Angi, Thumbtack, text messages, phone calls, referrals
- Workiz parses incoming leads from these sources
- Manual review and response required
- Response speed depends on Dan being available
- Many leads lost due to slow follow-up (especially Angi/Thumbtack)

### Pain Points
- Not AI-driven — Dan-dependent
- Slow response = lost jobs (competitors beat us)
- Large backlog of old unconverted leads from Angi/Thumbtack
- No automated pricing or instant quote capability

### Goal
- AI responds instantly to every incoming lead
- AI qualifies the lead (what service, location, property type)
- AI provides instant pricing estimate
- AI attempts to convert lead to booked job automatically
- No Dan involvement until job is confirmed

---

## 2. QUOTE & JOB CREATION

### Current State (Workiz)
- Lead becomes a quote (sometimes set up as lead — not a clean process)
- Job types: Windows In/Out, Outside Only, Solar, etc.
- Dan manually texts the quote to the customer
- Customer accepts via text
- Dan changes job type, adds line items, sets pricing, schedules date
- No formal estimate system used — kept simple intentionally

### Pain Points
- Process is not clean or consistent
- Entirely manual — no automation
- No online self-service quoting

### Goal
- AI-driven quote generation based on service type and property
- Customer can self-schedule via Calendly link in every communication
- Quote approval triggers automatic job creation in Odoo

---

## 3. JOB CONFIRMATION SEQUENCE

### Current State (Workiz)
**After Scheduling:**
- Automated text sent with: job details, tech name, date, location
- Customer replies "OK"
- Dan manually flips tag to "OK" on calendar

**48 Hours Before:**
- Automated confirmation text sent with link
- Customer clicks link → confirms
- Dan manually flips tag to "CF" on calendar

**Night Before:**
- Automated reminder text sent
- Includes gate access reminder (gated community instructions)

### Tags Used on Calendar
- `OK` = Customer acknowledged job details
- `CF` = Customer confirmed appointment

### Pain Points
- Tag flipping is 100% manual — biggest daily friction
- Requires Dan to monitor and respond to customer replies

### Goal
- Auto-detect customer "OK" reply → automatically flip tag to OK
- Auto-detect confirmation link click → automatically flip tag to CF
- Zero manual tag management
- Gate access reminder sent intelligently based on customer address

---

## 4. DAY OF JOB

### Current State (Workiz)
- Arrive on site, start timer in Workiz
- Complete the job
- Collect payment by method:
  - **Zelle/Venmo:** Text customer with amount and payment info → receive payment → manually text confirmation "funds received"
  - **Credit Card:** Stripe integration (clean, no issues)
  - **Cash/Check:** Collected in physical envelope/wallet, entered at end of day

### Pain Points
- Zelle/Venmo payment detection is manual
- "Funds received" confirmation text is manual
- End of day cash/check entry is manual

### Goal
- Detect incoming Zelle/Venmo payment → auto-send "funds received" text
- Streamline end-of-day cash/check entry
- All payment methods log automatically to Odoo

---

## 5. JOB CLOSEOUT

### Current State (Workiz)
- Enter payment → balance goes to $0
- Change job status to "Done" → removes from calendar, closes job
- Check if customer is on maintenance program:
  - **Maintenance customer** → auto-create next scheduled job (ALREADY BUILT in phases)
  - **On-demand customer** → create follow-up activity in Odoo
  - **"Nightmare Sunday"** → unscheduled job placed 6 months out as trigger to reach out

### What's Already Built
- Phase 3-6 automation handles maintenance scheduling
- On-demand follow-up activity creation
- Reactivation trigger logic

### Goal
- Full closeout automation — no manual steps after payment collected
- Intelligent routing based on customer type (maintenance vs on-demand)
- Calendly link included in all follow-up communications

---

## 6. REACTIVATION & CRM CAMPAIGNS

### Current State (Workiz)
- **Reactivation Program:** Targets customers 1+ year inactive → automated message via Workiz
- **Unscheduled Job Pipeline:** Jobs placed in unscheduled state to enable Workiz communication without hitting calendar
- **Old Leads:** Large backlog of Angi/Thumbtack leads never converted — no current follow-up system
- **Physical Mail:** EDDM postcards used for new customer outreach (cheap via own printing company)
- **Calendly:** Set up and used in reactivation — want it everywhere

### Pain Points
- Workiz CRM is poor — primary reason for Odoo migration
- Campaigns are manual and Dan-dependent
- Old lead database untapped
- No multi-channel campaign capability

### Goal
- AI-driven campaigns that run without Dan
- Old lead reactivation campaign (AI reaches out, qualifies, books)
- Multi-touch campaigns: text, email, postcard triggers
- Calendly booking link in every customer touchpoint
- Odoo CRM handles full pipeline visibility
- Campaign suggestions and strategy from AI

---

## 7. ACCOUNTING

### Current State
- Workiz invoices sync automatically to QuickBooks Online
- Bank statements imported to QuickBooks
- Manual reconciliation in QuickBooks
- No formal expense tracking (expenses captured from bank statements only)
- No P&L or balance sheet currently generated regularly

### Goal
- Replace QuickBooks with Odoo Accounting
- Full P&L, balance sheets, tax reporting in Odoo
- Bank statement reconciliation in Odoo
- Invoice → payment → accounting fully automated
- Expense tracking (light — from bank feed is acceptable)

---

## 8. COMMUNICATION INFRASTRUCTURE

### Current State
- Workiz is the SOLE communication number for the business
- ALL customer texts go through Workiz
- To text a customer, a job must exist in Workiz (pipeline limitation)
- This is why unscheduled jobs are used as communication vehicles

### Critical Dependency
- Moving off Workiz requires replacing this communication layer
- Odoo must become the single communication hub
- SMS capability in Odoo is essential before Workiz can be dropped

### Goal
- Odoo handles all outbound/inbound SMS
- No job required to initiate communication
- Full conversation history in Odoo CRM per customer

---

## SUMMARY — WHAT NEEDS TO BE BUILT TO DUMP WORKIZ

| Workflow | Status |
|---|---|
| Maintenance auto-scheduling | ✅ Already built (Phases 3-6) |
| On-demand follow-up activity | ✅ Already built |
| Reactivation campaign | ✅ Already built |
| Job status → Odoo sync | ✅ Already built |
| Auto tag flipping (OK, CF) | ❌ Needs building |
| AI lead intake & conversion | ❌ Needs building |
| AI pricing & quoting | ❌ Needs building |
| Zelle/Venmo payment detection | ❌ Needs building |
| SMS via Odoo (replace Workiz) | ❌ Critical dependency |
| Calendly throughout all flows | 🔶 Partial (reactivation only) |
| Old lead AI reactivation | ❌ Needs building |
| Multi-channel CRM campaigns | ❌ Needs building |
| Odoo Accounting (replace QBO) | ❌ Needs building |
| Online self-service quoting | ❌ Needs building |

---

## RECOMMENDED NEXT PRIORITIES

1. **SMS in Odoo** — nothing else can be completed without this
2. **Auto tag flipping** — highest daily friction, fastest win
3. **AI lead response** — biggest revenue impact
4. **Zelle/Venmo detection** — daily manual task elimination
5. **Old lead campaign** — untapped revenue sitting there
6. **Odoo Accounting** — replace QuickBooks

---

*This document should be reviewed with Claude in Cursor against the existing 
phase documentation in `3_Documentation` and the built phases in 
`2_Modular_Phase3_Components` to produce a full gap analysis and development roadmap.*
