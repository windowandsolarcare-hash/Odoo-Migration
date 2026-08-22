---
name: reference_app_ai_prompts
description: Inventory of every AI persona/system-prompt in the Render app + the house AI philosophy (comprehensive prompt >> many tools). Read before writing/tuning any in-app Claude prompt.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-18T05:14:38.384Z
---

# App AI prompt inventory + house style (saunders-render-app)

**★ House philosophy (DJ, confirmed by the code):** a rich, COMPREHENSIVE system prompt beats a pile of narrow tools that can be called incorrectly. Inject facts into context; don't build a fetch-tool per fact. The SAME full prompt runs on every model tier (escalation = power, never a dumber prompt).

**The agent engine:** `routers/owner/field.py._agent_loop(client, model, system_prompt, messages, mode, max_loops)` (~line 2704) — Haiku (max_loops=4) → Sonnet (max_loops=8) on `[ESCALATE]`/exhaustion. REUSE this for any new tool-using Claude; don't write a new loop.

**Where the prompts live:**
- `field.py` `SYSTEM_PROMPT` (~2506) — the flagship "Claude, DJ's field assistant & business operator". 34 tools BUT really 2 generic (`odoo_query`/`odoo_write`) + prompt teaches whole Odoo/Workiz schema. Voice-first, numbered options, confirm-before-mutate.
- `sms.py` `_INBOX_BRAIN` (~472) — inbox triage, **ZERO tools** (facts injected via `_inbox_ai_facts`), 4-intent sort, "NO RESPONSE NEEDED / never reply to a 'thanks'", propose-don't-act. Also `_TRIAGE_SYSTEM`, `_draft_options`, confirm/book SMS writers.
- `reactivation.py` `_AI_DRAFT_SYSTEM` (~943) — richest single prompt, **no tools**: Mode A/B decision tree, banned phrases, false-confirmation rail, opt-out-vs-decline, NOTE-TO-DAN. Writes AS Dan.
- `specialist_booking.py` — JD + Handbook stored in `ir.config_parameter` (editable without deploy); draft-only, no tools.
- `myday.py` — quick-capture router + **Ask-AI router** (`_AI_MODELS`: quick=Haiku, deep/search=Opus `claude-opus-4-8`; Haiku routes → Opus/Opus+web_search) + `_vm_meta` voicemail parser.
- `hiring.py` — resume scorer (Haiku single / Sonnet batch w/ caller-supplied prompt).
- `library.py` `_VERIFY_SYS` — Truth-Meter fact-checker (Sonnet + web_search).
- `ideas.py` — Idea Board "thinking partner" respond (~156) + `_SCAN_SYS` idea extractor + card_respond/card_suggest.
- `followups.py`, `reminders.py` — Haiku micro-classifiers.
- The `specialist_*.py` family (billing/digest/morningnews/payroll/paywatch/reschedule) are **deterministic, NO AI** — rule-based HUD feeders.

**House voice conventions:** two identity modes — "You are Claude" (operator-facing) vs "You are Dan Saunders" (customer-facing message). Warm, first-name, plain, no emoji/hashtags, never "WSC", concise (phone), number every option. Guardrails everywhere: never invent a price/date/address/total; no bracketed placeholders; propose-don't-act for customer/money; when-in-doubt defaults spelled out; `messaging.send` = ONLY outbound-to-customer path.

**Model strategy:** Haiku classify/first-pass → Sonnet (`CLAUDE_MODEL`) hard threads → Opus (`claude-opus-4-8`) reasoning-heavy / web-search.

**Exemplars of comprehensive-prompt-over-tools:** `_INBOX_BRAIN` (0 tools), `_AI_DRAFT_SYSTEM` (0 tools), field.py (2 generic tools + schema in prompt), specialist_booking (editable handbook). See also `3_Documentation/INBOX_ASSISTANT_SPEC.md` + `INBOX_ASSISTANT_PROMPT.md` (the approval-card/trust-dial doer pattern) and `IDEA_BOARD_ASSISTANT_SPEC.md` (applies all of this to the Idea Board's third-partner Claude). [[project_idea_board]] [[project_cheryl_role_ai_front_office]]
