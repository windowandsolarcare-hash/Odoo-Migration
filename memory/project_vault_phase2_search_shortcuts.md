---
name: project_vault_phase2_search_shortcuts
description: "Vault Rework PHASE 2 (SHIPPED 2026-09-08): (A) INSTANT client-side fact-search — new scopable GET /api/notes/index (metadata-only, count=87 live) → client ranks exact-title>prefix>substring>tag>desc, forgiving, + matched-term <mark> highlight; Drive fullText = async deep fallback below. (B) OFFLINE-READ — IndexedDB wscVault v2 'notes' store caches md text on read/save, offline fallback, recents sweep. (C) SHORTCUTS home — unified top-of-home layer (pinned notes + reference cards, DISPLAY-only), pin relabeled 'Shortcut', private-by-default (scope=shared drops pinned = P3 seam). Spec: 3_Documentation/VAULT_PHASE2_APPROACH.md."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T21:55:24.831Z
---

**Built 2026-09-08 (DJ greenlit; Lead approved approach + conditions, QC'd each checkpoint). Fixes the V3 "search felt random" + V5 "Reference+pinned duplicate" trust-killers ([[project_vault_overhaul_spec]]). Builds on [[project_vault_phase1_md_notes]]. Design anchor: DJ = FAST forgiving FACT lookup (addresses/phones/account #s — "type a few chars, get the fact").**

**Checkpoint A — INSTANT search (the headline win):**
- **`GET /api/notes/index`** (notes.py) — lightweight, SCOPABLE, paginated index of Quick Notes: `{id,name,description(snippet),category,tags,kind,pinned,modified}` + `count`, metadata ONLY (no content fetch). Live count = **87** (confirms the "~3000" is the ARCHIVE, NOT quick-notes — the client index is tiny/instant). Scopable: `category` filter works today; `scope` is the P3 seam.
- **Client instant fact-search** (v2_vault.html): loads the index on boot + caches to `localStorage['wsc_note_index']` (instant next-boot + offline). On keystroke → `rankNotes()` scores over the cached index — **exact-title > title-prefix > title-substring > tag > all-tokens > description** (weights in tunable `_RANK`); `_norm()` is case/punct-forgiving. Renders INSTANTLY (zero Drive round-trip); the Drive `fullText` deep search (`runSearch`) runs async BELOW, deduped, both with matched-term **`<mark>` highlight** (`hl()` — highlights only during search via `VIEW==='search'&&_hlQ`). Minor (a): `_indexUpsert`/`_indexRemove` on create/md_save/Doc-save/delete → a new note is findable with no reload.

**Checkpoint B — OFFLINE-READ:**
- Extended the existing **IndexedDB `wscVault` DB → v2** with a **`notes` store** (`idbPutNote`/`idbGetNote`). md-note text cached on every fresh `/md` read AND on `md_save` (minor b — never stale). openEditor md branch: if `/md` fails (no signal) → serve `idbGetNote` copy with an "Offline copy — reconnect to edit" note. `sweepCacheNotes()` (init +3.5s) pre-warms the top ~10 recent md notes (throttled 400ms, stops on error). Instant search already works offline from the localStorage index.

**Checkpoint C — SHORTCUTS home (the DJ-visible reframe; Lead OPTION A = unified concept, DISPLAY-only, no data migration):**
- DJ's word "Shortcuts" = the facts he references fast+often. ONE layer at the **TOP of home** merging the two former quick-fact systems: **pinned notes** (Drive `pinned` property) + **reference.py cards** — both DATA STORES KEPT AS-IS (display unification only, per Lead; a deeper cross-store merge would be its own approach-first piece).
- v2_vault.html: the standalone "📌 Pinned" + "📇 Quick Reference" sections merged into ONE **"📌 Shortcuts"** section above Recents (pin-list + ref-list under one header + "＋ Add" fact-card + "Filter shortcuts…"). Pin button relabeled **"Mark as shortcut"/"Remove shortcut"** (★ still reads/writes the SAME `pinned` Drive property — key NOT renamed, so no pin is orphaned). Reference sheet → "New/Edit shortcut". "Mark as shortcut" = the relabeled pin (additive).
- ★ **PRIVATE-BY-DEFAULT (P3 seam wired now):** `/api/notes/index?scope=shared` **drops pinned (shortcut) notes** — so when Phase 3 serves Cheryl the shared "Documents" view, DJ's personal facts (account #s/addresses = his shortcuts) never enter her index. Owner passes no scope → gets everything. This also ANSWERED Lead's DJ-search-pattern question (he searches for account info + addresses = his shortcuts).

**Verify (Specialists-scope):** py_compile notes.py; node-check v2_vault inline JS (×3 checkpoints); backend boot-clean live; `/api/notes/index` → 200 count=87, `?category=Personal`→17 scoped (P3 seam). **Functional/live-UI QC = Lead's (owner cookie) + the final Auditor user-walk.** Additive throughout — P1 md notes + the Doc path + existing pins/cards all intact. **P2 COMPLETE.** Remaining Vault phases: P3 Cheryl-shared "Documents" (uses the scope seam) · P4 migrate the ~3000 archive Docs → md.
