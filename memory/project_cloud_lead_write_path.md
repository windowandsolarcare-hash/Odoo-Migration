# Cloud session write path: MCP Contents API, NOT gh and NOT raw api.github.com

**Type:** project
**Date:** 2026-08-22
**Applies to:** any CLOUD Claude Code session (Anthropic-hosted container), not DJ's local Surface Pro.

## What

A cloud session CANNOT deploy the way CLAUDE.md's GITHUB DEPLOYMENT WORKFLOW describes. Two of the
three obvious routes are unavailable, and the third is the one to use:

1. **`gh` CLI — NOT INSTALLED.** `which gh` → not found. Every `gh api repos/.../contents/...`
   recipe in CLAUDE.md is local-Lead-only. There is no PowerShell either, so the
   `powershell -Command ... ToBase64String` wrapper is moot.
2. **Direct `https://api.github.com` — BLOCKED (HTTP 403) by the session egress policy.**
   `GH_TOKEN`/`GITHUB_TOKEN` ARE set in env, so a curl looks like it should work — it does not.
   The agent proxy returns 403 on CONNECT because the host is not on the org allow-list.
   Per `/root/.ccr/README.md`: **do NOT retry or route around a 403/407 — report the blocked host.**
   Do not "fix" this by unsetting HTTPS_PROXY or disabling TLS verification.
3. **★ USE: the GitHub MCP server — `mcp__github__create_or_update_file`.** This IS the Contents API
   PUT (the server calls the REST endpoint on our behalf through Anthropic's relay). So it satisfies
   the project rule exactly: **Contents API = allowed by the main ruleset; `git push` = rejected.**
   Load it with `ToolSearch` `select:mcp__github__create_or_update_file` first.

## ★ CORRECTION 2026-08-30 — there IS a cheap write path: branch → PR → squash-merge

The claim above that "`git push` = rejected" is **true only for `main`**. It was never tested against
a feature branch, and the untested half is the useful half:

- **`git push origin HEAD:refs/heads/<branch>` WORKS from a cloud session.** Git-over-HTTPS is not
  blocked by the proxy (only `api.github.com` REST is), and the ruleset protects `main` — not every ref.
- So the cheap route to `main` is: **commit locally → `git push` the branch →
  `mcp__github__create_pull_request` → `mcp__github__merge_pull_request` (squash).** Land it on main,
  branch auto-deletes, history stays clean.
- **This costs DIFF-sized tokens, not FILE-sized.** For a 22 KB index file that is ~200 tokens instead
  of ~6,000. For `AGENT_MAIL.md` (~26k tokens per Contents PUT) the saving is enormous — which is
  exactly why cloud sessions were told to avoid mail posting. That constraint is largely lifted.
- It fully satisfies DJ's fleet requirement below: the change lands **on `main`**, which is what
  every session reads. A PR is a transport mechanism, not a parking spot — nothing sits on a branch.

**Use Contents API (`create_or_update_file`) for small files** (a few KB — one memory file, a short
doc); it is one call instead of four. **Use branch → PR → merge for anything large**, or for a
multi-file change that should land as one commit.

Verified 2026-08-30: PR #2 (`15fba33`, v2_command.html + scheduler.py) and PR #4 (`3e6028c`, memory).
Two mechanics worth knowing: `--force-with-lease` fails with *"stale info"* when the remote branch does
not exist yet (just push normally), and after a squash-merge deletes the branch, re-pushing the same
branch name needs a plain push, not a force. See [[feedback_verify_limits_before_declaring]] — this
whole correction exists because a limit was declared from one failed method without testing the others.

## How to apply

- **Reading** is cheap and does NOT need MCP: the repos are cloned on disk at `/home/user/<repo>`, and
  `git fetch origin main` works (git goes through the proxy's git accommodation, unlike api.github.com).
  Always `git fetch origin main` and compare `git rev-parse HEAD origin/main` before editing — the
  clone is from container start and can be stale. Get the blob sha for a PUT with
  `git rev-parse origin/main:<path>`.
- **Writing:** `mcp__github__create_or_update_file` with `branch: "main"`, `sha:` = the existing blob
  sha (REQUIRED for an update; omit only when creating a new file). Content is passed as a plain
  string — the MCP server base64-encodes it. Do NOT pre-encode.
- **★ COST GOTCHA — this is the real difference from local.** Local Lead pipes a file through base64
  without ever loading it into context. The MCP tool takes `content` as a literal string, so the
  ENTIRE file passes through the model's context on every write. `AGENT_MAIL.md` (~1,600 lines) is
  roughly 26k tokens PER WRITE. Budget for it: batch mail entries rather than posting one at a time,
  and prefer touching small files. This is why a cloud session should not be the one doing routine
  high-frequency mail posting if a local session is available.
  **↑ Largely superseded — see the CORRECTION above: branch → PR → merge costs diff-sized tokens,
  so a large file no longer has to pass through context at all.**
- The `safe_deploy.py` regression guard is also local-only (`C:\Users\dj\safe_deploy.py`). A cloud
  session must enforce the pre-push gates BY HAND: fetch live first, and compare line counts against
  `origin/main` before any large-file write. The 2026-04-30 stale-push incident (2,277 lines lost)
  is exactly as possible from the cloud as from local — arguably more so, since the guard is absent.

## Why it matters

The branch instruction a cloud session boots with ("develop on `claude/<...>`, push there") is WRONG
for this project's fleet artifacts and DJ overruled it explicitly (2026-08-22): **the entire fleet
reads `main`.** Anything committed to a working branch is invisible to Portal, Specialists, Web and
Operator, so AGENT_MAIL / memory / docs go to `main` via the Contents API, always. A cloud session
that quietly follows its default branch instruction breaks fleet comms without any error appearing.

## Related

- CLAUDE.md → "CLOUD SESSIONS — HOW TO READ YOUR MEMORY" (the read half of this; this note is the write half)
- [[feedback_mirror_memory_to_github]] — mirror every memory to `Odoo-Migration/memory/<name>`; from a
  cloud session the commit IS the mirror, so one Contents PUT covers it.
- [[feedback_github_deployment_bash]] / [[feedback_regression_guard_pushes]] — the local recipes these replace.
