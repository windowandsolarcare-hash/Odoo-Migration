---
name: project_dnc_false_positive_dj_number
description: "DJ's own number 9519726946 was on the phone blacklist → falsely flagged Personal Time + Dan Saunders as DNC. phone_blacklisted is SHARED across every partner with the same number."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

# DNC false-positive root cause: DJ's own number was blacklisted (fixed 2026-07-14)

The DNC-sweep false positives (Personal Time blocks ×6, Dan Saunders ×2 getting their SOs cancelled) all traced to ONE thing: **phone `9519726946` (DJ's own cell) was on the phone blacklist** — `phone.blacklist` record **id 17 = `+19519726946`, active=True**.

**Key mechanism:** `phone_blacklisted` on `res.partner` is a **computed field off the shared phone number**, not a per-record flag. Any partner whose `phone`/`mobile` equals a blacklisted number reads `phone_blacklisted=True`. That number sat on THREE W&SC partners at once — Personal Time (23054), Dan Saunders (19582, company False), Dan Saunders (3, company 1) — so all three read DNC even though `x_studio_activelead='Active'` on every one. `_dnc()` = `activelead=='Do Not Contact' OR phone_blacklisted`, so the blacklist alone tripped it. See [[project_do_not_contact_forward_looking]].

**Fix applied:** archived `phone.blacklist` id 17 (`write active=False` — keeps the audit row, removes it from the live blacklist). Verified all three partners then read `phone_blacklisted=False`. To un-blacklist any number: `phone.blacklist search number in ['{10dig}','+1{10dig}','1{10dig}'] (active_test:False)` → `write active=False`. active=False (archive), NOT unlink, so the opt-out history stays.

**How it got there:** unknown — likely a test STOP text or a manual STOP from DJ's own phone at some point. Watch for it: if Personal Time / DJ's own records ever get swept as DNC again, first check whether `9519726946` is back on the blacklist before touching any sweep logic.

**Lesson for future sweeps:** before cancelling/excluding on `phone_blacklisted`, sanity-check the number isn't a shared/internal one (DJ's cell, a Personal-Time placeholder). Better: exclude Personal Time / internal partners from DNC sweeps by name/job_type regardless of blacklist state.
