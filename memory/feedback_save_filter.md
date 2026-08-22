---
name: SHARED_MEMORY save filter — save at the right time, not all the time
description: DJ wants me to keep auto-saving (he doesn't want to invoke a skill). But filter what goes into SHARED_MEMORY so it doesn't bloat Render Claude's context.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
DJ confirmed 2026-04-26 that he wants me to keep auto-saving discoveries to SHARED_MEMORY (per the dual-write rule in CLAUDE.md). He does NOT want a `/save` slash command he has to invoke. The behavior is mine to own.

**His one ask:** be deliberate about WHEN — save at the right time, not all the time.

**Why:** SHARED_MEMORY loads into Render Claude's context every session. Bigger file = bigger system prompt = more tokens per query = costs DJ money. Same cost concern that came up with API-key spend.

**The filter to apply before each SHARED_MEMORY write:**

GOES IN:
- Workiz/Odoo API quirks Render Claude calls against (UUID-in-body, SubStatus parent, defaults required)
- Field name conventions, field defaults
- Status models, business rules DJ explicitly stated
- Tool semantic changes Render Claude needs to know (new tool exists, tool now copies extra fields)

STAYS OUT (local memory only):
- Implementation architecture (where session history lives, internal helpers)
- Why-we-fixed-it commit history (git log covers this)
- My debugging notes
- Things already in SHARED_MEMORY (don't duplicate)
- Things already in Render Claude's system prompt (don't restate)

**The test question:** "Does Render Claude need to know this AT RUNTIME to behave correctly?" If no, it's local memory only.

**Volume calibration:** typical days produce 1–2 SHARED_MEMORY-worthy discoveries. A day with 5+ is unusual (today 2026-04-26 was that — five Workiz fixes in a row). When volume is high, it should be because the DAY had many genuine discoveries, not because I'm dual-writing aggressively.

**If DJ ever asks "why are you saving so much?":** lead with the cause (today's discoveries) rather than jumping to "let me change the behavior." He may just want the explanation, not a fix.

**How to apply:** Before pushing any SHARED_MEMORY edit, run the filter mentally. If a candidate fails the filter, save it as local-only and skip the dual-write. Don't ask DJ — own the judgment.
