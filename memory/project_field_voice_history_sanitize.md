---
name: project_field_voice_history_sanitize
description: "Field voice assistant 400 'Extra inputs not permitted' (tool_use.toolset_name) — SDK model_dump() emits extra block fields the Messages API rejects on replay. Fixed by _sanitize_messages before every create()."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-19T21:01:57.263Z
---

**Bug (2026-08-19, field.py 86ee8a3):** the field voice assistant threw `Error 400 invalid_request_error: messages.3.content.0.tool_use.toolset_name: Extra inputs are not permitted` when DJ continued a session (his "1" reply that triggered a real tool call). Root cause: `_agent_loop` stores assistant turns via `b.model_dump()` and replays them from saved history; a newer deployed `anthropic` SDK's `model_dump()` on a tool_use block emits an extra field (`toolset_name`) that the Messages API **accepts on output but REJECTS on input**. Once a poisoned block was in the session history, every subsequent call 400'd — on BOTH the quick (Haiku) and deep (Sonnet) paths, since they replay the same history (so "try the higher model" would NOT have fixed it).

**Fix:** `_sanitize_block()` + `_sanitize_messages()` in field.py — whitelist only the API-accepted fields per block type (tool_use→{type,id,name,input}; text→{type,text}; thinking→{type,thinking,+signature}; redacted_thinking→{type,data}; tool_result→{type,tool_use_id,content,+is_error}) and run it on `messages` at the API boundary (`_ckw['messages']=_sanitize_messages(messages)`) inside `_agent_loop`, right before `client.messages.create`. Because it cleans on the way OUT to the API, **existing poisoned sessions self-heal** — DJ doesn't need to clear the chat.

**Lesson:** never replay `model_dump()` blocks verbatim to the Messages API across SDK versions — whitelist the fields. This affects any tool-use loop that persists + replays assistant content. Related: [[project_voice_text_draft_tool]], [[project_voice_deep_think_mode]].
