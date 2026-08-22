---
name: reference-render-drive-service-account
description: Google service account credentials for Render app Drive access — where the JSON key lives and how to restore if lost
metadata: 
  node_type: memory
  type: reference
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

# render-drive Service Account

**Purpose:** Allows the Render app (`wsc-field-assistant`) to read/write Google Drive (Saunders Vault) for the Notes app.

**Service account email:** `[SERVICE_ACCOUNT_EMAIL — in Render env]`

**Google Cloud project:** `gen-lang-client-0790905441` (project name: "Odoo")

**Key file (local backup):** `C:\Users\dj\Documents\Business\render-drive-service-account.json`

**Render env var name:** `GOOGLE_SERVICE_ACCOUNT_JSON`

**Drive folder shared:** Saunders Vault root (`1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q`) — Editor access granted to service account email above.

## OAuth credentials (current approach — service account had no quota on personal Drive)

Render env vars (set 2026-05-28):
- `GOOGLE_OAUTH_CLIENT_ID` = `[GOOGLE_OAUTH_CLIENT_ID — in Render env]`
- `GOOGLE_OAUTH_CLIENT_SECRET` = `[GOOGLE_OAUTH_CLIENT_SECRET — in Render env]`
- `GOOGLE_OAUTH_REFRESH_TOKEN` = `[GOOGLE_OAUTH_REFRESH_TOKEN — in Render env]`

OAuth client name: "Drive Folder Script" (Desktop type) in Google Cloud Odoo project.
To regenerate token: run `C:\Users\dj\get_drive_token.py`

## To restore if env var is lost

1. Read the file: `C:\Users\dj\Documents\Business\render-drive-service-account.json`
2. Use Render MCP `update_environment_variables` on service `srv-d78le0fkijhs738dsli0` with key `GOOGLE_SERVICE_ACCOUNT_JSON` and the file contents as the value (compact JSON, `\n` in private key must remain as `\\n` escape sequences)
3. Use `replace: false` to avoid wiping other env vars

## To create a new key (if this one is revoked)

Google Cloud Console → Odoo project → IAM & Admin → Service Accounts → render-drive → Keys → Add Key → JSON
