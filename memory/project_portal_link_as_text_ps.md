---
name: project_portal_link_as_text_ps
description: "DJ's framing for the customer portal — it's \"a P.S. to every text I send someone\", i.e. the portal link rides the SMS signature rail, resolved per recipient. Not built yet."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-18T22:49:43.162Z
---

DJ, 2026-08-18, on first seeing the customer portal: **"to me it's almost like a P.S. to every
text I send someone."**

That is the intended distribution model, and it's a useful reframe: the portal isn't a destination
DJ sends people to occasionally — it's meant to hang off the bottom of ordinary customer texts the
way a signature does.

**Why it matters:** it maps directly onto machinery that already exists. `sms.py` `WSC_SIGNATURE`
is auto-appended to every outbound text at the send funnel (`_apply_signature`). A portal P.S. is
the same rail, except the line is **per-recipient** (`portal.portal_url(partner_id)`) rather than a
fixed string, so it has to resolve inside the funnel where `partner_id` is known.

**How to apply / open questions before building:**
- `sms.py` is the **Specialists** session's file — this is a coordination item, not a Portal-only change.
- **Cost:** SMS segments at 160 chars. `WSC_SIGNATURE` already spends ~55. A `wscare.pro/p/<token>`
  line (~32) plus a lead-in would push many messages into a 2nd segment → roughly double per-text cost.
  So "every text" is a real money decision, not just a formatting one.
- Likely better than blanket-append: attach it where it earns its place — after a completed job,
  after a payment, after a reschedule — the same moments the photos link already goes out.
- DJ said **"we'll refine it soon"** — this is captured direction, NOT approved to build.

Related: [[project_customer_portal]]
