---
name: project_shared_text_thread_component
description: "wsc_thread.js is THE shared text-thread component (Texts modal). Put text/reply actions HERE so they appear on every surface at once — DJ wants shared, not duplicated."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-19T14:09:57.713Z
---

**DJ standing rule (2026-08-19): text/reply actions must be SHARED, not duplicated — "when I add one, it gets distributed everywhere."** He'll add many.

**`static/owner/wsc_thread.js` = `WSCThread`** is the shared text-thread modal used by the field **job-detail "💬 Texts" button** (`openTexts`), Customer Brain, v2_customers, v2_command, v2_reeng_review, etc. It renders the bubbles (`renderBubbles` — the ONE bubble renderer), a reply textarea + Send (`/api/inbox/send`), a "✨ Suggest a reply" (`/api/inbox/suggest`), an "⚡ Actions" bottom-sheet menu (`openMenu(items)` — hosts pass their own item list; "adding an action is one line"), and now (2026-08-19, commit e3fd02d) a **✨ Claude Rewrite** button in the reply row → `rewriteMsg()` → **`/owner/api/ai/rewrite {text,instruction,c}`** (the SAME endpoint the inbox `rewriteReply` uses; backend in `followups.py`). Type a draft → prompt for how to change it → rewrites in place.

**So: any new text-reply feature goes in wsc_thread.js, not per-page.** The inbox (`v2_inbox.html`) currently keeps its OWN composer (its own reply box + rewrite + intent row: booking/confirm/postpone via `/api/inbox/intent` → WSCSendBox) — that predates full sharing and is a partial duplicate. NOT yet unified into WSCThread. Next step DJ floated: bring the inbox's reply actions (send booking link, confirm appointment, postpone, suggest reply) into `WSCThread.openMenu` so they're shared everywhere too — but those open the branded send box (WSCSendBox), which must be wired into the modal first. Awaiting DJ's go.

Related: [[feedback_reuse_canonical_endpoint]] (don't duplicate logic for a new entry point), [[feedback_call_opens_dialer_never_dials]].
