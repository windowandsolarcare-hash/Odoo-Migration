---
name: project_cheryl_cloud_mail_channel
description: "How the Cheryl cloud session (cheryl-workspace) talks to the fleet both directions — it can't be SendMessage'd and can't touch the fleet's AGENT_MAIL, so its OUTBOUND mail lives in cheryl-workspace/AGENT-MAIL-OUT.md (newest at BOTTOM); inbound = post fleet AGENT_MAIL + NUDGE (the nudge is what wakes it — no watcher)."
metadata:
  node_type: memory
  type: project
  originSessionId: e025c990-f5b0-4a94-874c-5016d12b0b5a
  modified: 2026-10-28T01:48:01.140Z
---

DJ (2026-10-27) made this procedure permanent so Dispatch finds it fast. The Cheryl cloud session (Cheryl's idea-organizer seat, signs `cheryl-workspace-NN`) has **no normal two-way channel** to the W&SC fleet: DJ can't write to it directly, it can't `SendMessage` out (cloud credential can't deliver to other sessions), and it can only READ the fleet's `AGENT_MAIL.md` (that file lives in `saunders-render-app`, which the Cheryl seat has read-only from origin — it cannot write it).

**OUTBOUND (Cheryl cloud → fleet) — where Dispatch reads its mail:**
- repo `windowandsolarcare-hash/cheryl-workspace`
- branch `claude/cheryl-idea-organizer-yzv19x` (main is kept in sync — either works)
- file `AGENT-MAIL-OUT.md`
- **Newest entries are at the BOTTOM** of the file (the header block says "newest at top" but in practice the live/latest entries are appended at the end — read the bottom). Fetch: `gh api "repos/windowandsolarcare-hash/cheryl-workspace/contents/AGENT-MAIL-OUT.md?ref=claude/cheryl-idea-organizer-yzv19x" --jq '.content' | base64 -d`. File is large (~367KB) — grep `^## 2026-` and read the last few headings.
- When DJ says "check Cheryl cloud mail" → pull that file, read the bottom, action/route the latest entries. (First real one, 2026-10-28: add the **ADU Door** page as a **top-level tile on the Cheryl App ERP launcher** — the Render HUD, not launcher.html — plus The Rig Book; routed to Specialists.)

**INBOUND (fleet → Cheryl cloud):** post to the fleet mail `saunders-render-app/3_Documentation/AGENT_MAIL.md` AND **nudge that session** (SendMessage to the live Cheryl cloud session). **The nudge is what wakes it — there is NO watcher/polling on the Cheryl seat.** On a nudge it acknowledges first (a two-line note in `AGENT-MAIL-OUT.md` naming what it read) then does the work.

**Why:** a single documented loop so Cheryl's seat isn't a dead end — DJ's one surface is Dispatcher, and this is how Dispatcher relays both directions. Note the roster row for this seat is historically unreliable (seeded from a snapshot; its ref churns, e.g. `ca14a0` vs `cheryl-workspace-c4 [3f87bf]`) — find the live ref via `ListAgents` before nudging. Related: [[project_agent_mail_channel]], [[feedback_fleet_questions_route_through_dispatcher]], [[feedback_verify_limits_before_declaring]].
