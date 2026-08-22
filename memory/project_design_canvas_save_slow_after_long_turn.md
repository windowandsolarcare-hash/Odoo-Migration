---
name: project-design-canvas-save-slow-after-long-turn
description: Design-canvas Artifact saves hang for many minutes when they trail a long tool-heavy turn; issued on their own they take ~8-14s. Save as its own step.
metadata:
  type: project
---

Publishing/republishing a design canvas (the `/design` skill's seeded ~2.4 MB `.html`) to the same
Artifact URL shows two very different behaviors, observed 2026-08-22 on the WSC "See the Beautiful
View" 6x9 piece:

- Save issued as essentially the ONLY tool call in the turn → **8s and 14s** (two runs, timed).
- Save issued at the END of a long turn (Edit + image resize + heredoc writes + re-seed, then
  publish) → **hung 7 min and 10 min**; DJ interrupted both. Same file, same 2.4 MB, same path.

**Why:** ruled out the obvious suspects — file size was identical across all four attempts, and the
size of the design change is irrelevant (the whole page re-uploads every save, editor code included,
~2.2 MB of the 2.4 MB is the baked-in canvas editor). The remaining correlate is turn position. Not
proven causal, but 4/4 consistent. Secondary suspect: the artifact's background live-update
subscription re-arming (`action: "status"` / `unwatch` to test) — untested.

**How to apply:** do the build work — asset prep, artboard edits, re-seed, `--check` — in one turn,
then issue the **Artifact publish as its own step**, ideally first thing in the next turn. If a save
does hang, **stop it at ~60s** rather than letting it sit; nothing is lost (the local seeded file is
already written, the live link just still shows the previous version) and re-issuing it standalone
has cleared it every time. Do NOT tell DJ it is the file size or the size of his edit — it is not,
and he will (correctly) push back. Time saves with `date` on both sides so the claim is measured, not
guessed. See [[feedback_always_paste_preview_link]].
