---
name: project_voice_job_time_pacific
description: "Voice /owner/ask — job-time emitters must convert date_order UTC→Pacific (DST) via _dt_pt_label (raw date_order[:16] got quoted as PM); and open_text_draft is ALSO the read/reply-to-texts tool, not just send."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T02:01:21.386Z
---

Two voice-assistant bugs fixed + DEPLOYED 2026-10-09 (main 521ce5b8), both in **dashboard.py — the LIVE `/owner/ask`** (field.py's `/ask` twin is DEAD; main.py includes dashboard FIRST — fix dashboard.py only). Routed by Lead.

**1) Job times quoted as PM (UTC never converted).** `search_customers` (both the SO-number path AND the name path, key `job_date`) and `tool_get_job_details` (key `date`) returned the RAW `date_order[:16]` (UTC), so a 16:30-UTC job (SO 004550) read out as "4:30 PM" instead of 8:30 AM PT. Fix: new helper `_dt_pt_label(date_order_utc)` → "YYYY-MM-DD h:MM AM/PM", DST-correct (ZoneInfo `America/Los_Angeles`, reuses `_pt_date` + `_utc_str_to_pt`); applied at all 3 emitters (same bug class in 3 spots). **Why:** `date_order` is always UTC; a model-facing clock time must go through a PT converter, NEVER raw `[:16]`. **Check:** 16:30 UTC = **8:30 AM PST** (-8, after Nov 1) / **9:30 AM PDT** (-7, DST). Keys unchanged; nothing consumes them programmatically (tool output to the model only).

**2) "I don't have a tool to read text history."** On "look at <X>'s text" / "reply to <X>" the model did NOT call `open_text_draft` and claimed no tool (a never-say-can't violation). Root cause: the tool was framed send-only (triggers text/draft/send/message/ask) with no "opens the full thread" signal — but it opens `/static/owner/v2_inbox.html?open=<pid>&draft=...` = the FULL conversation thread (history). Fix (description + SYSTEM_PROMPT, no logic/send-path change): it is THE tool to **text, READ, or reply**; added triggers (reply to / look at / read / pull up / what did X say / see text history); stated opening it shows the whole thread so it's also how you read; extended never-say-can't to "can't read text history"; a plain read → call with no `intent` (thread still opens). **Rule for new text-related phrasings: route to `open_text_draft`, don't add a separate read tool.**

See [[project_cheryl_dan_shared_tasks]], [[feedback_times_in_pacific]], [[feedback_no_ai_offered_dates_use_link]].
