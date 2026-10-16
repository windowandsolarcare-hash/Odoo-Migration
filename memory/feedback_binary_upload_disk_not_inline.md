---
name: feedback_binary_upload_disk_not_inline
description: "Never hand-inline a large base64/binary blob into an upload tool (Drive create_file, etc.) — it silently corrupts bytes. Upload from disk (Artifact files/asset) and verify with a sha256 round-trip."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9e757d4b-c2ad-4e84-9c81-2f3aa11f1c2e
  modified: 2026-10-16T15:10:42.388Z
---

**Discovered 2026-10-16 building the Del Webb EDDM facing-slip PDF.** A ~10KB PDF uploaded to Google Drive via the Drive MCP `create_file` (base64Content inlined) came back with 2 of 5 page content streams corrupted — byte SUBSTITUTION with length preserved (deflate adler-checksum failures, two parsers choking). Root cause: a large base64 blob passed as a literal tool argument is reproduced token-by-token by the model and is NOT reliable — characters flip (I separately introduced a stray Cyrillic char hand-copying a 12KB blob the same session), and a 33KB blob can't even fully load into context to copy. Compressed PDFs make it catastrophic (a flipped byte kills the whole page via the Flate checksum).

**Why:** the corruption looked Drive-side/generator-side and burned multiple rounds of forensics; it was actually the inline transfer. Lead's render-based QC caught it (text-layer extraction alone would have missed slip-6/10 being destroyed) — see [[feedback_render_design_before_presenting]].

**How to apply:**
- **Upload binary from DISK, never inline.** The **Artifact tool `files` map** (`{"name.pdf":"<disk path>"}`) and `asset: true` uploads read the file straight off disk = binary-exact. This also gives DJ a stable claude.ai link that opens on his phone (good Drive alternative for PDFs; matches the "same stable link" Design principle).
- **Always verify with a sha256 round-trip:** sha the local file, download it back from where it landed, sha that, and RENDER + decode-check every page. sha match + clean render = airtight. sha differ = the transfer mangled it.
- **If you must use an inline-only uploader,** make the payload small AND uncompressed (reportlab `pageCompression=0`) so a flip is a nicked glyph, not a dead page — then still sha-verify and retry until it matches.
- Facing-slip generator + page live in this session's scratchpad (`facing_rl.py` uncompressed, `facing_page.html`). Artifact: https://claude.ai/artifact/DMQzXQ7pRZym4y7jPr4BMP
