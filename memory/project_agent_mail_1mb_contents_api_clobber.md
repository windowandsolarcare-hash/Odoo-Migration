---
name: project_agent_mail_1mb_contents_api_clobber
description: AGENT_MAIL.md >1MB → GitHub Contents API returns empty .content → fetch→prepend→PUT clobbers the whole ledger; read via Blobs API + guard
metadata:
  node_type: memory
  type: project
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-14T06:16:34.962Z
---

**AGENT_MAIL.md (and any file) over 1MB silently clobbers on our standard post pattern.** Discovered 2026-10-13 (Audit): the ledger grew to ~1.17MB / 124k+ lines / 419 entries. The **GitHub Contents API omits `.content` for files >1MB** — `gh api repos/<repo>/contents/<path> --jq '.content'` returns EMPTY (the blob `.sha` still returns fine). Our canonical ledger-post pattern is `gh api .../contents/AGENT_MAIL.md --jq '.content' | base64 -d` → prepend entry → PUT with that sha. At >1MB the base reads EMPTY, so the PUT writes "entry + nothing" and **OVERWRITES the entire ledger**. I hit it live posting a §15 review (re-fetch returned 0 lines), the PUT clobbered 419 entries down to ~40 lines (commit 2ed00154), and I restored the full ledger from the pre-clobber blob (commit 597ed6389) → verified 420 headings. No data lost, but it's a fleet-wide landmine: every session's post AND every mail-watcher that `.content`-scans is affected.

**Why:** GitHub REST Contents API hard-caps inline content at 1MB; above that it returns the metadata (incl. `.sha`) with empty/omitted `content`. Blobs API has no such cap (handles up to 100MB).

**How to apply:**
- READ ledger CONTENT via the **Blobs API**, not Contents, whenever the file may exceed 1MB:
  `sha=$(gh api repos/<repo>/contents/3_Documentation/AGENT_MAIL.md --jq '.sha')`  (Contents `.sha` still works → fine for watcher change-detection)
  `gh api repos/<repo>/git/blobs/$sha --jq '.content' | base64 -d > AGENT_MAIL.md`  (full content)
  then prepend your entry to THAT and PUT with `$sha`.
- GUARD every ledger PUT: assert the fetched base is non-empty / >1MB before building the payload; abort otherwise. (A `assert len(base) > 1_000_000` in the payload-builder would have caught this.)
- WATCHERS: a `.sha` change-detect still fires, but a `.content` scan returns empty → the watcher SILENTLY SEES NO MAIL (missed items) and a ✅-mark prepend-PUT CLOBBERS. Switch watcher content reads to the Blobs API too.
- DURABLE FIX: ROTATE the ledger — the protocol's "prune ✅-handled entries older than ~1 week" wasn't happening (419 live entries). Archive old handled entries to e.g. `AGENT_MAIL_ARCHIVE_<YYYY-MM>.md`, keep the active ledger under 1MB → restores normal Contents-API posting. Ledger-owner's call (Lead/Dispatcher), not unilateral.

Same trap applies to ANY large file pushed via the Contents API (SHARED_MEMORY.md, big docs). Relates to [[feedback_push_compare_and_swap]], [[feedback_gh_push_empty_file_guard]], [[project_agent_mail_channel]], [[feedback_agent_mail_autowatch]].
