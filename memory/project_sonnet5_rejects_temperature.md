---
name: project_sonnet5_rejects_temperature
description: "API gotcha: model claude-sonnet-5 REJECTS the `temperature` param → API 400. Found in the Mom's Care assistant compose (anthropic 0.122.0). Remove temperature; get determinism from the prompt/input-constraint/post-check instead. W&SC app is UNAFFECTED (uses claude-sonnet-4-6, passes no temperature)."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-21T23:46:18.044Z
---

**Found 2026-09-21 (Mom's Care assistant compose fix).** A `messages.create` call to model **`claude-sonnet-5`** that passes a **`temperature`** param returns an **API 400** (the momscare compose.py used `temperature=0` → every compose failed → fail-closed to fallback → the assistant was safe-but-useless). Builder-2's diag log pinned it; **removing the `temperature` param fixed it** (key + model id were fine all along). anthropic SDK pinned `==0.122.0`.

**How to apply:** any fleet Claude call using **`claude-sonnet-5`** must NOT pass `temperature` — drop it and rely on the prompt / a constrained input / a post-check for determinism (temp=0 was only defense-in-depth; the real guarantees are elsewhere). Sibling gotcha to the anthropic `0.122.0` pin (0.123/0.124 stamp `toolset_name` → 400).

**W&SC app is UNAFFECTED (verified 2026-09-21 by Specialists):** its Claude calls (/owner/ask, inbox draft/redraft, Haiku triage, meeting distill) pass NO `temperature` param, and `CLAUDE_MODEL` defaults to `claude-sonnet-4-6` (+ `claude-haiku-4-5`) — the only `temperature` refs in routers/ are the open-meteo WEATHER API. So the gotcha can't bite W&SC today; this is a heads-up for any NEW sonnet-5 call. (Second bug in the same fix: `anthropic` was missing from momscare-app requirements.txt → ModuleNotFoundError → added `anthropic==0.122.0`.) See [[project_momscare_phase2_data_source]].
