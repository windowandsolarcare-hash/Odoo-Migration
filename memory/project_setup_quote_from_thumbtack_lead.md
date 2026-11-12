---
name: project_setup_quote_from_thumbtack_lead
description: "How Operator sets up a quote from a Thumbtack (or Angi) lead via the app's own endpoints — where the window scope lives + the quote-tool create/price flow"
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-12T05:06:42.407Z
---

"Set up a quote for the recent Thumbtack message" = build a DRAFT quote SO in the app's quote tool for that lead, priced off DJ's own rate table, left as a draft for DJ to review/adjust/send. Nothing goes to the customer (quotes are review-then-send). Full path, all via the OWNER-cookie app endpoints (no raw Odoo writes):

**1. Find the lead in the inbox.** `GET /owner/api/inbox/list` → `conversations[]`. A Thumbtack lead's snippet reads "<Name> replied to you on Thumbtack. View the full conversation here: https://www.thumbtack.com/request/.../messages". The customer's own words follow after the `---`. Open the thread with `GET /owner/api/inbox/thread?c=<norm>` (param is **`c`**, the norm/phone — NOT `norm=`; messages are under `conv.msgs`).

**2. Get the WINDOW SCOPE — it's NOT in the SMS, it's in the crm.lead.** The Thumbtack webhook (`routers/thumbtack.py`) writes the lead's structured request into a **crm.lead** record: `name = "Thumbtack: <Category> — <Name>"`, `description = _build_desc(...)`. Read it (read-only RPC): `crm.lead search [['description','ilike','<street or negotiationID>']]` or `['contact_name','ilike','<name>']`. The description carries exactly what you need to price: **Number of windows (e.g. "21-25"), Building type (single-level→no second-story panes), Window features ("No grids, includes sliding doors"), Cleaning areas ("Interior, screens, and tracks"→in_out full service), Location/zip.** (Angi leads arrive the same shape in the inbox snippet: "Angi here: You have a new lead. Name/Service/Zip…".)

**3. Price + create via the quote tool.** Rates (single source of truth) = `GET /owner/api/quote/rates` → `{reg_panes, over_panes, ss_panes, reg_sliders, over_sliders, triple_sliders}` ($/unit) × difficulty {standard 1.0, hard 1.15, very_hard 1.3}. `_calc_quote_total`: `base = Σ count[k]*rate[k]`; **in_out** uses base as-is; **outside** = `base/2*1.10`; then ×difficulty. Create: `POST /owner/api/quote/save` {`partner_id`:<existing contact id>, `address`, `phone`, `name`, `mode`:"in_out"|"outside", `difficulty`, `counts`:{reg_panes,…}} → returns `{so_id, so_name, total}`. Requires total>0 (needs at least one count). It stamps `client_order_ref = "🔶 QUOTE ONLY"` so the quote surfaces in DJ's quote list; SO stays **draft**.

**4. Reuse the existing contact — don't dupe.** A Thumbtack/Angi lead already created the res.partner (from the ingest), so pass `partner_id` to `quote/save` (Path B with `partner_id` skips partner-create). BUT Path B only writes `street` when it CREATES a new partner — with `partner_id` given it does NOT patch the address. So follow with `POST /owner/api/quote/update` {`so_id`, `address`, `phone`, `name`, same mode/difficulty/counts}: it patches the linked partner's street/phone/name AND refreshes the priced line (`_replace_quote_line`, draft-safe). Net = one clean priced line + the property address on the contact.

**How to apply:** The one judgment call is the slider count — Thumbtack gives a window RANGE, not a panes-vs-sliders split. Make a sensible estimate (e.g. "21-25 windows, includes sliding doors" → ~22 reg_panes + ~3 reg_sliders), create the draft, and TELL DJ the assumption in one line — he one-taps the counts to reprice before sending. Don't idle asking; the draft is safe because nothing sends until DJ does. Real run 2026-11-11: Kathryn Robinson, 705 Hawkhill Trail (Indian Ridge, Palm Desert 92211), contact 27332 → quote **S00371** (id 17816), $263 in_out standard, 22 panes + 3 sliders.

Ties to [[feedback_assistant_use_app_workflow_not_raw_api]], [[project_new_job_via_app_endpoints]], [[feedback_dj_operating_instincts]] (two quote types, review-then-send), and the HUD-card/inbox pattern in [[project_hud_card_prefill_thread_deeplink]].
