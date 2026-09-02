---
name: project_zoo_estimate_form_prefill
description: "PARKED by DJ 2026-08-30. Prefilling Zoo Printing's Custom Estimate form via Chrome JS injection. ★ The business constants DJ confirmed: quantity is ALWAYS 1000, the trim note and comments are ALWAYS the same text, and VERSIONS is the only field that ever changes. Also: the AppleScript must find the Zoo tab BY URL across all windows, and a Saunders-app button cannot do this (cross-origin) — it has to be a bookmarklet or the Mac app."
metadata:
  node_type: memory
  type: project
---

**Status: PARKED.** DJ 2026-08-30: *"I want to stick a pin in the estimate logic we discussed.
let's come back to it later."* Nothing here is live. The bookmarklet was written but **never run on
DJ's Mac**, so treat every selector below as unverified until someone re-derives it against the
live page.

## Why this note exists

The business rules below came out of a long back-and-forth with DJ over screenshots and DOM dumps.
They are the expensive part — the selectors can be re-derived in ten minutes, but "quantity is
always 1000" is only knowable by asking DJ, and he already answered.

## ★ The business constants (DJ confirmed, 2026-08-30)

- **Quantity is ALWAYS 1000.** Never prompt for it, never vary it.
- **VERSIONS is the ONLY field that changes between estimates.** Everything else is boilerplate.
- **The trim note and the comments box are ALWAYS the same text** — fixed strings, not composed.
- Product = **Postcards**.
- The three option radios, in page order: **radio 1 = Yes, radio 2 = Yes, radio 3 = No.**

So the whole interaction reduces to: *fill the constant boilerplate, ask DJ only for Versions.*
That is the design. Do not build a form that re-asks him things he has already fixed.

## Two failures worth not repeating

**1. The script drove the wrong Chrome tab.** A DOM dump came back showing the **Claude.ai UI**, not
Zoo's form, because the script targeted the front window's active tab. **Find the tab by URL across
ALL windows** — iterate every window and every tab, match on the Zoo estimate URL, and act on that
tab index. Never assume the front tab is the right one.

**2. A button inside the Saunders app CANNOT do this.** DJ asked to "wire up a button in the
Saunders app." The app is served from `wsc-field-assistant.onrender.com`; the form lives on
`zooprinting.com`. **Same-origin policy means the app's JS can never touch that form** — no amount
of app-side code fixes it. The only two shapes that work are a **bookmarklet** DJ clicks while on
Zoo's page, or a **Mac-side app** (the `nbhof://` URL-scheme pattern already proven for the NBHOF
plaque-card automation — see [[project_nbhof_plaque_card_applescript]]).

## Selectors — UNVERIFIED, re-derive before use

Field names seen in the control dump were `versions` and `quantity1`. Everything else was still
being identified when DJ parked it. **Re-dump the form and confirm before writing any selector into
code** — CLAUDE.md rule 1 (never guess at formats) applies to DOM as much as to Odoo fields.

## If DJ un-parks this

1. Re-derive selectors from a fresh DOM dump of the live Custom Estimate page.
2. Prefer the bookmarklet — no install, no Mac dependency, works the moment he's on the page.
3. Prompt for exactly one value (Versions); fill everything else from the constants above.
4. DJ tests it; a cloud session cannot click a button on his Mac.

## Related

- [[project_zoo_printing_automation]] — the broader Zoo automation (order emails, `zoo_watcher`).
- [[project_nbhof_plaque_card_applescript]] — the working Mac-side pattern if a bookmarklet won't do.
- [[project_mail_watchers_two_mailboxes]] — ★ Zoo's live watcher reads `dan@scenicartprint.com`
  INBOX and is **UNSEEN-only**; never mark those emails read or archive them.
