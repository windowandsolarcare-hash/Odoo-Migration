---
name: project_predeposit_paid_cache
description: "WSCPaid localStorage cache hides just-paid jobs from pre-deposit lists offline, no network refresh. paid-cache.js shared across dashboard/stale_sos/pre_deposit/field. Read before touching pre-deposit display or payment flows."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

# Pre-deposit "recently paid" cache — hide paid jobs without a network refresh (2026-06-09)

**Problem DJ hit:** Pay a customer (e.g. Leonard Karp) on the Stale SOs page → navigate back to the dashboard → the dashboard **Pre-Deposit Check panel still shows them**, because the dashboard is restored from bfcache/cached DOM and `predepLoad()` doesn't re-run. Only a full app restart cleared the name.

**Constraint DJ set:** Do NOT make the dashboard fetch on every show to fix this — he's often offline and won't risk the dashboard hanging on no network. So the fix must be **network-free**.

**Solution — `static/owner/paid-cache.js`** (shared, included by index/stale_sos/pre_deposit/field):
- `window.WSCPaid.mark(soId)` — call on EVERY successful payment. Stores `{id,ts}` in localStorage `wsc_paid_sos`.
- `WSCPaid.has(soId)` — true if marked paid (and < 14 days old; auto-prunes).
- `WSCPaid.reconcile(serverUnpaidIds)` — after a real fetch, drops any marked id the server no longer lists as unpaid (server caught up). Keeps the set self-cleaning.

**Wiring:**
- **Payment flows mark paid:** stale_sos.html `confirmPayment()`, field.html `doPayment()` → `WSCPaid.mark(soId)`.
- **Dashboard (index.html):** cards carry `data-so-id`/`data-amt`; `predepHidePaid()` hides paid cards + recomputes badge, called after each render AND on `window 'pageshow'` (fires on bfcache back-nav too) → paid job vanishes instantly, no network. `predepLoad()` still fetches on cold load only (existing behavior) and calls `WSCPaid.reconcile`.
- **Standalone pre_deposit.html:** `render()` filters `unpaid` by `WSCPaid.has` + `reconcile`; re-renders from `_pdLastData` on `pageshow`.

**Why keyed by so_id:** every pre-deposit source and every pay flow shares the Odoo SO id; `unpaid_jobs` returns `so_id`. Server drops a job from pre-deposit only when `x_studio_x_studio_workiz_status` becomes Done/Canceled — so until that propagates, WSCPaid hides it client-side.

**Key idea reusable elsewhere:** to clear a stale item after an action without a network refresh, mark it in localStorage and re-filter the rendered DOM on `pageshow` (covers bfcache restores that don't re-run JS). [[feedback_no_mutating_smoketest_payroll]] · [[project_phase4a_sync]]
