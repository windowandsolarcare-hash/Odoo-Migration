---
name: project_review_request_picklist
description: "Review-request pick-list + draft queue (reviews program): routers/owner/review_requests.py + v2_review_requests.html — DJ picks past customers, queues a §9 review-ask draft he sends himself; GOOGLE_REVIEW_LINK + REVIEW_TEMPLATE are swap-in slots."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T10:13:06.162Z
---

**STAGED 2026-10-10 (branch specialists/review-picklist; held for Lead QC → DJ deploy). DJ-approved full build.** Part of the reviews / service-recovery program (replaces the old gated funnel). SEND is HARD-GATED on DJ's GBP "Get verified" — nothing can go to a customer until that + approved wording land.

**Files:** `routers/owner/review_requests.py` (NEW) + `static/owner/v2_review_requests.html` (NEW) + feed_live.py (live HUD producer) + main.py (register, prefix /owner).

**Flow:** DJ hand-picks a past customer → QUEUE builds a review-ask draft → opens the inbox PRE-FILLED (`/static/owner/v2_inbox.html?open=<pid>&draft=<text>` — the proven §9 path) → DJ reviews/edits/**sends himself**. The module NEVER sends. ONE message, BOTH links UNCONDITIONAL (Google review + `/feedback`), name-personalized only — NO rating gate, NO happy→public/unhappy→private branching (compliance north star).

**Routes (namespaced /owner/api/reviews/*, owner-gated):** `GET /owner/reviews` (page); `GET …/candidates?q=` (pickable customers — reuses the reactivation domain: `x_studio_activelead=='Active'` ⇒ STOP/DNC excluded, has window/solar service, not Dan/WSC, shared `analytics.setaside` excluded; newest-served first; minus asked-in-cooldown or queued-today); `POST …/queue {partner_id}` (gates: re-check Active, ~10/day cap `DAILY_CAP=10`, 365-day per-customer cooldown; returns the §9 draft_url); `GET …/queued` (today's ready list, live); `POST …/unqueue {partner_id}` (remove + clear cooldown). `ready_cards()` = live DJ HUD card "📣 N review requests ready to send" (self-hides at 0), registered in `feed_live.LIVE_PRODUCERS` via `_review_requests_ready` (lazy import).

**State:** `ir.config_parameter` blobs (low-write ≤10/day, like the thumbtack flow): `wsc.review.asked` {str(pid):'YYYY-MM-DD'} (cooldown + daily cap) + `wsc.review.queued` [{pid,name,phone,date,status}] (today's list; auto-prunes >2 days). NO new Odoo field, NO schema.

**SWAP-IN slots (one-line edits when Lead routes them):** `GOOGLE_REVIEW_LINK=''` → the real g.page/r/… from Web after GBP verify (while empty, draft shows `[Google review link — pending setup]` + the page shows a warning banner); `REVIEW_TEMPLATE` → Operator's approved final wording (placeholder now).

**⚠ feed_live cross-branch:** this branch + specialists/dj-assigned-provenance both edit feed_live.py in non-overlapping regions — the 2nd to merge re-applies onto fresh main (stale-base, [[feedback_staged_mirror_stale_base_refetch]]).

See [[feedback_no_inventing_customer_lines_hud_confirm]], [[feedback_no_ai_offered_dates_use_link]], [[feedback_hud_cards_live_not_inbox]], [[project_candidate_comparison_entrypoints]], [[feedback_reuse_canonical_endpoint]].
