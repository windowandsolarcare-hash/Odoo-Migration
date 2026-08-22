---
name: session_jun01_hiring_ats
description: "2026-06-01 full session — Indeed ZIP import, hiring ATS build, DJ batch scoring, Cheryl setup, PWA fixes"
metadata: 
  node_type: memory
  type: project
  originSessionId: 77ce3aa1-f52a-4a17-b1d6-97cfc23e5db5
---

## Hiring ATS — June 1 2026 Session

### What Was Built
- Full Indeed ZIP import: 64 applicants imported from gzip JSON files, all with AI scoring, structured resume text, raw JSON saved
- ZIP upload endpoint: `POST /api/hiring/import_zip_preview` on Render — parses all files server-side
- Batch scoring endpoint: `POST /api/hiring/score_batch` — takes custom system prompt + candidates, calls Claude Sonnet
- DJ Fleet Lead scoring: 100-point system run on all 64 candidates. Top: Joe Quevedo 72, Mark Valdez 68, Edgar Lopez 65, Breanna Shaw 63. Nobody hit 80+ (Tier 1).
- All-caps resume parser added (3rd pass in parseResumeIntoSections for SKILLS/EXPERIENCE/EDUCATION AND TRAINING format)
- Section completeness chips on cards (green/red per section)
- Consistent detail layout — all sections always shown, "None provided" when empty
- Sticky sheet headers so ✕ always visible while scrolling
- Save & Re-score fixed (was using wrong URL with backslashes, apiFetch not catching errors)
- Full Resume display fixed: falls back to ===RESUME=== when ===RESUME_TEXT=== is minimal (<150 chars)
- Back buttons on 6 pages fixed: `history.back()` → `window.location.href='/owner/'` (calendar, hemet, notes, quote, shift_review, submitted_jobs)

### Odoo Email Incident
- Stage 1 "New" had template "Recruitment: Application Acknowledgement" — fired on all 64 imports
- Email showed from dan@scenicartprint.com (Odoo outbound config), reply-to went to windowandsolarcare@gmail.com
- Company address in email was home address (32569 San Miguelito Dr) — changed to 41995 Boardwalk Ste. J, Palm Desert
- Template removed from Stage 1. All other stages already clean.
- Only Breanna Shaw replied (inkd.sk3ll1ngt0n16@gmail.com): "I look forward to hearing from you."
- Added mail_create_nosubscribe + tracking_disable + mail_notrack context to all hiring.py write calls

### Cheryl Setup
- Cheryl's dashboard (`/cheryl/index.html`) — 6th card "WSC Hiring [WSC]" added, links to /owner/hiring, auto-sets wsc_ac=wsc2026
- Cheryl login: name=Cheryl Johnson, PIN=1006
- Owner login: name=Dan Saunders, PIN=8487
- Cheryl's Claude tab: `C:\Users\dj\Documents\Business\Cheryl\` — read-only WSC data assistant
- Cheryl to use DJ's Claude account (Max plan) in second browser tab for now

### PWA Fixes — PARTIALLY WORKING
- login.html: instant redirect in <head> before CSS renders — eliminates login flash ✅
- pwa-track.js: injected into all 17 owner pages, saves current path — deployed ✅
- manifest.json: created at /static/manifest.json — deployed ✅
- Icons (icon-192.png, icon-512.png): sky blue circle with WSC text — pushed but NOT showing on phone ❌
- Last page resume: pwa-track saves path but still not resuming correctly on phone ❌
- **Why icon not showing**: Android caches aggressively; user must remove old shortcut and re-add
- **Why last page not resuming**: Unknown — may be manifest not loading, or pwa-track.js not firing on some pages

### Key File Locations
- Render repo: windowandsolarcare-hash/saunders-render-app
- hiring.py: routers/owner/hiring.py
- hiring.html: static/owner/hiring.html
- pwa-track.js: static/owner/pwa-track.js
- manifest.json: static/manifest.json
- Cheryl dashboard: static/cheryl/index.html

### Candidates Without Real Resumes (Need Indeed PDFs)
- Michael Zavala (score 3 — fake, location only)
- Eduardo Mosqueda (score 3 — fake, location only)
- David Osuna, Manuel Ramirez, Surileinne Sabanero — all PDF-only, minimal data
