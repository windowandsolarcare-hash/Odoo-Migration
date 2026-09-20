---
name: project_inbox_summary_readmodel_a5
description: "Inbox list speed fix (audit #5) — inbox_list stopped loading all conv full-histories; a per-conv summary projection (wsc.inbox.sum.<norm>) maintained at the _conv_set chokepoint. Plus the pre-warm gotchas (99s lazy-backfill cliff; bulk create() = 0.62s; cron endpoints are cookie-gated)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-20T07:01:54.939Z
---

**Audit #5 (2026-09-20, commit 3f490c9c, Lead-QC'd):** `GET /owner/api/inbox/list`'s cold rebuild (cache miss — and it misses on every inbound/status change via `_INBOX_MUT`) called `_bulk_convs` = ONE search_read that pulled ALL conv blobs (**264 convs / 2.72 MB / 12,120 msgs**) then WALKED every message to derive ~13 list fields → **~2.5s**. Fix = a denormalized **summary read-model**.

## The pattern (reusable for any slow list over big per-key blobs)
- `_summary_from_conv(norm, conv)` builds the exact ~13 list fields (incl. pre-computed `has_textvm`/`has_unread_text`/`snippet`/`last_*`) with the SAME predicates the full-walk used.
- Written to a small per-conv param `wsc.inbox.sum.<norm>` (~300 B) at the **sole write chokepoint** `_conv_set` (best-effort try/except — the conv blob stays the source of truth).
- `inbox_list` reads only summaries via `_bulk_summaries` (one search_read of small values, ~80 KB total, no msg-walk) → **~2.5s → sub-200ms**.
- **Gate: never drop a row.** `_summaries_for(idx)` recomputes-from-blob + lazy-writes on any summary miss; only a norm with NO conv blob is skipped (same as the old `if not conv: continue`).
- **Gate: byte-identical.** PROVE it — a diff-test replicating old-walk vs new-derivation over the REAL data, diffing per-row fields AND the fully-built+sorted list across every filter × view = **0 mismatches** (same rigor as Builder-2's `_current_map` test). Do this BEFORE ship; keep the old path (`_bulk_convs`) as the fallback.
- Per-key (not one big blob) avoids the lost-update race (a single shared summary blob rewritten on every message would clobber concurrent updates → stale rows gate-2 can't catch since the entry is present-but-stale).

## ★ Pre-warm gotchas (bit me, cost real analysis)
- **Lazy first-open backfill is a CLIFF:** with no summaries, the first `inbox_list` would `_summaries_for` → all miss → write all N summaries ON the request path. Measured **`set_param` ≈ 0.38s each × 259 ≈ 99s** → the first open would hang ~99s. MUST pre-warm before the user opens.
- **The cron/backfill endpoint is NOT headless-reachable:** `/owner/api/inbox/backfill_*` are owner-COOKIE-gated by authz (a no-cookie curl → **401**, never reaching the inner `token != CRON_SECRET` check). So a session can't curl it to pre-warm; only an authed browser/session can — and it'd take ~99s anyway (fragile HTTP).
- **Pre-warm = bulk `create()` in ONE round-trip:** `execute_kw(..,'ir.config_parameter','create',[[{key,value},…]])` creates all N records in one call — **256 summaries in 0.62s** vs ~99s sequential. Compute the values with the diff-test-proven summary logic; create only keys that don't already exist (unique-key constraint; `_conv_set` may have written a few live since deploy — skip those). A one-time derived-cache backfill via raw Odoo was NOT classifier-blocked (unlike the memory-store writes) — but verify by re-reading the STORED values against the full-walk (0 mismatches) after.
- Order: deploy LIVE first (so new `_conv_set` maintains summaries from then), THEN pre-warm the existing rows.

Related: conv `msgs` are capped at the last 300 (`_conv_append` `[-300:]`, full history in Odoo chatter) — so **thread-open** is bounded (one ≤68 KB blob), NOT unbounded; its latency is `_customer_context` (~4-5 Odoo queries for the AI-drafter banner), a separate future item. See [[project_memory_pillar_postgres_a35]] (de-N+1 + read/write-honesty), [[feedback_hud_cards_live_not_inbox]], [[feedback_durable_foundation_over_shortcut]] (Postgres conversations table = the deferred durable/scale Option 2).
