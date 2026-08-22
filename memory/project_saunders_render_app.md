---
name: Saunders Render App — Architecture & State
description: New multi-business Render app repo, login system, router structure, and deployment state as of 2026-04-19
type: project
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
# Saunders Render App

**Created:** 2026-04-19
**Status:** Scaffold live, login working, pointing at new repo

---

## GITHUB REPO
- **Repo:** `windowandsolarcare-hash/saunders-render-app` (private)
- **Local path:** `C:\Users\dj\Documents\Business\Saunders Render App\`
- **Branch:** `main`
- **Deploy:** Render auto-deploys on push to main

## RENDER SERVICE
- **Service name:** `wsc-field-assistant` (same service, repo changed)
- **URL:** `https://wsc-field-assistant.onrender.com`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port 8000`
- **Root directory:** blank (files at repo root)
- **Plan:** Starter ($7/month)

---

## FOLDER STRUCTURE

```
main.py                    ← entry point, mounts all routers
routers/
  auth.py                  ← login + role-based routing
  owner/
    dashboard.py           ← DJ's world (placeholder)
  tech/
    jobs.py                ← Danny's world (placeholder)
  cheryl/
    clients.py             ← Cheryl's world (placeholder)
shared/
  odoo.py                  ← Odoo RPC helper (shared by all routers)
  utils.py                 ← date/timezone helpers
static/
  login.html               ← login screen (name + PIN)
  owner/index.html
  tech/index.html
  cheryl/index.html
```

---

## LOGIN SYSTEM

- **Flow:** Name + PIN → POST /api/login → Odoo res.partner lookup → redirect by role
- **User storage:** `res.partner` in Odoo (no seats consumed)
- **Fields on res.partner:**
  - `x_render_pin` — 4-digit PIN (char, ID 19167)
  - `x_render_role` — owner / tech / cheryl (char, ID 19170)
  - `x_render_business` — wsc / cheryl / etc. (char, ID 19173)
- **Route map:** owner→/owner/, tech→/tech/, cheryl→/cheryl/

## DJ'S LOGIN RECORD
- Partner ID: 3 (Dan Saunders, original record)
- PIN: 8487
- Role: owner
- Business: wsc

---

## DEPLOY WORKFLOW (new repo)
Uses standard git push (not gh api like Odoo-Migration):
```bash
cd "C:\Users\dj\Documents\Business\Saunders Render App"
git add <file>
git commit -m "YYYY-MM-DD | filename | description"
git push origin main
```
Render auto-deploys on push. No manual trigger needed.

---

## KEY DECISIONS
- One Render service, one $7/month bill — no separate services per business
- res.partner for app users — no Odoo seats, no custom models
- Router-based separation — each business gets own router file(s)
- Old app.py (W&SC) still running on Odoo-Migration repo separately — migration to new repo is future work
- Fiduciary business (DJ's potential client) would get its own router + Odoo company, same pattern
