---
name: Window Quote Tool — full reference
description: 2026-04-29 — DJ replaced the AppSheets "Our Pricing" tool with /owner/quote (and /tech/quote) on Saunders Render App. Saves quotes as Odoo sale.orders with 3 watermarks (client_order_ref, job_type=Quote, QUOTE ONLY tag). Picks from schedule = updates existing Workiz-linked SO; walk-up = creates new partner + SO.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ THIS FIRST when editing /owner/quote, /tech/quote, /api/quote/*, or anything related to window-quoting.**

## ⚠️ 2026-06-16 UPDATES — supersede parts of the doc below
- **ROUTE SHADOW: the LIVE `/api/quote/*` routes are in `routers/owner/dashboard.py` (~line 5366+), registered BEFORE `routers/owner/quotes.py` → dashboard.py WINS; quotes.py is a dead duplicate.** EDIT dashboard.py (same trap as intake/reactivation). quotes.py was kept in sync but is not what runs. (De-dup later like intake/reactivation.)
- **Pick-from-schedule now BRANCHES on the picked job's `x_studio_x_studio_x_studio_job_type`:**
  - **== 'Quote'** (a call-in quote DJ entered in Workiz → synced to schedule) → **reuse it IN PLACE** (`_replace_quote_line` + watermark on that SO). It already has the Workiz #/uuid, so Approve works immediately. No new SO, no orphan.
  - **anything else (real work, e.g. solar)** → **create a SEPARATE new quote SO** from the picked SO's `partner_id`+`partner_shipping_id` (property link carries gate/pricing/address). The picked (solar) SO is UNTOUCHED. (Old always-update-in-place behavior caused the solar-overwrite bug.)
  - Walk-up (no pick) = Path B, creates a fresh contact + SO (unchanged).
- **Approve & Push (`/api/quote/push_to_workiz`)**: if the quote SO has no Workiz uuid, `_create_workiz_for_quote(so_id)` creates the Workiz job (SA 1338 from scratch, UNSCHEDULED, customer+property fields incl. ServiceArea/gate/pricing/last_date_cleaned/ClientId), stamps uuid+link, and **renames the SO to the Workiz SerialId** `str(int(SerialId)).zfill(6)`. Then pushes notes. Approve button always shows now.
- **Phase 4 backstop**: any uuid-linked SO still on a native `S0…` name gets renamed to its 6-digit Workiz SerialId on the next poll (also fixes existing strays). See [[project_quote_tool]] companion details in [[project_new_job_intake]] / the shared-scheduler notes.
- Full rationale (incl. why New Job is NOT on this model — Phase 4 treats Workiz as line-item source of truth on confirmed SOs) is captured at the time of this change.

## What it is

Replacement for DJ's AppSheets "Our Pricing" tool. Mobile-first quote calculator with auto-save to Odoo. DJ uses it on a doorstep with a customer; backend stores everything as a draft `sale.order` (or updates an existing Workiz-linked one).

## Files

- `Saunders Render App/static/owner/quote.html` — single-file UI for both owner and tech (role detected via URL path)
- `Saunders Render App/routers/owner/dashboard.py` — endpoints: `/api/quote/save`, `/api/quote/update`, `/api/quote/get`, `/api/quote/list`
- `Saunders Render App/routers/tech/jobs.py` — `/tech/quote` route mirrors the same HTML
- `Saunders Render App/static/owner/index.html` + `static/tech/index.html` — orange "💲 Window Quote" tile on both dashboards

## Pricing model (rates per unit, in `dashboard.py`)

```python
QUOTE_RATES = {
    'reg_panes':      7,    # Regular Panes
    'over_panes':     8,    # Oversized Panes
    'ss_panes':       9,    # Second Story Panes
    'reg_sliders':   25,    # Regular Sliders
    'over_sliders':  30,    # Oversized Sliders
    'triple_sliders':35,    # Triple Sliders
}
```

## Modifiers

- **Mode** (radio):
  - `in_out` (default) — uses Odoo product **141** "Windows In & Out - Full Service"
  - `outside` — total ÷ 2 × 1.10, uses Odoo product **103** "Outside Windows And Screens"
- **Difficulty** (3 buttons):
  - `standard` ×1.00
  - `hard` ×1.15
  - `very_hard` ×1.30
- Total formula: `sum(count × rate)` → if outside, ÷2 × 1.10 → × difficulty multiplier → round to 2dp

## Watermarks (the 3 signals that mark an SO as a quote)

Applied by `_apply_quote_watermark()`:

1. `client_order_ref` = `'🔶 QUOTE ONLY'` — visible at top of SO form
2. `x_studio_x_studio_x_studio_job_type` = `'Quote'` — selection field, valid value
3. `tag_ids` += "QUOTE ONLY" tag (orange, color 2) — auto-created on first quote save

Phase 4 will eventually clear these on conversion (task #16, not built yet — DJ removes manually for now).

## Save flow — two paths

**Path A: Picked from schedule (so_id present)**
- `_replace_quote_line(so_id, line_create_tuple)` — soft-deletes existing lines (qty=0, price=0; can't unlink on confirmed SOs per `project_so_lines_zero_means_deleted.md`)
- Adds the new quote line with the marker `[Render Quote Tool]` in description
- Patches partner contact details (street/phone/name) if changed
- Applies watermarks
- Returns existing `so_id` and partner_id from the SO

**Path B: Walk-up (no so_id)**
- Auto-creates `res.partner` from name + street + phone
- Creates fresh draft `sale.order` with the quote line
- Applies watermarks
- Returns new `so_id` and partner_id

## Edit flow — `/api/quote/get` + `/api/quote/update`

Saved Quotes panel lists active quote SOs. Tap one → fetches `/api/quote/get?so_id=N` → returns full `{name, address, phone, counts, mode, difficulty, total, partner_id}`. Form fills, Save button switches to "Update Quote" → calls `/api/quote/update` which patches the existing line + partner contact fields. State doesn't matter (works on draft AND confirmed SOs).

## Round-trip data preservation

Quote line description has format:

```
[Render Quote Tool]
2× Regular Panes ($7) · 3× Oversized Panes ($8)
Mode: Windows In & Out
Difficulty: Standard (+0%)
__QUOTE_JSON__:{"counts":{"reg_panes":2,...},"mode":"in_out","difficulty":"standard"}
```

The trailing `__QUOTE_JSON__:` blob lets `/api/quote/get` reconstruct the form state on load. There's a legacy fallback parser (`_parse_quote_json_from_line`) that re-extracts counts/mode/difficulty from the human-readable text for quotes saved before the blob existed.

## Saved Quotes filter — IMPORTANT

`/api/quote/list` filters by `client_order_ref = '🔶 QUOTE ONLY'` (the watermark text, only set by this tool, cleared by Phase 4 on conversion). **DO NOT** filter by `job_type='Quote'` alone — that catches every historical Workiz Quote-type job that Phase 3 imported (was 18 SOs going back to 2022 on 2026-04-29 when the bug was caught and fixed in commit `755d9617`).

The watermark filter:
- ✅ Catches both walk-up draft SOs and updated Workiz-linked confirmed SOs (state=sale) — both get the watermark applied by `_apply_quote_watermark`
- ✅ Excludes pre-Render-tool Workiz quotes (they have `job_type='Quote'` but no watermark)
- ✅ Auto-drops accepted quotes when Phase 4 clears the watermark on conversion

- **Owner role** (URL `/owner/quote`): no limit, sees every active Render-tool quote
- **Tech role** (URL `/tech/quote`): `limit=1`, just their most recent. **Caveat:** filtering by `create_uid` doesn't truly partition because every Render-driven RPC runs as ODOO_USER_ID=2. So tech sees the latest globally, not their own. Real per-tech filtering needs PIN-based auth on save (deferred).

## "Pick from schedule" flow

- "📅 Pick from scheduled jobs" button at the top of the customer block
- Modal lists upcoming jobs from `/api/upcoming` — name, time, address, phone
- Tap → fills name/address/phone (autofills via partner_shipping display name + walks Property→parent for phone) + sets `linkedSoId` + `linkedPartnerId` + shows green banner
- Save uses `linkedSoId` → triggers Path A (update existing SO)
- ✕ on banner OR typing in name/address fields clears the linkage → falls back to Path B (walk-up)

## Address autocomplete

Google Places Autocomplete (New) — see `reference_google_cloud_apis.md`. Key embedded in HTML; restricted to `wsc-field-assistant.onrender.com/*`. Biased to Palm Springs (lat 33.83, lon -116.54), filtered to US.

## UX details DJ asked for

- Two-row stacked counter layout (label+subtotal on top, [−] count [+] on bottom) — tested overflow on phones, fits cleanly
- 5-second undo grace was a separate feature DJ asked for in the activities flow, not directly in quote — but could apply if needed
- Save Quote button is **disabled** until name + address + total > 0 (validateSaveButton called from every input + counter change + mode/difficulty pill click)
- Haptic vibration (12ms) on +/- and 8ms on mode/difficulty pill taps (Android only — iOS Safari blocks Vibration API)

## Architecture decisions (locked)

1. **Quote save = update existing SO when from schedule, create new when walk-up** — DJ's pivot 2026-04-29 to leverage existing Phase 3/4 infrastructure rather than running a parallel SO-creation path.
2. **Soft-delete (zero qty + price) for existing lines** instead of unlink — Odoo blocks unlinking on confirmed SOs.
3. **Three watermark signals** because each surfaces in a different Odoo view (SO form top / dashboard filters / list pills).
4. **`Quote` is an existing valid job_type** — already in the selection list. Don't need to add a new one.
5. **No new custom Odoo fields** — uses built-in `client_order_ref`, existing job_type selection, and crm.tag (auto-creates "QUOTE ONLY" tag if missing).

## Future work (parked as activities #67, #68, #69 due today, plus Render task list)

- **Task #16 / Activity #67** — Phase 4 auto-clear watermarks when Workiz substatus leaves Quote. Modify `zapier_phase4_FLATTENED_FINAL.py` in Odoo-Migration repo. Set job_type from product mapping: 141→"Windows Inside & Outside Plus Screens", 103→"Outside Windows and Screens". Clear `client_order_ref` and remove QUOTE ONLY tag.
- **Task #17 / Activity #68** — Workiz "Quote" substatus + automation webhook → Render endpoint, replaces Phase 3 polling for instant sync. Pattern matches existing STOP webhook (`odoo_webhook_stop_handler.py` in Odoo-Migration). Blocked on DJ creating the substatus.
- **Task #18 / Activity #69** — "Push to Workiz" button on accepted quotes — writes line-item breakdown to Workiz JobNotes (or custom field — DJ to confirm). Uses existing `workiz_post`/JobNotes append-prepend pattern. Pair with #67.
- **Tech-specific saved-quotes filter** — needs PIN-based auth on save endpoint to capture creator's hr.employee ID. Currently all Render writes show as user_id=2.

## Common pitfalls

- **Don't forget the `_apply_quote_watermark` call** after save / update — without it, the SO won't show in the Saved Quotes list.
- **Don't try to unlink existing lines on a confirmed SO** — `_replace_quote_line` already handles the soft-delete pattern correctly.
- **Don't re-use the customer's "QUOTE ONLY" tag** — the helper handles get-or-create. Multiple tags with the same name break filtering.
- **The SO state doesn't matter for the list** — filter is on job_type only. So Path A SOs (state='sale') and Path B SOs (state='draft') both appear.
- **"Pick from schedule" only shows the next 14 days from /api/upcoming.** If DJ created a Quote-substatus job further out, it won't appear until it's within window.

## Related memory

- `reference_google_cloud_apis.md` — API key + project info
- `project_so_lines_zero_means_deleted.md` — why we soft-delete instead of unlink
- `feedback_activity_notes_self_contained.md` — pattern for activities #67-69 notes
- `project_workiz_substatus_needs_status.md` — Workiz API quirk for the future webhook work
