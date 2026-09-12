---
name: feedback_design_end_to_end_workflow
description: DJ's design workflow — he says "design X", Design does everything, and hands back ONE Google Drive link per piece. Dev proofs carry trim/safe guide lines; "I need my Zoo files" means drop the guides and produce clean CMYK press PDFs.
metadata:
  type: feedback
---

**DJ, 2026-09-12, stating how he wants Design to run end to end:**
*"Where I say start this design, you do everything, and then I just say show me the end result —
which is exactly that link. You could show me that link each time."*

## The loop
1. DJ names a piece. **Design does the whole thing** — no check-ins for routine choices.
2. Design renders it and **looks at it** ([[feedback_render_design_before_presenting]]).
3. Design hands back **a link per piece**, every time. Not a file card, not a canvas publish.
4. DJ reacts; Design iterates and sends the link again.
5. When DJ says **"I need my Zoo files"** -> guide lines come OFF, clean CMYK press PDFs go out.

## Proofs during development CARRY guide lines — he wants them
*"I don't care if you got crop marks. Matter of fact, if you got crop marks, it's even better. It
allows me to understand where things are… I might even have you drop in lines of safety lines, you
know, for the text, to make sure that it's not too close to the border."*
So the dev proof shows, as an overlay that is never baked into artwork:
- **magenta dashed** = trim
- **cyan dashed** = safe margin (.25 in inside trim)
- **orange line + label** = the USPS "address must be above this" top-half line, on the ADDRESS SIDE
  ONLY (on a front it is noise and it sat on the body copy — fixed)
- a note that the image edge is the bleed
Guides live in `_design_build.py`; `dev` mode draws them, `clean` mode doesn't. Same artboards both
ways, so a proof and a press file can never disagree.

## ★ DELIVERY: Google Drive links, not file cards
DJ is usually **on his phone**, and SendUserFile cards **did not open for him** — twice. Canvas
artifact publishes have repeatedly failed to reach him too (each publish needs his approval and the
prompt kept getting dismissed). What works:
**Google Drive for Desktop is mounted at `G:\My Drive`.** Copy the file into the right Drive folder,
then get its id with the Drive MCP (`search_files`, `title contains '...'`) and hand him
`https://drive.google.com/file/d/<id>/view`. It's his own Drive, so no sharing step is needed and it
opens on the phone. This is the default delivery path for every design deliverable now.

### ★ NEVER OVERWRITE A PROOF — give every revision a NEW filename (DJ 2026-09-12, "exactly what I wanted")
Google Drive keeps serving the **cached thumbnail** of an overwritten PNG. PDFs re-render their
preview straight away; PNGs do not. So after a copy revision DJ opened the proof, saw the OLD
headline, and reasonably concluded "the proof is wrong copy, the Zoo file is right" — when in fact
both were built from the same artboard in the same run and never disagreed. Only the *picture of the
proof* was stale.

**So: proofs get a revision number in the filename — `...-PROOF-r4.png` — never an overwrite.**
New file, new id, new preview, nothing to fight. It also leaves DJ a trail of revisions he can flip
back through, which he wants. Press PDFs can still overwrite (their previews refresh), but keeping a
revision on those too costs nothing.

The piece's archive folder is
`G:\My Drive\Window & Solar Care — Design\2026\<piece>` with `1 SOURCE`, `2 MASTER`,
`3 PRINT READY — what goes to Zoo`, `4 PROOFS — with guide lines`. Put things where they belong and
park superseded press files in a clearly-named subfolder rather than deleting them — a wrong-size PDF
sitting next to the right one is a real money risk.

**Never make DJ chase a file.** One link per piece, in the reply, every time — including re-sends.
Related: [[feedback_always_paste_preview_link]], [[feedback_drop_link_table]] (one link, not a menu).
