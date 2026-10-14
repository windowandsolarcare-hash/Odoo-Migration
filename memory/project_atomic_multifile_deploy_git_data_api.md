---
name: project_atomic_multifile_deploy_git_data_api
description: "Deploy infra (verified 2026-10-13): a SINGLE ATOMIC commit of MULTIPLE files to main IS possible via the GitHub git Data API (blobs/tree inline-content -> one commit -> PATCH refs/heads/main) and the main branch ruleset ACCEPTS it (same as the Contents API). Use it when files have a deploy-ORDERING dependency (e.g. server must be live before client) so all land in ONE Render deploy = ZERO mixed window. The Contents API is still one-file-per-commit (N commits -> N deploys -> mixed window)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-14T01:23:59.575Z
---

## The fact (verified live 2026-10-13)
The main branch ruleset blocks `git push` but allows the **GitHub git Data API** to update `refs/heads/main` — so a **single atomic commit touching MANY files** lands cleanly, exactly like the Contents API does for one file. Proven on the gateway-retry deploy: 4 files (sms.py, messaging.py, wsc_send.js, v2_inbox.html) committed together as `0b07d96c` → ONE Render deploy → no mixed window. Lead blob-SHA-matched all 4 on main vs the reviewed branch (identical).

## Why it matters — deploy-ORDERING dependencies
The Contents API (`PUT /contents/<path>`) commits **one file per call** = N commits = N Render auto-deploys in arbitrary order. When files have an ordering dependency, that mixed window is a live bug. Real case: the gateway-retry fix's CLIENT (wsc_send.js retry) going live BEFORE the SERVER (sms.py up-front `client_msg_id` claim) would retry against a server with only the per-minute idem → the ≥2-min-boundary DOUBLE-TEXT the fix exists to kill. Atomic commit removes the window entirely.

## How to do an atomic multi-file deploy (gh api, one commit)
1. `GET /git/refs/heads/main` → `object.sha` (current HEAD commit).
2. `GET /git/commits/<head>` → `tree.sha` (base tree).
3. `POST /git/trees` with `{base_tree:<tree.sha>, tree:[{path, mode:'100644', type:'blob', content:<utf-8 file text>}, ...]}` → new tree sha. (Inline `content` makes GitHub create blobs byte-identical to the reviewed bytes → blob-SHA match passes.)
4. `POST /git/commits` with `{message, tree:<new tree sha>, parents:[<head>]}` → new commit sha.
5. `PATCH /git/refs/heads/main` with `{sha:<new commit sha>, force:false}` → atomic; this is the step the ruleset could reject (it did NOT — it passed). A rejected PATCH is atomic (no partial state, only dangling objects) → safe to try-then-fallback.
Pass each payload via `--input <file.json>` (json.dumps handles unicode/newlines); big content breaks `-f` flags.

## Fallback if the atomic ref-update is ever rejected
SERVER-FIRST via the Contents API: PUT the server files, **confirm the NEW instance is LIVE-SERVING** (Render deploy `status:"live"` + `/healthz` 200 on the new bytes, recycle-window-aware — a pushed-but-old-instance-still-serving does NOT count), THEN PUT the client files. Server-before-client, never the reverse. Within the server pair, order is safe if the changes are additive/backward-compatible.

Scratchpad pattern: `deploy_gateway_atomic.py` (this session). Deploy governance unchanged: only DJ's genuine picker tap IN the executing session authorizes the PUT — see [[feedback_dj_deploy_control_stage_and_trigger]], [[feedback_staged_mirror_stale_base_refetch]], [[feedback_verify_collection_and_live_pipe]].
