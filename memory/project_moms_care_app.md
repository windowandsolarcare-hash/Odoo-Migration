---
name: project_moms_care_app
description: Mom's Care — DJ's walled-off PHI-grade eldercare app (own private repo + Render web + own Postgres + own auth, Odoo OUT). Built overnight 2026-09-21 by Builder-2, Lead orchestrating, Cheryl security-reviewing. Infra facts + conventions + gates.
metadata:
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-21T06:25:47.980Z
---

**A separate PHI-grade family eldercare app (4 caregivers + Mom), fully WALLED OFF from W&SC** — own repo, own Render service, own Postgres, own session secret + Fernet key, **Odoo/Google/Drive/OAuth entirely OUT**. Same GitHub/Render account is fine (Cheryl's rule: the wall is around DATA+CREDENTIALS, not the account). Spec: `C:\Users\dj\MomsCare\MOMS_CARE_SPEC.md`; board `MOMS_CARE_BOARD.md` (M4/M5); Cheryl's review `MomsCare/DESIGN_REVIEW.md` (cheryl-workspace `MOMS-CARE-DESIGN-REVIEW.md` @5f152dff).

## Infra (provisioned 2026-09-21, DJ-authorized, cost pre-cleared)
- **Repo:** `windowandsolarcare-hash/momscare-app` (PRIVATE). Local build dir `C:\Users\dj\MomsCare\app\` (git repo; push via `git push` — NEW repo, no branch protection, unlike W&SC's gh-api-only rule). ⚠ the fleet OAuth token lacks `workflow` scope → CANNOT push `.github/workflows/` (gitleaks CI is staged at `security/gitleaks-workflow.yml` as a template DJ enables).
- **Render web:** `momscare` = `srv-daocjjbm8hqs73e5hu0g` → https://momscare-m0hp.onrender.com (Oregon, starter, autoDeploy from main). Runtime python, `uvicorn main:app`.
- **Render Postgres:** `momscare-db` = `dpg-daocj0btqb8s73eq8kt0-a` (Oregon, basic_256mb, PG18) — ★ SEPARATE from W&SC DB; **ipAllowList EMPTY = internal-only** (external SQL BLOCKED, SSL-required). So verify its data via the APP's own endpoints, NOT the render PG-query MCP (which can't reach it — that's the wall working).
- **Env (Render, secret-clean — never printed/committed; local copy `C:\Users\dj\mc_secrets_momscare.txt`):** MC_DATABASE_URL (own DB), MC_SESSION_SECRET (own, never wsc_session), MC_FIELD_KEY (Fernet, PHI field enc), MC_SETUP_TOKEN (gates the one-time seed). Set via Render API with shell-resolved values.

## Stack + conventions (FastAPI, flat repo root, absolute imports)
- `db.py` single-conn+lock + `ensure_schema()` (idempotent, all tables day-one); tables `mc_users/mc_grants/mc_sessions/mc_audit/mc_meds/mc_med_history/mc_symptom_logs/mc_adherence/mc_requests/mc_messages/mc_emergency/mc_consent/mc_documents/mc_login_throttle`. Boots DORMANT if MC_DATABASE_URL unset.
- `crypto.py` Fernet field-enc on `*_enc` PHI cols (fail-closed if MC_FIELD_KEY unset).
- `auth.py` — OWN session secret; PBKDF2 **600k**; server-side sessions (revoke=instant offboard); ★ least-privilege BY DATA CLASS deny-by-default: `allowed(user, data_class, write)` → no grant row = DENY (owner short-circuits full). Data classes: symptoms/adherence/meds/documents/coordination/admin. Login throttle/lockout (5 fails→exp backoff). `reauth()` step-up. `audit()`.
- `main.py` — `require_class(data_class, write)` dep (deny+audit); /api/login (pw or Mom PIN), /logout, /me; **/api/admin/export + /delete_all need STEP-UP re-auth** (password) + owner; /api/setup/seed (MC_SETUP_TOKEN, idempotent-fresh-only); **/api/mom/today** (role=mom-only server-assembled minimal view — Mom has NO meds grant). Screen routers `from routers import ...`.
- `seed.py` — 100% FICTIONAL (persona **Anita Saunders**; NEVER the real person's name/data — Lead: the name isn't a discrepancy, it's PHI-safety; real data waits for DJ's demo→real flip, encrypted, never committed). Mom grants MINIMAL (symptoms:w, adherence:w, coordination:rw). Owner=dj/demo-owner-pw; caregivers karen/mike/susan; mom=anita/PIN 1955.

## Status + gates (2026-09-21)
- ✅ Repo + security SPINE (Lead HARD-QC pass + all 6 Cheryl-rubric fixes: 600k PBKDF2, throttle/lockout, export/delete re-auth, doc-storage-design signed-URL/metadata-only, crypto threat-model, gitleaks template) + provisioned + isolation VERIFIED + fictional seed + spine proven end-to-end (Mom-confinement 403 by-URL, re-auth 401-without-pw, med-history append, Fernet round-trip, creds-excluded-from-export).
- 🟡 IN PROGRESS: screen routers (meds w/ edit-append, symptoms, adherence, emergency, requests, channel, ask, overview) + port demo HTML data-free (all via authed API). Demo artifact ref: claude.ai/artifact/B6ZG2WoAAuCHrkdm1j4tGD.
- ⏸ WAITS FOR DJ (gated, do NOT do overnight): 4 real family logins; demo→real-data flip (gated on Cheryl's security BLESS); the Care Assistant (Phase 2, hard-gated — licensed interaction DB + zero PHI retention + non-overridable 911 guardrail; OFF now).
- Build gotcha: `psycopg[binary]==3.2.3` NOT on this Render Python's wheel index (only 3.2.10+) → use `psycopg[binary]==3.2.13`.

Related: [[feedback_never_relay_credential_via_session]], [[feedback_gh_push_empty_file_guard]], [[feedback_durable_foundation_over_shortcut]].
