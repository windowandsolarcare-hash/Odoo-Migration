---
name: project_vault_rework_greenlit
description: "DJ GREENLIT the Vault rework 2026-09-08. Decision-1 chosen = rebuild note storage OFF Google-Docs-as-body to a controlled format WE own (still in Drive) → safe saves + real checkboxes + instant search + offline. 4 phases; Phase 1 (new note format + editor) building approach-first. The reworked Vault = the Cheryl app's 'Documents (W&SC)' tile. AFTER all 4 phases → full Auditor user-walk of the whole Cheryl app → punch list."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-08T21:06:25.702Z
---

**DJ greenlit the Vault rework 2026-09-08** (after I read him the plan aloud + he made the storage decision).

**The decision (Decision-1 from [[project_vault_overhaul_spec]], now MADE):** move quick NOTES off Google-Docs-as-storage (where saving replaces the whole Doc body → destroys formatting, no checkboxes) to a **controlled format WE own, still living in Google Drive** next to the files. Root fix. Unlocks: safe saves, real tap-to-check checkboxes, instant search, offline.

**What STAYS untouched:** Drive storage (5 TB), files/scans/PDFs, search-inside-docs (OCR). Only the note editor / storage-format / home-screen / access get reworked. No new systems, no Odoo model, no seats.

**4-phase plan (the artifact "Vault Rework Plan"):**
1. **New note format + real editor** (safe saves + checkboxes) — the core. **BUILDING NOW, approach-first:** Specialists to propose format (JSON/MD structure for text+checkboxes), storage mechanics (Drive file replacing the Doc-create path), editor tech (CSP-safe, phone/sunlight-readable), coexistence read-path for existing ~3000 Docs notes, search impact — for Lead review BEFORE building.
2. Redesigned home + search.
3. **Open it to the Cheryl app** — the reworked Vault becomes the live **"Documents (W&SC)"** tile (currently coming-soon) that DJ + Cheryl both use.
4. Migrate the ~3000 existing notes across + polish. (Coexistence throughout: existing notes stay readable; new notes use new format immediately; gradual migration, never a big switch-over.)

**★ AFTER all 4 phases ship (DJ directive 2026-09-08):** run the WHOLE Cheryl app through **Auditor** — a full USER-perspective walk → punch list of anything unplanned (edit/delete/edge cases/dead-ends). See [[feedback_auditor_user_perspective_gapfinder]]. This is the finish-line gate; Lead triggers the Auditor walk when the Vault rework completes.

**Reliability item to fold in:** the Drive OAuth token expires ~weekly + needs manual refresh — permanent fix during the rework so the Vault never quietly stops syncing.

**How to apply:** the Vault rework is the ONE big remaining Cheryl-app build; everything else on the Cheryl app is functional. Phase-gate the build; Lead QCs each phase; Auditor closes it out. See [[project_cheryl_library_vs_documents]] (Documents≠Library), [[project_cheryl_workspace_next_phase_brief]].
