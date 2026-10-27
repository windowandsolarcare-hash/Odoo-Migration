---
name: project_customer_brain_dossier_index_vs_id_desync
description: "Customer Brain showed one customer's header/stats with ANOTHER customer's jobs — frontend index-vs-id async desync, not an Odoo data bug"
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T19:10:27.769Z
---

Discovered 2026-10-27 (DJ hit it live ~11:52 AM searching "Nan"): Customer Brain card showed **Nancy & Bob McDonald**'s header + correct stats ($690 · 8 visits), but the **Jobs** list under it was **Nancee Gauthier**'s SOs (003386, 001809, 000427, 000423).

**NOT a data bug.** Odoo is clean — verified by direct RPC: McDonald (contact 23943) owns property 26264 "194 Inkster Way" with his OWN 16 SOs (8 Done = the real "8 visits/$690"); Gauthier's SOs sit correctly under her own contact 23663 (props 25858 + 26288). No mis-parenting. `customer_jobs(23943)`→McDonald's 16; `customer_jobs(23663)`→Gauthier's 4-5. Backend + live==mirror, both correct per-id. The header/stats come from `custCard` (always the current `CUSTS[i]`), so they were right.

**Root cause (frontend — `static/owner/v2_customers.html`):** the dossier jobs are fetched async (`/owner/api/customer_jobs?partner_id=c.id`) and rendered into slot `doss-<i>` **by ARRAY INDEX**; `OPEN_I` is also an index. `doSearch` reassigns `CUSTS=d.results` on every new search **without resetting `OPEN_I`**, and `toggleDossier` had **no id-check after the `await`** (only `if(OPEN_I===i)`). So after a re-search or rapid tap, an earlier/in-flight `customer_jobs` response resolves against a now-reassigned `CUSTS` and paints one customer's `res.jobs` into a slot that now belongs to a DIFFERENT customer → current header + stale jobs. Intermittent by nature (needs an interleave), which is why a single clean search never reproduces it. Tell-tale: the 4 jobs were Gauthier's list MINUS her SO created that morning = a stale earlier response.

**Fix (staged branch `feat/custbrain-dossier-idguard`, commit 2cdee232bf, 4 surgical lines):** bind the async fetch/render to the partner **id**, not the index — `doSearch` sets `OPEN_I=null` on new results; `toggleDossier` captures `var cid=c.id` and both after the `await` and before the final `renderDossier` guards `OPEN_I===i && CUSTS[i] && CUSTS[i].id===cid` (drops a stale response whose slot no longer holds the same customer). Frontend-only, no route change.

**General rule:** any list UI that renders an async per-row detail (cards, HUD, dossiers) must key the response to a STABLE id and re-verify the row still holds that id before painting — never trust the array index across an `await`, because the backing array can be reassigned (re-search/refresh) mid-flight. See [[feedback_hud_cards_live_not_inbox]], [[feedback_nav_bug_is_the_consumer_not_the_string_source]].
