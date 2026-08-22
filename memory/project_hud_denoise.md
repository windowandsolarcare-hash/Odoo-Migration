---
name: project_hud_denoise
description: "HUD too noisy (DJ 2026-08-07): rocket-FAB badge showed 70 = SUM of every inner item.badge across cards, not a card count; and customer texts appeared in multiple places (19 inbox_ai HUD cards + Follow-ups). DJ-approved fixes: badge = COUNT OF CARDS (~8), customer texts live in the INBOX only (one capture), clear-once-clears-everywhere. Speced to specialist (feed.py/inbox_ai/HUD)."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-08T00:12:01.470Z
---

**DJ live 2026-08-07:** rocket-FAB badge = **70**, same customers in 2+ places, too much noise.

## Diagnosis
- **Badge (70):** `fabBadge()` (v2_apps.js) reads `/owner/api/feed/badge` (feed.py) = **SUM of `item.badge` across all live feed cards** (My Day 34 + inbox ~20 + billing 7 + reschedule 6 + 19 inbox_ai + …). So it counts the ITEMS INSIDE cards, not the cards. Cards=folders, tasks/items=papers; it was counting papers.
- **Duplication:** customer replies/reschedules show as **19 individual `inbox_ai:*` HUD cards** AND on the **Follow-ups** screen (source `outreach`, "16 need you"). Feed had 29 cards / status new:13 seen:16; by source: inbox_ai 19, billing 2, reschedule 1, reminders 1, myday 1, journal 1, authz 1, outreach 1, maint_advance 1, library 1.

## DJ-APPROVED fixes (speced to specialist — feed.py/inbox_ai/HUD_BADGES their domain)
1. **Badge = count of CARDS** (ideally only `status=='new'`/unseen), NOT the sum of inner item.badge → ~8, honest. Keep each card's own inner badge (My Day card still shows "34"); only the FAB total changes.
2. **One capture per customer text = the INBOX** (DJ's call). Don't fan out 19 individual inbox_ai HUD cards — roll into ONE "Inbox — N need you" HUD card. Follow-ups stays for the post-visit "did we hear back" flow (distinct population).
3. **Clear once → clears everywhere** (resolve on any surface removes all copies).

Net: HUD shows a SMALL set of distinct "needs me" items, each ONCE, honest badge. See [[project_hud_feed_ordering]] [[project_inbox_intent_buttons]].
