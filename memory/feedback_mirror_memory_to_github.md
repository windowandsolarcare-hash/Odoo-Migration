---
name: feedback_mirror_memory_to_github
description: "★ STANDING RULE (DJ via Lead 2026-08-22): whenever you write/edit ANY memory file, ALSO mirror it to GitHub windowandsolarcare-hash/Odoo-Migration → memory/<name> via `gh api` Contents PUT (fetch sha first if it exists) — in ADDITION to the SHARED_MEMORY.md dual-write. Use gh api, NEVER git push (main is ruleset-protected; Contents API is allowed)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-22T17:37:39.080Z
---

**The full project memory is now mirrored to GitHub** (`windowandsolarcare-hash/Odoo-Migration` → `memory/`). It was local-only + unbacked — a drive failure would have lost 600+ files.

**Why:** memory is the single highest-leverage habit — it's how a blank new session comes up to speed in minutes; and now it's crash-safe (backed to GitHub).

**How to apply:**
- After writing/editing any local memory file `memory/<name>.md`, push it to `Odoo-Migration/memory/<name>.md`: fetch its sha if it already exists (`gh api repos/windowandsolarcare-hash/Odoo-Migration/contents/memory/<name>.md --jq '.sha'`), then Contents PUT the base64 content with that sha (or no sha for a new file). This is IN ADDITION to updating `3_Documentation/SHARED_MEMORY.md` in the saunders-render-app repo.
- **`gh api` Contents PUT only — NEVER `git push`** (main is ruleset-protected and rejects direct git pushes; the Contents API is allowed). Same pattern as every other deploy in this project.
- Also mirror `MEMORY.md` and the touched `idx_*.md` index when they change.
- Capture discoveries the MOMENT they happen (field name, quirk, decision, "we agreed to X") — self-contained + dated. A background agreement that isn't written down does NOT survive to the next session.

Applies to ALL sessions (Lead/Specialists/Web/Portal/Operator/Design). See [[feedback_save_filter]] and the DUAL-WRITE rule in CLAUDE.md.
