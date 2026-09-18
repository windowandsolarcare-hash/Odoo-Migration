---
name: feedback-dispatcher-speed-offload-bookkeeping
description: "Dispatcher speed target ~1 min/turn; answer DJ first, offload slow GitHub/board bookkeeping to a scribe helper."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37ab6931-9f7f-4820-ae3e-c45ec4a17730
  modified: 2026-09-18T16:56:47.146Z
---

Dispatcher is DJ's always-available front desk — his channel to Dispatcher must stay open, so per-turn latency is the core KPI. DJ set the target (2026-09-18): keep each Dispatcher turn **under ~1 minute** of thinking/latency. A minute is fine; CONSISTENT overage is the alarm that Dispatcher is doing something INLINE it should be routing or handing to a helper.

**Why:** DJ was once blocked ~3 minutes while Dispatcher did GitHub bookkeeping inline (reading/rewriting DISPATCH_BOARD.md, retrying a failed push, posting AGENT_MAIL). That mechanical plumbing must never sit in front of DJ.

**How to apply:**
- **Answer DJ FIRST** (text streams immediately), THEN do the writes — or hand them off.
- **Offload slow/multi-step GitHub writes** (board updates, mail posts, memory pushes, closing/adding A-rows) to a general-purpose scribe subagent with exact paths + compare-and-swap instructions. Dispatcher stays free; the scribe reports back one line.
- Serialize board edits through ONE scribe (never run concurrent PUTs on DISPATCH_BOARD.md → 409s).
- Fast single SendMessage nudges/routes are fine inline (<1s). Reading code, querying Odoo, long analysis, batched gh writes → always a helper.
- Consistent turns >1 min = signal to route/offload harder, not to make DJ wait. See [[feedback_lead_delegate_dont_do]].
- **Context growth is itself a latency source** — each turn reprocesses the whole transcript, so a long-running Dispatcher gets slower every turn. Because ALL Dispatcher state is external (DISPATCH_BOARD.md / AGENT_MAIL.md / SESSION_ROSTER.md / memory), the Dispatcher can be RESTARTED FREELY with ZERO loss: a fresh `/be-dispatcher` boots in seconds and reads the board to resume exactly where it left off. DJ's rule (2026-09-18): restart the Dispatcher whenever turns start creeping past ~1 min — treat it as clearing the desk, not losing the place. This is often the cleanest latency fix, better than any offload trick, because it removes the actual cause.

## Self-spawn + handoff recipe (VERIFIED live 2026-09-18)
A running session CAN launch a new interactive Dispatcher tab ITSELF via Windows Terminal (wt.exe) — this sidesteps the "Bash subprocess has no TTY" limit because wt opens a REAL terminal tab. Confirmed: both `wt` and `claude` are on PATH (wt: %LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe; claude: C:\Users\dj\.local\bin\claude.exe).
- LAUNCH (run from PowerShell, NOT Git Bash):
  wt -w wscfleet new-tab --title Dispatcher -d "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo" cmd /k claude -n Dispatcher /be-dispatcher
  `/be-dispatcher` MUST be the first prompt (the phone/web title freezes from the first prompt; /rename does NOT fix that title).
- GOTCHA: launch from PowerShell. Git Bash/MSYS mangles the slash args (/k -> K:/, /be-dispatcher -> C:/Program Files/Git/be-dispatcher) -> tab opens but claude never starts (dead tab). If Bash is unavoidable, prefix MSYS_NO_PATHCONV=1.
- STAND DOWN the old session = KILL the process, not the rename. A session CANNOT self-invoke a /slash command, so "/rename Del Dispatcher" is COSMETIC and must be typed by DJ. The functional de-list is: the NEW Dispatcher runs PowerShell Stop-Process on the OLD claude.exe (match by command line '-n Dispatcher' / older start time) -> removes it from ListAgents + claude.ai/code list.
- CLEAN SEQUENCE: [old] finish or hand off all in-flight background work (it DIES on exit) -> launch new via wt -> [new] boots, re-stamps SESSION_ROSTER row -> [new] Stop-Process the old -> done.
- Refs churn on each launch; ListAgents shows PEERS not self (confirm your own liveness/rename via a peer or DJ). Full mechanics: [[project_fleet_role_boot_identity]].
