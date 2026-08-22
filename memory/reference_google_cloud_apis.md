---
name: Google Cloud project + API keys for Window & Solar Care
description: DJ has a Google Cloud project ("Odoo", id gen-lang-client-0790905441) with billing enabled. API keys live under APIs & Services → Credentials. Each key is restricted by HTTP referrer to keep it safe to embed in frontend HTML.
type: reference
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
DJ's Google Cloud project for W&SC integrations:

- **Account:** `windowandsolarcare@gmail.com`
- **Project name:** Odoo (yes, confusing — predates the Odoo migration project, was already there)
- **Project ID:** `gen-lang-client-0790905441`
- **Project number:** `786167717152`
- **Billing:** enabled (required for Maps Platform). $200/month free credit covers normal usage.

## Enabled APIs (as of 2026-04-29)

- **Places API (New)** — used by `/owner/quote` address autocomplete
- **Maps JavaScript API** — enabled but not yet integrated (available if we want to embed actual maps)
- **Weather API** — DJ enabled this for a future idea (not yet wired)
- **Gemini API** — pre-existing from earlier work

## API keys

### "API key Render"
- **Key:** `AIzaSyA2D5Sd7IPOi2h65G4pew7QuXAko3bOO60`
- **Application restriction:** HTTP referrer — only `https://wsc-field-assistant.onrender.com/*` can use it
- **API restriction:** Places API (New), Maps JavaScript API
- **Where used:** `Saunders Render App/static/owner/quote.html` — embedded as `GOOGLE_PLACES_KEY` constant
- **Safe to embed in frontend** because the referrer restriction means a leaked copy can't be abused from another domain.

### "Odoo" (pre-existing)
- Used for Gemini API, possibly other older integrations.
- Don't reuse for new Maps/Places work — make a dedicated, narrowly-scoped key per use case.

## Pattern for adding a new Google API integration

1. Enable the API in console.cloud.google.com (search → Enable)
2. Create a NEW API key (don't reuse) → APIs & Services → Credentials → Create credentials → API key
3. Restrict it to:
   - **Specific APIs only** (the ones the integration needs — never "all APIs")
   - **HTTP referrer** matching the deployed origin (e.g. `https://wsc-field-assistant.onrender.com/*`)
4. Save the key + restriction details in this memory file under "API keys"
5. For frontend use, embed in HTML/JS as a named constant. For backend use, store in env var on the server, never commit.

## Why per-use-case keys (not one shared key)

- Blast radius: if one integration leaks, only that key is compromised.
- Granular metering: each key's usage is visible separately in the Cloud Console → Metrics tab.
- Different referrer restrictions: Render production site needs `wsc-field-assistant.onrender.com`, but a local-dev integration needs `localhost:*`. One key can't be both narrowly-restricted and dev-friendly.

## Cost watch

- Places Autocomplete (New): ~$2.83 per 1000 sessions. DJ does ~5 quotes/day = 150/month = ~$0.42 — entirely under the $200 free credit.
- Maps JavaScript API map loads: ~$7/1000. Free tier covers thousands per month.
- If a notification hits about hitting limits, check Console → Billing → Reports for which API.
