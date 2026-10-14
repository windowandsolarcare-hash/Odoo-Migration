---
name: project_atomic_multifile_deploy_git_data_api
description: "To deploy INTERDEPENDENT multi-file changes to main in ONE Render deploy (no mixed-version window), use the GitHub git Data API — create blobs → one tree off main's tree → one commit (parent=main HEAD) → update refs/heads/main once. Proven 2026-10-13: the main-protection ruleset ACCEPTS this atomic ref update (it is not `git push`)."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-14T01:24:46.168Z
---

Proven 2026-10-13 on the gateway-retry deploy (commit 0b07d96c, 4 files: sms.py + messaging.py + wsc_send.js + v2_inbox.html).

**Problem it solves:** the Contents API PUT is ONE file per call, so a multi-file change lands as N separate commits → N separate Render auto-deploys → a MIXED-VERSION WINDOW where some files are new and some old on the serving instance. For INTERDEPENDENT files this can be a live bug: e.g. gateway-retry's client (wsc_send.js with the auto-retry) going live BEFORE the server (sms.py with the up-front client_msg_id claim) would re-open the exact double-text the fix closes (client retries against a server that still has only per-minute dedup). See [[feedback_deploy_tap_reaches_executor_not_relayed]] and the gateway-retry work.

**The fix — ONE atomic commit via the GitHub git Data API:**
1. Create a blob per file (`POST /repos/{repo}/git/blobs`, base64 content).
2. Create a tree off main's current tree (`POST .../git/trees` with `base_tree`=main HEAD's tree, and the changed paths → new blob shas).
3. Create one commit (`POST .../git/commits`, `tree`=new tree, `parents`=[main HEAD sha]).
4. Update the ref ONCE (`PATCH .../git/refs/heads/main`, `sha`=new commit).
→ ONE commit on main → ONE Render rebuild/deploy → server + client land TOGETHER → zero mixed window.

**Key fact (the unknown this run resolved):** the `main`-protection RULESET **ACCEPTS** this git-Data ref update — it is NOT `git push` (the thing the ruleset rejects), it's the REST git Data API, same class of allowed write as the Contents API PUT. So "gh api Contents PUT to main, never git push" still holds; the git Data API is an additional allowed path. A rejected ref update would be atomic (no partial state, only harmless dangling objects), so try-atomic-then-fallback is safe.

**Fallback if ever rejected:** deploy in dependency-safe ORDER — the backward-compatible side first, confirmed LIVE-SERVING (recycle-window-aware, not just pushed — see [[project_render_instance_recycle_502]]), then the dependent side. For a client/server pair: SERVER (additive/backward-compatible change) first, live-confirmed, THEN client. Never client-before-server.

**How to apply:** when a single logical change spans >1 file and the files are interdependent at runtime (a client calling a new server contract, two modules that must agree), deploy them ATOMICALLY via the git Data API — do not let them land as separate Contents PUTs. Lead byte-QC verifies post-deploy by blob-SHA-matching EVERY file on main vs the reviewed branch (atomic commit → all match) and confirming the new instance serves the new bytes on BOTH sides. Ties [[feedback_regression_guard_pushes]], [[feedback_staged_mirror_stale_base_refetch]], [[feedback_verify_collection_and_live_pipe]].
