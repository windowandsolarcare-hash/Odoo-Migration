---
name: Pending - review Cursor chat history for lost solutions
description: DJ needs to share old Cursor session history so we can extract historical bug fixes and failed approaches into CLAUDE.md — raise this at the start of the next session
type: project
---

DJ has Cursor chat history from before the Claude Code migration (pre 2026-03-19) that likely contains previously discovered solutions — things like Odoo safe_eval quirks, Workiz API behaviors, field name corrections — that were never formally captured.

**Why:** We rediscovered two known-pattern errors in this session (datetime.datetime.now() and action=False) that were probably solved before. Getting the Cursor history reviewed would prevent future sessions from hitting these again.

**How to apply:** At the start of the next session, remind DJ: "When you have time, can we go through your Cursor chat history to pull out any past bug fixes or failed approaches we haven't captured yet?" Don't push if DJ is busy — it's a when-you-have-time task, not urgent.
