---
name: project_inbox_history_parse_empty_speaker
description: "Imported text-history parser bug — '[ts] : text' empty-speaker lines (our logged outbound reactivations) folded into the prior bubble, corrupting 169/187 stored convs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-05T03:14:18.972Z
---

**Bug (found 2026-08-04 via Stephen Margetic's HUD card):** the imported Workiz text-history transcript (`ir.attachment` `description='[workiz-history]'` on res.partner) has TWO header formats:
- `[2026-04-14T09:11:07] Stephen Margetic: Mondays are a tough day for me` — normal, speaker present.
- `[2026-07-16T09:02:58] : Hi Stephen, Mondays are off the list! ...` — **EMPTY speaker** (space then colon). These are OUR system-logged outbound reactivation sends.

`_HIST_HDR` in sms.py was `^\[([0-9T:\- ]+)\]\s+([^:]+?):\s?(.*)$` — the `([^:]+?)` speaker required ≥1 non-colon char, so the empty-speaker lines FAILED to match and got **folded into the previous message's body** (`_history_msgs` appends non-header lines to `cur`). Result: a customer bubble like "Mondays are a tough day for me" had the entire next outbound reactivation text mashed onto it, and the reactivation never appeared as its own outbound message. Looked like the customer said things "out of the blue."

**Fixes (deployed 2026-08-04):**
1. `_HIST_HDR`: `([^:]+?)` → `([^:]*?)` (allow empty speaker).
2. `_history_msgs` direction: empty speaker → `'out'` (`'out' if (not sp.strip() or _is_dan_speaker(sp)) else 'in'`) — empty = our logged outbound reactivation.
3. Added consecutive-exact-duplicate collapse (some transcripts double-log a line).
4. **HUD display** (`v2_hud.html` `tailHtml`→new `tailWhen`): thread_tail times showed ONLY clock time (no date), so 2024 & 2026 texts both read as a bare time and looked same-day / out of order. Now shows date when not today, +year when not this year. (WSCThread's own `timeStr` already showed month/day — unaffected.)

**Stored-data impact:** the bad parse was baked into stored convs (`ir.config_parameter` `wsc.sms.conv.<norm>`, msgs list) AND into HUD card snapshots (`wsc.feed.items` → `inbox_ai:<norm>` → `thread_tail`). Code fix only affects FUTURE parses. **169 of 187 convs** carry folded bodies. Repair = re-parse from the transcript attachment (source of truth) with the corrected parser, PRESERVING any genuine live msg (ts > max transcript ts). Stephen (norm 9495100262 / pid 23659) repaired manually + his card tail patched.

**SWEEP COMPLETE (2026-08-04, DJ approved after 2 extra test cases proved no live-msg loss):**
- **Live-msg preservation rule:** a genuine live app-sent/received msg (via `_conv_append`/`_now()`) carries a **tz offset** (`+00:00`) in its ts; imported-history ts are naive (no offset). So `is_live = ('+' in ts or ts.endswith('Z'))`. Repair keeps all live msgs, rebuilds only history, sorts by `ts[:19]`.
- **Two repair methods** (both idempotent): (a) re-parse from the transcript attachment (`text_for` = pid→parent→children in one prefetched attmap of all 548 `[workiz-history]` attachments); (b) for convs whose transcript is unreachable (partner_id changed/unlinked, or pid=None), **un-fold in place** — re-serialize the stored history msgs to `[ts] {Dan Saunders|Customer}: body` lines and re-parse, which splits the folded `[ts] :` segments back out WITHOUT needing the transcript. Method (b) keeps live msgs aside first (their `+00:00` ts would fail the HDR regex, which has no `+` in its char class).
- **Result:** 96 rewritten via (a) + 21 via (b) = 117 fixed; 59 already-clean; 25 skipped (no transcript, untouched); 7 empty/placeholder params (test 555-000-xxxx numbers). **Final scan: 0 convs still folded; all 34 live app-msgs across 13 convs intact.** ~30 HUD `inbox_ai:*` cards refreshed. Scripts in scratchpad: `_runsweep2.py` (transcript sweep), `_unfold_all.py` (transcript-free), `_final.py` (verify).

Related: [[project_shared_text_thread_component]] (the shared view reads these same conv.msgs), [[project_inbox_assistant_p1]].
