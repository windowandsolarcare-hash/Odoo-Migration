---
name: project_vault_phase3_sharing
description: "Vault Rework PHASE 3 (SHIPPED 2026-09-08): per-note MULTI-RECIPIENT sharing. DJ marks a note shared with specific people (res.partner w/ x_render_role — Cheryl now, employees as onboarded) or Everyone; PRIVATE by default. Stored in Drive props shared_with (comma ids) + shared_all. Recipient view = /cheryl/documents (routers/cheryl/documents.py). SECURITY: recipient id SERVER-DERIVED from session `p` (never a param), EXACT-id match (never substring), default-deny, shortcuts(pinned) never shared, share-setting owner-only. Flipped Cheryl's Documents tile LIVE."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T22:46:53.228Z
---

**Built 2026-09-08 (DJ refined P3 from a Cheryl-binary into a scalable multi-recipient model; Lead approved approach + 1 security condition). The note-level expression of [[feedback_dj_owns_cheryl_erp_access]]. Builds on P1/P2 ([[project_vault_phase1_md_notes]], [[project_vault_phase2_search_shortcuts]]).** Spec: `3_Documentation/VAULT_PHASE3_APPROACH.md`.

**Recon that grounded it:** app login is **res.partner-based** (`auth.py` queries res.partner by `x_render_pin`+`x_render_role`; the authz session carries `p` = that partner id; Cheryl = partner **23243**). So recipient identity = res.partner id, matched against the session `p`.

**Recipient source (auto-grows):** `GET /api/notes/share_targets` = res.partner WHERE `x_render_role` set (excl. owner) = everyone with app access. Onboard an employee (give them a login) → they auto-appear as a share target. Cheryl is the first.

**Storage:** Drive `properties` (same as tags/pinned/wnote → works on md notes + Doc archive): `shared_with` = comma-joined partner ids, `shared_all` = '1'. **PRIVATE = both absent (default).**

**Owner side (notes.py + v2_vault.html):** share picker in the editor "more" area — per-person checkboxes + "Everyone" + private default; `POST /api/notes/{id}/share {with:[ids],all:bool}` (owner-only) validates each id ∈ real targets, writes props. `list_notes`/`notes_index` return `shared_with`/`shared_all` so the picker shows current state.

**Recipient side (routers/cheryl/documents.py — new, registered main.py):** `/cheryl/documents` page (static/cheryl/documents.html, read-only viewer) + `/cheryl/api/documents` (list) + `/cheryl/api/documents/{id}` (read). Home "Documents (W&SC)" tile flipped coming-soon → LIVE `/cheryl/documents`. (The Real-Estate Documents tile stays coming-soon.)

**★ SECURITY (Lead conditions, all baked):**
- **EXACT-ID match, NEVER substring** — `_shared_set(props)` splits the comma list; `_shared_visible_to(props,pid)` = `shared_all` OR `str(pid) in the set`. Partner '23' can NEVER match '23243' (substring `contains` on an access-control surface = privilege escalation, same lesson as the /owner allowlist). Used in the list filter AND the per-note read.
- **Recipient id SERVER-DERIVED from the session** (`session_from_request(request).get('p')`) — NEVER a client `as` param. `documents_for_recipient(viewer_pid)` / `recipient_read(viewer_pid, note_id)` (both in notes.py) are called ONLY by the cheryl delegation with the session pid.
- **DEFAULT-DENY:** no share props ⇒ private (owner-only). `recipient_read` re-verifies the share on THAT exact note before returning any content.
- **Shortcuts (pinned) excluded** from every shared view + read (belt — DJ's account #s never leak even if mis-shared; revisitable later, not hardcoded impossibly).
- **Share-SETTING endpoints owner-only** (under /owner); **company_id rigor** kept.
- **Employee-session note (Lead):** shipped Cheryl (proven `p=23243`); when the FIRST EMPLOYEE gets vault access, ADD a session-identity assert before trusting their `p` as a recipient — don't let a mis-identified employee session pull another's docs. NOT built yet (no employee has vault access).

**Verify (Specialists-scope):** py_compile notes.py + main.py + documents.py; node-check v2_vault + documents.html; all endpoints registered (401 not 404: share_targets, /cheryl/api/documents[/{id}], /cheryl/documents, POST /share); app healthy = the new router booted. **Functional/cheryl-cookie QC = Lead's** (share→appears; private/shortcut never appears; exact-id boundary; no spoof) + surface to DJ. Additive — P1/P2 + Doc path intact. **Remaining Vault: P4 = migrate the ~3000 archive Docs → md.**
