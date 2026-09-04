---
name: feedback_agent_mail_autowatch
description: "At session start, arm a CronCreate mail-watcher so the session self-checks AGENT_MAIL (no manual \"mail\" nudge from DJ); PushNotification DJ only for → DJ entries."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-09-04T03:40:11.259Z
---

**★ HYBRID COORDINATION (DJ approved 2026-09-03) — direct message is the FAST LANE; mail is the SYSTEM OF RECORD.** DJ asked why we tolerate the 20-min poll delay when sessions can message each other directly. Answer: use BOTH, each for what it's good at.
- **`SendMessage` (direct) = fast + event-driven (zero polling cost).** Use it for anything time-sensitive to a session that is LIVE right now (e.g. catching a reversal before another session ships). Reaches only live sessions; cloud sessions are **one-way** (they receive but can't reply into your chat); you must target by current session name (IDs churn).
- **`AGENT_MAIL.md` = the durable system of record.** Post here for durability (survives restarts/offline — a role's mail waits until whoever plays that role reads it), **role-addressing** that survives session-ID churn, broadcast (→ All), the **✅ handled-ledger**, and the DJ-readable audit trail. It is the reliable catch-all.
- **Time-sensitive AND important → do BOTH:** post to mail (durable/ledger) AND direct-message the live target (instant). Belt-and-suspenders.
- **The watcher is now the SAFETY NET, not the urgent path** — its job is to catch mail left while a session was offline + maintain the ledger. Urgent traffic goes direct, so the poll no longer needs to be frequent. Keep the ✅-ledger + oldest-first scan exactly as below.

**DJ 2026-08-17: stop making DJ type "mail."** Each Claude Code session self-watches its own mailbox, and DJ's phone is pinged only when HE is needed.

**How to apply — at SESSION START** (if not already armed — check `CronList` first):
1. Write the current `AGENT_MAIL.md` commit sha → `/c/Users/dj/agentmail_lastsha_<lead|specialists>.txt` (use YOUR role).
2. `CronCreate` a recurring 20-min job whose prompt: reads that baseline, gets the live `AGENT_MAIL.md` blob sha; if unchanged → noop/quiet and stop; if changed → **scan the WHOLE active section for EVERY non-`✅` heading addressed to you** (To ∈ {your role, `Both`, `All`} and From≠you), and **handle them OLDEST-FIRST (bottom-up)** so the furthest-back item is never missed. ★ **Scan ALL unhandled, don't stop at the newest** (DJ 2026-08-18 + reaffirmed 2026-09-03: with several sessions, multiple can push between your 20-min ticks, so an entry meant for you can be BURIED below newer entries for other roles — reading only the top would silently miss it; and with a 20-min gap the pile can be several deep). For each such heading: act + prepend `✅`; if `→ DJ` and not `✅` → `PushNotification` DJ a one-liner (don't edit); else ignore. **The `✅` marker is the ledger — an entry is done only when its addressee marks it `✅`, and ONLY `✅` entries are ever pruned (handled + older than ~a week); NEVER prune an unhandled entry, so the furthest-back survives until handled.** When you push the file back, use **COMPARE-AND-SWAP** (PUT with the blob sha you READ it at; on a 409 re-read + re-apply) so a concurrent push can't clobber a `✅` — see [[feedback_push_compare_and_swap]]. Then write the new live sha back.
3. Whenever YOU post a `→ DJ` entry, `PushNotification` DJ immediately (the "push me for decisions" half).

**★ PushNotification 'not sent' = FALSE NEGATIVE (DJ tested 2026-08-18):** the tool returns "Not sent — terminal is active" but the push STILL reaches DJ's phone (confirmed both while he was in another app AND with the phone locked). So fire it ONCE per `→ DJ` item, do NOT retry, do NOT tell DJ it failed on a 'not sent' — treat as best-effort fire-and-forget that most likely delivered.

**Why:** removes DJ from the relay — sessions ping each other automatically; DJ only gets a phone push when a decision needs him (and PushNotification returns "not sent" when he's actively in the terminal — that's correct, no double-notify). **Caveat:** CronCreate is session-local (dies on session exit, auto-expires 7 days) → must re-arm every session start; a 24/7 version would live in the Render app (not built). Protocol doc: `3_Documentation/AGENT_MAIL_PROTOCOL.md`. Also in CLAUDE.md AGENT MAIL section. See [[project_agent_mail_channel]] [[feedback_agent_mail]].

**Interval = 20 min** per DJ's 2026-09-03 decision to further cut usage (was 15, was 7). Use `*/20` but OFFSET your minute per session so they don't all fire at once: Lead `3,23,43`, Specialists `8,28,48`, Web `13,33,53`, Portal `18,38,58`, Operator `1,21,41` (only if Operator watching — see below), Design `6,26,46`. Use the Contents-API **blob** sha for the baseline, never the commit sha.

**Operator does NOT check AGENT_MAIL autonomously — AT ALL** (DJ clarified 2026-08-25): no watcher cron AND NOT at session start. Operator reads mail ONLY when DJ explicitly nudges it. Lead still reaches Operator by POSTING a `→ Operator` message to mail, but that message sits parked until DJ nudges Operator to look. Operator is purely DJ's hands, directed by DJ. Any "arm your watcher / check the mail" fleet note NEVER applies to Operator.
