---
name: project_git_data_api_atomic_multifile_push
description: Land many files in ONE commit/deploy on protected main via the GitHub Git Data API (blobs→tree→commit→refs PATCH) — it works; plus the Windows cp1252/emoji gh-JSON decode fix.
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-19T06:58:16.503Z
---

Discovered 2026-09-18 building A19 (referrer-aware Back) — needed to tag ~38 back controls + a binder in ONE atomic commit (Contents API is one-file-per-commit → 38 commits/deploys = unacceptable).

**★ The GitHub Git Data API DOES work on this protected `main`** (repo `windowandsolarcare-hash/saunders-render-app`) — it is NOT blocked like plain `git push`. Sequence (all via `gh api`):
1. `GET repos/<R>/git/ref/heads/main` → head sha; `GET repos/<R>/git/commits/<head>` → `.tree.sha` (base_tree).
2. Per file: `POST repos/<R>/git/blobs` with body `{content:<b64>, encoding:"base64"}` → blob sha. **Pass blob content via stdin (`--input -`), NOT `-f content=` — a whole file's base64 exceeds the Windows command-line length limit ([WinError 206]).**
3. `POST repos/<R>/git/trees` `{base_tree, tree:[{path,mode:"100644",type:"blob",sha}]}` → tree sha (via `--input -`).
4. `POST repos/<R>/git/commits` `{message, tree, parents:[head]}` → commit sha.
5. `PATCH repos/<R>/git/refs/heads/main` `{sha:<commit>}` → **succeeds** (verified; refs PATCH is allowed, unlike git push).
The refs PATCH is the only step that changes `main` — build blobs/tree/commit freely, it fails closed if ever blocked. Landed 39 files (A19 P1) + 9 (P2) + 3 (P3) each as ONE commit = ONE deploy.

**Why:** the "gh api Contents PUT, never git push" rule is about the transport git-push uses; the REST Git Data API (blobs/trees/commits/refs) is a different, ALLOWED path and is the right tool for an atomic multi-file change.

**★ Windows Python `subprocess` + gh JSON = force UTF-8.** `subprocess.run(text=True)` decodes gh's stdout with the locale codec (cp1252 on DJ's Surface), which throws `UnicodeDecodeError: 'charmap' can't decode byte 0x8f` on any gh response containing emoji — e.g. `GET .../commits/<sha>` (recent commit MESSAGES here carry ✅/→/📅). Fix: `subprocess.run(..., capture_output=True, encoding="utf-8", errors="replace")` (drop `text=True`). Bit me mid-A19; fixed. (Tangent: `GET .../git/commits/<sha>` [git-data] is lighter than `GET .../commits/<sha>` [REST] but both can carry the message.)

**How to apply:** for any change touching many files atomically (global-nav sweeps, mass attribute rollouts), use the Git Data API multi-file commit via `gh api` from a Python orchestrator with `encoding="utf-8"` + blob content over stdin. One commit = one deploy = no thrash. Still run pre-push gates (node --check / py_compile) on the edited files first. See [[feedback_github_deployment_bash]] and [[feedback_bash_tmp_not_persistent]].
