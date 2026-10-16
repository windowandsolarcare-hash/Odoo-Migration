---
name: feedback_binary_upload_sha_roundtrip_verify
description: "Hand-inlining a large (~tens-of-KB) base64 blob into an MCP/tool upload call (e.g. Drive create_file) can SILENTLY byte-substitute the binary → a PDF that opens but has some compressed streams failing their Flate adler checksum, so it renders fine on some pages and destroyed on others. Upload binaries from DISK (tool reads the file, binary-exact), and QC a binary deliverable by sha256 ROUND-TRIP + decode-EVERY-stream + RENDER the pages — never trust the text layer or a content snippet."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-16T15:14:05.263Z
---

During the Del Webb EDDM facing-slip QC (2026-10-16), Design's first upload of a 10-slip PDF to Google Drive was CORRUPT: the stored 9580-byte file opened and rendered slips 1-5,7-9 fine but slips 6 and 10 were DESTROYED (empty route box, no piece count, route number spilling huge/overlapping at the page bottom). Forensics on the exact stored bytes (my downloaded copy = stored size exactly, so NOT a retrieval artifact): decoding each page's content stream showed **2 of 5 compressed streams (pages 3 & 5) failed zlib with "incorrect data check" (adler checksum) — 0 bytes recovered**, while the other 3 decoded clean. A checksum failure = byte SUBSTITUTION after compression; a generator (ReportLab) never emits a bad adler, so it was NOT the generator and NOT my retrieval.

**Root cause (confirmed):** the ~33KB base64 of the PDF was being **hand-inlined into the Drive MCP `create_file` call**. A blob that large can't be reliably carried inline through the tool channel → silent byte-substitution in transit. Fix: a **disk-based upload** (the publish/upload tool reads the PDF straight off disk, binary-exact — here an Artifact `files` publish) made the bytes lossless. Belt-and-suspenders: regenerate the PDF **uncompressed** (`pageCompression=0`) so there is no Flate stream and thus no adler to fail — a stray byte-flip can then at worst nick one visible glyph instead of nuking a whole page.

**The verify gate that proved it clean (airtight):**
1. **sha256 ROUND-TRIP** — hash the local file you upload, download it back from the published/stored location, hash THAT; the two must be IDENTICAL. A match = the transport is lossless end-to-end. (Here local == downloaded == my independent fetch = 890e3921…88.)
2. **Decode EVERY stream / parse every page** — not just "it opens." A corrupt stream opens fine and fails only on decode.
3. **RENDER the pages** (especially the ones carrying UNIQUE data — here slip 10 = the short final bundle, PIECES 10 not 100) and LOOK. Text extraction alone missed it: two parsers (MuPDF vs Google Drive's snippet) recovered DIFFERENT subsets of the corruption, and the Drive content-snippet is lossy — only rendering the actual pages showed the real breakage.

**How to apply:**
- Never hand-inline a large base64 blob into an upload tool call. Upload from disk so the tool reads the bytes binary-exact. If only an inline path exists, prove it with the sha round-trip before trusting it.
- QC a binary deliverable (PDF/image/zip) by: sha round-trip (integrity) + full parse/decode (structure) + render-and-look at the data-bearing pages (content). "It opens" and "the text extracts" are NOT a pass.
- A size-exact copy with some compressed streams failing adler = post-generation transport byte-substitution; a copy that won't open at all = usually total transport failure; garbage INSIDE a cleanly-decompressing stream = generation-time. The failure MODE tells you the layer — check it before blaming the generator.

Sharpens [[feedback_verify_collection_and_live_pipe]] and [[feedback_odoo_verify_content_not_status]] (verify by CONTENT, fire the real artifact) into the binary-asset case; sibling to [[feedback_push_compare_and_swap]] / [[feedback_github_deploy_python_fallback]] (binary-safety on the GitHub path) and [[feedback_audit_stamp_confirm_firsthand]] (I re-QC'd firsthand, didn't rubber-stamp Design's gate).
