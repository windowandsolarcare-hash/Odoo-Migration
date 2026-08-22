---
name: project_silent_lie_swallowed_reads
description: "Rule (Portal 2026-08-19): `except: return []` (or return {}) on a read that FEEDS A PAGE is not resilience — it's a silent lie if the empty value renders as plausible-but-false content. Raise instead; soften only where empty and failed mean the same to the viewer."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-20T05:24:16.561Z
---

**Discovered via the Odoo-429 shared-helper bug (2026-08-19).** `shared/odoo.py`'s `odoo_rpc` did a bare `return res["result"]`; on a 429 the body has no `result` → `KeyError` → 500. That was the visible symptom. The *worse*, invisible one was in the portal: its reads did `except: return []`, so a rate-limit didn't surface as an error — it rendered a **confidently WRONG page**. A 24-visit customer got an EMPTY service history, no upcoming visit, no rain-guarantee, and "Ready whenever you are." A customer watching their own history vanish is worse than one seeing "try again" — silence made the failure invisible.

**The rule:** `except: return []` / `return {}` on a read that feeds a page is NOT resilience — it's a silent lie **when the empty value renders as plausible-but-false content.** Before swallowing a read error, ask: *what does the empty result render as to the person looking at it?*
- If empty renders as **plausible-but-false** (no history, no balance-due, no upcoming job when there IS one) → **RAISE**; let the caller catch and degrade HONESTLY ("couldn't load — try again"), never fabricate a clean-looking empty state.
- Swallow/soften ONLY where **empty and failed mean the same thing to the viewer**, and the failure is in the SAFE direction: a missing photo link shows nothing (fine); a balance we can't verify is a balance we don't demand (fine).

**Fixed live:** portal.py 5c24a7f0 (core partner/jobs reads raise → `portal_me` catches → honest degrade; peripheral photo/balance reads still soften, safe direction). portal.html 26b1daee (transient failure now reads "Your link is fine — give it a moment and refresh" + Try-again, instead of wrongly telling a customer with a perfectly good link to phone in for a new one). Related: [[project_odoo_rpc_429_retry]], [[project_odoo_200_not_success]], [[project_company_filter_fails_open]] (same "verify/handle for real, don't assume the happy path" family). Also a Lead lesson from the same incident: don't diagnose from a traceback without checking the fix didn't postdate the logs, and `KeyError:'result'` (error-key checked first) ≠ a masked Odoo error.
