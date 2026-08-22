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

## Related environment facts for cloud sessions (same discovery, 2026-08-22)

The cloud sandbox's network allowlist may permit **only `api.github.com`**. `wscare.pro`,
`wsc-field-assistant.onrender.com` and `window-solar-care.odoo.com` all returned proxy 403s
(`curl` exit 56). Check with `curl -sS "$HTTPS_PROXY/__agentproxy/status"`, which lists recent
`connect_rejected` hosts. **Consequence: a cloud session cannot verify by content, cannot smoke-
test a live endpoint, and cannot query Odoo** — so anything shipped from cloud needs a local
session or DJ to run the content verification ([[feedback_odoo_verify_content_not_status]]).
Say so explicitly rather than implying a change was verified. DJ is opening the allowlist.

Related: [[feedback_gh_push_empty_file_guard]], [[feedback_github_deployment_bash]],
[[feedback_regression_guard_pushes]], [[feedback_mirror_memory_to_github]]
