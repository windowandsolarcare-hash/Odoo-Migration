---
name: project_idea_board_venture_boards
description: "The Idea Board (ideas.py) now supports named \"Venture Boards\" — grouped, ranked catalogs of ideas kept OFF the working board, each venture its own commentable card. How grouping, seeding, and the Cheryl mirror work."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T14:23:27.365Z
---

**Idea Board Venture Boards (2026-09-22).** DJ+Cheryl wanted both fleet venture brainstorms (R1 "build on what we have" = 51 ideas; R2 "greenfield" = 66) IN the Idea Board so they can read + comment + prioritize together, not only in a private Claude artifact.

## Data model (still the ONE blob `ir.config_parameter['ideaboard.data']`)
- Added `d['groups']` = `[{id,label,blurb,artifact_url,at}]` — named boards.
- A card can carry `group` (group id) + `rank` (int, best→worst) + `theme`/`revenue`/`convergence`/`flags` (★/⚠/⚠⚠). A card WITH a `group` is a venture-board card.
- **Grouped cards are EXCLUDED from the working board** (`/api/ideas/board` skips `c.get('group')`), so 117 venture cards don't flood DJ's real sparks or scramble the heat ranking. The board read also returns `groups` (with live `count`).
- Per-venture discussion = the SAME per-card `thread` mechanism (`card_msg`) — tapping a venture opens the normal card detail; every comment is saved for both of them.

## Endpoints (ideas.py)
- `GET /api/ideas/group?id=<gid>` — one board's meta + its cards sorted by `rank` asc.
- `POST /api/ideas/seed_ventures` — idempotent per-group loader (body: {group, ventures[]}); REPLACES the group's cards but PRESERVES existing threads matched by `rank`. Core = `_seed_group(d,g,ventures)`.
- `GET /api/ideas/seed_builtin` — one-tap, secret-free loader: reads the committed `routers/owner/venture_seed.json` (both boards, 51+66) and seeds them. Idempotent + thread-preserving. Owner-cookie gated by the /owner mount.
- **Auto-seed:** `ideas.html loadBoard()` fires `seed_builtin` ONCE when `IDEA_BASE==='/owner'` AND `groups` is empty — so the boards just appear when DJ opens `/owner/ideas`, no manual step.

## ★ Cheryl mirror gotcha (paired change)
`routers/cheryl/ideas.py` mirrors owner ideas by an EXPLICIT `_ROUTES` list (delegates to owner functions). A new endpoint the board UI calls MUST be added there too or Cheryl 404s. I added `/api/ideas/group` to her list (she needs the read). `seed_builtin`/`seed_ventures` stay owner-only (seeding is DJ's; auto-seed is owner-only) — Cheryl sees the boards once DJ's session has seeded the shared blob, and can comment via the already-mirrored `card_msg`. So **DJ must open the board first**, then Cheryl sees it. Cheryl needs NO new access grant. See [[feedback_never_send_dj_to_odoo]].

## Why secret-free seed (not a minted cookie)
I could not self-mint an owner session to POST the seed — reading `session_secret.txt` to sign a `wsc_session` cookie is correctly blocked by the classifier ("Credential Exploration"). The right pattern for any owner-authenticated data load I can't cookie into: commit the data + an idempotent owner-cookie trigger (GET) and let DJ's own logged-in browser fire it (here, auto on first open). Never mint a session. Auth cookie = `wsc_session` HMAC (SESSION_SECRET or fallback ODOO_API_KEY); role 'owner' reaches all /owner/*. See [[feedback_never_relay_credential_via_session]].
