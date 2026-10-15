---
name: feedback_field_whitelist_strip_silent_inert
description: "When a feature adds a NEW field that must travel accessor → serving-endpoint → render, a field-WHITELISTING intermediate layer silently DROPS the new field — so the feature ships INERT while LOOKING done, and an accessor-level unit test is structurally blind to it. QC/tests must trace the FULL pipe, not stop at the accessor."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-15T15:20:13.144Z
---

During the §15 stranded-transcript fix (2026-10-15), the plan's Lane A accessor (`get_all_calls` in sms.py) emitted a new `no_recording` flag, and Lane B's render branch read it. The plan's offline unit tests asserted on `get_all_calls` directly and all PASSED. But Audit's fresh-eyes pass caught **F1**: the serving endpoint in between — `_all_calls` (hiring_compare.py:334-340) — rebuilds each item through a **4-field whitelist (`id, when, audio_url, transcript`)** that DROPPED `no_recording` in transit. So `cl.no_recording` was always `undefined` on the page, the render branch NEVER fired, and EVERY stranded card (100%, incl. the Norberto case that prompted the fix) would still show "Recording still processing…" forever.

**Why it's a trap (nearly shipped):** the feature *looked* done because the transcript TEXT still surfaced (its disclosure is keyed on `cl.transcript`, which DID survive the whitelist) — only the audio-slot label was wrong. Neither the syntax gate NOR the accessor unit test caught it, because the unit test asserts one layer UPSTREAM of the strip. A green deploy + passing tests + visible transcript = "done" by every cheap signal, while the actual new behavior was inert.

**The principle:** whenever a feature adds a NEW field that must travel through more than one layer (accessor → serving endpoint → client render), any intermediate layer that **re-maps / whitelists / re-serializes** fields (a `dict` rebuild, a Pydantic/response model, a `SELECT`-column list, a `.map` projection) is a silent-strip point. A test that stops at the accessor cannot see a strip downstream of it.

**How to apply:**
1. **Trace the FULL pipe for any new field.** Byte-QC and tests must cross accessor → serving-endpoint → render, not stop at the producer. Add a test that asserts the field survives THROUGH the serving endpoint (here: test (g) asserts `get_all_calls → _all_calls` preserves `no_recording`), and the QC gate traces the full seam live.
2. **Grep every re-map layer between producer and consumer** for an explicit field whitelist; confirm the new field is added to each. A field-whitelisting endpoint is the specific at-risk shape.
3. **"Visible partial output" is a false all-clear** — if the feature shares a payload with data that DOES survive (transcript text here), the surviving part makes it look done. Verify the SPECIFIC new behavior, not just that the screen populated.

Sharpens [[feedback_verify_collection_and_live_pipe]] (green deploy ≠ works; fire the real live request) with the intermediate-whitelist-strip case. Ties [[feedback_audit_stamp_confirm_firsthand]] (§15 fresh-eyes caught exactly this), [[feedback_reuse_canonical_endpoint]], and the route-shadow / multi-layer discipline. Caught by Audit, confirmed firsthand by Lead on the bytes.
