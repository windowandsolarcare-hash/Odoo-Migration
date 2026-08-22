---
name: project_memory_index_structure
description: "How the memory index is structured — MEMORY.md is a sharded TOC, detail lives in idx_<domain>.md; how to add a memory without re-bloating it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

The memory index was restructured 2026-07-10. It had grown to **one flat MEMORY.md of 147 KB / 445 lines / 341 entries averaging 426 chars each** — but only the first ~24 KB loads at session start, so ~85% of the index was invisible each session. Memory itself was fine (341 topic files, 1.45 MB detail); the *index* had outgrown its load budget.

**New layout (all in the memory dir):**
- `MEMORY.md` = a small **TOC** (~11 KB, always loads): domain sub-index links + counts, plus the ~48 `feedback_*` standing rules inlined as hooks (behavior rules stay always-on).
- `idx_<domain>.md` = per-domain sub-index of one-line hooks. Domains: field_app, scheduling, outreach_crm, myday, vault_notes, odoo, workiz_sync, infra_deploy, saunders_printing, business, misc. Each is ≤~9 KB (one `Read` away).
- Full pre-split backup: `MEMORY_full_backup_2026-07-10.md`.
- Re-shard script: `C:\Users\dj\reindex_memory.py` (parses the backup, compacts hooks, classifies by domain, writes shards + TOC). Rerun only if a full rebuild is ever needed — normally just hand-append.

**How to ADD a memory (the rule that keeps this from re-bloating):**
1. Write the topic file as usual.
2. Add its one-line hook (≤~145 chars; detail stays in the topic file) to the matching `idx_<domain>.md` — **NOT** to MEMORY.md.
3. Only edit MEMORY.md itself to add a new `feedback_*` standing rule or to create a brand-new domain shard.

**Why:** the whole point is keeping MEMORY.md fully loadable each session. The old "one line per entry in MEMORY.md" habit (from the base memory instructions) is what blew the budget — for a project this size the index must be sharded, and hooks must stay short. To find a memory across domains, `Grep` the memory dir. See [[feedback_proactive_inefficiency_capture]].
