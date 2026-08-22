---
name: project-design-canvas-png-export-is-1to1
description: VERIFIED — design-canvas PNG export is 1:1 with the artboard's CSS px, so authoring the artboard at 300-DPI dimensions yields a true press-res file. No AI upscaler needed.
metadata:
  type: project
---

Verified 2026-08-22 on the WSC 6x9 "See the Beautiful View" litho piece. Artboard authored at
**2775 x 1875 CSS px** (= 9.25 x 6.25 in at 300 DPI: a 9x6 trim plus .125 bleed). DJ exported PNG
from the canvas toolbar; the file (`Main@1x.png`) came back **exactly 2775 x 1875**.

**Why it matters:** the `/design` skill says export is "screen-res (96 DPI)" and the canvas is a proof
tool, not a press RIP. That is true about the *default* authoring scale, NOT a pixel ceiling — the
export is 1:1 with whatever CSS px the artboard is. So authoring at press dimensions makes the export
the press master. This removes the whole "export a 96-DPI proof then run it through Upscayl" step DJ
had planned, and with it the risk of an AI upscaler inventing letterforms in his logo and headline.
Type renders NATIVELY at full size — inspected the export at 1:1 and the Barlow Condensed edges are
crisp, no interpolation. (Google Fonts DID render in the export here, contrary to the skill's warning
that exports fall back — still pick close-metric fallbacks, but don't assume the fallback.)

**How to apply — authoring:** compute the artboard as `trim_inches + 2*bleed` x 300. Keep every inset
in those same 300-DPI px (for a .125 bleed: trim sits 37.5px in from each edge, a .25in safe margin
sits 112.5px in). Embed the photo at the artboard's full pixel width or the export is soft. Cost: the
page grows (~3.0 MB here vs 2.4 at 96 DPI) since the whole document re-uploads on every save.

**How to apply — handing the file to DJ (both bite):**
1. **No DPI tag is embedded.** Photoshop opens it as 72 DPI / ~38.5 in wide and it LOOKS wrong.
   Fix is a relabel, not a resample: Image Size, **uncheck Resample**, set Resolution 300 -> reads
   9.25 x 6.25 with zero pixels changed. Say this every time or he'll think the export failed.
2. **Export is RGBA** (carries an alpha channel) and RGB color. Flatten, then convert to CMYK for
   litho. PNG is the right thing to pull out (lossless master); rewrap to TIFF/PDF for the printer.
3. **Do NOT use "Export PDF" for press** — it rasterizes to JPEG and builds the page at 96 css px/in,
   so a 2775px-wide artboard becomes a ~28.9in page. Pixels right, page size wrong.

See [[project_design_canvas_save_slow_after_long_turn]].
