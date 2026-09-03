---
name: feedback_agent_mail_autowatch
description: "At session start, arm a CronCreate mail-watcher so the session self-checks AGENT_MAIL (no manual \"mail\" nudge from DJ); PushNotification DJ only for → DJ entries."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-09-03T14:02:09.072Z
---

**DJ 2026-08-17: stop making DJ type "mail."** Each Claude Code session self-watches its own mailbox, and DJ's phone is pinged only when HE is needed.

**How to apply — at SESSION START** (if not already armed — check `CronList` first):
1. Write the current `AGENT_MAIL.md` commit sha → `/c/Users/dj/agentmail_lastsha_<lead|specialists>.txt` (use YOUR role).
2. `CronCreate` a recurring ~15-min job (`*/15 * * * *`) whose prompt: reads that baseline, gets the live `AGENT_MAIL.md` sha; if unchanged → "mail: no change" and stop; if changed → **scan the TOP ~40 entries (≈ head -260 lines), NOT just the newest** — act on EVERY unhandled entry addressed to you. ★ **Scan-deep, don't just read the top entry** (DJ 2026-08-18: with 4 sessions, two can push between your ticks, so an entry meant for you can be BURIED below a newer one addressed to someone else — reading only the top would silently miss it). For each heading in the window: if To ∈ {your role, `Both`, `All`} and not already `✅` and From≠you → act + prepend `✅`; if `→ DJ` and not `✅` → `PushNotification` DJ a one-liner (don't edit); else ignore. If you marked any `✅`, push the file back with a b64-length guard. Then write the new sha back.
3. Whenever YOU post a `→ DJ` entry, `PushNotification` DJ immediately (the "push me for decisions" half).

**★ PushNotification 'not sent' = FALSE NEGATIVE (DJ tested 2026-08-18):** the tool returns "Not sent — terminal is active" but the push STILL reaches DJ's phone (confirmed both while he was in another app AND with the phone locked). So fire it ONCE per `→ DJ` item, do NOT retry, do NOT tell DJ it failed on a 'not sent' — treat as best-effort fire-and-forget that most likely delivered.

**Why:** removes DJ from the relay — sessions ping each other automatically; DJ only gets a phone push when a decision needs him (and PushNotification returns "not sent" when he's actively in the terminal — that's correct, no double-notify). **Caveat:** CronCreate is session-local (dies on session exit, auto-expires 7 days) → must re-arm every session start; a 24/7 version would live in the Render app (not built). Protocol doc: `3_Documentation/AGENT_MAIL_PROTOCOL.md`. Also in CLAUDE.md AGENT MAIL section. See [[project_agent_mail_channel]] [[feedback_agent_mail]].

**Interval = 20 min** per DJ's 2026-09-03 decision to further cut usage (was 15, was 7). Use `*/20` but OFFSET your minute per session so they don't all fire at once: Lead `3,23,43`, Specialists `8,28,48`, Web `13,33,53`, Portal `18,38,58`, Operator `1,21,41` (only if Operator watching — see below), Design `6,26,46`. Use the Contents-API **blob** sha for the baseline, never the commit sha.

**Operator does NOT check AGENT_MAIL autonomously — AT ALL** (DJ clarified 2026-08-25): no watcher cron AND NOT at session start. Operator reads mail ONLY when DJ explicitly nudges it. Lead still reaches Operator by POSTING a `→ Operator` message to mail, but that message sits parked until DJ nudges Operator to look. Operator is purely DJ's hands, directed by DJ. Any "arm your watcher / check the mail" fleet note NEVER applies to Operator.
