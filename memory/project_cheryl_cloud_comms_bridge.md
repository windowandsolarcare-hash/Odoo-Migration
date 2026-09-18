---
name: project_cheryl_cloud_comms_bridge
description: "The fleet is 7, not 6 — the 7th is Cheryl's cloud (Cheryl-repo, cloud, Cheryl-only, one-way comms). Lead is the communicator/relay between her and the six. Plus the mail-as-record vs message-as-nudge discipline DJ re-stressed."
metadata: 
  node_type: memory
  type: project
  originSessionId: f880d1bb-9267-4822-b2b2-324215c0ff46
  modified: 2026-09-18T00:21:35.436Z
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

## ★ CONFIRMED by DJ 2026-09-17 (fleet clarifications)
- **Specialists codes for Cheryl too.** Cheryl's cloud is NOT a coder — it routes its coding needs to **Specialists**, who owns/handles Cheryl's app code/repo as well as DJ's ERP app. Cheryl's cloud is Cheryl's non-coding, **security/risk-focused** session (analogous to what Operator is for DJ — hands/advisor, not builder); DJ values that it scrutinizes risk/security harder than any other session.
- **Domains (authoritative):** `windowandsolarcare.com` = the PUBLIC marketing site (Web owns it; everyone sees it). `wscare.pro` = the address of the **Render-hosted app**, whose customer-facing slice is the **customer portal** (branded pages texted via link; Portal owns it, Specialists may also touch it) + owner ERP + Cheryl's app behind login — NOT the marketing site. `scenicartprint.com` = Saunders Printing — currently DOWN as a website (bring-up stalled), used mainly for EMAIL; a separate in-system "Saunders Printing" APP is unrelated to that domain. See [[reference_domain_dns_hosting_map]].
- **Fleet watcher policy:** **Operator runs NO mail-watcher** (works directly with DJ; reads mail at start + on nudge). **Portal's watcher is ARMED** (2026-09-17 — portal work ramping; no longer on-demand). Other roles run their offset watchers per [[feedback_agent_mail_autowatch]].


## ★ TWO-PHASE Cheryl watch (DJ 2026-09-18) — split liveness from results
When Lead messages/nudges Cheryl's cloud and expects a reply, DO NOT arm a flat 15-min poll (you'd wait 15 min blind, never knowing if she even received it).
- **Phase 1 — LIVENESS (~2 min):** the instant you nudge her, arm a ~2-min watch on her AGENT-MAIL-OUT.md. If a quick "copy" appears -> she got it, she's alive, right session reached. If nothing after ~2 min -> she did NOT get it (dead / wrong session) -> retry or escalate to DJ, don't keep waiting.
- **Phase 2 — RESULT (~15 min):** ONLY after the "copy" lands, switch to the ~15-min watch, because now you're waiting on her actual work product, which takes longer.
- **DEPENDENCY (must be set up on HER side):** the local six ACK via SendMessage automatically; Cheryl can't SendMessage, so her "copy" is a WRITE to AGENT-MAIL-OUT.md. Her boot/charter must tell her: on ANY inbound nudge, FIRST write "copy — got it, working" to AGENT-MAIL-OUT.md, THEN do the task. Without that, the 2-min check finds an empty file even though she's alive. This mirrors the fleet-wide ACK rule (see [[feedback_agent_mail_autowatch]]) adapted for a one-way cloud session.
