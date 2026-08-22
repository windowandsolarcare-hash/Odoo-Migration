---
name: project_vault_overhaul_spec
description: "Vault complete-overhaul spec (2026-07-26) — why Vault lost to Evernote (fragile editor, no snippets, scattered saves) + 6 workstreams. Read before ANY Vault/notes work."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-07-26T21:34:35.497Z
---

DJ (2026-07-26): Vault isn't strong enough to replace Evernote; wants a complete overhaul. Code review of live vault.py + v2_vault.html found 3 trust-killers: (1) editor = plain textarea whose save REPLACES the whole Google Doc body — destroys formatting, NO checkboxes (a DJ must-have); (2) search returns filename+date with NO matched-sentence snippet → feels random, 2 Drive calls = slow; (3) saves scatter — AI auto-files but Recents shows only Quick Notes stream, items vanish from view; Reference cards (Odoo) + pinned (Drive) duplicate the quick-facts job.

DJ's real Evernote usage = the spec: scanner default-saves PDFs to a watched "evernote" folder (Evernote desktop auto-uploads — replicate with a PC watcher → Vault); quick notes into a never-organized inbox (~3,000 notes — design FOR no-filing, don't fix it); Shortcuts = 5-second access to addresses/phones/bank+routing numbers; great search; checkbox lists inside notes.

DECISION 1 (root cause, pending DJ): move quick notes OFF Google-Docs-as-storage to a format we control (Drive keeps files/scans + OCR); unlocks safe saves, checkboxes, instant search, offline. Evernote archive stays as searchable basement.

Workstreams: V1 capture (PC watched folder + one-step quick note); V2 guilt-free inbox + ONE "everything I added" stream; V3 search with snippets + own instant note index; V4 solid editor w/ first-class checkboxes; V5 merge Reference+pinned into one offline pinned layer (sensitive cards wait for auth — [[project_render_app_no_auth_layer]]); V6 resurfacing brain (related old notes surface on new ones — the beat-Evernote feature, LAST).

Email-in already works (+vault@ → Email Documents folder; +task@ → My Day task) — DJ had forgotten; keep as-is.

PROGRESS — SLICE 1 LIVE 2026-07-26 (V2+V3 partial): `/owner/api/vault/recent` = unified "everything I added" stream (newest files ANY Vault folder; v2_vault Recents renders it when no filter active — filtered view unchanged; notes→editor, files→preview via openRecent). Search now returns `snippet` per content match: top-6 Google Docs get the actual sentence around the hit (4s time-budget, text/plain export), PDFs/images get "🔍 matches inside this scanned document". Verified on live data: recents spanned 3 folders; q=window → 120 results, 77 with snippets, real context shown. STILL TO DO: V1 (PC watched scan folder + one-step quick note), V3 rest (own instant index, offline recents, highlight term in snippet), V4 editor/storage (Decision 1 approved: own format), V5 pinned merge, V6 resurfacing.

**Why:** DJ said "I probably need to use it more" — wrong direction; the tool lost him at editor+search for legitimate reasons. Fix those and usage follows.
**How to apply:** any Vault/notes change should advance one of V1–V6, and V4 must not start before Decision 1 is made. Full spec: 3_Documentation/HUD_MASTER_SPEC.md §4. Parent strategy: [[project_hud_one_roof_spec]].
