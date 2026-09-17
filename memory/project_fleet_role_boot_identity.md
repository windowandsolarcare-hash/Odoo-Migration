---
name: project_fleet_role_boot_identity
description: "How the fleet survives a machine reset — per-role boot packs + /be-<role> commands + session naming, and WHERE each surface's session name populates from (the mobile-title discovery)."
metadata: 
  node_type: memory
  type: project
  originSessionId: f880d1bb-9267-4822-b2b2-324215c0ff46
  modified: 2026-09-17T23:22:01.278Z
---

**Problem (DJ 2026-09-17):** a machine reset/power-loss wipes all local sessions; rebuilding roles by hand is dread work. Worse, after a FULL restart the terminal is empty and `resume` shows sessions with useless auto-titles, so DJ can't tell which is which ("four said audit, two said lead") and has to resume each blind then ask "who are you?". Goal: minimal-input, reset-proof recovery.

**Verified Claude Code facts (v2.1.274, confirmed live this session):**
- `-n/--name <name>` and `/rename <name>` set a session **display name** — but it ONLY shows at the bottom of the terminal (the prompt bar). It does NOT change the tab title and does NOT change the phone/web list name.
- ★ **KEY DISCOVERY — where the mobile/web session name comes from:** it is the **AI-generated TITLE derived from the session's FIRST real prompt, and it is FROZEN at that point.** Proof: this session's first task was "re-arm the stale watcher crons" and the Claude Code mobile app listed it as "Rearm Stale Watcher Chrones" even AFTER `/rename Lead`. So `/rename` does not fix mobile; the first prompt does.
- **Terminal TAB title** is NOT set by Claude Code at all (stays "C:\Windows\System32\cmd..."). Only fix = the launcher sets it: `wt new-tab --title <Role>` at open. `/rename` won't touch it.
- **`resume` restores the ACTUAL prior session** (full context/memory intact) — so for the restart case we don't need to re-boot from a pack; we just need to IDENTIFY which is which. Resume by id/name: `claude --resume <id|name>` (cross-project in v2.1.223+). Transcripts: `~/.claude/projects/<project>/<session-id>.jsonl` (id IS the filename).
- Custom slash commands are just markdown files: `~/.claude/commands/<name>.md` (personal, all projects) or `<project>/.claude/commands/<name>.md`. Filename = command; body = the prompt that runs. First-created has a one-time indexing lag before it shows in the `/` menu.

**The architecture (Lead, DJ-approved concept):** ONE action labels a role session on ALL surfaces because we make **`/be-<role>` the session's FIRST prompt**:
- phone/web list → auto-titles toward the role (first-prompt = the fix DJ couldn't crack)
- terminal bottom bar → the boot runs `/rename <Role>`
- terminal tab → the launcher's `wt --title <Role>`
- every boot ends with the standing status line `🟢 <Role> — OVER` (DJ's existing "who + idle" signal) — see [[feedback_over_status_line]].

**Build shape (durable, survives wipe):**
- Boot pack lives in the REPO: `saunders-render-app/3_Documentation/roles/<ROLE>.md` — a THIN LOADER that points at the role's authoritative docs (charter, handoff brief, memories) + a Boot Checklist (rename, register in SESSION_ROSTER, arm mail-watcher at the role's offset minute, announce+OVER). Not a copy of the charter (avoids drift).
- Local `~/.claude/commands/be-<role>.md` = a thin fetcher: reads the repo pack via `gh api` and executes it. (Mirror the command files into the repo too so a wipe can restore the whole commands folder from git — TODO after all 7 roles built.)
- Recovery batch file (TODO): opens all role tabs, each `wt --title` + `claude --resume <name>` (or `-n <role> /be-<role>` for from-scratch).

**Decisions:** Cloud stays BENCHED — its dealbreaker is one-way comms (can receive, can't SendMessage back; replies lag via mail). Local wins because SendMessage is instant two-way. Lever-1 "hunt live sessions and convert them" retired as too messy. Internet-only outage is already handled by Remote Desktop + `/rc`.

**Status:** DESIGN pilot **VALIDATED 2026-09-17** — DJ ran `claude -n Design` → `/be-design` in a fresh session: phone auto-titled **"Design"** AND it signed off `🟢 Design — OVER`. Fleet directory (ListAgents) also shows it as `Design`. So naming + frozen-first-prompt title + boot pack + OVER handshake all confirmed working.

**★ REFINEMENT (the pilot's first real Q exposed it):** DJ asked the booted Design "who's our printer" — it answered Zoo Printing + all specs correctly but called the EDDM postcard "6×9". Root cause: `DESIGN_SESSION_HANDOFF_BRIEF.md`'s build section still describes the SUPERSEDED 9×6 build (artboard 2775×**1875**); the correct EDDM size is **9×6.5 (2775×2025)** per `project_eddm_mailing_rules` (9×6 fails USPS flat-size 6-1/8" bar → not EDDM-Retail eligible). **PRINCIPLE (bake into every role pack): a boot pack must FORCE-READ the role's critical memories IN FULL at boot — not just list them by name — because a fresh session auto-loads only the memory INDEX (MEMORY.md), not each file's content.** Fix applied to roles/DESIGN.md: mandatory `gh api`-read of `project_eddm_mailing_rules` + `project_wsc_print_build_pipeline`, a top-line "EDDM=9×6.5, memory wins over the brief on size" fact block. Design (live) was direct-messaged to fix its own stale brief.

**Next:** replicate the pattern (incl. force-read-critical-memories) to Specialists/Operator/Web/Portal/Audit/Lead → build the one-click recovery batch file (`wt --title` + `claude --resume <name>` per role) → optional statusline showing session_name.

Links: [[feedback_over_status_line]], [[feedback_lead_roster_restamp]], [[project_agent_mail_channel]], [[feedback_agent_mail_autowatch]], [[feedback_durable_foundation_over_shortcut]].
