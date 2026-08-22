---
name: project_notes_google_oauth
description: "Notes app (Saunders Vault on Google Drive) auth = OAuth USER creds (GOOGLE_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN). Token dies every ~7 days if the OAuth app is in Testing mode → ALL notes 500. Service account can't create Docs (quota). Fix = renew token + publish app to Production."
metadata:
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**2026-06-11 incident:** Saving a note (text OR photo) failed with "Internal Server Error" → frontend showed "Unexpected token 'I', "Internal S"... is not valid JSON".

## Root cause
`routers/owner/notes.py` `_drive_service()` authenticates to Google Drive with **OAuth USER credentials**: env vars `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN`. The **refresh token expired** → `creds.refresh(Request())` (notes.py ~line 41) raised a `google.auth` RefreshError. The handlers only caught `RuntimeError`, so it escaped as a raw 500 (plain text "Internal Server Error"), breaking the frontend's `JSON.parse`.
- **Whole Notes app depends on this** — every endpoint calls `_drive_service()`. When the token dies, ALL notes (list/search/create/photo) 500, not just photos.
- **Why it expires:** Google OAuth apps in **"Testing"** publishing status issue refresh tokens that **die after 7 days**. Notes set up ~Jun 3 → broke ~Jun 11. **Permanent fix: publish the OAuth consent screen to "In production"** in Google Cloud Console.

## Fix shipped 2026-06-11 (graceful only)
`_drive_service()` now wraps `creds.refresh()` in try/except and re-raises as `RuntimeError("Google Drive needs reconnecting…")` so every endpoint returns a clean 503 JSON instead of a raw 500. **This does NOT restore notes** — it just makes the failure legible. Real fix still needs a new refresh token.

## Service account does NOT work for Notes (tested 2026-06-11)
Vault = `1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q` "Saunders Vault", a **My-Drive folder** (driveId=None) shared with the render-drive SA (`render-drive@gen-lang-client-0790905441.iam.gserviceaccount.com`, key at `C:/Users/dj/Documents/Business/render-drive-service-account.json`). The SA **can create FOLDERS** in it but **cannot create Google DOCS** → `403 storageQuotaExceeded` ("The user's Drive storage quota has been exceeded"). Service accounts have 0 My-Drive quota; native Docs still need a quota-bearing user. So Notes MUST use OAuth user creds (or move the Vault to a Workspace Shared Drive, or re-platform notes onto Odoo).

## RESOLVED 2026-06-11 (token renewed)
Re-auth'd via local script `C:/Users/dj/mint_google_token.py` (pulls client id/secret from Render, runs `InstalledAppFlow.run_local_server`, prints new refresh token — DJ ran it, clicked Allow). New token validated against Google, written to Render via **single-var PUT** `PUT /v1/services/{id}/env-vars/GOOGLE_OAUTH_REFRESH_TOKEN` (safe, no wipe). **Env-var write did NOT auto-redeploy** — had to POST `/v1/services/{id}/deploys` to load it. Notes confirmed working.
- **Render env-var values ARE readable** via REST `GET /v1/services/{id}/env-vars` (MCP `get_service` hides them; the raw API returns values). Render API key = `rnd_…` in `~/.claude/mcp.json`.
- **RESOLVED — app is already "In production"** (verified 2026-06-11 via Google Auth Platform → Audience → Publishing status = "In production", User type External, 1/100 user cap). The OLD token died because it was minted while the app was still in Testing (~Jun 3 → 7-day expiry). The NEW token was minted while In production, so it should NOT expire on the testing clock. Nothing more to do. (Project = gen-lang-client-0790905441; in the new "Google Auth Platform" UI the publish status lives under **Audience**, not "OAuth consent screen".) OAuth client is Desktop type (localhost redirect worked first try).

