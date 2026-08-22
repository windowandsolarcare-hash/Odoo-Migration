---
name: project_open_items_2026-07
description: "Open/unhandled items from the July 2026 outreach-CRM + cockpit sessions — things DJ and I discussed but did NOT close out. Working backlog to revisit."
metadata:
  node_type: memory
  type: project
  originSessionId: 6f63b0d4-dd6a-4dd1-aac3-e533a99e7526
---

Backlog of things discussed but not yet handled (captured 2026-07-09 at DJ's request "save all that"). Revisit these; check each off when done.

1. **Overdue maintenance customers — need next-job scheduled.** When we dug into the stranded maintenance jobs, 5 real overdue people surfaced who still need their next job created/placed: **Mette Haydt, Vince Russo, Art Martel, Joan Flickinger, Wayne Geringer**. (2 others were deleted false positives: SO 003361, 003697; 3 were live/fine: Rob Seedorf, Gary Marsalone, Jerry Smith Oct 2026.) DECISION PENDING: reschedule now via the smart scheduler (get_best_fit) vs. drop into a worklist for DJ. See [[project_daily_sync_date_window_excludes_old.md]].

2. **Walter Keller double-book — CORRECTED (was wrong before).** ★ SubStatus **"API SMS Test Trigger" is NOT a test** — it's the LIVE status that fires the reactivation SMS to the customer (misnamed, never renamed from its test days). The reactivation text goes out by setting the customer's graveyard Workiz job's SubStatus to "API SMS Test Trigger". When the customer books online FROM that text, the booking MUST reuse that same job — not clone a new one. Walter (contact 23655, lead 375, graveyard job **1EN4KG**/#4828, "Reactivation Lead", still SubStatus "API SMS Test Trigger", unbooked) booked online and approve CLONED a new job **2TKO6K** (Jul 16 9:30 AM, has his gate-directory notes). ROOT CAUSE: booking_requests.py reuse search required `stage_id = 5` but Walter's lead was stage 4 (Won). **FIXED 2026-07-09 (commit 5d36c2ae):** search now matches ANY non-Lost (`stage_id != 6`) reactivation lead with a graveyard uuid, and gates reuse on the Workiz job's SubStatus still == 'API SMS Test Trigger' (unbooked) so it won't overwrite an already-scheduled real job. ✅ RESOLVED 2026-07-09: orphan 1EN4KG DELETED (DJ said yes); Walter left with only real job 2TKO6K (Jul 16 9:30, gate notes), lead 375 stays Won. ★ Workiz job delete body MUST be JSON (`Content-Type: application/json`, body `{"ID":UUID,"auth_secret":SEC}`, browser UA) — form-urlencoded returns HTTP 412 "Invalid JSON"; success = 200 `{"flag":true,"msg":"Job deleted"}`, GET after = 204. See [[project_reengagement_vs_reactivation]] [[reference_odoo19_unlink_tracking_bypass]].

3. **Two cockpit numbers deferred (no clean source wired).** Dashboard cockpit (static/owner/index.html) still lacks "jobs to invoice" and "skipped to reschedule" counters — deferred because there was no clean source to count from. Decide the source + wire if DJ wants them.

4. **Call-only customer channel-awareness (NOT built).** Barbara Cameron (23589-type phone customer) — entire text history is transcribed voicemails; a text re-engagement aims the wrong channel. PROPOSED: teach ai_draft to detect call-only patterns → return "CALL, don't text" flag → route to a 📞 Call task; plus a manual "call only" switch. `x_studio_x_studio_ok_to_text` is blank on ~761/762 contacts so it's useless as a filter. See [[project_ai_draft_from_conversation]].

5. **Maintenance next-job flow going Odoo-native when Workiz retires.** The smart scheduler is ALREADY wired for next-job placement (Phase 5 get_best_fit → /api/scheduler/best-fit). The remaining gap is running the whole maintenance next-job creation natively in Odoo once Workiz goes away (today Phase 5 still clones the Workiz job via SA1338). This is the real long-term maintenance work.

6. **Render build-minutes reset date unknown.** DJ got a Render email about build/pipeline minutes (500 free/mo, $5 per 1000 overage). Exact monthly reset date is unknown — I can't log into the Render dashboard for him. DJ said "continue as normal." Revisit only if builds start getting throttled.
