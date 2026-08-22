---
name: reference_recurring_paid_services
description: "Inventory of the recurring services DJ pays for (from a Gmail receipt audit 2026-07-04), grouped by entity. ~$1,929/mo total. Amounts drift; the list + who-pays is the value."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# Recurring paid services (Gmail receipt audit, 2026-07-04)

★ The windowandsolarcare@gmail.com inbox is a **catch-all for 4 hats**: W&SC, Saunders Printing, Cheryl (realtor/personal), and DJ personal (`dj@mirrokoat.com`). "What costs me money" spans all of them. Amounts change month to month — treat as approximate.

**Software/tools:** Anthropic/Claude **$100/mo fixed** (+ variable API top-ups; was $137 in June)(W&SC) · Gusto payroll $61 (Saunders) · Intuit/QuickBooks $48 · Google One 5TB $19.99 (= the Vault storage) · Render hosting ~$15 (W&SC) · Calendly $12 (W&SC) · Midjourney $10 · HP Instant Ink $8.49 · Everlance $99.99/yr (Cheryl) · DreamHost domain windowandsolarcare.com $19.99/yr · Google Workspace scenicartprint.com (amount only in PDF, not fetched) · Workiz annual, renews **Aug 15** (price not in email; being retired).

**Utilities/insurance/storage/mortgage:** Mortgage → Mortgage Funding Corp **$1,115.94/mo** (personal, via Ally) · **Extra Space Storage $235/mo** (biggest discretionary — candidate to cut) · KW Specialty homeowners insurance $1,642.63/yr (~$137/mo, personal) · Spectrum internet $75 · Coachella Valley Water $23.43 (Cheryl) · SoCalGas $21.23 (Cheryl).

**Monthly total ≈ $1,929** (~$23k/yr). ★ But ~$1,490 of that is 3 personal/household lines (mortgage + homeowners insurance + storage). **Actual business software ≈ $275/mo**, mostly Claude ($100).

**Not billing (checked):** Cursor — DJ moved to Claude Code; last money event was a *refund* Feb 2026, only marketing since (no active sub). Zoom/Adobe/Roku/Pabbly — marketing emails only, unconfirmed.

**Stripe keys note:** there are TWO live secret keys — a general "Secret key" AND a dedicated **"Odoo Credit Card"** key (`sk_live_…xya1`) which is what processes Odoo card payments. Rotating the general key does NOT affect card processing. See [[feedback_api_keys_via_file]].
