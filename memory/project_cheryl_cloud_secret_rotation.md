---
name: project_cheryl_cloud_secret_rotation
description: "CHERYL_CLOUD_SECRET (the x-cheryl-cloud-secret header auth for cloud-Cheryl) is now validated by a SHA-256 HASH stored in ir.config_parameter 'wsc.cheryl.cloud_secret_hash', constant-time; rotated server-side via POST /owner/api/cheryl_cloud_secret/rotate (owner-admin only). Plaintext lives ONLY in a Drive vault file."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-16T09:51:55.593Z
---

**Built 2026-09-16** (Cheryl-cloud security-reviewed + ruled; DJ-approved). Files: routers/owner/secret_sync.py, routers/cheryl/voicenote.py (_secret_ok), main.py registration.

## How cloud-Cheryl auth works now (CHANGED from plain env compare)
`routers/cheryl/voicenote.py _secret_ok` validates the `x-cheryl-cloud-secret` HEADER by:
1. `sha256(header)` compared **constant-time** (`hmac.compare_digest`) to the hash stored in
   `ir.config_parameter 'wsc.cheryl.cloud_secret_hash'` (authoritative once a rotation has happened).
2. MIGRATION fallback: if that hash is absent (pre-first-rotation), constant-time compare against
   `sha256(os.environ['CHERYL_CLOUD_SECRET'])`.
3. Fail-closed if neither is set. Header-only (never a query param).
The **plaintext value is never stored server-side** — only its hash. The live value lives ONLY in a
Google Drive vault file (the out-of-band channel the cloud operator reads).

## The rotate endpoint (POST /owner/api/cheryl_cloud_secret/rotate)
Owner-ADMIN only (`role=='owner'` AND `session_actor=='dan'`); deliberately NOT in any GRANTED_OWNER
allowlist. Zero input (destination file id is hard-coded from env `CHERYL_CLOUD_SECRET_VAULT_FILE_ID`).
Flow: mint `secrets.token_urlsafe(32)` → **write vault file FIRST** → **store sha256 hash SECOND** →
abort if vault write fails (old secret still validates = no lockout). Returns only {ok, rotated_at,
vault_file_id} — never the value. Every call audited to `ir.config_parameter 'wsc.secretsync.log'`
(who/when/file/result, no value). Vault write uses a **dedicated service-account** credential
(`GOOGLE_SERVICE_ACCOUNT_JSON`, scope `drive.file` ONLY) — separate from notes.py's full-drive OAuth.

## Gotchas / setup deps
- `GOOGLE_SERVICE_ACCOUNT_JSON` was in the Render env but UNUSED by any code before this; now it's LIVE
  (this endpoint). `drive.file` scope can only write files the SA CREATED — so the vault file must be
  SA-authored, and its id put in `CHERYL_CLOUD_SECRET_VAULT_FILE_ID` (until set, rotate 503s safely).
- **Open follow-up tickets (BUILD_LOG, Cheryl-flagged, don't quietly close):** (a) audit the full-scope
  Drive OAuth credential (`_drive_service`, notes.py) — it can read the whole Google account incl the
  Odoo + Stripe keys; (b) confirm/verify the SA's DOMAIN-WIDE DELEGATION is off/appropriate (if on +
  unneeded = a bigger key than the secret). Delegation status can't be read from code — Workspace admin console.

## How to apply
- Debugging cloud-Cheryl 403s: check the header, then whether `wsc.cheryl.cloud_secret_hash` is set
  (post-rotation) vs the env fallback (pre-rotation). It's a HASH now — you can't read the value back.
- Never echo/relay the secret value; the rotate returns only metadata. See [[feedback_never_relay_credential_via_session]], [[project_res_partner_no_mobile_field]] (adjacent secret-handling), [[project_feed_submit_item_contract]].
