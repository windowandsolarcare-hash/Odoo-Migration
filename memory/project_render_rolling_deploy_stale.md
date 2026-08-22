---
name: Render rolling deploys can briefly serve stale code from old instances
description: After a deploy "finishes", an older instance may still serve traffic for a minute. Don't trust user-reported behavior immediately after a fix push — verify via logs/instance ID.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Render's deploy lifecycle:

1. New deploy created → builds → status=live
2. New instance starts up (gets a unique instance ID like `srv-XXX-tssvt`)
3. Old instance keeps serving traffic until new one is healthy
4. Old instance is drained (graceful shutdown — finishes in-flight requests)
5. Now only the new instance serves traffic

During step 3, both instances exist. Requests can hit either one. The old instance runs the OLD code.

**Real example 2026-04-27:** Pushed search-fuzzy fix at commit `54eaf59` (deploy finished 07:10:56). DJ tested at 07:16:08 and got OLD-code results (Bob Jones for "Jon Hamm"). The request hit instance `tssvt` which was actually running pre-fix code. Subsequent test at 07:24 (different instance `smgvp`) returned the correct fix.

**Why:** When users report "it didn't work" within 1-2 minutes of a deploy, do NOT immediately assume the fix is broken. Check Render logs for `instance` label — if it differs from the one running the new code, you're seeing stale-instance behavior.

**How to apply:**
- After a deploy, wait ~2 minutes before asking the user to re-test.
- If user reports failure right after a deploy, check the deploy status (`mcp__render__list_deploys`) and confirm `status: live`. Then check the request log for `instance` label.
- If instance ID matches a known new deploy: code is suspect, debug further.
- If instance ID is from an older deploy: ask user to retry; deploy hadn't fully cut over.
- For high-confidence verification: ship a temporary `print(...)` log line, deploy, ask user to retry, pull logs filtered by `text=["[search]"]` or similar marker.
