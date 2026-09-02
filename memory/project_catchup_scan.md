# Catch me up — the one scan before you reply
**Type:** project
**Created:** 2026-09-02 (Lead, cloud)
**Trigger:** Christopher Brown texted in; the suggested reply was useless because nothing on
screen said we had already quoted him $270 windows / $150 solar back on Jun 10.

## What it is
`GET /owner/api/catchup?partner_id=N` — `routers/owner/catchup.py` (app repo). READ-ONLY.
One aggregator that answers *"is there already something hanging out there for this customer?"*
before DJ replies. **It adds no new data source** — every fact already existed, just spread
across four screens.

Returns `{ok, name, phone, last_job, items[], n_action, nothing, brief}`.
`items[]` = `{kind, icon, title, detail, tone}` where tone is `stop|act|info`.
`brief` is a paste-able plain-text summary.

Kinds it detects: `blocked` (STOP / Do Not Contact) · `upcoming` (job on the books) ·
`submitted` (draft SO nobody scheduled) · `offer` (pending slot offer — the double-offer trap) ·
`outreach` (reactivation / re-engagement, **plus** the most recent message that quoted a price) ·
`owed` (unpaid invoices) · `due` (overdue Maintenance).

## Two surfaces, ONE renderer
`static/owner/wsc_catchup.js` — never fork it.
- **Customer Brain** (`v2_customers.html`): rides the dossier's existing `Promise.all`, paints at
  the top of the card. Collapses to one quiet line when nothing is outstanding.
- **Inbox Actions** (`v2_inbox.html`): "🔎 Catch me up on them", placed ABOVE "Suggest a reply" —
  the point is to look before you draft.

## Why: three things that were only found by testing it LIVE
1. **The price is in an older message than the last nudge.** Showing only the newest outreach hid
   the quote. Now shows the newest AND the most recent priced one.
2. **Extract money from the RAW body, not the trimmed gist.** The gist cut at 150 chars and the
   `$270` sat past the cut, so `findall` returned nothing on a message that plainly had prices.
   When a message quotes money, show the *sentence the money is in* — not the greeting.
3. **Frequency/type-of-service come off the JOB first** (`x_studio_x_studio_frequency_so`,
   `x_studio_x_studio_type_of_service_so`), partner second — same precedence as the customer card.
   Only `Maintenance` can be "late"; On Request / Unknown never are.

## Dashboard discipline (see project_hud_dashboard_not_inbox.md)
Nothing is stored. Every item recomputes per call and **self-withdraws when it stops being true** —
an outreach with a job booked after it drops to `info`, an expired offer is not an open offer.
Verified live on Clark Argeris: two outreaches correctly demoted to info because he booked.

## How to apply
Before building any "what's going on with this customer" surface, call this — don't re-derive it.
It is importable in-process too: `from .catchup import scan; scan(partner_id)`.
Path is feature-namespaced (`/owner/api/catchup`) so an earlier-registered router can't shadow it.
