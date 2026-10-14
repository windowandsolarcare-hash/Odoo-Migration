---
name: project_agent_mail_1mb_contents_clobber
description: "GitHub Contents API OMITS .content for a file >1MB (returns the blob metadata with empty/missing content). So the standard AGENT_MAIL fetch→prepend→PUT reads EMPTY and the PUT CLOBBERS the entire ledger with just the new entry. Hit live 2026-10-13 at ~1.17MB/419 entries. Three guards + rotation below."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-14T06:24:29.765Z
---

Caught by Audit 2026-10-13 when `3_Documentation/AGENT_MAIL.md` (saunders-render-app) crossed 1MB (~1.17MB, 421 headings, 272 of them unhandled `[ ]`). Audit's own fetch→prepend→PUT read empty and clobbered the ledger; it restored all 419 from the pre-clobber blob. No data lost, but the trap was armed for every session + every mail-watcher cron.

**The trap:** `gh api repos/<r>/contents/<path> --jq '.content' | base64 -d` returns EMPTY once the file exceeds **1 MB** (GitHub Contents API hard limit — it omits `.content` for >1MB files; `.sha` still returns). The standard ledger-write pattern (read content → prepend new entry → PUT full content with the sha) then PUTs just the new entry over the whole file = a silent full clobber. Watchers are hit too: a `.content` scan returns empty → silent missed mail, and a ✅-mark PUT clobbers.

**THREE DURABLE GUARDS (every session + every watcher):**
1. **Empty-base guard (mandatory):** before ANY ledger PUT, if the fetched base is empty / <1000 bytes, ABORT — never PUT an empty-based ledger. `[ "$(wc -c < base)" -lt 1000 ] && abort`.
2. **Blobs-read if >1MB:** read CONTENT via the Blobs API (the sha from Contents still works): `sha=$(gh api .../contents/AGENT_MAIL.md --jq .sha); gh api .../git/blobs/$sha --jq .content | base64 -d`. The Blobs API serves up to 100MB (base64). Use it for any read of a file that may exceed 1MB.
3. **Mark handled entries ✅ (root cause):** the bloat came from 272 UNHANDLED `[ ]` entries — the ✅-discipline had lapsed (handled entries that were never marked, so never pruned). Mark addressed entries ✅ when done; rotation prunes handled/legacy. A lean active ledger is also DJ's token-cut win (every session re-reads it each watcher tick → see [[feedback_token_budget_fleet]]).

**ROTATION (how it was fixed, and how to redo it):** keep the ACTIVE `AGENT_MAIL.md` under 1MB by moving handled/legacy entries to a dated archive. 2026-10-13: active = all 272 `### [ ]` unhandled entries (764KB, <1MB — NEVER archive an unhandled entry); archive = the 149 non-`[ ]` (handled `[x]`/✅ + legacy date-prefixed) entries → `3_Documentation/AGENT_MAIL_ARCHIVE_2026-10.md` (nothing deleted, relocated only; read via Blobs). Reconcile counts (active+archive == original heading count) before trusting it. Do it with a SCRIPT that pipes the blob to a local file + splits in python — do NOT read 1MB into your own context (that's the Lead-context-growth cost DJ is cutting). PUT the archive first (data safe), then the trimmed active with CAS on the sha you read; if the archive PUT 400s "Problems parsing JSON", use the python-json.dump payload fallback ([[feedback_github_deploy_python_fallback]]).

**How to apply:** when AGENT_MAIL (or any ledger/log file written by fetch→prepend→PUT) approaches 1MB, rotate BEFORE it crosses; always guard the base-non-empty on a ledger PUT; read big files via Blobs. Ties [[project_agent_mail_channel]], [[feedback_agent_mail_autowatch]], [[feedback_push_compare_and_swap]], [[feedback_staged_mirror_stale_base_refetch]].
