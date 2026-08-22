---
name: project_email_to_myday_task
description: Forward an email to windowandsolarcare+task@gmail.com → it becomes a My Day task. Built+deployed 2026-07-05; BLOCKED on GMAIL_WSC_APP_PASSWORD env var not set on Render.
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e8d15b5-9a20-4187-90d6-6f63266f2498
---

**Feature (DJ asked 2026-07-05):** forward any Gmail email to **`windowandsolarcare+task@gmail.com`** → app polls it and creates a My Day `project.task` reminder (subject→title with Fwd:/Re: stripped, body→note, best-effort customer match by an email address parsed from the forwarded body, due = today 9am PT).

**Built + deployed (saunders-render-app):**
- `routers/owner/myday.py`: `_pull_email_tasks()` + `GET /api/myday/pull_email_tasks`. IMAP `imap.gmail.com` login `windowandsolarcare@gmail.com` / **`os.environ['GMAIL_WSC_APP_PASSWORD']`** (mirrors the printing watchers, which use `GMAIL_SCENIC_APP_PASSWORD`/dan@scenicartprint.com). Search: X-GM-RAW `deliveredto:` then **fallback to `(TO "…+task@…")`** — ★ the TO fallback is the RELIABLE path (deliveredto: returned EMPTY for a self-sent/forwarded test; TO matched). Dedup by RFC822 Message-ID in ir.config_parameter `myday.email_task.processed_msgids` (capped 500). Process-local 45s throttle so page loads don't hammer Gmail. Marks msgs \Seen.
- `static/owner/myday.html`: `pullEmailTasks()` fires on My Day load (non-blocking); toasts + reloads if `created>0`.

**★ BLOCKER (the only thing left):** the live endpoint returns `{"ok":false,"error":"GMAIL_WSC_APP_PASSWORD not set"}` — the env var is NOT set on Render svc `srv-d78le0fkijhs738dsli0` (memory said it was set in May for the HOF watcher, but that watcher moved to scenic and this var is now absent/wiped). NEEDS DJ: generate a Google **App Password** for windowandsolarcare@gmail.com (needs 2FA on: Google Acct → Security → App passwords) and add **`GMAIL_WSC_APP_PASSWORD`** in the Render dashboard → wsc-field-assistant → Environment (dashboard is safest — raw-API PUT env wipes all vars unless you GET+merge first). Can't set it from here: Render MCP disconnected + reading the Render API key from ~/.claude/mcp.json is blocked by the auto-mode credential classifier.

**SIBLING — email → VAULT DOCUMENT (built+deployed 2026-07-05):** forward to **`windowandsolarcare+vault@gmail.com`** → attachments saved to a Vault folder **"📧 Email Documents"** (body → a Doc if no attachment). In `routers/owner/vault.py`: `_pull_email_docs()` + `GET /api/vault/pull_email_docs` (same IMAP `(TO "…+vault@…")` search + Message-ID dedup param `vault.email_doc.processed_msgids` + 45s throttle). Reuses notes.py Drive helpers: `_drive_service`, `_find_or_create_folder`, `_make_doc`, `_verbatim_html`, `odoo_rpc` (★ `odoo_rpc` is defined in **notes.py L101**, NOT shared.py — import it from `.notes`). `_upload_file()` uploads attachments (resumable >5MB). `static/owner/vault.html` calls `pullEmailDocs()` on load (toast + reload). SAME blocker: `GMAIL_WSC_APP_PASSWORD` (one password powers BOTH +task and +vault). Also needs the Vault Google OAuth token alive (GOOGLE_OAUTH_REFRESH_TOKEN, dies ~weekly). Test email "ZZVAULT test doc 7Q2" queued to +vault.

**TEST VECTOR waiting:** a real test email is sitting UNREAD in the inbox — subject "Fwd: ZZTEST call Jane about quote 9F3K", to the +task addr (sent via Odoo mail.mail 2026-07-05). Gmail connector is READ-ONLY (can't trash it / can't get its Message-ID to pre-seed). WHEN the password is set: run `GET /owner/api/myday/pull_email_tasks`, confirm it creates the "ZZTEST call Jane about quote 9F3K" task (end-to-end proof), then DELETE that test task. See [[project_myday_action_catalog]] [[project_myday_reminders]] [[feedback_api_keys_via_file]].
