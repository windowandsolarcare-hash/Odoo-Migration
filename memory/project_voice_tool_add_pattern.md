---
name: project_voice_tool_add_pattern
description: "How to add a field-voice WRITE tool to dashboard.py /ask (the LIVE one): 4 edit sites (schema, execute block in execute_write_tool, preview block, WRITE_TOOLS set) + wire it to the canonical endpoint via an extracted SYNC core (run_agent is sync-in-async-loop, so no asyncio.run). Deterministic QC via POST /owner/execute — no LLM. /ask body key is 'input'."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-05T15:02:25.816Z
---

**Voice tools batch 1 shipped 2026-09-05** (commits quotes 1aef47a, scheduler 5cdd7b0, dashboard 6f7721a): added 4 write tools to the LIVE field-voice assistant (`dashboard.py` `/ask`, NOT field.py — see [[project_ask_route_shadow_dashboard]]): `quote_to_current_job` (wraps accept_to_job_core — put a quote price on the picked scheduled job, refuses priced jobs), `maint_set_time` (wraps set_time_core — tighten a Submitted maint job's time without promoting), `send_confirmation` (wraps `send_maint_stage('confirm', so_id)` — review-then-send), `send_job_photos` (wraps _photos_send_core — review-then-send gallery link).

**To add a WRITE voice tool = FOUR edit sites in dashboard.py (all four or it half-works):**
1. **Schema dict** in the `TOOLS`/tools array (the big `[...]` that ends right before `WRITE_TOOLS = {`). `{"name","description","input_schema"}`. Put DJ's instincts IN the description (warm wording, review-then-send, one clarifying Q).
2. **EXECUTE block** — `if tool_name == 'X':` inside **`def execute_write_tool(tool_name, args)`** (starts ~L1264; the dispatch-1 region with reschedule_job/convert_quote_to_job execute blocks). This does the real work and RETURNS A STRING.
3. **PREVIEW block** — a SECOND `if tool_name == 'X':` in the dispatch-2 region (~L2743–2925, the confirm-preview strings; convert_quote_to_job has its preview twin here). Returns the "here's what I'll do" string DJ confirms. Display-only, no writes.
4. **Add the name to the `WRITE_TOOLS` set** (~L3628) so it's confirm-gated (preview → yes/no → execute).

**Wiring MUST use an extracted SYNC core, NOT asyncio.run.** `run_agent` (dashboard.py ~L4347) is a **sync def called directly inside the async `/ask` handler** (L4485, `result = run_agent(...)` — not threadpooled) → there IS a running event loop, so `asyncio.run(async_handler(...))` from a tool dispatch FAILS. So to reuse a canonical endpoint's logic, extract its body into a plain sync `def name_core(...) -> dict` and make BOTH the async HTTP handler (`body=await request.json(); return JSONResponse(name_core(...))`) AND the voice tool call that ONE core (feedback_reuse_canonical_endpoint → no drift). Done for accept_to_job_core (quotes.py), set_time_core (scheduler.py), _photos_send_core (dashboard.py). Lazy-import the cross-file core INSIDE the execute block (`from routers.owner.quotes import accept_to_job_core`) — `from .shared import *` won't surface it (see [[project_shared_star_import_scoping_gap]]). Resolve so_id from so_id/so_name with the existing `_find_so_by_identifier(str)` helper.

**★ DETERMINISTIC QC without the LLM — POST `/owner/execute`.** `@router.post('/execute')` takes `{"write_action":{"tool":<name>,"args":{...}}}` and calls `execute_write_tool(tool, args)` directly — i.e. it runs your EXECUTE block with no agent/LLM in the loop. This is THE way to throwaway-QC a voice write tool's dispatch wiring end-to-end (owner-cookie gated under AUTH_ENFORCE=1 — mint a cookie via POST /api/login). Test send-type tools safely by routing to a no-op (send_confirmation on a non-pending SO → "[CONFIRM] not pending"; send_job_photos on a no-phone contact → "[PHOTOS] No phone on file") so no real text fires. `/ask` itself reads body key **`'input'`** (not 'message') and forces `mode='confirm'` server-side (every voice write is confirm-gated; a body `mode:'immediate'` is ignored).

**Batch 2 (queued, waits for DJ's look):** book_from_schedule (offer-link tap-to-book wrapping slot_offers.py /api/offers/reserve+send — the existing schedule_job DIRECT-books with no customer-confirm link), multi-method payment (card/cash/zelle/venmo — own DJ nod + QC), read Cheryl decisions/stale surfaces.
