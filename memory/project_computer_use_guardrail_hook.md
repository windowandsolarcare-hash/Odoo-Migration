---
name: project_computer_use_guardrail_hook
description: "DJ hard rule — NO computer use (mcp__claude-in-chrome__*) without his explicit per-use okay. Enforcement hook BUILT (deny-by-default + DJ-sourced single-task grant); a session CANNOT install it (settings.json edit = [Self-Modification] blocked) — DJ applies the settings block."
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-22T16:44:15.772Z
---

**DJ's hard security rule (2026-09-22):** no browser automation / Claude-in-Chrome / computer-use without DJ's EXPLICIT per-use okay — every time, not blanket, not a session's own call. Reading/analysis via API/gh/files is fine; this is specifically about driving his browser/computer. Full: [[feedback_computer_use_requires_dj_permission]].

**Enforcement hook (built by Builder-2 2026-09-22, fleet-wide, in `C:\Users\dj\.claude\hooks\`):**
- `computer_use_gate.py` — **PreToolUse** hook, matcher `mcp__claude-in-chrome__.*`. DENY-by-default (exit 2), ALLOW (exit 0) only if a valid DJ grant flag exists for this session; consumes one use per call. FAIL-CLOSED (any error/missing/expired → deny). Same contract as `known_bad_fields.py` (reads PreToolUse payload on stdin, exit 2 = block).
- `computer_use_grant.py` — **UserPromptSubmit** hook, the ONLY writer of the grant flag. Writes `C:\Users\dj\cu_grant_<session_id>.flag` (JSON `{expires, uses, granted_at}`) from DJ's typed grant phrase ("computer use ok" / "take the tab" / "okay to use the browser"); single-TASK window (20 min + use cap, NOT standing). ★ Refuses to grant from injected/relayed content (`<cross-session-message>`, `<system-reminder>`, …) so a peer message can't self-grant. "revoke computer use" clears it. ALWAYS exits 0 (never blocks DJ's prompt).
- Grant flag semantics: DJ's okay = one task window (many browser calls), then it expires — re-grant per task. A session cannot fabricate it (only DJ's real typed input reaches UserPromptSubmit).

**★ A SESSION CANNOT INSTALL IT — DJ applies the settings block.** Editing `~/.claude/settings.json` to wire the hooks in is **blocked by the auto-mode classifier as `[Self-Modification]`** — the correct guardrail (a session must not edit its own permission config, even to tighten it). So the scripts are ready but the activation (add `PreToolUse` + `UserPromptSubmit` keys alongside the existing `PreCompact`) is DJ's one-paste — steps in `C:\Users\dj\.claude\hooks\INSTALL_computer_use_gate.md` (backup at `settings.json.bak-*`). **How to apply:** any permission-config change (settings.json hooks/allow/deny) must be applied BY DJ, not a session — build+test+propose the exact block, hand it to DJ. Tested cases all pass (deny-default / grant / decrement / injected-no-grant / non-chrome-unaffected / expired-cleanup).
