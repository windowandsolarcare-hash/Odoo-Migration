---
name: project_realesrgan_upscaler
description: "Local AI upscaler (Real-ESRGAN, portable ncnn-vulkan) for the print pipeline — path, invocation, and the 4x-then-downscale pattern. Better than Lanczos for hero photos."
metadata:
  node_type: memory
  type: project
  originSessionId: edbb1e65-a23a-493e-83d1-f6b164f0621e
  modified: 2026-09-30T23:29:29.373Z
---

Lead installed a working local AI upscaler on DJ's Surface (2026-09-30), because `pip install realesrgan`
fails here (basicsr wheel build fails; `torchvision` not installed — only `torch`).

- **Binary:** `C:\Users\dj\tools\realesrgan\realesrgan-ncnn-vulkan.exe` (portable, runs on the Intel GPU
  via Vulkan; the `models\` folder sits next to the exe).
- **Invoke:** `realesrgan-ncnn-vulkan.exe -i in.png -o out.png -n realesrgan-x4plus -s 4`
  (add `-t 200` if a large photo runs out of memory). ~11s for a small image; a ~1400px hero → 4x in
  well under a minute.
- **Output is ALWAYS 4x.** For our ~2x need: upscale to 4x, then Lanczos-downscale to the exact press
  size (2775×2025). e.g. `Image.open('out.png').resize((2775,2025), Image.LANCZOS)`.
- **Only upscale the PHOTO, never the composite/type/logo** (real type is rendered native at press
  size on the canvas). Pattern: clean photo → Real-ESRGAN 4x → Lanczos down → composite type → CMYK PDF.
- **Verified better than Lanczos** on the Fall-Refresh hero (2026-09-30): stone/wood-grain/window-frame
  detail noticeably crisper. Use this for final press files; Lanczos is an acceptable fallback at ~2x.

**Why:** DJ wants the source photo AI-upscaled to hit true 300 DPI at full-bleed without softness.
**How to apply:** fold this call into the print build for any hero that starts below the artboard's
pixel width. See [[project_wsc_print_build_pipeline]] and the Fall-Refresh piece `design/fall-refresh-eddm/`.
