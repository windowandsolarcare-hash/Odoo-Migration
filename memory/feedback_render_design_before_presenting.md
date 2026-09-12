---
name: feedback_render_design_before_presenting
description: Never present a design built by math alone — render it to a PNG with headless Chrome, LOOK at it, and hand DJ the image (not just a canvas link).
metadata:
  type: feedback
---

**DJ, 2026-09-11/12:** never hand him a design positioned by calculation alone. RENDER it, LOOK at it,
fix what you see, then present. Now a standing rule in `DESIGN_CHARTER.md`.

**Why:** on the 6×9 postcard BACK I sized the copy column by adding up font sizes and margins, and the
phone/URL block overflowed onto the logo. DJ caught it instantly — *"you would think that you would be
able to see that. And don't do that."* Arithmetic is not verification; eyes on the rendered output are.
Text height is the specific trap: a body paragraph I estimated at 3 lines wrapped to 5.

**How to apply:**
1. Strip the `.dc.html` to a standalone page (content between `<x-dc>`/`</x-dc>`, `<helmet>` contents
   hoisted into `<head>`). A `.dc.html` won't open alone — its `support.js` is injected by the editor.
2. `python -m http.server 8731` in that folder. The browser tooling refuses `file://`, and relative
   image `src`s must resolve.
3. `chrome.exe --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1
   --window-size=<W>,<H> --screenshot="<abs>\out.png" http://127.0.0.1:8731/_preview.html`
   `--window-size` IS the PNG size, so pass the artboard's exact px — 2775×1875 comes back 2775×1875,
   i.e. true 300 DPI press size. Chrome is at `/c/Program Files/Google/Chrome/Application/chrome.exe`.
4. Read the PNG as an image AND measure collision-prone elements with `getBoundingClientRect()` in the
   served page. Numbers catch a 10px overlap the eye misses; the eye catches a washed-out photo or a
   dead gap that numbers call fine.
5. **Send DJ the PNG file** via SendUserFile. Publishing the canvas artifact needs his approval each
   time and he has repeatedly not gotten it — an image file always reaches him. See
   [[project_design_canvas_png_export_is_1to1]].

**Related trap, same session:** my roster heartbeat had the session ref HARDCODED, so it stamped a dead
ref for days while looking healthy. Any "re-stamp your whole row" heartbeat must read the ref from
`ListAgents` on every tick — a constant in the script defeats the entire point of the self-heal.
