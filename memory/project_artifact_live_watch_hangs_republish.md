---
name: project-artifact-live-watch-hangs-republish
description: An ACTIVE artifact live-subscription (watch) makes Artifact republishes hang for many minutes. Unwatch the artifact and republishes take ~10-20s. Unwatch right after the first publish.
metadata:
  type: project
---

Observed 2026-08-22 building the WSC 6x9 "See the Beautiful View" canvas. Six republishes of the
same ~2.4-3.0 MB seeded design-canvas file to the same artifact URL:

| # | live watch state | result |
|---|---|---|
| 2 | active | hung 7 min, DJ interrupted |
| 3 | paused (by #2's interrupt) | **14 s** |
| 4 | active (resumed by #3) | hung 10 min, interrupted |
| 5 | paused (by #4's interrupt) | **8 s** |
| 6 | active (resumed by #5) | hung 7 min, interrupted |
| 7 | `action: "unwatch"` first | **19 s** |

**Why:** publishing an artifact arms a background live-update subscription. An interrupt PAUSES it and
"the next publish resumes it" — which is exactly why every post-interrupt publish was fast and every
publish that ran with the watch live hung. Six for six. Explicitly unwatching reproduced the fast
path without needing an interrupt (`Live subscription: skipped`).

**Ruled out** (do not repeat these guesses to DJ — he pushed back, correctly): file size (identical
across fast and slow runs), the size of the design edit (irrelevant — the whole document re-uploads
every save), and turn position / how many tool calls preceded the publish (run #5 followed a large
combined build and was 8 s).

**How to apply:** on a design canvas being iterated conversationally, call
`Artifact {action: "unwatch", url}` right after the FIRST publish, then republish freely. Only re-arm
a watch if the user asks or someone else may be editing the artifact — the watch's purpose is to catch
other people's saves, which does not apply when one session owns the file. If a save does hang, stop it
at ~60 s; nothing is lost (the local seeded file is already written, the link just still shows the
previous version). Time saves with `date` on both sides so any claim is measured, not guessed.

See [[project_design_canvas_png_export_is_1to1]].
