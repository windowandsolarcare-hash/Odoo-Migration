---
name: project_memory_ask_relevance
description: "Memory \"Ask\" (/api/memory/ask) firehose fix — stopwords + IDF weighting + cap; and the pending Part 2 (Haiku answer-synthesis, answer-don't-list)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-10T23:38:55.846Z
---

**Bug (DJ live 2026-09-10):** `/owner/api/memory/ask` (memory_store.py `ask()` + `_ask_score`) was a FIREHOSE — "what credit card should we use for canva" returned 59 cards (all the GBP ones too). Root cause: tokens = `q.lower().split()` with NO stopword filter; a record scored +1 for ANY single token appearing anywhere; any record with score≥1 was returned; no cap. Filler words (we/use/for/card/what) appear in nearly every card → ~everything matched. (Same endpoint serves DJ's Memory AND Cheryl's Ask.)

**Part 1 — relevance (SHIPPED 2026-09-10, tip ad8b463, memory_store.py `ask()`):**
- `_ASK_STOPWORDS` frozenset (what/which/we/our/for/to/use/card/… — tunable). Tokens = query minus stopwords; if that leaves 0 (all-stopword query) fall back to the raw tokens.
- **IDF weighting:** gather candidates once (decisions current-per-topic + register stores campaigns/content/roadmap/sops/reference/forecast), compute `doccount[t]` = #candidates whose text contains t, weight `w(t)=1/(1+doccount[t])`. A card's score = Σ w(t) for its matched tokens — so a rare token (canva, doc=3 → 0.25) outweighs a common one, and the right card dominates.
- Require a real match (score>0) + **cap top 8** (by score, then recency). Empty-query top-25 convenience unchanged; `memory_pointers.ask_pointer` live-answer still surfaces on top.
- VERIFIED on live data: the Canva query → tokens {canva,credit} → 82 candidates, **3 matched** (was 59), #1 = design_tooling_canva_premium (0.75). GBP cards drop out.

**Part 2 — ANSWER don't list (PENDING — the real ask):** after ranking, take top ~5 cards and synthesize a 1-2 sentence DIRECT answer with the source (e.g. "Your ThankYou business card — Canva decision, 2026-09-10"), show related cards below as collapsed "sources." Reuse the existing in-app Haiku path (field.py `_agent_loop` / Haiku tier per [[reference_app_ai_prompts]]) — inject the top cards as facts, no tools. Also needs the v2_memory.html Ask-box to render answer-vs-list. Not yet built. See [[project_meeting_distill_truncation_and_rekick]] (the reference[] prompt tweak feeds better cards into this).
