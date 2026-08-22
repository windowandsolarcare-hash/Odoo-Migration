---
name: reference_v2_checklist_vault_doc
description: V2 App Redesign Master Checklist lives as a Vault Google Doc — update it whenever a v2 page ships or a replacement is approved
metadata: 
  node_type: memory
  type: reference
  originSessionId: 17f1db69-cc3e-47ab-9387-b6a4dee9ca9a
---

The running tracker for the v2 redesign is a Google Doc in the Saunders Vault (Quick Notes/W&SC Operations), created 2026-07-18 at DJ's request ("check boxes so we can keep up with which ones have a v2 done").

- **Doc ID:** `1nykUGClPG0kngSvj9jC_1_WAq1A6GLbTjOtOXQHPetQ`
- **URL:** https://docs.google.com/document/d/1nykUGClPG0kngSvj9jC_1_WAq1A6GLbTjOtOXQHPetQ/edit
- Created via `POST /owner/api/notes/create` {text, category:'W&SC Operations', title}; shows as a note card in `/owner/notes`.

**How to apply:** whenever a v2 page ships, a replacement is approved, or the plan changes, update the doc — flip its `[ ]`/`[x]` lines. Update path: Google Drive MCP (`mcp__claude_ai_Google_Drive__*`) on the doc, or `PATCH /owner/api/notes/{file_id}/update` (check its payload in notes.py first). Keep the "REPLACEMENTS APPROVED" section accurate — it starts empty; each entry needs DJ's explicit OK. See [[project_render_app_redesign]] for the full v2 state.
