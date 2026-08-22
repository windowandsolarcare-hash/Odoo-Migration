---
name: feedback_field_readability_sunlight
description: "DJ has limited vision and works outdoors in bright sun — every field/owner UI must be large-text and high-contrast, with a genuinely sunlight-readable day mode. First-class requirement, not polish."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

DJ (2026-06-21): "the text of the old [Field Assistant] is hard to read. My eyes are not great and in the field with the sun it's even tougher."

**Why:** He uses the Field Assistant on a phone, outdoors, in direct sunlight, with less-than-great eyesight. Small/low-contrast text is unusable in those conditions. This is an accessibility + operational requirement, not a cosmetic preference.

**How to apply:**
- Default to **larger** font sizes for anything that matters in the field (customer name, address, gate code, totals, status). Avoid tiny 10–12px labels for real content.
- **High contrast** everywhere: don't use dim grays for important text. On dark, lighten the dim/muted tokens; on light/day mode, make text near-black and borders dark so they survive glare.
- The **day (light) mode must be truly sunlight-readable** — DJ specifically tests it outside. When in doubt, push contrast and size HARDER, then ask him to verify in the sun.
- Applies to the whole ERP redesign too, not just the Field Assistant. See [[project_report_hub_redesign]] design principles and [[reference_brand_logo]] (brand blue #0090d0).

Field Assistant cohesion Chunk 1 (2026-06-21) already raised --text-dim/--text-muted contrast and bumped key sizes (customer 18→21, gate 13→14.5, card-hdr 10→12, status/freq 12→13.5) — but treat readability as an ongoing dial to keep turning up based on his in-sun feedback.
