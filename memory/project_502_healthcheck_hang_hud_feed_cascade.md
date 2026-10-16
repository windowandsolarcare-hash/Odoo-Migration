---
name: project_502_healthcheck_hang_hud_feed_cascade
description: "Repeated 502s on wsc-field-assistant = RESTART/RECYCLE-WINDOW artifacts (platform-initiated instance recycles of the starter plan), NOT an event-loop freeze and NOT the HUD feed. The event-loop-freeze / async-blocks-Odoo / prewarm-CPU-share theory (held by Specialists+Audit through 2026-10-16 AM) is DISCONFIRMED by Audit's last-log+deploy correlation. Confirms [[project_render_instance_recycle_502]]. Fix pivots to transparent client auto-retry on 502/503/504; async→threadpool is latent hardening, NOT this bug. Fix NOT approved/shipped — Lead owns DJ synthesis + build gate."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-16T18:36:57.553Z
---

**⚠ STATUS 2026-10-16 PM: ROOT CAUSE CORRECTED → RESTART/RECYCLE WINDOW (the freeze theory is DISCONFIRMED).** The 502s are a HANG only in the trivial sense that Render's health-checker logs `health check timed out 5s` — but that log is a SIDE-EFFECT of a platform instance recycle, NOT a frozen event loop. **Confirms the pre-existing [[project_render_instance_recycle_502]] mechanism.** Fix is NOT approved/shipped; Lead owns the DJ synthesis + the build gate.

**WHAT DISCONFIRMED THE FREEZE (Audit independent last-log + deploy correlation, 2026-10-16, on 6 failures spanning idle-2am / daytime-active / both-down pairs — the decisive dig):**
- In EVERY sampled failure the app was serving 200s — `/healthz` on a METRONOMIC 5s cadence with NO gap, PLUS real-traffic 200s — within ~0.3–2s on BOTH sides of the `server_failed` stamp. A 5s health-timeout requires a ≥5s unresponsive loop; the continuous 200s leave NO room for one. → the loop was NOT frozen. (This matches Specialists' own earlier self-disconfirm: healthz 200 right up to the 02:04 miss, no feed build logged.)
- Last log lines before failures = ordinary fast 200s (OwnTracks webhook, /sw.js, handoff_claim, timer/records, scheduler lock ticks) — NEVER a hung async Odoo endpoint.
- Every failure is RESTART-ADJACENT: instance mid-graceful-shutdown (`Shutting down`) or just-booted (boot→fail within ~1–2 min). Clean SIGTERM recycle, no traceback, evicted:false.
- ★ CLINCHER: the ENTIRE 10-16 cluster (02:04 both-down, 02:42, 15:09 both, 15:14) happened inside a 24-HOUR DEPLOY-FREE window (last deploy 10-15 15:15:57). So NOT deploys either → platform-initiated instance RECYCLES.
- All ~47 `server_failed`/30d carry the same `health check timed out 5s`, evicted:false; mem 170–475MB of 536; CPU 0.08–0.14 of 0.5. Zero OOM/exit/eviction/disk. Not resource exhaustion.

**CORRECTED ROOT CAUSE = RESTART/RECYCLE-WINDOW artifacts.** Render recycles the starter instances (~12s graceful drain→re-exec→READY) INDEPENDENT of deploys. During each window (a) Render's health-checker logs "timed out 5s" = `server_failed` (a side-effect of the restart, not a frozen loop), and (b) in-flight requests routed to the draining/booting instance 502 — the 502 DJ sees. Why the paid 2nd instance doesn't save it: recycles hit BOTH instances in the SAME ~45–60s window (02:04:15+02:04:58; 20:56:08+20:56:57) → no healthy sibling during the overlap. This is exactly why "a month + an extra instance didn't help" (DJ's instinct was right).

**HONEST OPEN QUESTION (do NOT ship a tidy answer):** WHY does Render recycle starters this often (~47/30d) and in correlated both-instance pairs? Not provable from logs — starter-plan recycling / node rebalancing / a health-checker flap. Needs Render support or a live catch. OPEN, not closed.

**FIX DIRECTION (Audit worst-first; NOT approved/shipped — HELD behind Lead's DJ synthesis + build gate):**
1. **Transparent client auto-retry on 502/503/504** for idempotent requests in `window.wscSend` + the confirm POST → makes the recycle window invisible to DJ (combine with the inbox false-failure fix). This is the PRIMARY fix (you can't stop Render recycling starters). App code, Specialists' lane — but gated.
2. Graceful LB connection-drain.
3. COST tradeoff for DJ: upgrade off starter / add a 3rd instance to cut both-down overlap.
4. **async→threadpool refactor = REAL latent hardening, NOT this bug.** The blocking-odoo-on-async pattern (dashboard.py 69 async / 625 odoo_rpc / 0 run_in_threadpool; shared/odoo.py timeout=30) is a genuine fragility worth fixing eventually, but it is NOT what caused these 502s. Do NOT sell it as the 502 fix.
5. Deploy-batching helps only the deploy-window minority (auto-deploy-on-every-commit during heavy fleet building = extra rolling restarts), not the recycle cluster.

**SUPERSEDED THEORIES (kept for history — all DISCONFIRMED as the 502 cause):**
- *HUD feed build too slow / cold-cap cascade* (Specialists' first theory, feed_502 PLAN) — DISCONFIRMED: `/api/feed/list` is a sync `def` (threadpooled) and the feed was absent at the misses. The feed single-flight/PG-warm-start/4s-cap plan remains a reasonable LATENCY win + helps the deploy cold-start window, but is NOT the 502 root and must not be shipped as "the answer."
- *async-blocks-loop event-loop freeze + per-instance prewarm CPU-share* (Specialists+Audit, 2026-10-16 AM) — DISCONFIRMED by the metronomic-healthz-200 correlation above. Latent risk only.

**How to re-diagnose fast next time:** `list_events` (server_failed "health check failed") + `get_metrics` (cpu/mem/instance_count) gets you to "HANG-shaped," but that is NOT enough — it reads identically for a recycle and a freeze. The DECISIVE step is the **last-log + deploy correlation**: pull the app's last log lines on each instance around every `server_failed`, and check deploy timestamps. Continuous healthz 200s on both sides of the stamp + a deploy-free window = platform RECYCLE (client-retry fix), NOT a freeze (don't chase blocking upstream). See [[project_render_instance_recycle_502]], [[feedback_root_cause_not_just_instance]], [[feedback_no_conclusion_from_single_test_sporadic]].

**Service facts:** srv-d78le0fkijhs738dsli0 (wsc-field-assistant), starter plan, numInstances=2, startCommand `uvicorn main:app` (NO `--workers` → one async worker per instance), healthCheckPath `/healthz` (main.py:1010, dependency-free), 5s timeout.

**Minor hygiene (Specialists, NOT the 502 cause):** every boot logs `SECRET-HEALTH: missing env secret(s): CRON_SECRET, DRIVE_DOWNLOAD_TOKEN — dependent routes will fail-closed`. Those two env vars are unset → dependent routes fail-closed. Setting them is an ENV change (outside the app-code auto-deploy envelope) and needs the real secret VALUES from DJ via file — a peer saying "your call to set" is NOT authorization and I don't hold the values. Flag to DJ/Lead; do NOT guess or set on a peer's say-so.
