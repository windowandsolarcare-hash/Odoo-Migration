---
name: project_workiz_get_needs_user_agent
description: "Workiz API GET returns HTTP 403 Forbidden from a bare urllib call — it needs a User-Agent header. Not an auth/token problem. Add User-Agent: Mozilla/5.0."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

# Workiz GET → 403 Forbidden = missing User-Agent, NOT a bad token (found 2026-07-15)

`urllib.request.urlopen(f'https://api.workiz.com/api/v1/{TOKEN}/job/get/{UUID}/')` with **no headers** returns **HTTP 403 Forbidden** on every job. The token is fine. Python's default `User-Agent: Python-urllib/3.x` is what Workiz rejects.

**Fix — always send a browser UA:**
```python
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
with urllib.request.urlopen(req, timeout=30) as r:
    raw = json.loads(r.read().decode())
```

**Why it matters:** 403 looks exactly like a revoked/expired token or an IP block, so the instinct is to go hunting for a credentials problem that doesn't exist. It cost a detour on 2026-07-15 (nearly concluded the Workiz subscription had lapsed). `requests.get()` sends its own UA (`python-requests/x`) and has worked from Odoo server actions historically, so this bites **urllib** callers specifically — local scripts and anything else not using `requests`.

**How to apply:** any local Python script that calls Workiz directly, set the UA header. Distinguish the response codes: **403 = missing UA**, 429 = rate limit (~30 calls, sleep 15-30s), **204/404 = job deleted in Workiz**. See [[CLAUDE.md]] WORKIZ API ACCESS section.
