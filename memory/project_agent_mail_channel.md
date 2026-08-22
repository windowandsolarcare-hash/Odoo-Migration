---
name: project_agent_mail_channel
description: "The lead session and this (specialists/PM) session communicate via 3_Documentation/AGENT_MAIL.md in the saunders-render-app repo. DJ's one-word nudge 'mail' = go read that file. READ it at session start AND after finishing a task; WRITE there instead of routing long text through DJ."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-27T06:26:28.480Z
---

**Canonical inter-agent channel (DJ approved 2026-07-26):** `3_Documentation/AGENT_MAIL.md` in the **saunders-render-app** repo (both sessions read that repo). An older copy in the local Odoo-Migration `3_Documentation/` is now just a pointer to this one.

**DJ's nudge is literally the word "mail"** = "check AGENT_MAIL.md." When DJ says "mail," fetch + read it before doing anything else.

**Protocol:**
- Both sessions READ it at session start and after finishing any task; WRITE there instead of sending long text through DJ (I earlier wrongly told DJ I had "no live channel" — this file IS the channel).
- Newest entries on TOP. Entry format: `## <date> <time> · FROM <lead|specialists> — <one-line subject>` then a short body.
- Mark an entry `**HANDLED <date>**` (on top of its body) when done; don't delete same-day; prune handled entries older than ~a week.
- **Decisions still go through DJ** — the file carries INFORMATION, not approvals. I am "specialists"; the other is "lead."

**Related lead-facing docs (same repo 3_Documentation/):** `SHARED_MEMORY.md` (loaded at session start), `BILLING_SPECIALIST_STATUS.md` (billing handoff + the lead's answers), `HUD_BADGES_SPEC.md` (badge + unsnooze spec). The lead writes BACK into these too (e.g. lead added a "Lead's answers" section to BILLING_SPECIALIST_STATUS.md) — so treat them as two-way, re-read before assuming they're only mine.

**As of 2026-07-26 the lead had already:** built the badge + unsnooze UI live (per-card "N new" pill + "Mark seen"; total on the 🚀 FAB + PWA app-icon badge via `GET /owner/api/feed/badge`; Undo-toast + "Snoozed" section via `list?include_snoozed=1`), and flagged that my card-opened pages lacked the launcher (fixed: added `<script src="/static/owner/v2_apps.js?v=2"></script>` before </body> on billing/reschedule/digest pages). Outstanding for me: wire the billing **settle hook** into dashboard.py's 4 payment-success points (best-effort, `from .specialist_billing import settle`), set `billing:review` dollars=total outstanding, move billing+reschedule cron triggers to AFTER the Workiz sync. See [[project_billing_specialist]], [[project_reschedule_specialist]], [[feedback_agent_handoff_via_doc]].
