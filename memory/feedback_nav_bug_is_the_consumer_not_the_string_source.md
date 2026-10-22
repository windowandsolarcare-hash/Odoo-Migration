---
name: feedback_nav_bug_is_the_consumer_not_the_string_source
description: "A street-ish string is a nav/geocode bug ONLY if its CONSUMER is a Navigate destination — trace the data flow forward to navUrlForJob, don't rank the string's build site."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-22T16:06:17.407Z
---

When auditing a nav / map mis-geocode bug, a partial or name-parsed address string is only an **offender if its CONSUMER is a Navigate destination** (a Google-Maps `dir/?api=1&destination=` URL, `navUrlForJob`, or a payload field a Navigate button reads — `nav_addr`/`address`/coords). Where the string is BUILT tells you nothing; where it is CONSUMED decides it.

**Why:** 2026-10-22 nav mis-geocode sweep — I flagged both `_find_invoiceable_sos_for_partner` twins (field.py ~3283/3324 + dashboard.py ~5012/5056, the `pid[1].split(',',1)[1]` street-only name-parse) as Tier-1 nav offenders while noting their consumer was unconfirmed. A firsthand trace (Specialists caught, Lead confirmed) showed that `address` feeds ONLY the `record_check_payment` clarify TEXT label (dashboard.py ~2274, "• SO X — $Y — @ addr") — never a Navigate. So they are **cosmetic display**, not nav bugs (my own "keep cosmetic display" call applied — I just didn't apply it to myself). Over-ranking a string's build-site as a nav offender wastes the fix's scope and, under §9 "fix the whole class," risks consolidating the WRONG class. The actual gap was a DIFFERENT class: `api_so_history` (dashboard.py ~5508) returns `street,city` only with NO `nav_addr`/coords, and `openJobById` passes only `address` through on the deep-link job-open — i.e. **job-open/nav-payload builders that feed `navUrlForJob` without `nav_addr`/coords.**

**How to apply:** for any suspected nav/geocode offender, grep FORWARD from the string to its render/consumer and confirm it reaches a Navigate before ranking it. If the only consumer is a text label, a form prefill, or a customer-facing display, it is cosmetic — leave it (keep-cosmetic-display). The correct offender class for "wrong door" nav bugs is **every payload builder feeding `navUrlForJob` (or a maps `dir` URL) that lacks a full-structured `nav_addr` + coords** (the canonical source is `_nav_by_partner`, dashboard.py:4983 — coords + `street, city, state zip`). The earlier build-site sweep still earned its keep: it found the genuinely-uncovered TECH app surface (static/tech/app.html — no tech-side `nav_addr` producer at all; Navigate falls back to the SO name / customer name). See [[feedback_auditor_user_perspective_gapfinder]] and [[feedback_check_endpoint_map_first]].
