---
name: project_ask_ai_router
description: Ask AI page /owner/ai — a cheap/fast model (Haiku) reads a question and either answers it or escalates to Opus (deep) or Opus+web-search (current info). One-tap override to a bigger model. Anthropic only (DJ declined Gemini).
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

# Ask AI — model router (built 2026-07-16)

DJ's idea: "ask a question, a cheap model reads it and picks the best price/knowledge model to answer." Built Anthropic-only — **DJ explicitly declined adding Gemini** (Google AI Pro $20 sub is chat-only / no API; the $10 Cloud credit wasn't on his billing account — only two EXPIRED Free Trial credits; not worth a second provider's auth/error/deprecation overhead for ~$5/mo of Gemini).

**Where:** `/owner/ai` (`static/owner/ai.html`) + endpoints in `routers/owner/myday.py` — `ai_page()` and `POST /owner/api/ask`. Commits myday.py c5b3438 / ai.html 41183da.

**Flow (one Haiku call routes AND may answer — don't burn a call just to classify):**
- `/api/ask {text}` → Haiku returns JSON `{"action":"answer","answer":...}` (simple → answers outright), or `{"action":"escalate","target":"deep"|"search"}`.
- `deep` → Opus (`claude-opus-4-8`). `search` → Opus + server-side `web_search_20260209` tool (max_uses 4), for current/live info.
- Override tap: `/api/ask {text, model:'deep'|'search'|'quick'}` skips routing, goes straight to that model. UI shows escalate buttons for the routes that AREN'T the one that just answered.

**Model list is a CONFIG ARRAY** `_AI_MODELS` at top of the ask block (quick=CLAUDE_HAIKU, deep/search=claude-opus-4-8) — retiring/adding a model is a one-line edit, not a code hunt. Same lesson as the Inputs CHOICES array [[project_feature_consolidation]].

**Robustness:** `_ai_answer()` handles `pause_turn` (server-tool resume loop, ≤5 hops) and wraps the web-search attempt in try/except → if the tool type is unsupported by the installed SDK/API it falls back to a plain Opus answer + a "couldn't search" note rather than failing. Front-end: 30s fetch timeout (Opus/search is slow), double-tap `_busy` guard, every answer shows a model badge (⚡ Haiku / 🧠 Opus / 🔎 Opus+web).

**Follow-ups (added 2026-07-16, commits myday.py cb9f8c8 / ai.html 9fe2fcb):** now a THREAD. Client holds `_turns[]` (server stays stateless) and sends `history[]` on every `/api/ask` call; `_clean_history()` caps 10 turns / 6k chars each, keeps only user/assistant text. Router uses `system=` for the rule + `messages=history+[q]` so a follow-up ("explain that more") routes/answers in context. Override tap (Ask Opus / Search web) RE-ANSWERS the last question with the forced model and replaces that answer (history = turns before it), not a new turn. ＋New button wipes `_turns`. Whole conversation replays across models fine (no extended thinking used, so no thinking-block replay issues).

**v1 cut (not built):** streaming, saved/persisted history (thread is in-memory only — a page refresh clears it), markdown rendering (answers render as escaped plain text w/ preserved newlines), home-screen tile (reachable at /owner/ai directly — tile is the obvious next add). Model IDs are hardcoded in `_AI_MODELS`, NOT env-overridable like CLAUDE_MODEL/CLAUDE_HAIKU in shared.py — deep/search = claude-opus-4-8 literal.
