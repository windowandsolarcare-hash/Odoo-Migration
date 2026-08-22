---
name: feedback_python_patch_escaping
description: "When patching Python source files: use chr(92)+'n' to write \\n escape sequences — never use '\\n' in replacement strings or you embed actual newlines"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

Never use `'\\n'` in a string that gets written into Python source code via a patch script. Python evaluates `'\\n'` as backslash+n at the script level, BUT when that string is used as a replacement and written to a file, the result depends on context and can embed actual newline characters → `SyntaxError: unterminated string literal`.

**Why:** During 2026-05-23 source stamp patching, `'\\n\\n📍 Source...'` was used in a `.replace()` call, which wrote actual newlines into the target file's string literal, breaking the syntax.

**How to apply:** When writing Python escape sequences into a source file:
```python
bs = chr(92)          # backslash character
correct_line = f"some code + '{bs}n{bs}n📍 stamp'"
```
This writes `\n\n` (literal backslash+n) to the file, which Python correctly parses as newline escapes.

**Diagnostic:** `repr()` of a correctly patched line shows `\\n` (double-backslash in repr = one backslash in file); a broken line shows `\n` (single = actual embedded newline).

**Quick syntax check after any Python file patch:**
```bash
python3 -m py_compile path/to/file.py && echo "SYNTAX OK"
```
Always run this before deploying.
