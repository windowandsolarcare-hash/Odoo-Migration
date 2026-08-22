---
name: project_job_photo_gallery
description: "Share a job's photos with the customer via a LINK. Token-signed public gallery of the SO's image attachments + a 'Text photos to customer' button (field app photo card). Built 2026-08-05."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-14T04:49:35.227Z
---

**DJ wants to text a customer a link to the job photos he took** (job photos = image `ir.attachment` on the sale.order, res_model='sale.order', mimetype image/, excluding description='community_pass'). Built 2026-08-05 (lead, dashboard.py).

## Endpoints (dashboard.py)
- **`GET /owner/api/job/gallery?so_id=&sig=`** — customer-facing branded HTML gallery (dark, responsive grid, tap-to-fullsize). PUBLIC (whitelisted PUBLIC_EXACT). Header "Hi {first} — here are the photos from your service on {date}".
- **`GET /owner/api/job/photo?so_id=&att=&sig=`** — serves ONE image. Token-scoped: sig must match SO AND the attachment must be an image ON that sale.order (can't walk to other records). PUBLIC (PUBLIC_EXACT).
- **`POST /owner/api/job/photos_send {so_id, send, edited_body?}`** — send=false PREVIEW `{ok, preview, text, to, name, count, has_phone, url}`; send=true texts the link via `messaging.send` (STOP/DNC/quiet honored, no idem so it can re-send). DJ-facing → PROTECTED (NOT whitelisted).
- **Token:** `_photo_sig(so_id)` = HMAC(SESSION_SECRET or ODOO_API_KEY, 'photos:<so_id>')[:16]. `photo_gallery_url(so_id)` builds the wscare.pro link.

## ★ authz gotcha
`/owner/api/job/photo` added to **PUBLIC_EXACT (exact match), NOT PUBLIC_PREFIXES** — a prefix would also expose `/owner/api/job/photos_send` (starts with "…/photo"), which sends texts and must stay protected. Same collision class as the voice webhooks.

## Frontend
**`v2_field.html`** photo card (under "📸 View Photos", ~L610): **"📤 Text photos to customer"** (`textJobPhotos()`, ~L2895) → preview → native `confirm()` showing count + the drafted message → send:true → showToast. (confirm() yes/no is fine; not a text-input prompt.)
★ **V2 TWIN TRAP (burned again 2026-08-05):** first added it to `field.html` (the legacy twin) — DJ's screen is **v2_field.html** (Snap Photos / Gallery / View Photos + Timer + Record Payment). Both files exist + both have a Photos section; DJ uses V2. The field.html copy is harmless dead cruft. Rule 10: edit the v2_ twin. Backend endpoints are shared, so only the button/JS needed re-homing.

## Name gotcha (fixed)
photos_send first resolved `name` from the partner that had the phone = the PROPERTY record ("727 Inverness Dr") → texted "Hi 727,". Fixed: `name = so['partner_id'][1].split(',')[0]` (the display incl. the person → "John & Dawson Bullock"). Phone still walks property→parent. See [[project_respartner_no_mobile_field]] / person-property split.

Verified live on John Bullock SO 17389 (22 photos): gallery renders, images serve, message = "Hi John, here are the photos… <link> – Dan". Reuses the Stripe logo endpoint for branding. See [[project_zelle_customer_ux]] (same public-page + preview/send pattern).

## "Last sent" log line (DJ 2026-08-06)
DJ: don't change the button to "Already sent" (he must be able to RE-SEND) — instead show a log line UNDER it. So: `photos_send` (send:true) writes `ir.config_parameter wsc.job.photos_sent.<so_id>` = {at,count,held,to}; `GET /owner/api/job/photos_sent?so_id=` returns it; v2_field `loadPhotoSentLog(soId)` (called on job open at the photo-odoo-link show + after a send) renders `#photo-sent-log`: "📤 Sent N photos · <when>" (or "🌙 Queued N photos (sends 8am) · <when>" when quiet-held). Button unchanged/re-sendable. Held sends DO record (messaging._hold returns ok:True). Backfilled John 17389.

## Holding card fixes (2026-08-06)
DJ sent John's during quiet hours → held correctly. Two card bugs: (1) **"sends at Invalid Date"** — `v2_holding.html` ran `new Date(it.sends_at)` but `sends_at` is already a friendly LABEL ("8:00 AM PT"); fixed to only date-parse a real ISO, else show the label. (2) card **name = "727 Inverness Dr"** (property) not "John" — holds endpoint (messaging.py, specialist) resolves name from partner_id(=property); mailed specialist to use the partner display/parent like photos_send does.

## DJ picks WHICH photos to share (2026-08-13)
DJ: "I'd like to select the ones I want them to see." `textJobPhotos()` (v2_field.html) no longer sends all — it now fetches `/api/job_photos`, opens a **tap-to-select grid** in the list modal (`_photoSelPhotos`/`_photoSel` Set, default ALL selected; ✓ badge + green border on selected, dim on deselected; Select-all / Clear; a live "📤 Text N photos" button → `_photoSendSel`). Send posts `att_ids:[...]` to `photos_send`. **Interaction (DJ 2026-08-13, commit 384649b):** tap the PHOTO = `_photoBig(id)` full-screen viewer (fixed inset:0 overlay, tap to close); tap the **✓ corner button** (top-right, `event.stopPropagation()`) = include/exclude. Not a whole-tile toggle.
Server (dashboard.py, commit ca9d1db): `photos_send` accepts `att_ids` (validated to images ON the SO), `cnt` = len(selection), and on send stores `ir.config_parameter wsc.job.gallery_sel.<so_id>` = the chosen id list (empty = all). New `_photo_selection(so_id)` helper. **`/api/job/gallery` filters to the stored selection; `/api/job/photo` 403s any att not in it** — so a deselected photo isn't viewable even by guessing the att id. Latest send overwrites the selection (link always reflects the newest pick). Commit v2_field 81e5b16.

## Broken-tile fix (2026-08-05)
DJ: "not all preview correctly" — a few grid tiles showed the broken-image icon. Diagnosed: ALL 22 photos serve fine individually (each 200 + full bytes) — it was a LOADING BURST: 22 `<img>` firing at once, each making the server read a ~400KB base64 blob from Odoo → a few requests fail under load → broken tiles. **Pillow is NOT installed** (not in requirements, no `from PIL` anywhere) so no server-side thumbnails without a rebuild — skipped. Fix = client-side: gallery now renders `.ph` divs with `data-src` and a JS loader that loads **4 at a time** (queue) + **retries a failed image up to 3× with backoff** (`url+"&r="+tries`), tap a loaded tile = full size, permanently-failed tile gets a ⚠ placeholder. No broken tiles now.
