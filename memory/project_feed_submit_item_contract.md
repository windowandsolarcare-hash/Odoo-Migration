---
name: project_feed_submit_item_contract
description: "feed.submit_item (HUD cards) validates hard — kind must be 'attention'|'approval', urgency 'interrupt'|'today'|'glance', and action{label,href} is REQUIRED on EVERY card. Invalid → silently rejected (submit_item returns {ok:False} that most callers ignore)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-16T00:44:08.467Z
---

**Learned 2026-09-12** building the Thumbtack capture card (a card silently never appeared until I read validate_item).

## The HUD feed contract (`routers/owner/feed.py` → validate_item / submit_item)
`submit_item(item)` calls `validate_item` and, if there are ANY problems, returns `{'ok': False, 'errors': [...]}` and writes NOTHING. Most producers call submit_item inside a `try/except: pass` and do NOT check the return, so an invalid card just silently never shows up on the HUD. When a card you submitted isn't appearing, check the contract FIRST.

Hard rules (as of 2026-09-12):
- **Required fields on EVERY card:** `id, kind, source, title, why_now, urgency, action, created`. Missing any → rejected. (`action` is required even for non-approval cards.)
- **`kind` ∈ `('attention', 'approval')`** — there is NO custom kind. `_KINDS` gates it.
- **`urgency` ∈ `('interrupt', 'today', 'glance')`** — NOT 'soon'/'now'/etc. `_URGENCIES` gates it.
- **`action` must be `{label, href}`** (both non-empty) when present — and it IS required, so always supply it.
- **`title` ≤ 80 chars.**
- **`kind=='approval'`** needs EITHER a `draft={summary, body, on_approve{method, href}}` (one-tap approve, e.g. payments) **OR** just a valid `action{label,href}` (opens a review screen). ★ CORRECTED 2026-09-16: it used to require the draft UNCONDITIONALLY, which silently rejected every action-only approval card. See the incident below.
- `badge` must be numeric (a string label is auto-moved to `pill`).
- Terminal statuses: `approved / declined / done`. Resubmitting the same `id` preserves status unless it was terminal AND `created` changed (→ resets to 'new').

## How to apply — a card that needs a CUSTOM render (e.g. two input fields)
Don't invent a new `kind` (it'll be rejected). Use `kind='attention'` + a custom MARKER field (validate_item ignores unknown fields) and branch the renderer on the marker. Example: the Thumbtack two-field capture card uses `kind:'attention', captureform:True` and `static/owner/v2_hud.html` `card()` branches on `it.captureform` to render the cell+email inputs; the live banner (`v2_needsyou_banner.js`) excludes `it.captureform`. Still supply a valid `action{label,href}` (e.g. a self-link to the HUD card).

## Incident 2026-09-16 — this class bit HARD (16-day silent gap)
`reminders.py _card_for` was changed 2026-08-31 (bbdea6af) to submit the appointment-reminder card as `kind:'approval'` with an `action` and **no draft** (DJ's review-screen design). The then-unconditional draft requirement rejected it every time; `_card_for` **ignored the `{ok:False}`** → the confirm + night-before HUD cards silently never stored for ~16 days (clean "built" log, empty feed). Maint-stage cards were unaffected (they're `kind:'attention'`, no draft needed). Fixes: validate_item now accepts approval draft-OR-action (feed.py 4e89874a); `_card_for` now logs a rejected submit (reminders.py 76043bfc).
**THE governing lesson: NEVER ignore an `ok:False`/falsy return from a store write** (`submit_item`, DB wrappers, any validate-then-return-errors API). A silent-reject contract fails invisibly when its caller assumes success — check and log every one.

Related: [[project_thumbtack_proxy_numbers]], [[feedback_hud_cards_live_not_inbox]], [[feedback_odoo_verify_content_not_status]].
