---
name: project_operating_system_vision
description: "DJ's north-star: the app is becoming an owner's OPERATING SYSTEM — humans for physical work, AI specialists for digital work, DJ as fallback. Higher layer above the built tools = a dispatch + in-app approval-inbox spine. Each AI duty = a specialist (shared handbook + its own job-description prompt)."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T09:53:57.106Z
---

**2026-07-26 strategy conversation (design decisions, not yet built — direction for future work).** DJ's founding goal (7 months in): hire people for PHYSICAL work (cleaning), use AI + Python automations for everything DIGITAL, with himself as the fallback. He built bottom-up (left Workiz for cost → jobs+invoicing → grew into the whole business, customized to spec). Now wants a higher-level layer above the pieces already built. My "operating system" framing resonated. This becomes a project-management / operations app where "Goals" is just one project TYPE.

**Locked design decisions:**
- **Top layer = dispatch + approval spine** (NOT a big new PM app). Every unit of work gets a DOER: DJ / physical hire / an AI specialist / Cheryl (she'll likely help). Projects/milestones/tasks (the Goal Board engine already built) are the ORGANIZING layer underneath that feeds the spine. Reuse everything.
- **Approval = a per-duty TRUST DIAL, default manual.** AI does the work → draft/proposed action lands in an in-app APPROVAL INBOX → DJ reviews, tweaks a few words, approves → it launches. Once DJ trusts a specific duty he can PROMOTE it to run end-to-end autonomously — BUT most customer-facing output stays manual forever ("I know certain customers certain ways"). Not blanket-permanent, not blanket-auto.
- **Approval inbox = in-app, modeled on the existing voicemail/text inbox** (snooze / set-aside / send-back / work-on / notifications). NOT Gmail, not SMS (his text is already too cumbersome).
- **AI architecture = specialists, not one generalist.** Pattern DJ already proved: rich prompt + tools + approval (tools-only was a retooling nightmare; detailed prompt+tools works). Each AI duty = a SPECIALIST = **shared "handbook" (business facts/voice, written once, reused) + its own "job description" prompt** (this duty's tone, steps, allowed tools, guardrails). Focused prompts = more reliable than one god-prompt. Specialists AI-A/B/C = same engine, different job descriptions = the "AI doers" in the dispatch.
- **Microphone (old VoiceQuick) redesign:** stop making one generalist mic guess intent. Add a step BEFORE speaking: pick the specialty (AI-A/B/C…) → loads that specialist's prompt+tools → THEN speak. The pick is a "gear selector" so it interprets correctly. DJ wants to re-test the mic under the new prompting (it predates the reprompt).
- **Discipline (guards his own "over-complicate & stall" obstacle):** start with a HANDFUL of specialists on duties with clear payoff + callable data, grow one at a time. Don't build a maze of half-baked agents or the full cockpit before the engine.

**Already-working proof (retires the "can AI reliably do a duty" risk):** reactivation/re-engagement TEXT drafting (reads prior texts, writes a natural reply in DJ's voice, comes for approval — he tweaks a few words; runs through Workiz for now because numbers aren't [[feedback_ported_means_twilio|ported]] yet); and Claude Code writing the ~2 dozen detailed Twilio support emails DJ reviews+sends. DJ trusts these, good results, no hallucination blowback.

**Open next step:** DJ to name the first 3-4 specialties to build (reactivation-text-drafter already exists). Honest sequencing I recommended: don't build the whole cockpit first — the make-or-break is reliable AI execution + callable data per duty, not the shell. See [[project_goal_board]], [[project_ask_ai_router]], [[project_voicemail_to_task]].
