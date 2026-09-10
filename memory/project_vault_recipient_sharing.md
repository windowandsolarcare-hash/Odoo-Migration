---
name: project_vault_recipient_sharing
description: "How Vault per-note/file sharing reaches a recipient (Cheryl's \"Shared with me\") — whole-vault scan + the app-share≠Drive-ACL open fix. notes.py documents_for_recipient / recipient_file_bytes."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-10T04:02:11.023Z
---

The Vault is Google Drive under `VAULT_ROOT_ID = "1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q"` (notes.py). Sharing is per-item: a Drive file's `properties.shared_with` = comma list of recipient partner-ids, or `shared_all='1'`. Gate = `_shared_visible_to(props, vp)` = exact-id (never substring — `_shared_set` splits on comma) OR shared_all. `pinned='1'` = DJ's personal shortcut, never shown to a recipient. Recipient identity = the session `p` (partner id), taken from the authenticated session ONLY (cheryl/documents.py `_viewer_pid`), never a client param. Cheryl's view = `/cheryl/api/documents` → `owner_notes.documents_for_recipient(pid)`; open one = `/cheryl/api/documents/{id}` → `recipient_read` (re-verifies the share, default-deny).

**Bug + fix (2026-09-10): a shared FILE never reached the recipient; shared NOTES did.**
- **LISTING root cause:** `documents_for_recipient` scanned ONLY the Quick Notes tree (`qn_id` + its category subfolders + note-folders). A file shared from ANY other Vault folder (uploads land in `Quick Notes/<category>/` or a `group_name` bundle, but files can live elsewhere) was never in the scan → dropped. FIX: added `_all_vault_folders(svc)` (BFS the whole VAULT_ROOT subtree) and `documents_for_recipient` now scans EVERY vault folder (chunked 30 ids/Drive query), listing each file gated per-file by `_shared_visible_to`. **Widening the scan is SAFE — the per-file gate is the access boundary, unchanged, so it can't over-expose.** Quick-Notes note-folder BUNDLING preserved (children counted, folder shown if shared); a file INDIVIDUALLY shared inside a bundle now also lists (was hidden).
- **OPEN root cause (app-share ≠ Google Drive ACL):** `recipient_read` returned a raw Drive `webViewLink` for a file — which 403s a recipient who isn't on that Drive file's Google ACL. The app-level `shared_with` does NOT grant Google Drive access. FIX: `recipient_file_bytes(viewer_pid, note_id)` (re-verifies share, default-deny) streams the raw bytes via `svc.files().get_media` (like the md1 note path); new endpoint `GET /cheryl/api/documents/{id}/raw` (cheryl/documents.py) serves them `Content-Disposition: inline`; `static/cheryl/documents.html` opens a file via that app URL, not the Drive link. **Rule: a recipient opens shared files THROUGH the app (get_media), never via a Google Drive link — the app is the UI, users never touch the backend** (see [[feedback_never_send_dj_to_odoo]]). Native Google docs (`application/vnd.google-apps.*`) aren't raw-downloadable → recipient_read serves their exported text instead.

The `/raw` endpoint is under `/cheryl`, so it's also protected by the role-isolation guard ([[project_auth_role_model_cheryl_isolation]]) — only a cheryl session reaches it. Share targets = res.partner with `x_render_role` set (≠owner), company_id in [1,False] (notes.py `share_targets`).
