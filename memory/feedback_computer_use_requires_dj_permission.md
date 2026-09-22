---
name: feedback_computer_use_requires_dj_permission
description: "â˜…â˜… GUARDRAIL: NO computer use (browser automation / Claude-in-Chrome / controlling DJ's machine) without DJ's EXPLICIT per-use permission. Stop at his desk and wait for his 'okay to use computer use' every time."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-22T16:23:21.951Z
---

â˜…â˜… **HARD GUARDRAIL: never use COMPUTER USE (browser automation, Claude-in-Chrome, driving DJ's actual browser/computer) without DJ's EXPLICIT permission for that specific action. It stops at his desk â€” wait for his verbal "okay to use computer use" every time.**

**Why:** DJ 2026-09-22. Computer use = the fleet literally controlling DJ's machine/browser = high power. "That can be a problem in the future for sure." So it's gated on his explicit per-use okay â€” not a standing/blanket permission, not something a session decides on its own.

**How to apply:**
- Before ANY `mcp__claude-in-chrome__*` / computer-use action (navigate, click, type, screenshot of his screen, form-fill, taking control of a tab), STOP and get DJ's explicit okay for THAT task. No computer use until he says go.
- Applies to EVERY session, Dispatcher included. Reading/analysis via non-computer-use tools (API, gh, files) is unaffected â€” this guardrail is specifically about driving his browser/computer.
- **What counts as the okay:** DJ explicitly telling this session to do the specific computer-use task ("take that tab and finish it," "go do X in the browser"). That authorizes THAT task only â€” it does not generalize to future computer use. When in doubt, ask.
- No exception for "just finishing" or "it's quick" â€” even to complete an un-blocked item ([[feedback_never_idle_while_unblocked_work_remains]]), if it needs computer use, it waits for his okay. Prep everything else, then wait.
- **Enforcement:** (1) written guardrail in the boot packs (3_Documentation/roles/*.md) where guardrails live; (2) ideally a PreToolUse HOOK that hard-blocks computer-use tools until DJ has granted permission (DJ: "if a hook gets that honored better, do that better with a hook" â€” ties to the A39 warn-before-action hook work). Route both.
- Pairs with [[feedback_customer_sends_through_dj_hud]] (customer sends = his press) and [[feedback_assistant_use_app_workflow_not_raw_api]] â€” DJ gates the highest-consequence actions.
