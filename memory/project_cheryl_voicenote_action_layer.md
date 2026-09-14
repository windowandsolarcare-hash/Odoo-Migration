---
name: project_cheryl_voicenote_action_layer
description: "Cheryl's voice-note ACTION layer (built 2026-09-14): Cheryl records a thought on her mic → tells Cheryl's-cloud 'process voice note X' → cloud PROPOSES an action (task/project/memory) → Cheryl approves on her HUD → app EXECUTES. Security = cloud is PROPOSE-ONLY (fail-closed secret header, hardcoded Cheryl author); only the Cheryl cookie can APPROVE+EXECUTE."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-14T08:33:59.777Z
---

**Built 2026-09-14 (DJ-designed over the marathon session). Sits ON TOP of the base Voice Notes app ([[project_voice_notes_app]]) — that app records+transcribes+keeps; THIS layer turns a kept note into an action.** The base mic on Cheryl's app is also the "get it off my mind fast" capture (DJ: mic fades 100%→~10% like the idea button; must keep the phone awake while recording — reuses wsc_recorder.js screen-wake nets).

**The flow DJ specified (verbatim intent):** "Cheryl says to cloud, listen to xxxxx voice note (she needs to be able to identify it) and process it... cloud can ask questions, get approval, or better yet utilize Cheryl HUD so Cheryl can approve it." So:
1. Cheryl records a voice note (identifiable in her past-notes list).
2. In **Cheryl's-cloud** she says "process voice note <that one>" — cloud reads the transcript, uses judgment, and decides what it should become (a task, a project/goal, run-through-memory like meeting recordings, etc.).
3. Cloud does NOT execute. It **PROPOSES** — enqueues a proposal that surfaces as a **Cheryl-only HUD approval card** (`_cheryl_voicenote_proposals`).
4. Cheryl **approves on her HUD** → the app executes (creates the task/project/memory via the canonical endpoints).

**Security model (the important part — a cloud session is untrusted-ish, so it is deliberately capped):**
- **Cloud = PROPOSE-ONLY.** `routers/cheryl/voicenote.py`: `/list` + `/propose` are reachable by the cloud via a **fail-closed shared secret header** `x-cheryl-cloud-secret` (`_secret_ok`, env `CHERYL_CLOUD_SECRET`) — NOT the cookie. These endpoints HARD-CODE `author='cheryl'` / company 2 / pid 23243 — the cloud cannot act as DJ or anyone else, and cannot pick the author from the request body. If the secret is missing/wrong → fail closed (deny).
- **Execute = COOKIE-ONLY.** `/execute` (turn an approved proposal into the real object) requires Cheryl's own logged-in cookie — it is NOT on the secret whitelist. So even with the secret, the cloud can never execute; only Cheryl (on her HUD, in her session) can.
- Net: cloud can *suggest*, Cheryl *decides*. Mirrors the app-endpoints-not-raw-writes rule and Cheryl-isolation.

**★ CHERYL_CLOUD_SECRET handling (do NOT leak):** value lives ONLY in `C:\Users\dj\_cheryl_cloud_secret.txt` (local) + Render env `CHERYL_CLOUD_SECRET` (set via MCP env merge, replace=false so other vars survive) — NEVER in the repo, AGENT_MAIL, chat, or a nudge. Delivery step (doc `3_Documentation/CHERYL_CLOUD_SECRET_DELIVERY.md`): DJ runs `! type C:\Users\dj\_cheryl_cloud_secret.txt`, copies it, pastes into Cheryl's-cloud with the instruction "send it as header `x-cheryl-cloud-secret` on every `/cheryl/api/voicenote/*` call." Minted with `secrets.token_urlsafe(36)`. Redact the secret SHAPE in any memory/commit (secret-scanning).

**Status at hand-off (2026-09-14 morning):** backend minted + endpoints built + env set; the ~30-sec paste-into-cloud step is PENDING DJ (his "do it in the morning"). Until then the cloud can't authenticate to `/propose`, so the loop isn't live end-to-end yet.

**How to apply:** any future "let the cloud take an action" pattern follows this split — cloud proposes through a fail-closed secret-gated, author-hardcoded endpoint; the human approves+executes through a cookie-gated one. Never let a cloud/secret path execute or choose its own author. See [[feedback_assistant_use_app_workflow_not_raw_api]], [[project_auth_role_model_cheryl_isolation]], [[feedback_dj_owns_cheryl_erp_access]], [[feedback_recordings_chunk_stream_durable]].
