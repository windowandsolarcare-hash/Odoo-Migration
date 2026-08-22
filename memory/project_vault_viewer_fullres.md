---
name: project_vault_viewer_fullres
description: "Vault file preview now shows full-res images with rotate+zoom, streams PDFs full-res, and shows the filed-in folder"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

Vault preview (`openPreview` in vault.html) used to load `https://drive.google.com/file/d/{id}/preview` in an iframe — **low-res, no good rotate/zoom** on mobile. Fixed 2026-07-11 (vault.html 7118be2, vault.py e3522e7):

- **Images** → custom viewer: `<img id="pvImg">` in `#pvImgWrap` (overflow:auto, touch-action:pinch-zoom) sourced from **`/owner/api/vault/file?id=`** (streams the REAL full-res file bytes, not Drive's downsampled preview). Controls: `pvRotate()` (90° via CSS `transform:rotate`), `pvZoom(±)` (scale 0.5–6), `pvZoomReset()`. State `_pvRot`/`_pvScale`, applied via `pvApply()`.
- **Real PDFs** → the `#pvFrame` iframe points at `/api/vault/file?id=` (browser-native PDF viewer = full-res + real zoom).
- **Google Docs / Photo Notes** (mime `application/vnd.google-apps.*`) → iframe uses Google's NATIVE viewer `https://docs.google.com/document/d/{id}/preview` (commit cb3c6c8). ★ Photo Notes (vault camera → notes.py) are Google DOCS with the photo EMBEDDED in the doc HTML (data-URI `<img>`, no separate original file kept) — the PDF export path downscaled the embedded photo, so the native docs viewer shows it crisply. e.g. "2026 RV Registration" (Google Doc, folder Personal).
- **Filed-in folder** → new `GET /api/vault/file_folder?id=` (vault.py) returns `{folder, path}` via `_breadcrumb(svc, parents[0])`; preview header shows `📁 Vault / … / Folder`.
- Cache-first preserved: pinned/offline files still render from the local IndexedDB blob (`idbGet(id)`), only falling back to the stream when online.

**Photo notes now ALSO save the ORIGINAL photo as a separate full-res image file (notes.py cf67988):** `create_note_from_photo` keeps `originals=[(mt,raw_bytes)]` and, after `_make_doc`, uploads each via new `_upload_image(svc,name,data,mimetype,folder_id,tags)` (MediaInMemoryUpload) into the SAME folder, named `"<title> — original[.N].jpg"` (same tags). So the full-res photo is viewable via the image viewer (image/* → custom rotate/zoom), sidestepping the Google-Doc embed downscale. Applies to FUTURE notes only — existing photo-note docs (e.g. 2026 RV Registration) have just the embedded copy; view those via the native docs viewer, or re-photograph to get a separate original.

★ `/api/vault/file` (vault.py) is the full-res source of truth (get_media / export_media, Cache-Control private max-age=86400). Reuse it for any "show the actual document" need instead of the Drive `/preview` iframe. See [[project_vault_inbox_import_pending]], [[project_email_to_myday_task]] (+vault@ ingestion).
