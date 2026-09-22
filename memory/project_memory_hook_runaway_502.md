---
name: project_memory_hook_runaway_502
description: "2026-09-22 incident — the Memory-Pillar Stop hook re-POSTed /owner/api/memory/hook/resolve 6+/sec (a client bug), saturating the single 512MB Render worker → DJ's concurrent payment 502'd. Root cause + the two fixes (server flood-guard + the hook status-field bug)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T20:20:54.179Z
---

**Runaway /hook/resolve → payment 502 (2026-09-22 ~1:07pm/20:07 UTC).** DJ hit a 502 recording a payment. NOT a deploy. Logs: a FLOOD of `POST /owner/api/memory/hook/resolve` (6+/sec, all 200 OK) at 20:08-20:10 → on the single 0.5-CPU/512MB worker (numInstances=1) that saturated the worker → DJ's concurrent payment got no backend → gateway 502. Subsided when the looping sessions went quiet.

## Root cause — a CLIENT bug in the Stop hook
`.claude/hooks/mem_error_capture.py` (Builder-2's Memory-Pillar Stop hook; canonical mirror `3_Documentation/roles/hooks/`) POSTs `/hook/resolve` for each still-open signature in the per-session breadcrumb (`~/.mem_pending_error_<session>.json`), then clears the ones the server resolved. BUT it read `resp["record"]["status"]` — and the SOLVED response returns `status` at the **TOP LEVEL** (`{"ok":true,"status":"solved",...}`) with **NO "record" key**. So it read None on EVERY successful close → `None != "solved"` → KEPT the signature. ("No such signature" returns `record:None` → also kept.) So the breadcrumb NEVER cleared + GREW, and EVERY session Stop re-POSTed the whole accumulated set → the flood. Each call also did a full store `_load` → the saturation.

## Fix 1 — SERVER flood-guard (my layer, deployable, commit 6f7f593f)
`memory_store.py` `_hook_debounced(kind, signature)`: an in-process, thread-safe, bounded per-(kind,signature) debounce (10s). `hook_resolve` + `hook_observe` shed a same-signature repeat as a fast no-op (`{ok,signature,debounced:true}`) with ZERO store I/O (no `_load`/Haiku/`mem_update`). So a runaway CLIENT can NEVER saturate the worker again — the rate-limiting best-practice: a loop shouldn't be able to take down the instance. (recall = a GET read, left as-is: lower cost + shedding it would drop the fix-injection.)

## Fix 2 — CLIENT root cause (canonical hook, pushed)
`mem_error_capture.py`: clear the sig whenever the server is DONE — top-level `status=='solved'` OR `record is None` (no such sig) OR `debounced` — keep only genuinely-`open` or a network error. ★ The LIVE hook is PER-MACHINE (`~/.claude/hooks/mem_error_capture.py`) — Builder-2/DJ must REDEPLOY the fixed canonical to each machine that runs it (+ optionally clear stale `~/.mem_pending_error_*.json` to drop the backlog). The server guard holds the line until then.

## Lessons
- A hook/endpoint response-SHAPE mismatch (top-level vs nested field) can silently create an infinite retry loop — always clear/advance client state on ANY definitive server response, retain ONLY on a transient (network) failure.
- On a single small worker, ANY unbounded client loop is a latent DoS on unrelated requests (here, money). Headless/hook endpoints that do store I/O need a cheap shed-guard. See [[feedback_no_deploy_during_customer_payment]], [[project_hud_live_derived_flip]] (the 8s HUD cache is the same "don't hammer the worker" instinct).
