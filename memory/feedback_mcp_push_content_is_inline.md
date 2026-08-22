---
name: feedback_mcp_push_content_is_inline
description: "CLOUD sessions have no `gh` CLI — push via the GitHub MCP `create_or_update_file`, whose `content` is the FILE TEXT inline, not a path. Passing a path silently commits a tiny placeholder over the real file."
metadata:
  node_type: memory
  type: feedback
---

**Discovered 2026-08-22 by the Portal session, first cloud session to push.**

## The trap

Cloud Claude Code sessions (Anthropic-hosted, not DJ's Surface Pro) **do not have `gh`
installed** — `gh: command not found`. So the whole documented deploy path in CLAUDE.md
(`gh api ... --input payload.json`, `deploy_to_github.sh`, `safe_deploy.py`) is unavailable.
The replacement is the GitHub MCP tool **`mcp__github__create_or_update_file`**, which uses the
same Contents API under the hood, so it still satisfies the "Contents API, never `git push`"
rule that the protected `main` ruleset requires.

**But its `content` parameter is the file's FULL TEXT, passed inline — NOT a file path.**
It is not `gh api --input`, and it is not `--local`. There is no path-taking variant.

I passed `content: "// see local file"` expecting the tool to read the local file. It did not.
It committed an **18-byte file** over the intended one and returned a perfectly normal success
response with a commit URL. Nothing errored. Caught only because I read `size` in the result.

## Why this is dangerous, not just annoying

This is the same failure class as [[feedback_gh_push_empty_file_guard]] — a near-empty file
silently replacing a real one — but it arrives through a **new door**, so the old guard does not
catch it:

- `safe_deploy.py`'s line/byte regression guard **is not in the loop** (that's a local script).
- The Render `github_push_file` server-side guard **is not in the loop** either.
- The MCP tool has **no size or regression guard at all**.

On a doc it's embarrassing. On `portal.py`, `dashboard.py` or `field.html` it is an outage —
an 18-byte Python file crashes app boot on the next Render deploy.

## How to apply

1. **Write the file locally first** (Write/Edit), then **Read it back and pass its exact text**
   as `content`. Never pass a path, a placeholder, or a summary.
2. **Check `size` in the tool result** before calling the push done. Compare it to the local
   file's byte count. A three-digit `size` on a file you know is thousands of bytes = you just
   clobbered it; fix it immediately with a second push using the `sha` the bad result returned.
3. **Updating an existing file requires its blob `sha`.** Get it from `git rev-parse main:<path>`
   or from the previous push's result. Omitting it fails; passing a stale one fails.
4. The commit-message convention is unchanged: `YYYY-MM-DD | filename | description`.

## You cannot script a guarded push — MCP is the ONLY GitHub path

Do not burn time trying to rebuild `safe_deploy.py`'s guard as a shell script. **Raw `curl` to
`api.github.com` is blocked for both reads and writes**, even though `GITHUB_TOKEN` / `GH_TOKEN`
are present in the cloud env. Writes return *"Write access to this GitHub API path is not
permitted through this proxy"*; reads return *"GitHub access is not enabled for this session."*
The env tokens are not usable for this. `git fetch` **does** work (separate git proxy), which is
the one useful lever — see the verification trick below.

So the guard has to be **manual discipline on every push**: check the local byte count first,
then check `size` in the MCP result.

## Verifying a cloud push BY CONTENT

The MCP result's `size` is a good first check but only proves length. For a real content check,
use git (which is not proxy-blocked):

```
git fetch origin main -q
git show origin/main:<path> | diff - <local file>     # silence = byte-identical
```

Do NOT use `git diff origin/main -- <path>` for a file you just created: a locally **untracked**
file shows as a full deletion and looks alarming for no reason. Diff the blob, as above.

That same `git fetch` also reveals **concurrent pushes from other sessions** — worth a look
before assuming your local copy is current.

## The broader cloud limits live elsewhere

`gh` absence, the GitHub-only network allowlist, no auto-loaded `~/.claude` memory, and the fix
(open the environment's network allowlist) are all documented in
**[[project_cloud_session_env_limits]]** — written the same day by the cloud-Lead session. Keep
the environment facts THERE and the push mechanics here; don't restate them in both or they will
drift.

Related: [[feedback_gh_push_empty_file_guard]], [[feedback_github_deployment_bash]],
[[feedback_regression_guard_pushes]], [[feedback_mirror_memory_to_github]]
