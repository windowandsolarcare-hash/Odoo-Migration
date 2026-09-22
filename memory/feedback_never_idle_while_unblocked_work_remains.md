---
name: feedback_never_idle_while_unblocked_work_remains
description: "â˜… GOVERNING: never go idle while un-blocked work remains. When DJ's quiet and the little things are done, pull the next NOT-done item (incl. deferred ones) and do it. Only DJ-blocked work waits. Deferred â‰  parked-and-forgotten."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-22T16:07:00.896Z
---

â˜… **Do NOT go idle while there is work that ISN'T blocked on DJ. The only thing allowed to remain undone is something genuinely waiting on DJ. Everything else gets done before anyone goes idle.**

**Why:** DJ 2026-09-22. The Mom's Care document-scan feature got sequenced "at the end" (correctly â€” it's the most security-sensitive) but then just SAT deferred for days while the little things got finished and the fleet kept going idle. DJ: "At any point when we go idle and I haven't given you anything, everything's done on the little side â€” so the next step is: what's left NOT done? Instead of going idle. That piece never gets pulled off the parked list back onto 'needs to get done.' We should never go idle until everything is done that is not waiting on me. Otherwise why go idle while there's still stuff left? Do not go idle â€” get it all done, THEN go idle. That should be the rule."

**How to apply:**
- **Sequencing (easy-first, sensitive-last) is fine â€” LEAVING IT DEFERRED is not.** Order the work sensibly, then actually work down the list. When the easy tier is done, the sensitive/deferred tier becomes the active work â€” pull it forward and build it, don't idle.
- **"Deferred" must never become "parked-and-forgotten."** A deferred item stays on the active backlog and gets built as soon as the things ahead of it clear. If it's un-blocked, it's fair game â€” do it.
- **The ONLY legitimate reason to stop/idle is that everything remaining is blocked on DJ** (his 2FA/go, his login, a decision only he can make, content only he has). If un-blocked work exists, the fleet keeps working it.
- **Dispatcher's job:** maintain the full open-item backlog (MOMS_CARE_BOARD + DISPATCH_BOARD), and keep every owning session fed with its next un-blocked item â€” don't let a session sit idle while its backlog has un-blocked work. Don't tell DJ "all done" while un-blocked work still sits. When DJ goes quiet, that's the cue to drain the backlog, not to rest.
- Sharpens + operationalizes [[feedback_ship_dont_park]] and [[feedback_move_the_ball_decide_correct_at_test]] (this is the IDLE-state corollary: keep advancing un-blocked work) and [[feedback_never_idle_waiting_on_dj]] (park what needs DJ, keep building everything else) â€” extends it to: proactively pull deferred items forward rather than only building what was just asked.
