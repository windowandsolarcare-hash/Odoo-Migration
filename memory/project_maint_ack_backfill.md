---
name: project_maint_ack_backfill
description: "One-time maint-acknowledge backfill (2026-08-08) — marked jobs acknowledged whose customer said \"ok\" to the heads-up naming THAT job's exact date. Tie by date + non-Done, NOT just any \"ok\" in the thread (54 loose → 13 correct)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-08T14:20:28.874Z
---

**Why it was needed:** the maint "✓ Acknowledged" pill lights when `wsc.maint.advance.<so_id>` JSON `state=='ok'`. That state is only set when a heads-up sent via the CURRENT flow drops an "awaiting reply" marker and the customer replies yes. Customers who got the OLD-format heads-ups (pre-tracking, e.g. Apr 2026) replied "Ok" but no marker existed → never acknowledged. (Wayne Geringer SOs 17066/17067 was the trigger; hand-fixed first.)

**The correctness trap (DJ caught it):** you CANNOT just scan a thread for a heads-up→"ok" pattern. These customers have YEARS of maintenance history — a dozen old heads-ups + a dozen old "ok"s. A loose scan matched 54 upcoming jobs, but most were "ok" to an OLDER date or a since-rescheduled one. Auto-acking those would claim they confirmed a date they never saw.

**The correct tie (what actually shipped):** ack an SO ONLY if — (a) upcoming + `x_studio_x_studio_workiz_status not in [Done,Canceled]` (DJ: "if job is done, skip it"); (b) the conv has an OUT heads-up message that NAMES the SO's own `date_order` date (parse "Mon DD, YYYY" from the heads-up); (c) an IN yes-word reply follows THAT heads-up before the next different-date heads-up. Yes-words: ok/okay/yes/yep/sure/sounds good/perfect/great/that works/see you. That precise tie: 54 loose → **13 confident**. The other ~40 were correctly skipped (their "ok" was to a different/older date). Also excluded question/reschedule replies ("what dates are open?", "CONFIRMED ?").

**Committed 2026-08-08:** set `wsc.maint.advance.<so>` = `{"state":"ok","ts":<now>,"backfill":true}` for the 13 tied SOs (+ Wayne's 2 earlier). Script + candidate list in scratchpad (maint_ack_backfill.txt / ack_commit_ids.json). Going forward this is automatic (current heads-ups set the awaiting marker), so no repeat needed unless another batch of old-format threads surfaces. See [[project_hud_denoise_and_recent_strip]] (acknowledged[] added to /api/sched/states), [[project_request_confirm_flow]].
