---
name: feedback_cloud_clone_stale_verify_from_github
description: "FETCH BEFORE YOU READ, not just before you push. A session's local clone is a snapshot from session start and goes stale within hours when multiple sessions commit to main. Also: when DJ reports something you can't find, YOUR SOURCE is wrong — never conclude DJ is misremembering his own running app."
metadata:
  node_type: memory
  type: feedback
---

**2026-08-30 — cloud Lead answered a question about live app behavior from an 8-day-old clone and told DJ a button he uses daily did not exist.**

**What happened.** DJ asked what the "Run NBHOF Auto" button on each Saunders Printing job card does. Lead ran `grep` across `/home/user/saunders-render-app` (the container's clone, made at session start on 2026-08-22), found nothing, and reported: no such button exists, there is no AppleScript anywhere in either repo, and "possibilities for what you're remembering" — i.e. it concluded **DJ** was misremembering. DJ sent a screenshot of the button. A `git fetch origin main` immediately revealed it: `runNbhofAuto()` at `static/printing/index.html:440`, built **that same day** by another session (source comments tagged `Lead 2026-08-30`).

**Root cause — two separate errors, both worth remembering.**

**1. The fetch-first rule was read as a DEPLOY rule.** CLAUDE.md already says "FETCH THE LIVE FILE FIRST — never edit a local copy you didn't fetch this session… the local repo copy is assumed stale." But it lives under the heading **MANDATORY PRE-PUSH GATES**, so a session that is only *reading* skips it. **Staleness corrupts a READ exactly as badly as a WRITE.** A stale push destroys work loudly (and `safe_deploy.py` guards it); a stale read produces a confident wrong answer with nothing to catch it. There is no regression guard on being wrong out loud.

**2. Reliability of sources was inverted.** When the grep came back empty, the session trusted its own snapshot over DJ's direct observation of his own running app. That is backwards in every case. **DJ describing a button he presses is primary evidence; a container's filesystem is a cache.**

**How to apply — both are now standing rules:**

- **Any question about what the app currently does starts with a fetch, not a grep.** `git fetch origin main && git reset --hard origin/main` (2 seconds), or read through the GitHub Contents API. This applies to reading, reviewing, QC, answering a question, and planning — not only to editing.
- **A cloud session's clone is made ONCE at session start and never updates itself.** With 5 sessions committing to main all day, it is stale within *hours*. Session age is not a proxy for freshness — assume stale always. (Same trap on a long-running local session that hasn't pulled.)
- **When DJ (or any session) reports something you cannot find, re-fetch BEFORE contradicting them.** Treat "user reports X, I don't see X" as evidence your source is stale. Never write "what you may be remembering" about the user's own live system without a fresh fetch first.
- Corollary for QC/review work: a fresh-eyes review run against a stale clone reviews code that no longer exists. Fetch at the START of every review, not just before pushing the result.

**Why:** this was not a code bug — nothing broke and nothing was overwritten. The damage was an authoritative wrong answer to the owner about his own system, plus telling him he was misremembering. That failure mode leaves no trace in git and no error in a log, so the only defense is the habit.

**Related:** the `nbhof://` URL-scheme AppleScript app that `runNbhofAuto` deep-links to is NOT in either repo — it exists as a single `.app` on DJ's Mac with no backup and no version history. Flagged to DJ 2026-08-30.
