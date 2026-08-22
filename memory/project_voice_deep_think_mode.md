---
name: project_voice_deep_think_mode
description: "Field voice assistant has a 🧠 'Think hard' DEEP mode — button + spoken triggers route a request to the strong model + extended thinking, skipping the fast Haiku path."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-19T17:44:57.484Z
---

**Built 2026-08-19 (DJ request).** DJ wanted manual control over "which brain" handles a request — a button he can press to say *"this is complicated, figure it out"* and get the strong model with real thinking time, versus the quick path for easy stuff. (He noted the auto-escalation only kicks in when the fast model gives up; he wanted to force the heavy model from the first token, on demand.)

**How it works — two modes in `field.py run_agent(deep=False)`:**
- **Quick (default):** `_agent_loop(CLAUDE_HAIKU, max_loops=4)` → auto-escalate to `_agent_loop(CLAUDE_MODEL/Sonnet, max_loops=8)` only on `[ESCALATE]`/loop-exhaustion. Unchanged.
- **Deep (`deep=True`):** skips Haiku entirely → `_agent_loop(CLAUDE_DEEP_MODEL, max_loops=10, thinking_budget=DEEP_THINKING_BUDGET)` with the **`DEEP_MODE_ADDENDUM`** appended to the system prompt (think step-by-step, use tools aggressively, chase to a complete answer, then answer plainly).
- `CLAUDE_DEEP_MODEL` env (default = `CLAUDE_MODEL`, i.e. Sonnet 4.6 — DJ's "back a notch off the very top" sweet spot; bump to Opus later via env, no code change). `DEEP_THINKING_BUDGET` env (default 8000).
- `_agent_loop` gained a `thinking_budget` param: when set it passes `thinking={'type':'enabled','budget_tokens':N}` and sets `max_tokens=N+2048`. **Graceful degradation:** on APIStatusError OR TypeError (old SDK without `thinking`) it retries once with thinking off — so deep mode never hard-fails; worst case = strong model without thinking (still better than Haiku). Extended-thinking blocks are preserved across tool turns via the existing `model_dump()` on assistant content (required by the API); the `end_turn` text extraction skips thinking blocks (they lack `.text`).

**Triggers (either fires deep):**
- **Button:** the 🧠 "Think hard" toggle. ★ The LAUNCHER's "Voice Assistant" entry (v2_apps.js) opens **`v2_voice.html`**, NOT field.html — that's the page DJ actually uses, so the button HAD to go there (v2_voice.html `#deep-toggle`, commit 6f6bc0c). Also added to `field.html` (the older/other voice UI) in both the pane (`#deep-toggle`) and the voice modal (`#vm-deep-toggle`). ALL three share ONE localStorage key `wsc_deep_mode` (rule 12 — survives the constant refreshes; state consistent across pages). Rule-10 reminder: when adding a voice-assistant UI element, put it in **v2_voice.html** first — that's what the launcher opens. `wscDeep()`/`wscToggleDeep()`/`_wscDeepPaint()`. It's a **sticky toggle** (stays ON until tapped off) with a loud amber ON state, so DJ can leave it on for a hard back-and-forth. Both `voiceSend()` and `vmSend()` send `deep:wscDeep()` and show "🧠 Thinking hard…" status.
- **Spoken phrases** (server-side in `ask`, so they work regardless of input path): "think hard / think harder / figure this out / figure it out / big brain / use the big brain / deep mode / work it out / take your time / really think / think about this / think this through". DJ didn't want to memorize one exact phrase.

**Context DJ worked out with me (correct):** the model tiers differ in (a) raw capability AND (b) thinking time — not just speed; a cheap model is both faster AND less capable, so deep mode bumps BOTH (stronger model + extended thinking). And "Claude Code vs the API model" is mostly CONTEXT + TOOLS + LOOP + PROMPT, not a smarter model — which is why deep mode also loads the richer prompt. Commits: field.py 3ad881a, field.html 14ca6fb. Related: [[project_voice_text_draft_tool]] (agentic-mandate prompt work), [[feedback_field_readability_sunlight]].
