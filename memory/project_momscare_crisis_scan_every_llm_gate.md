---
name: project_momscare_crisis_scan_every_llm_gate
description: "Mom's Care safety-QC lesson: EVERY red-flag-scanning / LLM-facing entry point must run crisis_scan (self-harm→988) BEFORE scan_text, not just scan_text. The assistant shipped with scan_text but no crisis_scan — a self-harm message got a med answer, not 988. Cheryl caught it; Lead's QC missed it."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-21T22:58:45.386Z
---

**Discovered 2026-09-21 (Cheryl's pre-live clinical review of the Mom's Care clinical surface).** In `momscare-app`, the red-flag guardrail (`redflags.py`) has TWO scanners: `scan_text()` (911 medical red-flags — chest pain, BE-FAST, falls, etc.) and `crisis_scan()` (self-harm/suicidal ideation → the **988** CRISIS_CARD, NOT 911, NOT a log). The module docstring says: **run `crisis_scan` BEFORE `scan_text` in the flow.**

**The bug:** `routers/checkin.py` did this correctly, but `routers/assistant.py` (the Care Assistant's pre-model gate) ran `scan_text` + `streak_flag` and **omitted `crisis_scan`** — and `scan_text`'s patterns do NOT include the self-harm set. So a caregiver typing a self-harm concern INTO THE ASSISTANT got a med-label answer / fallback, **never the 988 card.** A genuine safety hole on a safety-gated feature. Fix = add `if redflags.crisis_scan(question): audit + return CRISIS_CARD` as the FIRST step of the pre-model gate (before scan_text). ~3 lines.

**★ THE REUSABLE LESSON (QC checklist item):** ANY input path that will be scanned for red-flags or fed to the LLM — the assistant, the check-in, and every future LLM-facing / symptom-input feature — must run **BOTH** `crisis_scan` (first) **AND** `scan_text`. Don't assume "it scans for red-flags" means self-harm is covered — the 988 crisis path is a SEPARATE scanner that's easy to forget. When QC'ing any such gate, explicitly verify crisis_scan is wired, not just scan_text.

**Also a Lead-QC lesson:** my milestone-(b) assistant QC verified scan_text was pre-model but did NOT check that crisis_scan was present — the layered review (Cheryl) caught it. Add "crisis_scan wired?" to the pre-model-gate QC checklist. See [[project_momscare_phase2_data_source]], [[feedback_auditor_user_perspective_gapfinder]].
