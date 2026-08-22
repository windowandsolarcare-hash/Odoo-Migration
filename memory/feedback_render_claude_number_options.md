---
name: feedback_render_claude_number_options
description: "Render Claude (field assistant) must ALWAYS present choices as a numbered list so DJ replies with a number — he's on a phone and won't type words."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

**Preference (2026-06-09):** When the field assistant (Render Claude) presents ANY choices — which customer, which service/JobType, which status, which job, yes/no — it must give a **NUMBERED list (1, 2, 3…)** so DJ replies with just the number. He's on a phone in the field and does not want to type words/names.

**Why:** DJ scheduling "Suzy" — it asked "what service? — Window Cleaning?" as free text, forcing him to type the answer (and the offered value was invalid too). Numbered options = one tap.

**How applied:** baked into the field.py `SYSTEM_PROMPT` as a top rule "## ALWAYS NUMBER YOUR OPTIONS" (commit d61e7f5d). If the prompt is ever rewritten, keep this rule. [[project_workiz_jobtype_valid_values]]
