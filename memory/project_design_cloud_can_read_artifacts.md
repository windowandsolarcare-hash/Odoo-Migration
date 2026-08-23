---
name: project-design-cloud-can-read-artifacts
description: VERIFIED 2026-08-23 — the CLOUD Design session CAN read published artifact content back via the Artifact tool's read action. The earlier "*.frame.claudeusercontent.com is proxy-blocked" finding does NOT break the edit-and-republish loop.
metadata:
  type: project
---

Tested 2026-08-23 from the cloud Design session (Anthropic-hosted, not DJ's Surface Pro), because
DESIGN_CHARTER.md warns that artifact reads may be impossible here and that this would break the
core edit-and-republish loop.

**Result: reads work.**
- `Artifact` with `action: "list"` returned all 10 published artifacts (title, URL, updated date).
- `Artifact` with `action: "read"` on the WSC EDDM Postcard
  (`https://claude.ai/code/artifact/f5bed7b3-cde9-472c-a630-d760bfa2024c`) returned the full page —
  2.1 MB — and saved it to a local file. The real artboard markup is in there (found the live copy
  string "Sparkling-clean windows & solar panels — done right, by your local desert crew." with its
  inline styles), not just the canvas runtime shell.

**Why the old 403 finding is not the same thing.** A raw `curl` to
`https://<id>.frame.claudeusercontent.com/_f/<build>/` still returns **403** — but the proxy prints
`HTTP/1.1 200 Connection Established` first, so the **CONNECT succeeded**; the 403 is the artifact
host itself refusing an unauthenticated direct fetch (its CSP is `frame-ancestors 'self'
https://claude.ai`, i.e. it expects to be framed by claude.ai). That is host auth, not a network
block. Whatever was measured as a proxy 403 earlier is not blocking this path now.

**How to apply:**
- Do not tell DJ the cloud Design session can't recover a design. It can.
- **Still keep the working `.dc.html` files locally between turns.** Read-back returns the whole
  published page with the artboard source embedded as a JSON-escaped string inside it — recoverable,
  but it needs extracting and unescaping. Local working files remain the fast path; read-back is the
  recovery path (files lost, or picking up a hand edit someone made in the canvas editor).
- Charter line "Requires the artifact host … If artifact reads fail, that is the cause" should be
  read as a contingency, not the current state.

**Cloud session limits that ARE real here (unchanged):** the env `GITHUB_TOKEN` is a 14-char
placeholder and direct `api.github.com` calls with it return 403 — GitHub writes go through the
GitHub MCP tools. `gh` CLI is not installed.

See [[project_design_canvas_png_export_is_1to1]], [[project_cloud_session_env_limits]].
