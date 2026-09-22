---
name: feedback_compile_gate_before_push
description: "CHAIN the syntax check into the SAME && as git commit+push — a separate compile line doesn't abort the push, so a syntax error ships and crashes boot."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-22T16:18:38.114Z
---

**Always chain `python -m py_compile ...` (and `node --check`) into the SAME `&&` chain as `git commit && git push`.** If the compile check is a separate statement/line, its failure does NOT stop the subsequent git commands — the broken file gets committed + pushed anyway.

**Why:** 2026-09-22 (Builder-2, momscare doc-storage) — a `-- SQL comment` accidentally left on a Python `_MIGRATIONS` line was a SyntaxError. The bash had `python -m py_compile ... && echo OK` on one line, then `git add && git commit && git rebase && git push` on later lines. The compile FAILED (no "OK"), but the git block still ran → a syntax-error db.py shipped to `main`. On a `uvicorn main:app` app that's a **boot crash**. (Saved here because Render kept the last-good version — a failing deploy fails its health check and is NOT promoted, so there was no downtime — but that's luck, not the gate.)

**How to apply:** one chain — `python -m py_compile <files> && node --check <js> && git add -A && git commit -m ... && git push`. A compile failure then aborts before the commit. This is the momscare git-push analogue of the W&SC pre-push gate 2 (`node --check`/`py_compile` before every push) — but the point here is the CHAINING: the gate only protects you if a failure blocks the push. Also: a real image-magic-number test needs REAL image bytes (a text file named `.png` is correctly rejected by a magic-number sniff). See [[project_moms_care_app]].
