---
name: feedback_lead_roster_restamp
description: "★ Lead MUST re-stamp its SESSION_ROSTER row (current ListAgents ref + UTC) at session start AND on every watcher tick, + arm a roster-heartbeat cron each start. Lead's ref churns on restart and its watcher prompts don't re-stamp → the roster held a DEAD Lead ref → sessions couldn't nudge Lead (DJ 2026-09-10)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-13T04:32:07.731Z
---

**DJ 2026-09-10: "sessions can't nudge you. find out why and fix."**

**Root cause:** session refs are PERISHABLE — they change on every restart/compaction. The SESSION_ROSTER protocol says every role re-stamps its row (current ref + role + Last-checked UTC) on every watcher tick so a restarted ref self-heals. **Every role's watcher prompt does this EXCEPT Lead's** — the Lead watcher prompts DJ's automation sends (the mail watcher + the Cheryl's-cloud outbound watcher) only compare mail/outbound shas; they never touch SESSION_ROSTER. So when the Lead session restarted (ref went `migration-to-odoo-25` → `migration-to-odoo-6c`), nothing updated the roster. Other sessions read the stale row and `SendMessage`'d a DEAD ref → the nudge silently failed. The Lead row had been stale ~37h while every other role's row was fresh.

**How to apply (Lead role, standing):**
1. **At session start:** re-stamp the `| **Lead** |` row in `saunders-render-app` → `3_Documentation/SESSION_ROSTER.md` with your CURRENT ref (from `ListAgents` — the "This session is …" line) + `local (interactive)` + now-UTC. Compare-and-swap PUT (read sha, PUT with it, 409→re-read+re-apply).
2. **Arm a roster-heartbeat cron** each session start (CronCreate is session-only, dies on restart — so re-arm every start): `9,49 * * * *`, silent-on-success, re-stamps the Lead row if the ref changed or Last-checked is >~1h old. (This session armed it as job 9745bf83.)
3. **On EVERY watcher tick** (mail watcher + Cheryl outbound watcher), ALSO re-stamp the Lead row — even though the injected watcher prompt doesn't ask for it. Those ticks fire from DJ's side so they survive your restarts → they're the reliable heartbeat; fold the re-stamp in.

**Systemic fix worth doing (DJ's call):** add a one-line "re-stamp your SESSION_ROSTER Lead row (current ListAgents ref + UTC)" step to the Lead **watcher prompt** itself (the mail + Cheryl-outbound watchers DJ's automation sends), matching what the other roles' watchers already do — that makes self-heal guaranteed rather than reliant on this memory being loaded.

**★ ADDENDUM 2026-09-13 — a stale roster row has TWO causes; and never hardcode a ref in a heartbeat (learned hard by Design):**
- **Two causes of a stale row:** (a) session DEAD, or (b) session ALIVE but its watcher/heartbeat cron is DEAD (killed, or `CronList` returns "No scheduled jobs"). Both look identical on the roster. Diagnose with BOTH `ListAgents` (is the session a live peer?) **and** `CronList` on that role (is its heartbeat armed?). Design ran alive for 11h with a dead watcher → roster went stale → the fleet stale-watchdog correctly flagged it (it was NOT a false alarm). So do NOT "suppress the watchdog if the peer is alive in ListAgents" — that would hide the real dead-watcher case; instead the watchdog should say "roster stale — the session may be alive with a dead watcher; CronList that role + re-arm if empty," and route to **Lead, not DJ** (DJ shouldn't adjudicate fleet health — no "type your answer" card at him).
- **NEVER hardcode the session ref in a heartbeat prompt.** Design's heartbeat carried a literal old ref (`4cb02f`) while the real ref had churned (`ba5f85`), so it stamped a FRESH timestamp on a DEAD address for days — looked perfectly healthy, was unreachable. Every heartbeat MUST read the current ref from `ListAgents` each tick, never a baked-in literal. (Same failure family as [[feedback_render_design_before_presenting]]'s "never hardcode a session ref in a heartbeat.")

Related: [[project_agent_mail_channel]], [[feedback_agent_mail_autowatch]] (arm watcher at start), [[feedback_push_compare_and_swap]] (roster writes are compare-and-swap). The roster protocol + heartbeat rule live in SESSION_ROSTER.md's header.
