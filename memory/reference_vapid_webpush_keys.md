---
name: reference_vapid_webpush_keys
description: "VAPID / pywebpush key handling for web push — from_pem works, from_string fails on PEM; pass a Vapid01 instance to webpush(). Render env vars + MCP merge semantics."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**Web push for the Render app (My Day notifications, [[project_myday_reminders]]).** Library: `pywebpush==2.3.0` (deps py-vapid 1.9.4, http-ece, cryptography). Render Python pinned 3.12.8 — build OK.

**Env vars (on srv-d78le0fkijhs738dsli0):**
- `VAPID_PUBLIC_KEY` — base64url of the uncompressed P-256 public point (87 chars). This is the browser `applicationServerKey` for `pushManager.subscribe`. Served by `GET /owner/api/myday/vapid`.
- `VAPID_PRIVATE_KEY_B64` — **base64 (standard) of the PKCS8 PEM** of the private key. Single-line, env-safe. Decode → PEM bytes at runtime.
- claims `sub` is hardcoded `mailto:windowandsolarcare@gmail.com` in myday.py (`VAPID_SUB`), not an env var.

**THE GOTCHA (cost real debugging 2026-06-16):**
- `Vapid01.from_pem(pem_bytes)` ✅ — correctly loads the PEM and derives a public key matching `VAPID_PUBLIC_KEY`.
- `Vapid01.from_string(pem_str)` ❌ — `from_string` routes to `from_der` (base64url-decodes + `load_der_private_key`) → ASN.1 "invalid length". It does NOT handle PEM.
- pywebpush `webpush(vapid_private_key=<str>)` calls `Vapid.from_string` for non-file strings → so passing a PEM string FAILS.
- **FIX:** build the signer once `Vapid01.from_pem(base64.b64decode(os.environ['VAPID_PRIVATE_KEY_B64']))` and pass the **Vapid01 instance** to `webpush(..., vapid_private_key=<instance>)`. pywebpush has `if isinstance(vapid_private_key, Vapid01): vv = vapid_private_key` — instance path skips from_string.

**Generate a fresh keypair (Python cryptography):**
```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64
pk = ec.generate_private_key(ec.SECP256R1())
pem = pk.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
pub = pk.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
VAPID_PUBLIC_KEY     = base64.urlsafe_b64encode(pub).rstrip(b'=').decode()
VAPID_PRIVATE_KEY_B64 = base64.b64encode(pem).decode()
```
Verify: `Vapid01.from_pem(pem).public_key` X962 b64url must equal VAPID_PUBLIC_KEY.

**Render MCP `update_environment_variables` MERGES by default** (`replace:false`) — safe to add vars without wiping others. This is DIFFERENT from the raw Render API `PUT /env-vars` which replaces the whole set (the 2026-05-14 wipe incident). Use the MCP tool, not the raw PUT.
