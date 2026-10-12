---
name: project_cancel_so_only_if_draft
description: "api_cancel_so(so_id, only_if_draft=False) — opt-in QUERY flag. Catch-up per-row Cancel passes only_if_draft=1 so the server re-reads state and refuses ({ok:false,now_confirmed:true}) if the SO raced to confirmed. Default-off keeps v2_calendar's cancel of confirmed jobs unchanged. Deployed 2026-10-11."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T03:00:07.590Z
---

**DEPLOYED 2026-10-11 to main (DJ "Deploy now" §12 picker; Lead QC-GREEN). Branch specialists/catchup-cancel-draftguard @ 1974cc56. Closes Audit's migration-cleanup Part-1 finding.**

**Problem:** the Catch-up per-row Cancel (`wsc_catchup.js` `sCancel`) called bare `/api/cancel_so/{id}` (`dashboard.py` `api_cancel_so`, LIVE copy ~:10010) with NO state re-check — a draft that raced to CONFIRMED before DJ tapped would get cancelled anyway, and the Undo only restores to draft.

**Fix (surgical, opt-in — do NOT blanket-guard cancel_so):** `cancel_so` has TWO live callers — catchup AND `v2_calendar.html:963` (which legitimately cancels CONFIRMED jobs). So added an **opt-in query flag**: `api_cancel_so(so_id: int, only_if_draft: bool = False)`. When `only_if_draft` is set, the server **re-reads state itself** (`odoo read ['state']`, never trusts the client) and if `!= 'draft'` returns `{ok:False, now_confirmed:True, state:...}` WITHOUT cancelling. Default-off → `v2_calendar` is byte-identical (still cancels confirmed). `wsc_catchup.js` sCancel now hits `?only_if_draft=1` and on `now_confirmed` tells DJ "just confirmed — it's on the schedule, open it" instead of cancelling.

**Undo correct by construction:** because the catchup path can ONLY cancel a draft, its Undo (`sRestore` → `residue_restore` → `action_draft`, guarded to state='cancel') always restores the correct pre-cancel state = draft. No draft/confirmed mismatch possible.

**KNOWN tiny polish (deferred, SAFE):** a vanished/deleted SO hits `st=None != 'draft'` → `now_confirmed:True` with slightly-off copy (says "confirmed" when it's actually gone) — nothing is cancelled, so harmless; generic-copy tweak is a later follow-up. ENDPOINT_MAP description refreshed via a new docstring on cancel_so (no route change). See [[project_stale_draft_cleanup]], [[feedback_architect_server_revalidate_bulk_mutations]], [[feedback_odoo_rpc_write_pattern]].
