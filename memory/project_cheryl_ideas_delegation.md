---
name: project_cheryl_ideas_delegation
description: "/cheryl/ideas delegation (routers/cheryl/ideas.py) serves the SHARED Dan<->Cheryl Idea Board inside Cheryl's silo — because authz._role_allowed walls cheryl-role to /cheryl/* ONLY, so /owner/ideas was a 401 DEAD DOOR for her. Mirrors cheryl/library.py: every route delegates to routers/owner/ideas.py; ideas.html self-detects IDEA_BASE from the path. /api/view/ideas + /api/ideas/me stay in cheryl/hud.py (don't double-register)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T16:11:35.820Z
---

**Built 2026-09-08 (Cheryl UX punch-list #4).** `authz._role_allowed(role,path)` returns, for `cheryl`, `path.startswith('/cheryl')` ONLY — so under AUTH_ENFORCE a cheryl-role session is **401'd on every /owner/* path**. The `/cheryl/` home Idea Board tile linked to `/owner/ideas`, so Cheryl literally could not open her own (shared) Idea Board — a 401 dead door. (Audit missed it walking AS the OWNER, who is allowed everywhere — hence the standing rule: **QC cheryl-facing routes with a cheryl cookie, never owner.**)

**Fix (mirrors [[project_cheryl_plan_views_sync]]'s sibling [[project_voice_tool_add_pattern]] /cheryl delegation + cheryl/library.py exactly):**
- **`routers/cheryl/ideas.py`** (new) — `router.add_api_route('/ideas', owner_ideas.ideas_page)` + a loop registering the FULL owner ideas API under /cheryl (list/add/respond/delete/board/propose/promote/proposal_dismiss/card_update/card_delete/card/card_msg/card_respond/card_suggest/hud/record/recording/session_audio/card_file[+/{att_id}]/card_file_delete/card_action/card_link/card_links/card_unlink), each DELEGATING to the `routers/owner/ideas.py` handler. Registered in main.py: `app.include_router(cheryl_ideas.router, prefix="/cheryl")`. **Delegate the FULL set** (not just the obvious calls) because ideas.html's `api(path,body)` helper hits `/api/ideas/<anything>` dynamically. **★ Do NOT register `/api/view/ideas` or `/api/ideas/me` here — cheryl/hud.py already registers them** (first-included wins; avoid the shadow).
- **`static/owner/ideas.html`** — added `var IDEA_BASE = location.pathname.indexOf('/cheryl/')===0 ? '/cheryl' : '/owner';` and rewrote all 18 hardcoded `/owner/api/ideas...` calls to `IDEA_BASE+'/api/ideas...'`, so at /cheryl/ideas the board calls /cheryl/api/ideas/* (cheryl-allowed) and at /owner/ideas it's byte-identical for DJ. Also `goHome()` is context-aware (→ /cheryl/ under /cheryl). Authorship still comes from the SESSION (session_actor), so a cheryl session authors as cheryl.
- **`static/cheryl/index.html`** — Idea Board tile now `href="/cheryl/ideas"`.

**Verification:** deploy went LIVE (a wrong handler name in the module-level `add_api_route` loop crashes boot at import, so live == all 26 handlers resolved + routes registered). The auth wall 401s ALL /cheryl/* before routing (even /cheryl/zzznope), so HTTP status can't distinguish a registered route from a 404 without a cookie — the boot is the registration proof. **The cheryl-COOKIE click-through (open board, add an idea, Back→/cheryl/) still needs a cheryl session to confirm HER path** — a Specialists session cannot mint one; that final QC is Lead's (as he did for /cheryl/library). See [[project_customer_edit_endpoint]] company-scope pattern + [[feedback_verify_limits_before_declaring]].
