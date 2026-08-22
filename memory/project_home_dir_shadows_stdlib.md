---
name: project_home_dir_shadows_stdlib
description: "Running python from C:\\Users\\dj shadows stdlib: a dev file C:\\Users\\dj\\calendar.py (a FastAPI router) hijacks `import calendar`, breaking `requests` import chain with ModuleNotFoundError: No module named 'fastapi'. Run scripts from a neutral dir (e.g. the scratchpad)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

# Don't run python from C:\Users\dj — home dir has files that shadow the stdlib (2026-07-16)

`cd /c/Users/dj && python ...` puts the home dir on `sys.path[0]`. There's a **`C:\Users\dj\calendar.py`** (a FastAPI router copy) that shadows Python's stdlib `calendar` module. `import requests` → ... → `http.cookiejar` → `from calendar import timegm` picks up the wrong `calendar.py` → crashes with a misleading `ModuleNotFoundError: No module named 'fastapi'`.

**Fix:** run any `python - <<EOF` / script from a directory that has no colliding filenames — e.g. `cd "<scratchpad>" && python ...`. The scratchpad dir is safe. (Also `safe_deploy.py` etc. live at C:\Users\dj — but the shadowing bites when cwd=home AND the script imports something whose chain hits `calendar`/other shadowed names.)

**How to apply:** for local Odoo JSON-RPC / requests scripts, don't `cd /c/Users/dj` first. cd to the scratchpad (or any neutral dir) and run there. Watch for other shadowers too (any `C:\Users\dj\<stdlibname>.py`).