## 2026-06-19 — TOKEN DIED AGAIN (~8 days after the 6/11 renewal) — publish fix did NOT hold
The OAuth refresh token expired/revoked again on/before 2026-06-19, ~8 days after the 6/11 re-mint — i.e. the classic 7-day Testing-mode clock, despite the 6/11 note claiming the app was "In production." So either the consent screen is NOT actually published (verify in Google Auth Platform → Audience for project gen-lang-client-0790905441), or printing/drive_filer uses a different OAuth client. **Re-minting only buys ~a week; genuinely publishing the app is the permanent fix — re-verify the publish status.**
- **Printing/Drive filing depends on the SAME `GOOGLE_OAUTH_REFRESH_TOKEN`** (`routers/printing/drive_filer.py`, OAuth user creds). When it dies, BOTH Notes AND printing Drive-filing (PO/invoice/NBHOF-email) go down. Symptom seen: `POST /printing/api/jobs/{id}/file-to-drive` → `{"ok":false,"message":"RefreshError: invalid_grant: Token has been expired or revoked."}`.
- **PENDING (DJ doing it at home):** re-mint via `C:/Users/dj/mint_google_token.py` (prints `1//…`), then update ONLY `GOOGLE_OAUTH_REFRESH_TOKEN` (single-var, no wipe) + redeploy. THEN: re-file the **Dawson** posted invoice (`POST /printing/api/jobs/po-043859/file-to-drive`) — its Drive "final" is STILL the DRAFT (file "Invoice 200238.pdf" reads "Draft Invoice 200238", dated 06/13, modified 6/14; the 6/19 send's Drive re-file silently failed on the dead token). Verify the overwrite lands (file should read "Invoice 200238", modified today).
- **SILENT-FAILURE TODO:** `jobs.py send_invoice` swallows the Drive re-file error (`try/except pass`) → DJ got a draft as his "final" with no warning. Make it surface the failure (notify DJ / return a warning in the send response) so a dead token can't silently leave a draft as the filed final. (Not yet built — DJ aware.)

## 2026-06-22 — re-minted AGAIN (died ~3 days after the 6/19 renewal)
Token dead again. Re-auth'd the same way and it's working: **recreated `C:\Users\dj\mint_google_token.py`** (it had been deleted) — self-contained: scrubs its own dir from sys.path (dodges the local calendar.py stdlib-shadow), reads CLIENT_ID/SECRET from Render `GET /v1/services/srv-d78le0fkijhs738dsli0/env-vars`, runs `InstalledAppFlow.from_client_config({installed…, redirect http://localhost}).run_local_server(port=0, access_type='offline', prompt='consent')`, prints the `1//…` refresh token. Ran it with `python -u` in BACKGROUND (run_local_server BLOCKS on the localhost callback). Browser opened on DJ's PC → DJ clicked **Advanced → Go to (unsafe) → Allow**. Then one script: validated (refresh→access_token OK) → single-var PUT `…/env-vars/GOOGLE_OAUTH_REFRESH_TOKEN` {value} (no wipe) → POST `/deploys` to load it. DJ's screenshot TODAY confirmed **Audience → Publishing status = "In production"** (with a "Back to testing" button) — yet it STILL expired in ~3 days. So "In production" is NOT stopping the expiry — the recurring death is real and publish is NOT the cure. **Likely the Drive scope is RESTRICTED + the app is UNVERIFIED → tokens get capped regardless of publish status.** Real permanent fix is probably one of: (a) Google verification of the app, (b) move the Vault to a Workspace Shared Drive + use a service account, or (c) re-platform Notes off Drive. For now it's a manual ~weekly re-mint with the script. **STILL PENDING from 6/19:** re-file the Dawson invoice (`POST /printing/api/jobs/po-043859/file-to-drive`) now that the token is live — its Drive "final" is still the DRAFT.

## To renew the token again if needed (needs DJ's Google login once)
1. Get `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` (Render env, or Google Cloud Console OAuth client). get_service does NOT return env var values.
2. Run an `InstalledAppFlow` (offline access, scope `https://www.googleapis.com/auth/drive`) on DJ's PC → browser consent → prints refresh_token.
3. Update Render `GOOGLE_OAUTH_REFRESH_TOKEN` — **merge, don't wipe** (Render PUT wipes all unspecified vars — see [[feedback_render_put_env_vars]]).
4. Publish the OAuth app to Production so it stops expiring.

Photo OCR model 2026-06-11: `create_from_photo` image analysis switched **Haiku → `CLAUDE_MODEL` (Sonnet 4.6)** + strict no-hallucination prompt ("transcribe EXACTLY, [illegible] for unclear, never invent, no narrative"). Haiku was hallucinating handwriting (turned a sticky note into a fake "Dear Richard" letter). `_analyze_note` summary still on Haiku (fine once transcription is faithful).

DONE 2026-06-11: Notes now supports **multiple photos** + separate **📷 Camera** (`capture="environment"`) and **🖼️ Gallery** (`multiple`) buttons. Frontend `selectedPhotos[]` array + thumbnail strip (`#photo-strip`, remove per-thumb, max 8). Backend `create_from_photo` reads `form.getlist('photo')`, analyzes all images in one Claude vision call, embeds all in the one note (25MB total cap). [[project_saunders_vault_notes]]
