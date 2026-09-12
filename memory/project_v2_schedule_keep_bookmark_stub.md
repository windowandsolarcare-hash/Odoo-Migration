---
name: project_v2_schedule_keep_bookmark_stub
description: "static/owner/v2_schedule.html is a KEEP — a redirect stub that forwards OLD BOOKMARKS to v2_command.html (DJ's live Command Center). It has ZERO code refs but deleting it would 404 DJ's saved bookmark. Never retire it despite looking dead."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T15:27:45.954Z
---

**DJ 2026-09-12:** `static/owner/v2_schedule.html` must NOT be deleted, even though it looks dead.

- It is a **bookmark-forwarding redirect stub** — its body just forwards to **`v2_command.html`** (DJ's live Command Center, his most-important screen). Title reads "Moved to the current version."
- It has **zero inbound CODE references** (not in any launcher/home, no links) — so automated "dead file" / prune scans flag it as dead. **But user bookmarks are not code refs.** DJ has the old URL saved; deleting the file would 404 his bookmark into the screen he uses most.
- **Rule:** a redirect/forwarding stub with zero code refs is NOT automatically dead — check whether it protects a user-facing URL (bookmark, QR code, printed link, external integration) before retiring. Keep v2_schedule.html.
- Inventory reflects this: `3_Documentation/CAPABILITY_INVENTORY.md` row = KEEP; `PRUNE_REVIEW_LIST.md` B2 = DO NOT DELETE. The only remaining delete candidate in that sweep is `v2_vault_wysiwyg_test.html` (pending DJ's final yes).

Related: [[feedback_never_remove_working_code]], [[project_two_quote_pages_two_launchers]].
