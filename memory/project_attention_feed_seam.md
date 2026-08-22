---
name: project_attention_feed_seam
description: "feed.py (attention-feed seam) is LIVE 2026-07-26 — submit_item/delete_item + /owner/api/feed/* verified in production. Specialists import from .feed, no stubs needed."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-07-26T18:12:21.950Z
---

`routers/owner/feed.py` shipped + registered in main.py (2-line add) 2026-07-26; deployed and smoke-tested end-to-end in production (submit valid/invalid, list+rank, snooze/unsnooze, done, include_done, delete — all passed, test data cleaned).

- Stable API for specialists: `from .feed import submit_item, delete_item` (contract: `3_Documentation/ATTENTION_FEED_CONTRACT.md` v1). HTTP mirrors: POST /owner/api/feed/submit, /delete, /ack; GET /owner/api/feed/list?include_done=1.
- Storage v0: ir.config_parameter `wsc.feed.items` JSON dict keyed by item id → {item, status, snooze_until, updated}. Internals may change; the two function signatures may not.
- Lifecycle (engine-owned): new → seen → approved/declined/done | snoozed (auto-returns to seen when due) | expired (auto on `expires`, silently dropped from list). Terminal + resubmit with different `created` = fresh occurrence → resets to new.
- Ranking v1 in list_items: urgency (interrupt→today→glance) then dollars desc then newest. Urgency is a REQUEST — delivery/push decisions belong to the priority engine (not built yet), never to specialists.
- Validation enforces contract: required fields, kind∈(attention,approval), approval needs draft{summary,body,on_approve{method,href}}, title ≤80 chars, action{label,href}.

**Why:** this is the agreed seam between the lead (HUD/inbox) lane and the goals-OS (specialists) lane — [[project_hud_one_roof_spec]]. Goals session builds specialists against the REAL module now, no local stub.
**How to apply:** specialists only submit/delete; never push notifications, never render UI, one item per subject, withdraw stale items. Next in lead lane: auth (Phase 2) which will gate /api/feed/ack + on_approve endpoints.

BRIEFINGS LIVE 2026-07-26: `routers/owner/briefing.py` + one scheduler entry in main.py (15-min `briefing_tick`, self-throttled via wsc.briefing.am/pm/attn params). Morning briefing fires once 6:30–9 AM PT, evening wrap once 7–10 PM PT (both push via myday's `_broadcast`/`_get_subs`, url → v2_hud); attention cards refresh hourly 6–21h. Derived cards: `myday:overdue` (count of slipped project-less to-dos) + `schedule:today` (jobs+$, expires 23:59 PT) — withdrawn at zero. Manual triggers: GET /owner/api/briefing/run?which=attn|am|pm|test. Verified in prod: attn refresh reported 22 overdue / 0 jobs (Sunday) and the feed showed BOTH lanes working — my myday:overdue card next to the goals-session's REAL `payroll:2026-07-20_2026-07-26` approval item, submitted through the contract on day one. Test push sent=1. NOTE: main.py is now an active two-agent file — ALWAYS fetch live before editing (caught specialist_payroll registration mid-flight; pushing a stale copy would have wiped it).

HUD FEED PAGE also live 2026-07-26: `static/owner/v2_hud.html` (new file) + launcher entry in v2_apps.js ("🛰️ HUD Feed", fav). Renders ranked cards (urgency stripe, NOW badge, Needs-your-OK badge, $), attention cards = Open/Done/⏰, approval cards expand to editable draft → Approve (calls on_approve w/ `edited_body` if edited, then acks approved — contract amended additively) / decline / snooze (1h / 6pm / tomorrow 7am). Deep link ?item=<id> opens a card. Draft bodies set via textarea .value, never innerHTML. Refreshes on pageshow/visibilitychange. VERIFIED: wscare.pro serves owner pages directly (https://wscare.pro/static/owner/v2_hud.html → 200) — the domain already covers the whole Render service. Two demo cards seeded (demo:welcome, demo:approval — approval's on_approve harmlessly GETs /api/feed/list); DJ clears them by using them.
