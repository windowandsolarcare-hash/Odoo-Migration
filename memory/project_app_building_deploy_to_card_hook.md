---
name: project_app_building_deploy_to_card_hook
description: "App Building 'ship system' deploy-to-card hook — LIVE 2026-10-13 (atomic commit fe478707). A ship_card is OPENED at work-start (problem/goal/scope) and CLOSED at deploy (solution/result) so every change leaves a permanent problem->fix->result record with an Audit/Lead/post-deploy review trail. Covers the endpoints, the hollow-Shipped enforcement, and who writes which review stamp."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-14T04:01:25.914Z
---

DJ revived App Building as the permanent record of problem->fix->result. Shipped LIVE 2026-10-13 (atomic git-Data commit fe478707; plan `3_Documentation/review/DEPLOY_TO_CARD_HOOK_PLAN.md`; code `routers/owner/ship.py` + `routers/authz.py` + `static/owner/v2_app_building.html`). Went through the full §15 gate (Audit plan-review 173e67e0 -> Lead firsthand confirm -> byte-QC 5b5942d3) and dogfooded itself (card id `deployhook`).

**Two-point hook:** OPEN the card at work-START (problem in DJ's words + goal + scope_in/scope_out), CLOSE at deploy (solution + result). A `card-<id>` commit on main derives the card's Shipped (existing git-signal mechanism, unchanged).

**`/api/ship/card/work_record` = THE one canonical UPSERT writer** for all 6 record fields at BOTH open and close (NOTIFY_SECRET, in PUBLIC_EXACT). Single atomic `INSERT ... ON CONFLICT (id) DO UPDATE SET <present fields>` — NOT SELECT-then-write (races `_birth_card`). **null-vs-'' enrich semantics:** a field absent/null is SKIPPED (left as-is), an explicit `''` CLEARS (the correct-down/blank path). `work_started_at = COALESCE(ship_cards.work_started_at, EXCLUDED.work_started_at)` so it is set ONCE and a later intake correction never resets it. `/api/ship/card/create` stays create-only (`ON CONFLICT (id) DO NOTHING`) — routing intake THERE silently drops it on an existing/auto-born card (returns ok:true but writes nothing), which is why work_record is the writer. A fresh card born via work_record is fine: `ship_cards` defaults `state='Captured'`, `created_at`/`state_changed_at=now()`, all else nullable.

**Enforcement — hollow Shipped can't hide (Audit BLOCKER 2):** `_derive_board` appends flag `shipped_no_record` when `state=='Shipped' and work_started_at IS NOT NULL and (not solution or not result)` — pure PG, no git_ok gate. Scoped to `work_started_at` so legacy pre-hook cards don't flood Needs-attention. The hub `v2_app_building.html` renders it via the generic `FLAG_TEXT[f]||f` path -> shows "⚠️ Shipped with no write-up..." in Needs-attention with NO viewer change. Visibility IS the enforcement.

**Review trail — `ship_card_reviews` (append-only; a wrong stamp is corrected by a newer one, newest-per-stage wins, never deleted).** Who writes which (the Q5 ruling — ties [[feedback_audit_stamp_confirm_firsthand]]):
- **Lead** writes `audit_plan` (evidence_ref = Audit's §15-COMPLETE AGENT_MAIL commit ref) and `lead_qc` (evidence_ref = byte-QC branch sha) — AFTER Lead firsthand-confirms Audit's stamp from the ledger. One accountable writer who verified both; builder never writes a review stamp (NOTIFY_SECRET is fleet-shared, so a self-stamp would be forgeable).
- **Deploying session** writes `post_deploy` (evidence_ref = deploy sha) — the only self-evidencing row.
- `verdict` is 400-validated to pass/changes/fail. The chip is **DISPLAY/MIRROR only — NO gate reads it;** the authoritative §15 stamp stays Lead-confirms-Audit-firsthand-from-the-ledger. Board shows newest-per-stage via ONE `DISTINCT ON (card_id, stage)` query (no N+1); detail returns full `reviews[]`.

**Aging ripple:** `ship_aging_alerts` uses the 120h Building threshold for a `work_started_at`-set Captured card (not 48h) so an actively-worked card doesn't fire a false "rotting" alert; the `dep_blocked` parked backstop (168h) stays the highest threshold.

**How to apply:** when a fleet session does DJ-directed work, OPEN a card via `/card/work_record` at work-start and CLOSE it (solution+result) at deploy; the review trail is written per the roles above. Hub viewer polish beyond the one flag label is a fast-follow branch (Specialists owns, app code). Ties [[project_atomic_multifile_deploy_git_data_api]], [[feedback_display_implies_crud_parity]], [[feedback_deploy_tap_reaches_executor_not_relayed]] (auto-deploy: §15 + byte-QC still gate even without a DJ tap).
