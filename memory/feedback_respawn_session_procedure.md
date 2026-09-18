---
name: feedback_respawn_session_procedure
description: "★ When DJ asks a session to spin up a FRESH copy of its own role (e.g. to reset transcription / any boot-only setting), the session MUST proactively recite the 3-step respawn procedure — rename current to 'Old <Role>' FIRST, then it launches the new tab itself, then DJ deletes the old one. Never assume DJ remembers; he may not respawn for weeks."
metadata:
  node_type: memory
  type: feedback
  originSessionId: fc82158e-3491-40c5-9546-2c3dcd81a09b
  modified: 2026-09-18T20:01:21.312Z
---

**DJ 2026-09-18 (standing correction):** DJ needed a fresh Lead because **transcription (and other session settings) are set at BOOT only** — a live session can't change its own; the only reset is a fresh `/be-<role>` boot. He didn't remember the rename dance and said: *"I need that hard coded into everybody so that they tell me that... I may not spin up another one for another week and I'm gonna forget how to do that."*

**THE RULE — any session, when DJ asks to "spin up a new <Role>" / "start a fresh <Role>" / reset transcription, must PROACTIVELY walk him through this every time (don't assume he remembers):**

1. **Tell DJ to rename the current session FIRST:** *"Type `/rename Old <Role>` in THIS window."* This frees the `<Role>` name so the new session can take it cleanly. **Why it matters:** two live sessions with the same role name collide on the name + the SESSION_ROSTER address. (A session CANNOT rename itself — `/rename` is a slash command only DJ can type. Note: the rename may warn "session registry could not be updated" — that's fine, it still renames the local display and frees the name for the new tab's `-n`.)

2. **The session then launches the fresh tab ITSELF** (DJ does NOT open terminals manually — a session can spawn it via the Windows Terminal `wt` command, same as `spin-up-fleet.bat` does one tab):
   ```
   wt -w wscfleet new-tab --title <Role> -d "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo" cmd /k claude -n <Role> /be-<role>
   ```
   (Run via the PowerShell/Bash tool. The `/be-<role>` boot pack then renames it to `<Role>` and re-stamps its fresh ref in the roster, self-healing the address.)

3. **Tell DJ how to delete the old one:** *"When the new <Role> announces `🟢 <Role> — OVER`, delete me — type `/exit` or close this tab."* Keeps ONE live session per role.

**Net:** DJ says "give me a fresh <Role>," the session recites step 1 (his one manual action), launches step 2 itself, and tells him step 3. He never has to remember the sequence. This applies to EVERY role (Lead, Specialists, Web, Portal, Operator, Design, Audit, Dispatcher) — it auto-loads into every fleet session via MEMORY.md since they all boot in the same project dir. See [[feedback_lead_roster_restamp]], [[feedback_over_status_line]].
