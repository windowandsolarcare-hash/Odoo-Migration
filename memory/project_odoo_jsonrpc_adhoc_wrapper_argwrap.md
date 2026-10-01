---
name: project_odoo_jsonrpc_adhoc_wrapper_argwrap
description: "Ad-hoc Odoo JSON-RPC wrapper for scans/tests — pass domain/ids/key as ONE arg, don't double-wrap; get_param key is a string"
metadata:
  node_type: memory
  type: project
  originSessionId: 430559b0-9410-47a6-ae47-0dc126d75711
  modified: 2026-10-01T14:04:05.748Z
---

When a local session writes its OWN thin Odoo JSON-RPC helper (for a read-only scan or a deploy verification test — NOT the app's `shared.odoo.odoo_rpc`, which already handles this), the execute_kw arg shape bites. The wrapper signature is `rpc(model, method, *args, **kw)` → payload `args=[DB, UID, KEY, model, method, list(args), kw]`. So each positional you pass becomes ONE element of the method's arg list. **Pass the domain / ids / param-key as a SINGLE argument object — never double-wrap:**

- `search_read`: `rpc(m,'search_read', [[leaf],[leaf]], fields=[...], limit=N)` — domain is a list-of-leaves = ONE arg (implicit AND). ✅
- `read`: `rpc(m,'read', [id1,id2], fields=[...])` — ids = `[id]`, NOT `[[id]]`. `[[id]]` → "unhashable type: 'list'". ❌
- `search`: `rpc(m,'search', [], order=..., limit=1)` — empty domain = `[]`, NOT `[[]]`. ❌
- `get_param`/`set_param`: `rpc('ir.config_parameter','get_param','my.key')` — key is a bare STRING, NOT `['my.key']`. A list key → "unhashable type: 'list'". ❌

**Why:** `list(args)` already wraps your args into the method arg list; wrapping again (`[[...]]`) nests one level too deep, so Odoo treats the inner list as the value (domain-leaf / id / param-key) and errors ("'list' object has no attribute 'lower'" for a domain, "unhashable type: 'list'" for ids/param-keys). Burned 3× in one session (2026-10-01) during the booking-dedupe verify. Kwargs (fields/limit/order) go in `**kw` and are fine. Verified the booking phone-dedupe end-to-end this way (reused contact, no dup, cleaned up). See [[feedback_proactive_inefficiency_capture]].
