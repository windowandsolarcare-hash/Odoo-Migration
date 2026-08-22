---
name: Cheryl Project Split Into Its Own Repo
description: 2026-04-20 Cheryl real estate code moved from W&SC Migration repo into its own local folder + GitHub repo + SHARED_MEMORY
type: project
originSessionId: 200f31b4-0c58-455f-b0db-ae50a45f5d8f
---
# Cheryl Project Split — 2026-04-20

Cheryl's real estate project was broken off from the W&SC Migration codebase into its own fully independent repo.

**Why:** Keep W&SC migration code clean. Cheryl is a separate business with no Workiz/Zapier — mixing them created confusion. Also prepares for per-business Render voice boxes (DJ → W&SC memory, Cheryl → her own memory).

**How to apply:**
- **Local:** `C:\Users\dj\Documents\Business\A Cheryl Real Estate\` (parallel to W&SC). Has its own CLAUDE.md, SHARED_MEMORY.md, PLAN.md, and folder skeleton (1_Production_Code, 2_Testing_Tools, 3_Documentation, 4_Reference_Data).
- **GitHub:** `windowandsolarcare-hash/cheryl-real-estate` (private, DJ is owner). Same `gh api` deployment pattern as W&SC.
- **Render:** no new service — Cheryl's voice box will live at `/cheryl/` route inside existing `saunders-render-app`. Role→repo mapping for SHARED_MEMORY sync to be added when the voice box is built (role `cheryl` → `cheryl-real-estate` repo, roles `owner`/`tech` → `Odoo-Migration` repo).
- **W&SC SHARED_MEMORY.md:** Cheryl section replaced with a 4-line pointer. Don't duplicate Cheryl content back into W&SC.
- **When working on Cheryl's project:** `cd` into `A Cheryl Real Estate` folder first — her CLAUDE.md and SHARED_MEMORY.md load there, not W&SC's.

**Deployment gotcha discovered:** The PowerShell-based `gh api` deploy script in W&SC's CLAUDE.md has an escaping issue when fetching the SHA of files in subfolders (404s even though file exists). Workaround: use Python subprocess to call `gh api` directly — works reliably. Pattern:
```python
sha = subprocess.check_output(['gh','api',f'repos/{repo}/contents/{path}?ref=main','--jq','.sha'], text=True).strip()
subprocess.run(['gh','api',f'repos/{repo}/contents/{path}','--method','PUT','--input','-'], input=json.dumps(payload), text=True)
```
