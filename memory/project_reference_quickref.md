---
name: project_reference_quickref
description: "Reference quick-ref mini-app (/owner/reference) — Evernote-Shortcuts replacement: a flat list of titled free-text cards (phone #s, addresses, account info). Odoo-backed (ir.config_parameter), NOT Google. Built 2026-06-17."
metadata:
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ (2026-06-17): "I need an area where I can post important things, like all my phone numbers, addresses like evernote shortcuts."** Showed an Evernote Shortcuts screenshot (Addresses / Account Info / Call Back Numbers / Equipment list / Kaiser Cards / etc.). Chose: **New Odoo-backed Reference area** + **flat list of titled cards**.

## What it is
A standalone owner mini-app: a scrollable flat list of titled cards, each holding free text. Tap a card → view/edit sheet; ＋ FAB → add; 🗑 in editor → delete; drag the ⠿ handle → reorder (persisted). Search box filters title+body. Slate theme, phone-friendly. Dashboard tile **📌 Reference** in the **My Day** group (after Notes), cls `card-personal`.

## Why Odoo-backed (NOT Google)
Deliberately stored in Odoo, not Google Drive, so it never breaks like the Notes app does on the ~7-day OAuth token expiry ([[project_notes_google_oauth]]). No external auth at all.

## Architecture
- **Router:** `routers/owner/reference.py` (registered in main.py as `owner_reference`, prefix `/owner`).
- **Storage:** ONE `ir.config_parameter` key **`owner.reference.cards`** = JSON list of `{id, title, body}`. List order = display order. `id` = ms timestamp (`int(time.time()*1000)`).
- **Endpoints:** `GET /owner/reference` (page), `GET /owner/api/reference` (`{cards:[]}`), `POST /api/reference/add` (returns `{ok,card}`), `/update` (`{id,title?,body?}`), `/delete` (`{id}`), `/reorder` (`{ids:[...]}` — reorders by id, appends any unnamed card for safety).
- **Page:** `static/owner/reference.html` — self-contained, no external JS. Drag via pointer events (touch+mouse); editor is a bottom sheet. Reorder disabled while a search filter is active (drag handle hidden).

## Verified live 2026-06-17 (self-cleaning)
Full round-trip on the live service: add×2 → list → update title → reorder → delete×2 → final list empty. Page 200, API `{cards:[]}` clean.

## Pattern notes (reusable)
- New owner mini-app = router file + `static/owner/<name>.html` + register in main.py (import + include_router) + a tile in `static/owner/index.html` GROUPS. Same shape as My Day.
- GH push gotcha this session: the CLAUDE.md heredoc-JSON push pattern threw "Problems parsing JSON" 400; building the payload JSON in **Python** (`json.dumps`) instead was reliable. Windows Python can't open `/c/...` paths — pass `C:/Users/...` to Python but `/c/Users/...` to `gh --input`.
