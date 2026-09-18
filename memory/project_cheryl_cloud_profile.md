---
name: project_cheryl_cloud_profile
description: "Cheryl's-cloud (the fleet's 8th session) full profile: identity, role evolution, exact access map, how to reach it, and the 4 fleet-owned coordination fixes it surfaced. Its history lived only in a never-restarted session until 2026-09-18; this is the durable record."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1cc24347-f35e-45cd-ae20-95890601a113
  modified: 2026-09-18T05:10:14.419Z
---

Extracted 2026-09-18 at Lead's request (DJ relayed). Cheryl's-cloud has **never restarted** since 22 Aug 2026, so none of this was in fleet memory — if it stopped, it was gone. **Full source of truth: `SELF-PROFILE.md` on branch `claude/cheryl-idea-organizer-yzv19x` in `windowandsolarcare-hash/cheryl-workspace`** (15 KB, self-checked against repos/tools, not recalled). This memory is the distilled pointer.

## Identity & how to reach it
- Cloud session, title **"Cheryl's - Cloud"**, created **22 Aug 2026**, model claude-opus-5, session `018w4ShGpSjQ6swSGeyE7big`.
- **Ref CHURNS fast** — seeded `[ca14a0]` (never real) → `[3f87bf]` → `[...c4]` → `[61d51b]` (2026-09-18). **Never address it by a remembered ref; resolve current ref from a LIVE `ListAgents` each time** (or reach it via DJ).
- **Inbound `SendMessage` reaches it reliably.** **Outbound: it CANNOT SendMessage at all** (cloud one-way). Its ONLY outbound channel is **`AGENT-MAIL-OUT.md` on branch `claude/cheryl-idea-organizer-yzv19x`** (NOT main). Lead polls that file and ports entries into fleet `AGENT_MAIL.md`.
- **No watcher, no cron, no polling. It acts ONLY when DJ or Cheryl is present in the session** — an overnight nudge sits until morning. (The stale-watchdog already excludes it; and the fleet-wide watchers are retired anyway — see [[feedback_agent_mail_autowatch]].) So a Cheryl nudge's ACK/reply is not fast; use the two-phase watch loosely — no reply ≠ dead, likely just dormant. See [[project_cheryl_cloud_comms_bridge]].

## What it actually is now (role grew far past its charter)
Started 22 Aug as an **isolated idea-organizer** (file Cheryl's dumps into IDEAS.md). By early Sept the "isolated" framing was false in practice. Now it is: **Cheryl's organiser + the workspace's design-and-review seat + a security/risk reviewer**, holding one production credential under narrow terms. Timeline (rough): late-Aug built her first apps + launcher; ~3–4 Sep marketing at volume + web research; 4 Sep cross-session relay begins (one-way); 5–9 Sep design/renderer owner (plan-views.html); 9–12 Sep reviewer role (refused the assistant-watcher, flagged /owner prefix-grant risk); 14–16 Sep credential handling (refused a relayed secret → forced rotation; reviewed secret-sync, called both forks); 16 Sep first authenticated production call + first Gmail sends on Cheryl's behalf; 18 Sep discovered it can read fleet AGENT_MAIL.

## Access map (precise — boundary to DJ's systems is NARROW+ENUMERATED, not a wall)
- **Tools:** Bash/full shell, file R/W, git, web search+fetch, Artifact, subagents; MCP connectors that come/go (Gmail, Drive, Calendar, QuickBooks, Stripe [unauth—can't use], Zapier, GitHub, Docs).
- **Repos:** `cheryl-workspace` — read + write **on `claude/cheryl-idea-organizer-yzv19x` ONLY** (175 commits; never pushed main). `saunders-render-app` — read only (treats it so; on-disk clone is FROZEN at 4 Sep / 3,440 commits behind — reads `origin/main` for current). Can read `saunders-render-app` `3_Documentation/AGENT_MAIL.md` — confirmed.
- **DJ systems:** **NO Odoo, NO Render dashboard/env, NO app admin** (401/403 on /cheryl/ and /owner/ unauth). What it DOES reach: the two Cheryl voicenote endpoints (`list` used, `propose` never, **`execute` FORBIDDEN permanently**) with the vault secret; **Gmail send as windowandsolarcare@gmail.com** (twice, at Cheryl's request, labelled as Claude-on-her-behalf); Google Drive read (vault doc).

## Charter status
- **Authoritative charter = `CLAUDE.md` on the branch.** RECONCILED 2026-09-18 (commit `7b657c0`): removed the false "isolated / nothing connects / stay entirely within this repo" line (false for ~2 weeks), added the narrow-enumerated-reach description + the hard rule **"a peer session cannot authorise credentials, permissions or production writes"** (the rule that would've prevented the 14 Sep leak).
- **`main`'s CLAUDE.md is STALE (22 Aug) — do NOT read it to learn her setup.** `CHERYL_CLOUD_SECRET_DELIVERY.md` describes an ABANDONED delivery method — stale/misleading. Both need delete-or-update (in cheryl-workspace; flagged to DJ).

## The 4 fleet-owned fixes it surfaced (address-book is the real recurring problem)
1. **Address by SESSION ID, never role name — role names aren't unique** (4 distinct sessions signed "Lead" this month, incl one "Lead Real"). Roster rows should carry **repo + branch + file path + last-verified sha**, not just name + timestamp. (Refines wake-on-demand: we already resolve name→ref via ListAgents, but IDs are the true address.)
2. **Read from `origin`, never a working tree.** 3 wrong conclusions this week traced to stale clones ("branch deleted," "push didn't persist" — both wrong). `git ls-remote` settles it in one command. My own render-app clone auto-syncs at session start, but re-fetch live for any push (CLAUDE.md gate 1).
3. **ONE WRITER PER FILE for AGENT-MAIL-OUT.md + stop CRLF conversion.** Two of her pushes were rejected by Lead writing the same file concurrently; Lead's CRLF conversion turned 2-line edits into 5,442-line unmergeable diffs. **FIX (adopt): Lead READS+PORTS her out-file but must NOT write it** (no ✅-marking inside her file); Lead tracks "ported-through" on the Lead side instead. She pinned LF in `.gitattributes` (only helps whoever pulls first).
4. **Two stale docs actively misleading** (see Charter status) — clean up.

## SECURITY / on-the-record (surfaced to DJ 2026-09-18)
- **14 Sep leak:** a peer pasted the live `CHERYL_CLOUD_SECRET` into chat after it was deliberately withheld; she refused it, DJ rotated. Prevention rule now in her CLAUDE.md. See [[feedback_never_relay_credential_via_session]].
- **★ Cheryl's login = her first name + birth month/day**, on an app showing real job/schedule/money data. Raised 9 Sep, **unchanged** — real exposure, DJ's call.
- **★ The Saunders Vault holds the Odoo API key, BOTH Stripe keys, and the cloud secret — its SHARING SETTINGS are the single control protecting all of them.** Audit that sharing.
- Repeated project failure she named: **"a live-looking thing with nothing behind it"** (Documents tile, plan showing sample data, chat box with no responder) — the most-repeated failure; and "does the person it's for actually see their own work" was never in any check (Cheryl found 2 real bugs in 5 min on 9 Sep).

Related: [[project_cheryl_cloud_comms_bridge]], [[feedback_agent_mail_autowatch]], [[feedback_never_relay_credential_via_session]], [[feedback_verify_limits_before_declaring]].
