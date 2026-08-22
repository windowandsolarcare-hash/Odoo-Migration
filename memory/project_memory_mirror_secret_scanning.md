---
name: project_memory_mirror_secret_scanning
description: "GitHub secret-scanning push protection BLOCKS any memory file that contains a live secret (Twilio SID/auth, Stripe/Google keys, OAuth client id/secret/refresh token). Redact to placeholders before mirroring; never write live tokens into memory notes."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T19:19:44.916Z
---

**When mirroring memory → GitHub (`Odoo-Migration/memory/`), files containing LIVE secrets are rejected with HTTP 409 "Repository rule violations found / Secret detected in content."** This is GitHub secret-scanning push protection, and it's correct — live credentials must not live in a repo.

**Discovered 2026-08-22** during the full memory→GitHub mirror. 9 of 607 files were blocked; all held real secrets that had been written straight into the notes: Twilio Account SID (`AC…`)/API key SID (`SK…`)/auth tokens (bare 32-hex), Stripe keys (`sk_live`/`rk_live`/`whsec_`), Google OAuth **client id** (`…apps.googleusercontent.com`), **client secret** (`GOCSPX-…`), and **refresh token** (`1//…`), plus a service-account block.

**Rules going forward:**
- **NEVER write a live secret into a memory file.** Memory = knowledge (how a thing works, which field, which SID *shape*). The actual token lives in **Render env vars** (source of truth) — reference it by name, don't paste it. Matches [[feedback_api_keys_via_file]].
- **To mirror a note that has a secret: REDACT first** — replace the token with a placeholder like `[TWILIO_ACCOUNT_SID — in Render env]`, then push. Scrub the LOCAL copy too (a live token in a plaintext local note is still a leak risk once we're multi-session/cloud).
- **Do NOT bypass** the block (GitHub offers a bypass URL) — putting live Stripe/Twilio keys in a repo, even private, is a real risk.
- Twilio **resource** SIDs (`RN`/`BU`/`IT`/`PN`/`TP…`) are NOT credentials and are NOT blocked — leave them; they're operationally useful (CNAM policy SID, trust-product SID, etc.).
- The 444-line `MEMORY_full_backup_2026-07-10.md` is intentionally NOT mirrored — redundant historical artifact (already sharded into topic files) and full of secrets; stays local-only.

Related: [[feedback_mirror_memory_to_github.md]], the memory-mirror section in CLAUDE.md.
