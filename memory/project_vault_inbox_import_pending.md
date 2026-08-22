---
name: project_vault_inbox_import_pending
description: "COMPLETE 2026-07-06 — Evernote 'Inbox' (3.3GB/2617 notes) fully imported into the Saunders Vault 'Inbox' folder, 0 errors."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# ✅ COMPLETE 2026-07-06 — all 2617 Inbox notes imported, 0 errors
DJ finished the run from his own PowerShell (Claude's `run_in_background` bash jobs kept getting killed; his own terminal ran uninterrupted). Final: **2617/2617 notes**, Vault Inbox folder `1cOXC2iynwJwxYunRn9rj6WjBgQS1SdQ3` now holds ~**1725 Docs + 3237 files + 1200 subfolders** (text-only→Doc; attachment-notes→subfolder w/ original files). 
★ 1 note errored ("Google speed test results - WASC") on `UnicodeEncodeError: 'ascii' codec` — root cause = googleapiclient's NON-resumable multipart flattener (`email.generator`) encodes the media body as ASCII and dies on non-ASCII **text/multipart** content (this note's attachment was a `multipart/related` web-clip). FIX = make uploads **resumable** (`MediaIoBaseUpload(BytesIO(...), resumable=True)`) in `import_inbox.py` upload_bytes + upload_doc (resumable uses chunked PUT, not the ASCII multipart path). Re-ran → caught it, 0 errors. ★ REUSABLE LESSON for any Drive upload: use resumable uploads for text/HTML/multipart content, or non-ASCII bodies blow up the non-resumable path. Importer + token.json live in `C:\Users\dj\vault_inbox_import\`.

# (historical) Evernote Inbox → Vault: not imported yet, pending (2026-07-04)

**Verified via Drive search:** the Evernote **"Inbox" notebook was never imported** into the Saunders Vault. No "Inbox" folder exists in the Vault. (The only 2 "Inbox" folders anywhere in DJ's Drive are OLD 2022 fax-scanner subfolders under "Fax" — unrelated.)

## Vault structure facts (confirmed 2026-07-04)
- Saunders Vault root folder = **`1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q`** on consumer acct **windowandsolarcare@gmail.com**.
- The original 67-notebook import organized notebooks as folders grouped under top-level **"… Stack"** folders (Accounting Stack, Personal Stack, Window and Solar Care Stack, Finances Stack, Medical Stuff Stack, Cheryl Stack, Old Notebooks Stack, etc.) + many individual note-folders + **"Quick Notes"** (the in-app capture folder, owned by service acct `render-drive@gen-lang-client-0790905441.iam.gserviceaccount.com`).
- The `mcp__claude_ai_Google_Drive` MCP is authenticated to this account (search/create_file/get_metadata work).

## The pending Inbox import
- File: `C:\Users\dj\Downloads\Inbox.enex` — **3.3 GB**, **2,617 notes** (1,417 text-only, 1,200 with attachments), **3,421 attachments**, one single note is **280 MB** (likely a video). Basically a second full import, bigger than the first (646).
- Target: DJ wants it as a **new top-level "Inbox" folder** in the Vault.
- ★ Too big for MCP/chat import (the 280MB note + 3.3GB of base64 attachments would choke the tool layer, and 2,617 notes = too many calls). Must run as a **LOCAL streaming importer** (lxml `iterparse` huge_tree) uploading via the Google Drive API — same method as the original import (see [[project_vault_evernote_drive]] for importer design: per-notebook try/except, idempotent, build_shell_index listing not name-query).
## BUILT + VALIDATED 2026-07-04 — only blocker left is DJ's one-time sign-in
Working dir **`C:\Users\dj\vault_inbox_import\`**:
- `mint_vault_token.py` — DJ runs ONCE interactively (browser → sign in windowandsolarcare@gmail.com → Allow). Uses the local `~/Downloads/client_secret_*.json` (NOT Render — the mcp.json scrape is blocked by the auto-mode credential classifier). Saves `token.json` next to it (nothing pasted in chat).
- `import_inbox.py` — streaming importer: lxml `iterparse(tag='note', huge_tree, recover, strip_cdata=False)` one note at a time (flat memory); resumable via `ledger.json` (set of done note-seq; save every 10); idempotent (find_child by name before create/upload); resumable chunked upload for attachments >5MB; retry/backoff on 403/429/5xx. Reads `token.json`, auto-refreshes + rewrites it. Structure = **text-only note → Google Doc in the Inbox folder; note with attachments → subfolder `{seq:05d} · {title}` holding original files (+ a Doc of the text if any)`. ENML `<content>` cleaned (strip xml/doctype/en-note/en-media) → uploaded as text/html → Doc.
- **Dry-parse against the real file CONFIRMED (no upload):** 2617 notes (1417 text-only / 1200 w/ attachments), full stream in 16s, parser extracts title/content/resource(mime,file-name,data) correctly. Mime mix: jpeg 1535, png 625, pdf 423, svg 365, webp 168, etc. Biggest attachments: note 1460 `Screen_Recording_..Workiz.mp4` 143MB-b64 (~107MB), note 2498 Temecula pics/videos ~270MB-b64 across 4 files (this is memory's "280MB note"). All covered by the resumable path.

## RUN IN PROGRESS — paused at 730/2617, DJ to finish from his own terminal
- Sign-in DONE 2026-07-04: `token.json` saved in the working dir (full drive scope + refresh token; signed in windowandsolarcare@gmail.com, 5.1TB free). Inbox folder CREATED in Vault = **`1cOXC2iynwJwxYunRn9rj6WjBgQS1SdQ3`**.
- Import ran and reached **730 of 2617 notes, 0 errors** (all in that Inbox folder). Ledger `C:\Users\dj\vault_inbox_import\ledger.json` holds the 730 done + the inbox_id.
- ★ **Claude's `run_in_background` bash jobs KEEP GETTING KILLED within seconds/minutes** (session lifecycle) — resumes fine each time but never finishes this way. STOP relaunching in background; it's pure churn.
- ★ **THE FIX = DJ runs it in his OWN terminal** (survives independent of Claude's session): open PowerShell →
  `python C:/Users/dj/vault_inbox_import/import_inbox.py`
  Leave it open ~1hr. It skips the 730 done, processes the remaining ~1887, prints "DONE". Fully resumable/idempotent (re-run same cmd if it stops; no dupes). DJ said (2026-07-05) he'll do this when he gets home.
- WHEN DONE: Claude to verify final counts (expect ~2617 notes → text→Docs + attachment-notes as subfolders w/ original files) and confirm the whole Inbox notebook landed in the Vault Inbox folder.

Scope confirmed: new top-level "Inbox" folder, text→Docs + attachments kept as original files, include the big video (biggest ~270MB across 4 files on note 2498). Client secret on disk = `~/Downloads/client_secret_786167717152-...json`; token at `C:\Users\dj\vault_inbox_import\token.json`. See [[project_vault_evernote_drive]].
