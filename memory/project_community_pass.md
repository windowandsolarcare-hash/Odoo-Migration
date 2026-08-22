---
name: project_community_pass
description: "Community/gate Pass on the field job detail — upload a photo or PDF (per-job), display + open full-screen, delete. Stored as ir.attachment on the SO tagged description='community_pass'. Built 2026-06-17."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ (2026-06-17): on the open job's detail, allow uploading "passes to get into a community" (gated-HOA access passes) and a way to display them.** Decisions: **per-job** (not property-level) and **photos + PDF**.

## Where it lives
- **Field job detail panel** (`static/owner/field.html`) — new **"🎫 Community Pass"** card, placed right before the Payment card (alongside Photos). Shows on the active job you have open (`activeJob.so_id`). `loadPasses(job.so_id)` is called from `openJob`.
- Functions: `loadPasses`, `renderPassRow`, `passSelected` (upload), `deletePass`. Image passes are compressed with the existing `compressImage`; PDFs uploaded as-is. Tap a pass → opens full-screen in a new tab (`window.open`) — zoomable, to show at the gate. (Deliberately did NOT use `openHistLightbox` — it's referenced by the existing photo code but **not defined anywhere** in field.html or the external js; the existing so_full/hist photo taps may be a latent dead reference. Not fixed here.)

## Backend (`routers/owner/dashboard.py`)
- **Storage = `ir.attachment` on `sale.order`** (res_model='sale.order', res_id=so_id), tagged **`description='community_pass'`** to separate passes from job photos.
- `POST /api/attachment` — EXTENDED to accept an optional `description` (was hardcoded photo-on-SO create). Reused for the pass upload. Returns `{status:'ok', attachment_id}`.
- `GET /api/passes?so_id=` → `{ok, passes:[{id,name,mimetype,is_pdf}]}` (description='community_pass').
- `POST /api/pass_delete {att_id}` → unlink, but **guards**: reads the att and refuses unless `description=='community_pass'` (so it can't delete a real photo by id). VERIFIED: deleting att_id=1 → "Not a pass attachment".
- Serve via the existing `GET /api/attachment_image?att_id=` (decodes `datas`, returns with mimetype — works for image AND application/pdf).
- The two regular photo queries (api_so_full ~L4349, so_history ~L6829) now exclude `description!='community_pass'` so passes don't show in the Photos section.

## Verified 2026-06-17 (live, self-cleaning)
PDF round-trip on SO 17359 (name 004604): create→id 1650, list shows is_pdf, serve HTTP 200 application/pdf, delete-guard refuses non-pass, delete ok, gone. Image path proven by the existing Photos feature (same create endpoint).

## GOTCHA — Odoo runs Pillow on image attachments
`ir.attachment.create` with an `image/*` mimetype post-processes the bytes through Pillow (`_postprocess_contents` → image_fix_orientation). A corrupt/truncated image → `OSError: Truncated File Read` and the create fails. Real phone JPEGs are fine; this only bit a hand-made 1×1 test PNG. PDFs skip this path.

## NOT done / future
- Per-property level (DJ chose per-job; a community pass is reusable, so property-level could be a future upgrade so it carries across visits). [[project_property_displayname_has_name]]
- Surfacing passes in the read-only so_full modal too (currently only the active job panel).
