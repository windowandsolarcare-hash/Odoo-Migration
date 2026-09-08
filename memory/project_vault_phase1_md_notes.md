---
name: project_vault_phase1_md_notes
description: "Vault Rework PHASE 1 (SHIPPED 2026-09-08): quick NOTES moved OFF Google-Docs-as-storage to OUR format — a text/plain Drive file whose content is MARKDOWN, marked property wnote='md1'. Fixes the destructive save (atomic files().update media replace, lossless, Drive revisions) + adds first-class tappable checkboxes. Doc path 100% intact (existing ~3000 Google-Doc notes open unchanged, zero migration — that's Phase 4). notes.py _make_md + /md + /md_save; vault.py snippet branch; v2_vault.html hybrid view/raw editor. Detection keys on the wnote PROPERTY, not mimeType."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T21:25:57.428Z
---

**Built 2026-09-08 (DJ greenlit the rework; Lead approved the approach + 5 conditions). The heart of the Vault overhaul: kill the destructive save + no-checkboxes trust-killers ([[project_vault_overhaul_spec]] V4 + Decision 1).** Approach doc: `3_Documentation/VAULT_PHASE1_APPROACH.md` (app repo).

**Format (the root fix):** a quick note is now a **plain Drive file, mimeType `text/plain`, CONTENT = Markdown**, `properties {wnote:'md1', tags_list}`, in `Quick Notes/<category>/` (same place as before). Checkboxes = GFM `- [ ]` / `- [x]` (checked-state lives in the text). **Why text/plain not text/markdown:** Drive-guaranteed fullText-indexed; **format detection keys on the `wnote` property, NOT the mimeType** — so read/search never depend on an unproven type (Lead condition 3). Why Markdown not JSON/HTML: fullText-clean, portable/greppable (survives the app — DJ owns his data), lossless round-trip, trivial Phase-4 migration.

**Backend (notes.py + vault.py, additive — Doc path UNTOUCHED):**
- `_make_md()` (after `_make_doc`) — `files().create(media=MediaInMemoryUpload(md,'text/plain'), properties={wnote:'md1',…})`; reuses the proven upload mechanic (no Doc import).
- `create_note` branches: **pasted-URL article → rich Google Doc (unchanged)**; every other **typed/blank note → `_make_md`**. New notes default to md going forward.
- `GET /api/notes/{id}/md` — reads raw bytes via `get_media` (NOT `files().export`, which is Doc-only). `POST /api/notes/{id}/md_save` — **safe save = atomic `files().update` media replace** (Drive keeps native revisions = rollback). It is NOT the old destructive bug because Markdown IS full-fidelity content (the old `update_note` re-imported a *rich Doc* from a lossy textarea). Guard: **refuses empty-over-nonempty unless `allow_empty`** (409).
- `list_notes` classifies `wnote:'md1'` as **kind='note'** (else Doc→'doc', else 'file').
- `vault.py` search: `_fmt` adds `is_mdnote`; the snippet loop downloads md bytes (`get_media`) for the sentence-window, so md notes are found AND get real snippets (old Docs still use `files().export`). Grouping as 'note' is automatic (parent in the Quick Notes subtree).

**Frontend (v2_vault.html) — hybrid editor, CSP-safe, dependency-free:**
- **VIEW** renders the markdown (tiny hand-rolled `mdRender`: headings/bold/italic/bullets/links) large+high-contrast; **checkbox lines = real tappable rows** (`.mdck`) → tap flips `[ ]`↔`[x]` in-memory (optimistic, instant) + a **debounced (800ms) safe-save**. **EDIT (✎)** = the raw-markdown `<textarea>` → Save. Empty note opens straight into edit.
- **Condition 1 (XSS):** `_mdEsc()` escapes `< > &` BEFORE `_mdInline` formatting — pasted `<script>`/HTML renders as literal text, never executes. Links restricted to `http(s)`.
- **Condition 2 (fail-graceful, rule 13):** on save FAILURE (dead OAuth / no signal) the note is queued to `localStorage['wsc_md_pending']` keyed by id + shows "Not saved — will retry ⚠"; `flushPendingMdSaves()` retries on next load; `_orgMdFlush()` flushes a pending toggle on close. No silent loss.
- **Coexistence:** `openEditor` branches doc/md/file — existing **Google-Doc notes open in the CURRENT textarea + current `/update` save, UNCHANGED**. `noteRow`, `isNoteItem`, `openNoteEntry`, and `_createAndEdit` are all md-aware (kind='note' / is_mdnote route to the editor; a pasted-URL create stays kind='doc').

**Conditions 4 & 5 (tracked, not built here):** (4) the **~weekly-expiring user OAuth token** ([[project_vault_evernote_drive]] / project_notes_google_oauth) is the reliability ceiling for ALL Vault writes — elevated as a near-term MUST; condition 2 bridges until a durable refresh fix lands. (5) **offline-READ caching of md notes → Phase 2** (with the V3 own-index/offline-recents work), not a P1 bolt-on; P1's fail-graceful saves cover the write-side gap.

**Verify (Specialists-scope):** py_compile notes.py+vault.py; node-check v2_vault inline JS; backend deploy boot-clean LIVE; `/md` + `/md_save` registered (401 not 404). **Functional QC = Lead's (needs an owner cookie):** new note saves as text/plain md (not a Doc); checkbox tap persists across reload; pasted `<script>` renders as text; save-failure surfaces + recovers; an existing Doc note still opens/edits; search finds both. **Phases remaining:** P2 search redesign + offline-read · P3 Cheryl-share · P4 migrate the ~3000 Docs → md.
