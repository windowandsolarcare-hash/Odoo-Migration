---
name: project_journal_feature
description: "Journal feature (v2_journal.html + journal.py): dated entries with guided AM/PM prompts, on-this-day memories, streak. Entries are Google Docs in the Vault's 'Journal' folder; editor reuses /api/notes text+update. Built 2026-07-25."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T09:02:26.723Z
---

**2026-07-25 — DJ's "journal to record things" idea (a line in his 'Things to program' note).** He asked to research the best journaling apps first, then replicate. Chose v1 = **guided AM/PM prompts + on-this-day memories + streak** (NO mood).

**Research takeaways (Day One / Journey / Stoic / Reflectly / Five Minute Journal):** guided prompts beat the blank page (biggest differentiator); morning/evening rhythm (Five Minute Journal); mood check; timeline/calendar + streak; "on this day" memories (Day One's most-loved); photos; AI reflection (v2 later).

**Build — reuses the Vault/notes Drive stack (no new store, no custom model):**
- `routers/owner/journal.py` (registered in main.py `owner_journal`): entries = Google Docs in a **"Journal" folder under `VAULT_ROOT_ID`** (`_find_or_create_folder`), titled `YYYY-MM-DD — Journal`. Imports `_drive_service`, `_find_or_create_folder`, `_make_doc`, `VAULT_ROOT_ID` from `.notes`.
  - `GET /api/journal/list` → `{entries[], streak, today_iso, has_today, on_this_day[]}`. Parses ISO date from the title; streak = consecutive days back from today (today-unwritten doesn't break it); on_this_day = same MM-DD, earlier years.
  - `POST /api/journal/today` → **get-or-create** today's entry (idempotent, one/day); new entries pre-fill the guided prompt template (`_prompt_html`). Returns `{id, url, created}`.
- `static/owner/v2_journal.html` (launcher fav 📔): streak card, "Write/Continue today's entry" button, On-this-day strip, month-grouped timeline. Entry editor is a self-contained full-screen textarea that **loads via `GET /api/notes/{id}/text` and saves via `PATCH /api/notes/{id}/update`** (same endpoints the Vault editor uses) — autosaves on pause + blur. Docs↗ opens the Drive doc.

**Verified live:** folder auto-created; POST /today made a doc with the AM/PM prompts; 2nd call returned created:false (same id); list showed it with streak=1. Commits: journal.py 845c0bd, v2_journal.html bdd8efc, main.py 17ac6a9, v2_apps.js cf89d6b.

**Bug fixed 2026-07-25 (commit 13cc4e7): tapping Today = blank screen, couldn't type.** `#view-entry{display:none}` in CSS, but `openEntry` revealed it with `style.display=''` — which REMOVES the inline style and falls back to the CSS `display:none`, so the entry editor never showed (both views hidden = blank). Fix: `style.display='block'`. **Reusable gotcha:** to show an element that has `display:none` in a stylesheet, set an explicit value (`'block'`/`'flex'`), NOT `''` — empty string reverts to the CSS rule.

**Not in v1 (offered/future):** mood tracking, photos on entries, AI "reflect on my week/patterns". Note: DJ also has separate legacy Drive folders "JOURNAL" (id 1QjIUL9…) and "Journals" (id 1YhFpf…) OUTSIDE the Vault — this feature uses its OWN Vault-managed "Journal" folder, not those.
