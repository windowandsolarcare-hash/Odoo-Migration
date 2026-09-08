---
name: project_cheryl_home_groups
description: "Cheryl home (static/cheryl/index.html) is grouped into 3 LABELED sections (DJ-finalized 2026-09-08): 'The Cheryl App' (Needs You/The Plan/Clients/Idea Board/WSC Hiring/HR + Documents-W&SC coming-soon), 'Real Estate' (Showings/Documents-RE/Resources/Accounting, all coming-soon), 'Personal' (Library). TWO SEPARATE Documents tiles (W&SC vs real-estate) — do NOT merge. FAB launcher APPS array must mirror this order."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T19:54:23.376Z
---

**Built 2026-09-08 (DJ-finalized placements, Lead-relayed, cheryl-cookie QC passed).** Cheryl's `/cheryl/` home was a flat tile list; now 3 `<section class="hub-group">` blocks each with a `.hub-group-title` header, in this fixed order:

1. **The Cheryl App** (Window & Solar Care): Needs You `/cheryl/hud` · The Plan `/cheryl/plan` · Clients `/cheryl/clients` · Idea Board `/cheryl/ideas` · WSC Hiring (`openWSCHiring()`→/owner/hiring) · HR (`openWSCHR()`→/owner/hr) · **Documents (W&SC)** — NEW **coming-soon** tile (sub "Vault · Photos · Job files"), backed by the Vault rework (planned, not built — flip live when that ships).
2. **Real Estate** — ALL coming-soon: Showings · Documents (real-estate, sub "Communication log · Disclosures") · Resources · Accounting.
3. **Personal**: Library `/cheryl/library`.

**★ TWO separate "Documents" tiles — DJ was explicit they are DIFFERENT, do NOT merge:** the W&SC one lives in Group 1 (Vault-backed), the real-estate one in Group 2. Both are `card-documents soon` (purple) but different subtitles/groups.

**Implementation notes:** grouping + section headers + one new coming-soon tile only — **every existing href/onclick preserved** (Clients/Idea Board/Hiring/HR moved INTO Group 1 from the old flat list; Idea Board was last, reordered up). Coming-soon tiles are `.hub-card ... soon` (`pointer-events:none`, `aria-disabled`). CSS: removed `flex:1` from `.hub-cards`, added `.hub-groups{flex:1}` + `.hub-group-title`; desktop media aligns the title to the 900px centered card row. 12 tiles, node-check clean, deploy live.

**★ FAB launcher must MIRROR this grouping/order** — `static/cheryl/launcher.js` APPS array (see [[project_cheryl_fab_launcher]]) should match; it's Cheryl's-cloud to align (don't fork). Flagged to Cheryl's-Cloud 2026-09-08. See [[project_cheryl_ideas_delegation]] (cheryl-role QC is Lead's, not a Specialists session).
