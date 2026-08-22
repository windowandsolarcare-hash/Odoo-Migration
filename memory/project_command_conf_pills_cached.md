---
name: project_command_conf_pills_cached
description: Command Center (v2_command.html) confirmed/accepted/acknowledged pills were blank for 7-10s on every login because the state maps were in-memory only. Now cached in localStorage + hydrated synchronously.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-11T14:11:00.528Z
---

**Symptom (DJ, 2026-08-11):** Every log out / log back in, the Command Center schedule came up with today's jobs NOT showing the ✓ CONFIRMED label, then it appeared 7-10s later. DJ: "the cached version should have had the confirmed label — I don't want to wait."

**Root cause:** v2_command.html renders jobs **cache-first** from IndexedDB (instant), but the status maps `_SCHED` / `_CONF` / `_ACK` were plain in-memory JS objects reset to `{}` on every page load. The confirmed/accepted/ack pills only populate after `loadSchedStates()` fetches `/api/sched/states` (6s timeout + field-signal latency). So the instant cached job render had blank pills until the network answered. Classic async-init race (CLAUDE.md rule 13).

**Fix (commit 65a1b7b):** persist the three maps to localStorage key `wsc_cc_states` (`{sched,conf,ack}`) inside `loadSchedStates()` via new `_saveSchedStates()`, and **hydrate them synchronously** at script load (IIFE right after the `var _SCHED/_CONF/_ACK` decls) BEFORE first render. Now the first cache render already shows ✓ CONFIRMED / Accepted / Acknowledged; the background fetch refreshes + re-saves. Confirmations are durable server state so a cached flag is accurate; the refresh corrects the rare un-confirm.

**Scope:** Command Center ONLY. v2_field.html does NOT render confirmed pills on the schedule LIST — it loads confirm state per-job when a job detail is OPENED (`loadSchedState(soid)`), so it has no equivalent blank-pill-on-list gap. See [[project_status_scheduled_now_confirms]].
