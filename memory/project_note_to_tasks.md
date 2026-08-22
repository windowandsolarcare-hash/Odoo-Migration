---
name: project_note_to_tasks
description: "Vault notes can spawn tasks: AI 'find action items' → pick → create N My Day tasks each linked to the note; '+ from selection'; tappable 'Tasks from this note' back-links. Actions section now expanded by default."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-24T23:03:59.702Z
---

**2026-07-24 (DJ: "collect my thoughts in a note, then create tasks from them; multiple tasks from one note is important").** Researched Amplenote/Evernote/Obsidian (all make tasks first-class INSIDE notes + a unified list, bidirectional). DJ's notes = Google Docs (Vault), tasks = Odoo `project.task` (My Day) — two systems — so we link instead of embed.

## Backend (routers/owner/notes.py)
- `POST /api/notes/extract_tasks {text}` → Haiku turns the note (often a rough IDEA) into concrete NEXT ACTIONS, returns `{tasks:[title,...]}`. Prompt is GENEROUS on purpose (breaks an idea into 3-6 steps); returns [] only for pure reference material. First prompt was too strict (returned [] for DJ's goal-setting note) — fixed to "derive next-actions from a thought."
- `POST /api/notes/create_todos {items,note_url,due_date,partner_id}` → creates a `project.task` per item, each description carries `<a href=note_url>View note in Drive</a>` (the Drive URL contains the note's file id → the link is the join key). Returns `{created:[{task_id,title}]}`.
- `GET /api/notes/task_list?note_id=<driveId>` → `project.task` where `description ilike <driveId>` → the note's tasks. No custom field/marker needed — reuses the Drive-id already in the note link.
- Existing single-task path `POST /api/notes/create_todo` (Haiku shortens title) unchanged; still used by "＋ Task (title)".

## Frontend (static/owner/v2_vault.html — note editor / org-more sheet)
- **Actions expanded by default**: `openEditor` now sets `$('org-more').open=true` (was `false` — DJ kept missing the To-do option).
- New in the "✅ Turn this note into tasks" block: `＋ Task (title)` (orgMakeTodo, existing), `＋ From selection` (orgTaskFromSelection — task from selected/current line of `#org-text`), `⚡ Find action items` (orgExtractTasks → checklist in `#org-task-list`, all checked) → `＋ Create N tasks` (orgCreateTasks → create_todos).
- **Back-links**: `renderNoteTasks(note)` (called on open + after any create) fetches task_list and renders "✅ Tasks from this note" — each a tappable `<a href=/static/owner/v2_myday.html?open=<task_id>>` (v2_myday already opens a task by id). Task→note link lives in the task description. Satisfies [[feedback_bidirectional_creation_links]].

## Note-from-Inputs opens the FULL editor (2026-07-24, commit c8c1a18)
DJ: making a note from Inputs dropped him in the slim home composer; to assign tasks he had to save + reopen. Tasks need the note's Drive URL (only exists after save), so the fix: v2_vault `?compose=<text>` now `_composeToEditor()` — POSTs `/api/notes/create` immediately, injects the returned `{doc_id,doc_url,title,category,tags}` into `_noteById`/`_allNotes`, and `openEditor(doc_id)` → lands in the FULL editor (org sheet, actions expanded, task tools ready). Fallback on failure: prefill `#cap-text`. Trade-off: a note is created on arrival (auto-filed, AI title) — DJ can edit title/text/delete in the editor. `create_note` returns `doc_id` = the Drive file id = the id openEditor/_noteById use.

## Pin + unchecked (2026-07-24, commits a13af63/474ff77)
Extract checklist boxes now UNCHECKED by default (DJ picks); each row has a 📌 pin toggle → `create_todos` accepts `items:[{title,pin}]` and sets `x_myday_pinned=True` (pin to top of My Day). "＋ From selection" = task from highlighted text / current line of `#org-text`.

## Also this session
v2_inputs.html capture box: single-line `<input>` → auto-growing `<textarea>` (min 58px, max 260px ≈ 10 lines then scroll); `autoGrow()` on input; Ctrl/Cmd+Enter submits, plain Enter = newline (commit 7973eb4).

Commits: notes.py 6a6e0a6 + 4cfbdcb (prompt), v2_vault c92a655, v2_inputs 7973eb4.
