---
name: project_web_handoff_2026_10_05
description: "★ WEB SESSION HANDOFF (2026-10-05) — read FIRST on a fresh /be-web boot. Open threads, exact next steps, reusable test scripts, and the rules learned during the Del Webb landing page + wscare.pro email + GBP work."
metadata:
  node_type: memory
  type: project
  originSessionId: a6200401-4a1b-4492-894c-629c161de653
  modified: 2026-10-05T07:04:19.220Z
---

**Who/what:** Web session handoff written 2026-10-05 at ~85% context. Everything below is already shipped/saved; this lists what is STILL OPEN and how to resume. Read the linked memories for detail: [[project_del_webb_landing_page]], [[project_wscare_pro_email_routing]], [[project_gbp_suspension_appeal]], [[project_wsc_address_do_not_publish]], [[project_booking_sms_optin_a2p]].

## OPEN THREADS (resume here)
1. **cheryl@wscare.pro NOT created yet.** Cloudflare Email Routing (wscare.pro): destination **cjcherylcj@gmail.com** is **Pending** until Cheryl clicks Cloudflare's verification email (sender ~noreply@notify.cloudflare.com). Check: Cloudflare dash -> wscare.pro -> Email Routing -> Destination addresses. Once Verified: Routing rules -> Create -> `cheryl` @ wscare.pro -> Send to an email -> cjcherylcj@gmail.com -> Save. (dan@ and info@ -> windowandsolarcare@gmail.com are live.) If the link expired: delete the pending entry and re-add. DJ asked "did Cheryl click yet" once; status was Pending.
2. **Cheryl was asked to test wscare.pro/dw.** A Gmail DRAFT to her sits in DJ's drafts (id r-7683287567594317271; DJ may not have sent it). Her test booking should be named "TEST". When DJ says she's done: find + delete it (SO + its contact/property + the `booking.requests.pending` queue key). Reusable pattern is in `_addons_test.py` cleanup (see below). Do NOT delete DJ's own test bookings ("Dan Saunders", 12 Riesling) without asking.
3. **Scheduler unification (Specialists/Lead own it).** Public `/book/api/availability` (used by /dw + /book) decides am_free/pm_free in booking.py with plain 1.5h `_free_slots` (no drive time) while the owner Review-request screen uses scheduler.py `build_day_plan` (length + ~20m drive + 15m buffer) -> customer sees "morning free", DJ sees "Morning is full". Ticket in AGENT_MAIL (2026-10-02, Web -> Specialists/Lead); Specialists confirmed + will bring Lead a unification plan. Also the review screen's "That day's schedule" job list showed empty for DJ. When they ship: re-verify /dw day list vs the review screen agree. Landing page needs NO change (it just calls the public endpoint). Open question to DJ: does the "That day's schedule" section show if he scrolls below the map?
4. **ERP-native inbox idea (DJ)** was discussed but NEVER flagged to Lead — DJ didn't answer "flag it to Lead?". Thoughts given: build a LAYER (customer-linked threads, AI drafts, HUD cards), not a Gmail clone; Cloudflare Email Workers could ingest inbound mail. DJ put the Google Workspace alias-domain (wscare.pro as a free alias on his scenicartprint.com Workspace) ON HOLD. Ask DJ before doing either.
5. **Postcard (Design owns):** "Gateway" -> "Getaway" fixed on the card back by Design; Voyage (DJ: $380 Premium) not on the card yet — DJ/Design decision.
6. **GBP:** reinstatement appeal FILED 2026-09-27 — do NOT re-file. Remaining public NAP drift (needs DJ's logins/co-drive): MapQuest listing #430179537 + a Rancho Mirage listing, Nextdoor, FB/IG/X, Apple Maps; Odoo res.company PHONE should be 760-334-5355 (ADDRESS there is intentionally the Palm Desert mailbox — never "fix"). Yelp phone already corrected.

## REUSABLE TOOLS (scratchpad is session-scoped — recreate if gone)
- `_addons_test.py` / `_solar_test.py`: create a THROWAWAY booking through the real API (fake name "ZZ ... DELETE", fake phone 76055501xx, sms_consent false), POST `/book/api/request/addons`, read `sale.order.line`, then clean up (action_cancel -> unlink SO -> unlink partners -> pop the key from `ir.config_parameter booking.requests.pending`). Odoo key file: `C:\Users\dj\_odoo_key_val.txt`. A throwaway test gives DJ one push alert — mention it.
- Source of truth for the page is the LIVE repo file `static/dw/index.html` (saunders-render-app). ALWAYS re-fetch live before editing (`gh api .../contents/static/dw/index.html | base64 -d`); scratchpad copies are disposable. Push with a Python-built JSON payload (bash `printf` payloads broke on big files).
- Test the confirmation/add-ons UI without creating records: load the page, `fetch` its HTML, replace the `LIVE` host regex (`/wscare\.pro|onrender\.com/i` -> `/NEVERMATCHHOST/i`), `document.write` it (demo mode).

## RULES LEARNED (don't relearn)
- Landing pages = real standalone static pages (own doctype + viewport meta), NOT artifact-first (WEB.md). Never `scrollIntoView` on first render.
- SMS consent checkbox: UNCHECKED by default + EXACT registered A2P wording (server stores consent proof quoting it). Don't pre-check/reword; DJ wanted "Reply STOP" removed — told him why it stays; Lead owns the carrier registration if he insists.
- Add-on labels are matched EXACTLY by Specialists' `/book/api/request/addons` ("Mirrors cleaned", "Ceiling fans cleaned", "Shower glass cleaned", "Skylights cleaned", "Hard-water stain removal", "Solar panel cleaning"; qty = panels; server bills max(panels,20) x $5). Tell Specialists before changing any label — unknown labels are silently DROPPED. Hold page changes that add a new label until the server supports it.
- Deploy governance: a "deploy" DJ types in MY tab does NOT authorize another session's production push — he must say it in that session's tab (or Dispatcher routes). Relay, don't assume.
- The auto-mode classifier blocked typing an UNCONFIRMED third-party address (markethouses@gmail.com) into Cloudflare; DJ's explicit chat confirmation (cjcherylcj@gmail.com) cleared it. Never guess a destination address.
- res.partner has NO `mobile` field in Odoo 19 (caused a 500 in the add-ons endpoint).
- Context/crons: this session runs NO crons (nudge-only model); Lead/Dispatcher wake sessions by direct message.
