---
name: project_vault_sharing_model
description: "Vault Phase-3 sharing model (DJ decided 2026-09-08): per-note, SCALABLE recipient sharing — each note has a share control where DJ picks recipients from a GROWING people-list (Cheryl now, EMPLOYEES as added) PLUS a 'share with everyone' option. PRIVATE by default. Generalizes 'share with Cheryl' into a real multi-recipient model that scales with the team. Shortcuts stay always-private."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-08T22:31:41.228Z
---

**DJ decided the Vault Phase-3 sharing model 2026-09-08** (evolving a simple binary into a real system — he was offered folder / share-all-except / per-note-toggle, and chose **per-note but SCALED**).

**The model:** each note/doc has a **SHARE control** where DJ picks the **recipients** — a **LIST of people that GROWS** (Cheryl now = res.partner 23243 / cheryl-role; **employees** as he adds them, future) — **PLUS a "share with everyone" option**. **PRIVATE by DEFAULT** — nothing is shared until DJ shares it. This turns "share with Cheryl" into a proper **multi-recipient sharing system that scales with his team**, not a Cheryl-hardwired switch.

This is the **note-level expression of [[feedback_dj_owns_cheryl_erp_access]]** — DJ grants access to the people he chooses, and it scales as his team grows.

**Build — routed to Specialists APPROACH-FIRST (2026-09-08; sensitive access-control surface, HOLD until Lead green-lights the approach):**
1. RECIPIENT SOURCE — the authoritative people-list + how it grows (Cheryl/cheryl-role today; future employees = hr.employee? app login/access-code users?), so "add an employee" auto-adds a share target.
2. PER-NOTE STORAGE — a note's `shared_with` set (Drive property list of ids + a `shared_all` flag); private = empty (default); must survive the P1 md model + the Doc archive.
3. SHARE PICKER UI — per-note control: people + checkboxes + "everyone" + "private"; phone/sunlight-friendly.
4. SCOPE SEAM EXTENSION — the index scope built in P2 (`?scope=shared` drops shortcuts) generalizes to a **per-recipient scope** → returns notes where `shared_with` contains that person OR `shared_all`. Cheryl's "Documents (W&SC)" view = notes shared with Cheryl (or everyone). **SHORTCUTS stay private always** ([[project_vault_shortcuts_vs_saved]]).
5. SECURITY — default-deny; a note reaches ONLY people it's explicitly shared with; keep `company_id` fails-open protections ([[project_company_filter_fails_open]]); never expose other-company data.

**How to apply:** Phase 3 is this sharing system (not a simple folder/binary). It's the ONE remaining Vault phase needing design; the P2 scope seam already proves the plumbing. P4 (archive migration) stays queued after. See [[project_vault_rework_greenlit]].
