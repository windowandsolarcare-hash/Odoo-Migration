---
name: feedback_script_insertion_anchor
description: "Never use rfind('</script>') to find insertion point — it finds the last tag, which may be an external script. Anchor to specific content instead."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a426dd8b-9b75-4779-8f66-583969d0c752
---

Never use `rfind('</script>')` to find where to insert JS into an HTML file.

**Why:** If the file has external scripts after the main inline script block (e.g. `<script src="ql_panel.js"></script>`), `rfind` finds the closing tag of the LAST external script — not the main inline script. Function ends up outside any executable script block. Happened 2026-06-03 with calendar.html — `goToField` was placed inside pwa-track.js's closing tag and never ran.

**How to apply:** Always anchor to specific content that's unique to the main script's end:
- Look for `init();\n</script>` or `loadField();\n</script>` or the last real function call
- Or use `rfind('</script>')` ONLY when you know there are no external scripts after the inline block — verify with `grep -n '</script>'` first
- Pattern: `old = '  init();\n</script>'` → `new = '  init();\n\n  function goToField(...) {...}\n</script>'`
