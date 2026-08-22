---
name: project_vault_note_full_editor_upfront
description: "Writing a NOTE in the Vault's 'Add to the Vault' box now lands in the FULL editor (create + openEditor), not the slim quick-save. DJ wants the detailed editor up front for notes. Photos/files still quick-save."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T09:14:28.643Z
---

**2026-07-25 (DJ: the initial Vault add editor is scaled-back; I want it as detailed as the editor I use when editing a note).**

`v2_vault.html` `saveCapture()` — the text-only branch (no staged photos/files) used to `notes/create` then quick-save + toast. Now, on a successful create (`d.doc_id`), it builds the note object, resets the composer, and calls **`openEditor(n.id)`** + returns — landing DJ in the same FULL note editor he gets when editing an existing note (with "⚡ Find action items", checklist, task creation, formatting). Photos (`create_from_photo`) and files (`upload_file`) are UNCHANGED — they keep the fast quick-save (no full editor needed).

This mirrors the earlier Inputs→note `_composeToEditor(text)` flow (?compose=, 2026-07-24) — now the Vault's OWN composer behaves the same. Commit f1bae77.

**UPDATE 2026-07-25 — small box fully RETIRED (DJ: "retire the smaller one across all apps; in the vault I want to start in the detailed box, not the small box"):**
- v2_vault.html composer: the `cap-text` textarea is GONE. Replaced with a `.newnote-btn` "✍️ Write a note" that calls `newNote()` → `_createAndEdit('', title, folder)` → creates the note and opens the FULL editor directly. The card now = [Write a note button] + "or save a photo/file/link" + title(for files) + attach buttons + Save. `saveCapture()` is photos/files ONLY (text branch removed; guard toasts "attach a photo/file or tap Write a note").
- **Compose flash fixed:** `_createAndEdit` opens the editor sheet (`org-bg`) IMMEDIATELY with a "Creating note…" state BEFORE the async create, so the composer never flashes. The `?compose` init check now runs FIRST (before `loadHome()`), so arriving from Inputs opens the editor before the home renders. `_composeToEditor(text)=_createAndEdit(text,'','')`. Commit 5b27e3d.

**BUGFIX 2026-07-25 (DJ: "Write a note" opened a broken editor with errors):** the "detailed sophisticated editor" DJ wants IS `openEditor` (the `#org-bg` sheet) — it has the **"⚡ Find action items in this note"** button (`orgExtractTasks`, make-tasks-from-notes) he specifically named. My new-note path was right, but `notes.py create_note` returned **400 "Note text is required"** for an empty note → the create failed and the editor errored. FIX (notes.py b9970fb): allow a BLANK note (removed the 400; skip `_analyze_note` when text is empty → title falls back to "Note"). Now "Write a note" creates an empty doc → `openEditor` opens the full editor for it.
- Inputs "Note / doc" pill now also opens that editor: the fallback `fb-doc` chip → `v2_vault.html?compose=` (empty) instead of the Vault home (v2_inputs 54f30a7). The classification alt already used `?compose=<text>`.
- Litter guard (v2_vault 7c69e77): a brand-new blank note auto-deletes on close if nothing was typed (`_blankNewId` set only when created empty; cleared on save / on opening any existing note; `closeOrganize` deletes it when `org-text` is empty). The detailed editor still saves on the **Save button** (no autosave) — so typed-but-unsaved text is lost on close, same as editing existing notes.

**Also 2026-07-25 — "Plan my day" retired from Inputs** (myday.py `/api/capture`, commit e3d450d): removed the `plan` type from the Claude prompt, the `_mk` plan branch, BOTH alts lists (winner-excluded + unclear-fallback), and the primary `if typ=='plan'` handler. Verified: capture alts now = Task / Customer note / Note-doc / Find only. (The v2_inputs fallback-picker plan chip was removed earlier.)
