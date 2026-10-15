---
name: project_agent_mail_1mb_contents_api_clobber
description: AGENT_MAIL.md >1MB → GitHub Contents API returns empty .content → fetch→prepend→PUT clobbers the whole ledger; read via Blobs API + guard
metadata:
  node_type: memory
  type: project
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-15T14:58:04.022Z
---

**AGENT_MAIL.md (and any file) over 1MB silently clobbers on our standard post pattern.** Discovered 2026-10-13 (Audit): the ledger grew to ~1.17MB / 124k+ lines / 419 entries. The **GitHub Contents API omits `.content` for files >1MB** — `gh api repos/<repo>/contents/<path> --jq '.content'` returns EMPTY (the blob `.sha` still returns fine). Our canonical ledger-post pattern is `gh api .../contents/AGENT_MAIL.md --jq '.content' | base64 -d` → prepend entry → PUT with that sha. At >1MB the base reads EMPTY, so the PUT writes "entry + nothing" and **OVERWRITES the entire ledger**. I hit it live posting a §15 review (re-fetch returned 0 lines), the PUT clobbered 419 entries down to ~40 lines (commit 2ed00154), and I restored the full ledger from the pre-clobber blob (commit 597ed6389) → verified 420 headings. No data lost, but it's a fleet-wide landmine: every session's post AND every mail-watcher that `.content`-scans is affected.

**Why:** GitHub REST Contents API hard-caps inline content at 1MB; above that it returns the metadata (incl. `.sha`) with empty/omitted `content`. Blobs API has no such cap (handles up to 100MB).

**How to apply:**
- READ ledger CONTENT via the **Blobs API**, not Contents, whenever the file may exceed 1MB:
  `sha=$(gh api repos/<repo>/contents/3_Documentation/AGENT_MAIL.md --jq '.sha')`  (Contents `.sha` still works → fine for watcher change-detection)
  `gh api repos/<repo>/git/blobs/$sha --jq '.content' | base64 -d > AGENT_MAIL.md`  (full content)
  then prepend your entry to THAT and PUT with `$sha`.
- GUARD every ledger PUT with a **FAILED-READ FLOOR, NOT the 1MB size**: `assert len(base) > 1000` (abort only if the base came back empty/failed). ★ Do NOT guard on the 1MB figure. A real ledger is routinely UNDER 1MB (806KB on 2026-10-14; rotation deliberately keeps it under 1MB), so `assert len(base) > 1_000_000` ABORTS every legitimate post and turns the writer into a SILENT no-op. That exact backwards guard shipped in the handoff launcher's `_post_agent_mail` (`len(content) < 1000000` → abort) and would have made the whole feature inert — Lead caught it on the bytes 2026-10-14. Keep the two concepts SEPARATE: the **1MB is the TRIGGER** of the Contents-API-omits-`.content` trap (the reason to read via Blobs, which has no size cap); the **guard is a small non-empty floor** that only distinguishes a failed/empty read (~0 bytes) from any real ledger (KBs to ~1MB). Conflating them is the trap-within-the-trap.
- WATCHERS: a `.sha` change-detect still fires, but a `.content` scan returns empty → the watcher SILENTLY SEES NO MAIL (missed items) and a ✅-mark prepend-PUT CLOBBERS. Switch watcher content reads to the Blobs API too.
- ★ POSTING HYGIENE (Audit 2026-10-15, two non-destructive traps hit live, no content lost): (1) **Preserve line endings.** The live ledger has **CRLF** endings; a Python `open(path, encoding='utf-8').read()` is TEXT mode → universal-newline collapses `\r\n`→`\n` on read, so the prepend-PUT rewrites the ENTIRE file CRLF→LF = a noisy ~75 KB whole-file diff (wc -c said 817372, python len said 741704 on the SAME file — the gap is one `\r` per line). Read in **binary** (`open(path,'rb')`) or text with **`newline=''`**, splice the entry as bytes, and PUT unchanged bytes so only your entry diffs. (2) **Top-heading skip.** `base.find('\n### ')` matches the first heading that has a PRECEDING newline → it SKIPS the file's very first heading (line 1, no leading `\n`) → your "newest-on-top" entry lands at position **2**, under a stuck top entry. To truly prepend, match `^### ` at offset 0 too (e.g. insert at index 0 if `base.startswith('### ')`, else before the first `\n### `). Neither trap loses content, but both make a messy ledger.
- DURABLE FIX: ROTATE the ledger — the protocol's "prune ✅-handled entries older than ~1 week" wasn't happening (419 live entries). Archive old handled entries to e.g. `AGENT_MAIL_ARCHIVE_<YYYY-MM>.md`, keep the active ledger under 1MB → restores normal Contents-API posting. Ledger-owner's call (Lead/Dispatcher), not unilateral.

Same trap applies to ANY large file pushed via the Contents API (SHARED_MEMORY.md, big docs). Relates to [[feedback_push_compare_and_swap]], [[feedback_gh_push_empty_file_guard]], [[project_agent_mail_channel]], [[feedback_agent_mail_autowatch]].
