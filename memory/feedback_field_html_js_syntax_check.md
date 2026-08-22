---
name: feedback_field_html_js_syntax_check
description: "ALWAYS run node --check on field.html JS before pushing — JS syntax errors kill window.load, leaving the unlock screen stuck (happened 3 times)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 981a3f4c-8c27-4362-b6cf-6f55a7e281ca
---

**Rule: Run `node --check` on extracted JS before every field.html push.**

**Why:** A JS syntax error in field.html's inline script kills `window.load`, which means `boot()` never fires, the unlock screen never hides, and the user is stuck. This has happened 3 times:
1. Backslash-escaped quotes (`\'`) from a bad Python patch inside `checkAccess()`
2. Unquoted Unicode chars (`✕`, `⚠`) in `_autoUploadPhoto` — JS treated them as undefined variable names
3. Double `async async function` — my patch inserted `async function foo` before a line that already began with `async`, creating `async async function`

**How to apply:** After every edit to field.html, before pushing, run:
```bash
gh api repos/windowandsolarcare-hash/saunders-render-app/contents/static/owner/field.html --jq '.content' | base64 -d | python3 -c "
import sys
content = sys.stdin.read()
start = content.find('<script>\nlet AC')
end = content.find('</script>', start)
js = content[start+8:end]
with open('C:/Users/dj/field_test.js', 'w', encoding='utf-8') as f:
    f.write(js)
" && node --check C:/Users/dj/field_test.js && echo "SYNTAX OK"
```
Or run it on the local patched file before pushing. Do NOT push if `node --check` fails.

**Additional rules:**
- Never embed bare Unicode emoji/symbols in JS — always wrap in quotes: `'✕'` not `✕`
- When inserting a new `async function` via string replace of `function foo()`, check if the target line already starts with `async` — you'll get `async async function`
- Python `chr(N)` in patch strings produces the raw character, which lands unquoted in JS
