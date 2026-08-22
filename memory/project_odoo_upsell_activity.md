---
name: Odoo native upsell activity from Field Service timer
description: Odoo auto-creates "Upsell" To-Do activity on SO when timer hours exceed ordered quantity — needs to be disabled
type: project
---

When DJ stops the Field Service timer and logged hours exceed the ordered quantity (e.g. 1.25h logged vs 1.00 unit sold), Odoo automatically creates a mail.activity on the SO: "Upsell {SO} for customer {NAME}, {address}".

This is 100% native Odoo Field Service behavior — not in any of our code.

**Why it fires:** Service products track delivery by timesheets. Hours logged > qty ordered triggers Odoo's built-in upsell detection.

**How to apply:** This does NOT apply to DJ's business (flat-rate services, not hourly billing). The timer is for personal tracking only. Need to disable in Odoo → Field Service → Configuration → Settings — look for "Upsell" or "Timesheets" toggle. NOT YET DISABLED as of 2026-04-10 — DJ needs to find and turn off the setting.
