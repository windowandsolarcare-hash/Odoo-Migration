---
name: project_session_transcript_persistence
description: Self-spawned fleet sessions ran with transcript saving OFF (inherited CLAUDE_CODE_CHILD_SESSION); fixed via CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1 in both settings.json + user setx. New sessions save; already-running unsaved sessions are unrecoverable on exit.
metadata: 
  node_type: memory
  type: project
  originSessionId: a5bf77bf-5348-4b7b-bca3-196b7cde1063
  modified: 2026-09-18T18:56:45.458Z
---

**Discovered 2026-09-18 (Dispatcher + claude-code-guide agent, DJ-flagged).** The fleet self-spawns sessions (the `wt.exe` self-spawn trick), so every child inherited the `CLAUDE_CODE_CHILD_SESSION` env marker. That marker **disables transcript saving** — no `~/.claude/projects/<project>/<session-id>.jsonl` is written — and the CLI showed: *"Transcript saving is off — inherited CLAUDE_CODE_CHILD_SESSION marker · restart with CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1 to keep future transcripts."* This silently affected Lead, Dispatcher, and every self-spawned role.

**The facts (verified):**
- `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1` overrides the child marker and forces transcript saving ON. It is read **at launch only** — it does NOT reach a process already running.
- An **already-running unsaved session's history is permanently lost on exit** — no in-RAM cache survives, and restarting starts it *fresh* (nothing to `--resume`, because nothing was written). There is **no retroactive save**. (DJ resumed "Del Lead" earlier only because that session *was* being saved — it is NOT evidence unsaved sessions recover.)
- A persistent user env var (Windows `setx`) is inherited by all future child processes, but only after the **parent restarts** (children snapshot the parent's env at spawn).

**Fix applied 2026-09-18 (three layers so it can't slip through):**
1. Project `.claude/settings.json` → added `"env": { "CLAUDE_CODE_FORCE_SESSION_PERSISTENCE": "1" }`.
2. Home `C:\Users\dj\.claude\settings.json` → same `env` block.
3. `setx CLAUDE_CODE_FORCE_SESSION_PERSISTENCE 1` (user-level, registry now = 1).

The `settings.json` env block is the durable foundation (version-agnostic, re-read every launch, no inheritance-timing dependency); `setx` is the belt for anything launched outside the project dir.

**Why:** without this, killing any self-spawned tab lost that session's entire transcript — a real risk for research/context that lived only in a session's head (e.g. Lead's GBP research). See [[feedback_durable_foundation_over_shortcut]].

**How to apply:**
- **Every NEW session now saves automatically** — no action needed.
- **Already-running sessions stay unsaved until restarted**, and the restart does not recover current history. Before exiting any live session that holds something valuable, dump it to durable files (DISPATCH_BOARD / memory / docs) FIRST, then relaunch (the new one saves from the start).
- To confirm a session's state: `echo $CLAUDE_CODE_CHILD_SESSION` (1 = child) and `$CLAUDE_CODE_FORCE_SESSION_PERSISTENCE` (1 = saving forced on).
