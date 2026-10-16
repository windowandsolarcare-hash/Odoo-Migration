---
name: project_render_502_event_loop_freeze_blocking_odoo
description: "The recurring app 502s are RESTART/RECYCLE-WINDOW artifacts — Render recycles the starter instances (~12s graceful drain→re-exec→READY), INDEPENDENT of deploys; the 'health check timed out 5s' is a SIDE-EFFECT of the restart, NOT a frozen loop. Proven by a 30-day log timeline. The earlier event-loop-FREEZE framing (in this file's name) is DISCONFIRMED."
metadata:
  node_type: memory
  type: project
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-16T18:33:23.266Z
---

★★ CORRECTED 2026-10-16 (Audit — the decisive last-log-line correlation Lead authorized). **The event-loop-FREEZE hypothesis this file's NAME encodes is DISCONFIRMED by the log timeline.** The app was demonstrably NOT frozen at any failure. Filename retained only to keep the GitHub mirror + idx hook linkage; read the corrected mechanism below. This is the SECOND memory-induced mis-diagnosis of this bug in a row — first [[project_render_instance_recycle_502]]'s "harmless 2-3h recycle" framing, then MY "event-loop freeze" over-correction — a cautionary example of exactly why a wrong memory is dangerous (it anchors the next session). DJ's "don't trust the tidy answer" applied to MY tidy answer too.

**WHAT THE 502s ACTUALLY ARE (evidence-backed, restart/recycle window):** Render recycles the starter instances — a clean graceful restart (`INFO: Shutting down` → `Waiting for connections to close` → `Application shutdown complete` → uvicorn re-exec → `[boot] ... READY`, ~12s) — and this happens INDEPENDENT of deploys. During each instance's ~12s restart window: (a) Render's health-checker records `HTTP health check failed (timed out after 5 seconds)` = the `server_failed` event (a SIDE-EFFECT of the restart, NOT a frozen loop), and (b) any in-flight request routed to the draining/booting instance 502s — that is the 502 DJ actually sees. Supersedes NOTHING of the mechanism in [[project_render_instance_recycle_502]] — it CONFIRMS it (that memo was right on mechanism, wrong only on "2-3h cadence" + "harmless").

**PROVEN (Render events + metrics + per-instance app-log timeline, 30 days):**
- All ~47 `server_failed` in 30 days = `health check timed out 5s`, `evicted:false`. ZERO OOM/exit/eviction/disk. (list_events.)
- Memory 170–475 MB vs 536 MB limit (peak away from failures); CPU ~0.08–0.14 of 0.5 core at 60s-res. NOT resource exhaustion. (get_metrics.)
- ★ THE DECISIVE READ: in EVERY sampled failure (6: m5kr8+kcgbl 02:04 both-down, kcgbl 15:09+15:14, m5kr8 02:42, n8s97 20:56) the app served requests — `/healthz` on a METRONOMIC ~5s cadence with NO gap, PLUS real traffic 200s — within ~0.3–2s on BOTH sides of the failure stamp. A 5s health-timeout requires a ≥5s unresponsive loop; the logs leave no room for one. → the single event loop was NOT frozen ≥5s. The blocking-`odoo_rpc`-on-`async def` FREEZE is NOT the cause.
- The last app log lines before failures are ordinary fast 200s (OwnTracks webhook, `/sw.js`, `handoff_claim`, `timer/records`, scheduler `lock acquired` ticks) — NEVER a hung async Odoo endpoint.
- Every failure is RESTART-ADJACENT: instance mid-graceful-shutdown (m5kr8 `Shutting down` 02:42:50; kcgbl 15:13:51) OR just-booted/stabilizing (kcgbl boot 02:03:34 → fail 02:04:58; n8s97 boot 20:55:50 → fail 20:56:08). Clean SIGTERM recycle, no traceback.
- ★ CLINCHER — NOT deploys: the ENTIRE 2026-10-16 cluster (02:04 both-down, 02:42, 15:09 both, 15:14) occurred inside a **24-HOUR DEPLOY-FREE window** (last deploy 10-15 15:15:57; next after 10-16 16:00). The 10-12 20:56 both-down was ~6 min AFTER a deploy had fully settled (n8s97 booted 20:55:50, 5 min post-deploy-end). So these restarts are platform recycles, independent of deploys. (list_events deploy_started/ended vs server_failed timestamps.)
- Why the 2nd instance doesn't erase it: recycles frequently hit BOTH instances within the same ~45–60s window (02:04:15+02:04:58; 20:56:08+20:56:57) → no healthy sibling to absorb the retry during the overlap. A 2nd instance only covers INDEPENDENT faults.
- Why it hid for a month: (1) "health check timed out 5s" LOOKS like a frozen-loop/slow-endpoint symptom → sent two digs (incl. mine) down the freeze path; (2) intermittent + clustered (pairs, then 12h+ gaps — NOT a clean cadence); (3) two memory notes mis-framed it in sequence (recycle-as-harmless, then freeze).

**HONEST OPEN QUESTION (do NOT ship a tidy answer — DJ-grade caveat):** WHY does Render recycle these starter instances so often (~47/30d), and why in correlated both-instance pairs? NOT provable from logs — candidates: starter-plan platform recycling behavior, node rebalancing, or a health-checker flap (one false timeout → Render recycles → more timeouts in the restart window). Resolve via Render support or a finer-instrumented live catch. The clustered both-down correlation is real but its precise trigger (co-located recycle vs load-shift cascade) is unproven.

**FIX (worst-first; the recycle memo's fix is now the RIGHT one — you cannot stop Render recycling starter instances):**
1. PRIMARY (durable, user-facing): transparent client auto-retry on 502/503/504/network-timeout for IDEMPOTENT POSTs in the shared send path (`window.wscSend`) + the confirm POST — makes the recycle window invisible. Same class as the inbox false-failure fix → combine. See [[project_render_instance_recycle_502]].
2. Graceful LB connection-drain so a recycling instance leaves rotation a beat before it stops answering `/healthz` (reduces the in-flight 502s). The app already does uvicorn graceful shutdown; the gap is the edge still routing to it briefly.
3. COST TRADEOFF to surface to DJ (don't default): upgrade off starter (fewer/less-aggressive recycles) or add a 3rd instance to cut both-down overlap probability.
4. Convert hot `async def` Odoo handlers to plain `def` / `run_in_threadpool` + cut the 30s `odoo_rpc` timeout — REAL hardening against a latent freeze risk, but NOT this bug's fix. Do not sell it as the fix.
5. Deploy-batching/warm-up helps ONLY the deploy-window 502 minority, not these recycle ones.

**Minor hygiene flag (Specialists):** every boot logs `⚠️ SECRET-HEALTH: missing env secret(s): CRON_SECRET, DRIVE_DOWNLOAD_TOKEN — dependent routes will fail-closed` (level=critical). Explicitly "not fatal / rest of app is up" — NOT the 502 cause — but those two env vars are unset on the service; worth setting so the dependent routes stop failing-closed.

**How to apply:** when the app 502s, pull Render `list_events` for the failure REASON (health-timeout vs OOM vs exit). health-timeout + `evicted:false` + the instance's app log showing a clean `Shutting down→READY` around it = a RECYCLE-window blip, NOT a crash and NOT a frozen loop — answer DJ "host auto-restarted the instance, your tap hit the ~12s gap, silent retry fixes it," and do NOT chase the event loop. Only a traceback / SIGKILL / `evicted:true` = a real crash. Relates to [[feedback_odoo_verify_content_not_status]], [[feedback_sporadic_bugs_repeat_test]], [[feedback_root_cause_not_just_instance]].
