---
name: feedback_spoken_friendly_responses
description: "★ REINFORCED 2026-08-31 (DJ, sharply): STOP explaining HOW things work. DJ is NOT technical — no file names, commit shas, function names, field names, line numbers, or mechanism in chat. Tell him WHAT it means for the business, whether it is fixed, and what HE must decide. Technical detail belongs in AGENT_MAIL/briefs/PRs where other sessions read it, never in his reply. Plus the original: plain spoken-friendly style for phone read-aloud, no markdown-heavy formatting."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ac2aeda5-6609-487b-94e3-132715d60520
---

DJ often has his phone READ responses aloud (Google Assistant "read this" / Select to Speak) while working on something else. Markdown (bold, tables, symbols like `*`, `#`, `|`, emoji) reads awkwardly via TTS.

**How to apply:** Default to a PLAIN, SPOKEN-FRIENDLY style — short sentences, no bold/italic markup, no tables, minimal/no symbols or emoji, and a one-line plain summary at the top. Read naturally when spoken.

**Revert:** This is a preference toggle. If DJ says "go back to the old way" (or similar), return to the normal formatted style (bold, tables, headers, etc.). Set 2026-06-28 as a trial — he may switch back.

Note: technical content (file paths, commands, code) can still be shown when needed; the plain style applies to prose/explanations.

---

## ★ 2026-08-31 — DJ pushed back HARD on this. Read before you write him anything.

His words: *"your going into a lot of technical details. telling me how each thing is done...
technical descriptions. im not tech enough to understand the weeds. I need you to be more focused on
telling me what i need to know in plain english."*

**The failure was not formatting — it was ALTITUDE.** A cloud Lead wrote him accurate updates full of
commit shas, file paths, function names, date-math tables, CRLF diffs and OAuth scopes. Every fact was
true and every one of them was useless to him. He does not maintain the code. He runs the business.

**How to apply — the test before you send:**
- Ask: *does DJ have to DO anything with this sentence?* If no, cut it. Not shorten — CUT.
- Say what it MEANS, never how it works. "Yesterday's jobs were showing a red warning by mistake;
  fixed" — not the date-parsing explanation.
- **Never in his reply:** file names, commit shas, function/field names, line numbers, API/scope
  names, diff stats, tool mechanics. If a technical fact matters to another SESSION, it goes in
  AGENT_MAIL or the brief or the PR body. That is what those are FOR. His chat is not the log.
- Lead with the answer or the decision he owes. Detail only if he asks "why" or "how".
- Numbers are fine when they are BUSINESS numbers (30,000 unread, $1.50/month, 5,000 cleared).
  Numbers are noise when they are engineering numbers (1,541 insertions, sha 4b8b8b6).
- Three short paragraphs beats fifteen bullets. He is on a phone, often driving, often listening.

**Why this keeps happening:** thoroughness feels like good work, and a session that just did careful
technical work wants to show it. Showing it to DJ is not the reward — it is the mistake. Put the
rigor in the work and in mail; give DJ the outcome.
