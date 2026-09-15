---
name: project_portal_care_seam_part_b
description: "Portal Part B shipped 2026-09-14 (portal.py e511d9eb / portal.html 2a91eef7): paged history (/portal/api/history + done_count), Care + Before/After read from routers/care_store.py (Specialists', import-only, lazy), POST /portal/api/care/decide (token→ownership→option whitelist→idempotent 409), photos_sent approval gate inherited, pre-job placeholder. How to test it (real tokens need Render's BOOKING_TOKEN_SECRET — the picker is behind login now)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-09-15T01:45:41.651Z
---

**What shipped (Portal, 2026-09-14, contract = `3_Documentation/PORTAL_SEAM_CONTRACT.md`, Lead-blessed):**
- **History is paged in Odoo**, not sliced from `_jobs` (cap 80): `_done_domain(ids)` + `history_page(ids, offset, limit≤50)` + `done_count(ids)` (search_count). `/portal/api/me` carries page 1 (`HISTORY_PAGE=12`) + `history_total/history_more`; **`GET /portal/api/history?token&offset`** serves the rest; portal.html "Show earlier visits" appends. `visits` now = real Done count (a 28-visit customer used to read 28 only by luck of the 80 cap).
- **Care + Before/After** read via `routers.care_store` (**Specialists owns it — import only, never edit; NO hard delete by design — `close_item(item_id)`/`reopen_item(item_id)` added 2026-09-15 set status closed/open, portal hides closed**). Imported LAZILY (`_care_store()`) because `main.py` imports portal.py at boot — a hard import of a missing module = whole app down. Isolation lives in the store (`items_for_partner`/`beforeafter_for_partner` filter by partner_id); portal asks only for `account()['ids']`.
- **Approval gate inherited:** `approved_so_ids(so_ids)` = jobs with `wsc.job.photos_sent.<so>` count>0. Care item TEXT always shows; its photos and any Before/After pair only when the job is approved (written ≠ shown — DJ's explicit call). Photo links = `photo_url(so_id, att)` → existing `/owner/api/job/photo?so_id&att&sig` rail signed by `dashboard._photo_sig` (SESSION_SECRET); that endpoint also 403s attachments outside DJ's `_photo_selection`, so the page hides `<img>` on error.
- **`POST /portal/api/care/decide`** `{token,item_id,choice}` → `_account_for(token)` chokepoint (503 blip / 403 dead+DNC) → item must be found via `item_for_partner` for one of the token's ids (else **404**, never reveals existence) → choice must be in the item's own `options` (**400**) → already decided: same choice **200**, different **409** (returns current) → `set_customer_choice` (update-by-id). Verified live on all branches.
- **Pre-job = `'prejob': {'items': []}`** — structure only, page renders nothing while empty. DJ wants a conversation before specifics (Part B §6).
- Option copy: do_now "Yes, take care of it" · book_quote "Send me a quote" · next_time "Next visit is fine" · no_thanks "No thanks". Equal-weight outline buttons on purpose (Care, not upsell).

**Why:** the tech app writes care items/pairs; the portal is the customer's view + their one write. Lifecycle/price/gate questions were left to defaults documented in the contract (show-until-decided, quote-only, gate kept).

**How to apply / test:**
- Real portal tokens need the LIVE `BOOKING_TOKEN_SECRET` — the stub's default `'wsc-portal-2026'` mints 403s. Read it in-process from Render env (`GET api.render.com/v1/services/srv-d78le0fkijhs738dsli0/env-vars`, key in `C:\Users\dj\_render_key_val.txt`), export, then `portal_token(pid)`. Never print it. **The picker `/owner/api/portal/link` is behind the login gate now** (401 anon) — can't be used to grab links from curl or a logged-out browser.
- Test data: `care_store.add_care_item(partner_id=26339 "Fred Test", ...)` creates; cleanup = `close_item(id)` (soft; or `_get_list`/`_set_list` to drop test rows outright). Heavy-history customers: Nick Conway contact 22986 (28 Done), Blair Irene Becker contact **23046** (24; property 24169) — 23376 is a different Becker record with 6.
- Local harness `C:\Users\dj\portal_work\stub_test.py` loads real `care_store.py` + `PORTAL_FILE=<file>`; `odoo.py` there reads the rotated key from `new_odoo_key.txt.txt`.
- Related: [[project_customer_portal]], [[feedback_odoo_verify_content_not_status]], [[feedback_push_compare_and_swap]].
