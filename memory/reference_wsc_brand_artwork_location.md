---
name: reference_wsc_brand_artwork_location
description: "WHERE the Window & Solar Care LOGO + brand/artwork library lives on DJ's computer. Logo master + all sizes: ...\\A Window and Solar Care\\Website\\Logo\\ (Logo-Org.png = transparent master). Full W&SC image library = the parent Website\\ folder (Solar/Windows/Gutter/Van/People/etc). One logo already mirrored in the repo at 4_Reference_Data/brand/. Design uses these as canonical brand assets."
metadata:
  node_type: memory
  type: reference
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-13T04:21:41.992Z
---

**Found 2026-09-13 (DJ asked Lead to locate W&SC artwork so Design could use it).** The W&SC logo was NOT in an obvious "Brand" folder — it's under the website assets. Check HERE before re-searching the disk (a whole-home glob times out; go straight to these paths).

## The logo
- **Folder:** `C:\Users\dj\Documents\Business\A Window and Solar Care\Website\Logo\`
- **Master:** `Logo-Org.png` (transparent bg) — the water-droplet **WINDOW** / solar-panel **& SOLAR** / underlined **Care** wordmark. Also `Logo-Org-Blk-Bgd-*` (black background) + every web size (150x150 … 2048x842).

## The full W&SC artwork/image library
- **Parent folder:** `C:\Users\dj\Documents\Business\A Window and Solar Care\Website\`
- Subfolders (service + brand imagery): Logo, Solar, Windows, Gutter, Pressure Washing, Van, People, House, Screens, Squeege, Water Drops, Stock Images, Coupon, Pricing, Care Program, Best Ribbon, Arrow, Window Washer, Equipment, Room, Dan, Home Advisor, Zips.

## Already in the repo (fleet/cloud-fetchable, no local FS needed)
- `windowandsolarcare-hash/Odoo-Migration` → `4_Reference_Data/brand/logo_window_solar_care_white_bg_500x235.png` (white-bg logo, added 2026-06-14). Only the logo — NOT the full library.

## ⚠️ TWO TRAPS in the Logo folder (found 2026-09-13, confirmed by view)
- **DEAD PHONE NUMBER baked into the header logos:** `Logo-Web-Site-Header*.png` + `cropped-Logo-Web-Site-Header*.png` (the LARGEST logo files, up to 2497x500) show **"Call (855) 245-2273 (CARE)"** — the RETIRED toll-free number. Current number is **760-334-5355**. Grabbing "the biggest logo file" ships a dead number on print/web. DO NOT use the Header versions for new work. A `_READ-ME-BRAND-WARNINGS.txt` was dropped in the Logo folder. SAFE logos (no phone #): `Logo-Org.png` (transparent master ~2700x1110, print-grade), `Logo-Org-Blk-Bgd-*`.
- **NO high-res / vector tagline lockup exists** (checked local disk + Google Drive). The tagline versions (`Logo-Org-and-Tag-*`) top out at ~500x251 = too soft for print. The logo has photographic fills (water droplets / solar-panel texture) so it likely was NEVER a clean vector. For print: use the sharp 2700px `Logo-Org.png` and set the tagline **"We don't just Clean, We Care!"** as LIVE TYPE beneath it (Design's proven workaround, Mission Hills postcard 2026-09-13). If DJ's original designer's layered/vector file ever surfaces, it's a recover-once asset.

## How Design gets it
The **local** Design session (roster: migration-to-odoo-11) can `Read` these paths directly. For **cloud** Design or portability, mirror the logo set + key service imagery to the Google Drive Vault and/or the repo `4_Reference_Data/brand/` folder (do NOT dump the whole hundreds-of-MB photo library into git). Use these as the canonical brand assets for postcards/flyers/social. Related: [[reference_domain_dns_hosting_map]], the Design charter/handoff briefs. NOTE the marketing TEMPLATE PSDs under `...\A Window and Solar Care\Marketing\1 - Window Cleaners Blue Print Book\` are a purchased generic industry kit ("Sparta Window", generic trust logos) — NOT DJ's real branded assets; don't mistake them for the W&SC logo.
