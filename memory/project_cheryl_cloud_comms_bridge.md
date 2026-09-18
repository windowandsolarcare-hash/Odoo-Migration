---
name: project_cheryl_cloud_comms_bridge
description: "The fleet is 7, not 6 — the 7th is Cheryl's cloud (Cheryl-repo, cloud, Cheryl-only, one-way comms). Lead is the communicator/relay between her and the six. Plus the mail-as-record vs message-as-nudge discipline DJ re-stressed."
metadata: 
  node_type: memory
  type: project
  originSessionId: f880d1bb-9267-4822-b2b2-324215c0ff46
  modified: 2026-09-17T23:59:42.423Z
---

DJ 2026-09-17, defining the fleet during the boot-pack build. **The fleet is SEVEN sessions, not six.** The six local roles (Lead, Specialists, Audit, Design, Web, Portal, Operator — that's the local set) PLUS a **7th: "Cheryl's cloud".**

## Cheryl's cloud (the 7th)
- Lives in **Cheryl's repo**, runs as a **cloud** session, and deals ONLY with Cheryl's stuff.
- **Comms are poor because it's cloud, not local** — cloud sessions are one-way (they receive, they cannot `SendMessage` back). See [[project_fleet_role_boot_identity]] (why DJ keeps the fleet local: SendMessage two-way).
- **THE BRIDGE = Lead's job.** Lead is the communicator between Cheryl's cloud and the other six:
  1. Cheryl's cloud **writes to a file in her repo** (her `AGENT-MAIL-OUT.md`, on her branch — NOT main).
  2. **Lead watches/checks it periodically (~15 min)**, reads new entries.
  3. Lead **copies the content into AGENT_MAIL.md** (the fleet's record) so the rest of the fleet can see it.
  4. If it's for a specific role (e.g. Specialists), Lead **`SendMessage`s that session "read the mail."**
- The roster row for Cheryl's cloud cannot self-heal (no main write) — reach it via her AGENT-MAIL-OUT.md or via DJ. See the SESSION_ROSTER lessons.

## ★ MAIL-AS-RECORD vs MESSAGE-AS-NUDGE (DJ re-stressed, 2026-09-17)
The whole point of the protocol: **the durable content goes in AGENT_MAIL.md (the RECORD); the SendMessage is only a NUDGE that says "read the mail."**
- **Do NOT put a documentable instruction only in a SendMessage** — a message dies with the session; it never becomes a record. Write it to AGENT_MAIL first, THEN nudge.
- **Lead's known failure mode:** getting "short-cutty" — just messaging instead of documenting. That's acceptable ONLY for throwaway/non-documentable "just get this across" notes. Anything that needs to persist or be a record MUST go through AGENT_MAIL.
- This is the same family as the fleet-identity lesson: **must-persist things need a durable mechanism, not a session-bound message.** See [[project_agent_mail_channel]], [[feedback_durable_watcher_not_session_cron]].

## Operator endpoints-mandatory (DJ re-stressed same convo)
Operator (and ANYONE doing ops, incl. Lead) must act via the app's OWN endpoints, NEVER raw Odoo writes — a raw job-create skips job-number/date formatting + the whole logic chain and is silently wrong. **Leads have broken this by adding jobs raw; Operator almost never does.** Baked into the Operator + Lead boot packs. See [[feedback_assistant_use_app_workflow_not_raw_api]], [[project_new_job_via_app_endpoints]].
