---
name: project-saunders-vault-notes
description: "Saunders Vault architecture, Evernote migration plan, and Notes app design decisions agreed 2026-05-27"
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

# Saunders Vault — Evernote Migration & Notes App

**Decided:** 2026-05-27

---

## VAULT LOCATION (Google Drive)

- **Saunders Vault root folder ID:** `1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q`
- **Unprocessed .enex files folder ID:** `1Y88XTkazutOCzNidf0_SWLD5Au3uAoU1` (50+ files, more pages)
- DJ has 5TB Google Drive — vault lives there, NOT in Odoo (Odoo can't handle volume)

## ALREADY PROCESSED (by CC, older session)

Two notebooks converted to folder-per-note + Note Content.txt + jpg attachments:
- **Accounting Stack** folder ID: `1cJT9RGvjIO6FTo7XR_Ymz_EoSXyLDy3u`
- **AI Agent Stack** folder ID: `1TdVppdvmFRE2oI595poDJEtNtwevb0lZ`

Structure CC used: `Notebook Name/ → Note Title/ → Note Content.txt + uuid.jpg files`

## AGREED PROCESSING FORMAT (going forward)

**Same folder-per-note structure, but Google Docs instead of .txt files.**

Each note becomes:
```
Vault Root/
  Notebook Name/         ← Drive folder (one per .enex file)
    YYYY-MM-DD Title/    ← Drive folder (one per note)
      Note Title         ← Google Doc (converted from ENML/HTML)
      attachment.jpg     ← image attachments uploaded separately
```

**Why Google Docs:** Editable, searchable natively in Drive, readable on mobile. .txt files are read-only archives.

## ENEX PROCESSING SCRIPT

**Written:** 2026-05-27
**Location:** `C:\Users\dj\Documents\Business\process_enex_to_gdrive.py`

Script reads local .enex files, parses ENML XML, creates Google Docs in Drive.

**Setup required before running:**
1. `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib lxml`
2. Download `credentials.json` from Google Cloud Console → OAuth 2.0 Client ID (Desktop App)
3. Place `credentials.json` in same folder as the script
4. Update `ENEX_DIR` in CONFIG block to point to local .enex file location
5. Run — browser will open for Google auth on first run, saves `token.pickle` after

**Note:** CC may have written an earlier version of this script but it was never found in GitHub or Drive. This is the current canonical version.

**ENEX files are on both:** Surface Pro (local) AND Google Drive (uploaded). Script reads local files.

## NEW NOTES APP (not yet built)

**Decision:** Notes are SEPARATE from follow-ups (would clutter the activities list).

**Architecture agreed:**
- New notes → Google Drive `Quick Notes/` folder (to be created in Vault root)
- Each note = Google Doc in Drive
- Optional customer link: Odoo partner_id stored in Doc metadata
- App page: `/owner/notes` with fast text entry at top, optional customer search, recent notes list below
- Voice input fits naturally here too

**Full flow when note is linked to a customer:**
1. User types note in Render app
2. Google Doc created in Drive (Quick Notes/)
3. AI (Claude) generates a summary of the note
4. Summary written into the Google Doc as first section, full note text below
5. Odoo chatter post on res.partner: summary text + link to Drive Doc
   Format: 📝 [summary sentence]. [View note ↗](drive link)

**Google Doc structure:**
```
── SUMMARY ──────────────────
[AI-generated 1-2 sentence summary]
─────────────────────────────
[full note text]
```

**Why this approach:**
- One source of truth (Drive)
- Odoo chatter shows summary + link — no duplication, no sync issues
- Works in both Render app and Odoo directly
- Summary makes notes scannable without opening the Doc

**Customer link on follow-up tasks:**
- `project.task` already has `partner_id` field — model supports it
- Currently the UI doesn't expose it when creating personal todos
- Fix = add customer search field to follow-up creation UI only (no storage change)

## WHAT'S NOT BUILT YET

1. The .enex processing script needs to be RUN (written, not executed)
2. `/owner/notes` page not built
3. Customer search field on follow-up creation not added
4. `Quick Notes/` folder in Google Drive not created yet

**Why:** to process .enex files → set up Google API credentials first (credentials.json from Google Cloud Console)

---

## CURRENT STATE (verified 2026-06-17) — most of the above IS now built
- **Vault is NOT empty.** Root `1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q` has **~28 top-level "Stack" folders** (Evernote-notebook mirror: Accounting, AI Agent, Business, Finances, Personal, Window & Solar Care, Kaiser, Medical, Real Estate, Auto, Travel, Tax Documents, Printing, Cheryl, Mom & Dad, Important, RV BuyWise, etc.) + **Quick Notes** + **Indeed**.
- **Notes app is LIVE** at `/owner/notes` (`routers/owner/notes.py` ~775 lines + `static/owner/notes.html`). Writes Google **Docs into `Quick Notes/`** (id `1m-rn3cmDcV3fG8ytkczj9nq73TL00z8K`). Auth = OAuth user creds — see [[project_notes_google_oauth]].
- **Notes features already built:** text notes, **photo notes** (camera+gallery, multi, AI OCR), paste-a-URL→article; **AI auto-summary**; **tags** (your tags-over-hierarchy decision — stored in Drive file `properties.tags_list`, AI auto-tags ≤3, pool/backfill/consolidate, tag filter + ✎ edit); **customer link** (Odoo partner → chatter post); note→to-do.
- **The "7–8 folders" = the 7 category subfolders inside Quick Notes**: Personal, Admin, Ideas & Projects, Finance, Saunders Printing, W&SC Operations, Customers. AI files each note into one. (Drive subfolders = source of truth; `_get_categories` seeds defaults if empty.)
- **Folder organizing UI ADDED 2026-06-17** (commits notes.py 650f6e98, notes.html 42e21f4a): pick folder at entry (or ✨ Auto-file by AI), **📁 New Folder** button (`POST /api/notes/category`), **folder filter** dropdown, **folder chip** on each card, and **move** between folders in the "Organize Note" modal (`PATCH /api/notes/{id}/move`). create + create_from_photo accept optional `category` override.
- **FILE UPLOAD ADDED 2026-06-17** (commits notes.py 24101b19, notes.html 75def271): **📎 button** uploads arbitrary attachments (PDF/Word/Excel/image/any) **stored as-is** into the selected Quick Notes folder via `POST /api/notes/upload_file` (multipart: file[1..N] + category + tags; 40MB total cap). `list_notes` query broadened from Docs-only to all non-folder files (adds `kind` doc|file + `mimeType`); cards show type icon (📄 pdf / 🖼️ image / 📃 word / 📊 sheet / 📎 other) and uploaded files support move+tags via the same Organize modal (share/to-do hidden for files since `/text` export only works on Docs). This is the procedure for "store downloaded Gmail attachments in the vault."
- **FOLDER-AS-NOTE + STAGED PICKER + DELETE 2026-06-17** (commits notes.py 1ef09f9a, notes.html 41d1ebc2): mobile multi-file picking is flaky, and DJ wanted "ONE note with N documents." Fix: 📎 now **stages** files (tap to add one at a time → `selectedFiles[]` strip, mobile-safe); on Save, if >1 file or a name was typed, `upload_file` gets `group_name` and bundles them into a **sub-folder = the note** (`Quick Notes/<category>/<group_name>/`). `list_notes` now also returns those sub-folders as **folder-note cards** (`kind:'folder'`, 📁 icon, document count, opens the Drive folder) and hides the files inside them. New **`POST /api/notes/{id}/delete`** (trash; folders trash contents too) → **🗑 button on every card** (the app had NO delete before). Stray test note 1_e9a4pb9… deleted via this endpoint (no auth needed on the POST). Single unnamed file still uploads loose.
- **Evernote import = STILL NOT RUN.** ~67 `.enex` notebook exports sit in unprocessed folder `1Y88XTkazutOCzNidf0_SWLD5Au3uAoU1` (some huge: Toyota Tacoma 147MB, Swamp Stuff 113MB, Siding Project, Kaiser Cards…). Only **2** notebooks ever imported (Accounting Stack, AI Agent Stack). Script `C:\Users\dj\Documents\Business\process_enex_to_gdrive.py` exists; needs creds + a run. **Next big task = run the import.**
- Documents-archive side (the ~28 Stacks) = the Evernote import target; Notes side (`Quick Notes/` + 7 categories + tags) = the live app. DJ confirmed he switched notes OFF Odoo → Google Drive (5TB).
