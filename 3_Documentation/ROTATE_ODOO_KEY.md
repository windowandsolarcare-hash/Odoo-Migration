# Rotate the Odoo API Key — Checklist

**Why:** the live Odoo API key (uid 2) was sitting in plaintext in `CLAUDE.md` + context docs, committed to the GitHub repo. Rotating kills the exposed copy for good. The key reads/writes every customer, invoice, and payment across all 3 companies — treat it as the crown jewel.

**Golden rule:** create new → deploy everywhere → verify → revoke old **LAST**. Never revoke first (instantly breaks the live app).

---

## DJ does (Odoo UI — needs your login):

**1. Generate the new key**
1. window-solar-care.odoo.com → log in as yourself.
2. Avatar (top-right) → **My Profile** / Preferences.
3. **Account Security** tab → **Developer API Keys** → **New API Key**.
4. Confirm password (+ 2FA if on).
5. Name it `render-app-2026-08`, pick duration.
6. **Copy the key — Odoo shows it ONCE.**
7. Leave the OLD key alive for now.

**2. Hand it to Lead safely**
- Paste it into `C:\Users\dj\new_odoo_key.txt` (NOT into chat).
- Tell Lead "it's in the file."

## Lead does (code + deploy — DJ does nothing):
- [ ] Read new key from file.
- [ ] Update Render env var `ODOO_API_KEY` (fetch ALL vars, merge, PUT full set, never partial).
- [ ] Fix hardcodes: `main.py:77`, `routers/printing/watcher.py:27` -> read env, not literal.
- [ ] Update 4 Zapier scripts: `zapier_phase3/4/5/6_FLATTENED_FINAL.py` (legacy/dormant, but scrub anyway).
- [ ] Redact `CLAUDE.md` (lines 47-49), `CLAUDE_CONTEXT.md`, `MASTER_PROJECT_CONTEXT.md` -> point at env var by name.
- [ ] Also dead Workiz token/secret on CLAUDE.md lines 48-49 = delete (Workiz retired).
- [ ] Trigger Render redeploy (field-assistant srv-d78le0fkijhs738dsli0).

## Lead verifies:
- [ ] Hit a read endpoint; confirm a customer loads, scheduling works. Report green.

## DJ does LAST (Odoo UI):
**3. Revoke the old key**
- Odoo -> Account Security -> Developer API Keys -> delete the OLD key.
- Now the copy in git history authenticates nothing. Done.

---
**Consumer count for reference:** ~50 one-off local scripts also hardcode the old key — pure cleanup, none run unattended, update opportunistically. The only LIVE consumer is the Render app (env var + the 2 hardcodes).
