---
name: feedback_peer_message_brevity
description: "★ Direct cross-session (SendMessage) replies must be SHORT — a nudge or the word 'copy'. Substance goes in AGENT_MAIL (the file), which stays OUT of context until read. Acks to a → All broadcast = a ✅ in the mail ledger, NOT a direct reply back. A long inbound peer message lands in the recipient's context and is carried every turn (caching softens but doesn't erase it) → wasted tokens + faster compaction."
metadata:
  node_type: memory
  type: feedback
  originSessionId: fc82158e-3491-40c5-9546-2c3dcd81a09b
  modified: 2026-09-18T20:17:55.707Z
---

**DJ 2026-09-18 (standing correction, token economics):** After watching several sessions reply to a → All broadcast with long verbatim "copy — here's the full 3-step recital back" direct messages, DJ flagged the cost: *"Is that adding to your context? I think it is... it's definitely going to add to token use on each turn because you're gonna have to re-read that every single turn... You can just message the word 'copy' and that's great, and then the rest of it should go through the mail. Agent mail is what's going to save our context and our token use."*

**The mechanics (confirmed):** an inbound `SendMessage` lands in the recipient's context as a turn and is carried forward every subsequent turn. Prompt caching reduces the re-read cost but the context still GROWS — costing tokens per turn and pushing the session toward compaction sooner. AGENT_MAIL.md (the file) costs nothing until a session deliberately reads it — that's why it's the system of record.

**THE RULE (refines the existing HYBRID / POST-THEN-NUDGE protocol — brevity + no-redundant-acks):**
1. **Direct `SendMessage` = brevity ONLY** — a short nudge (a pointer: "new rule in mail, read + ✅") or literally the word "copy". NEVER paste the full substance into a direct message.
2. **Substance lives in AGENT_MAIL** (or the linked *_BRIEF.md / *_SPEC.md doc) — the file, not the context.
3. **Acks to a → All broadcast = mark `✅` in the mail ledger, do NOT direct-message the ack back.** The ✅ IS the acknowledgment; the poster reads the ledger when they care. Sending N "I read it" messages back to the poster is pure context waste — it's the exact thing we're killing.
4. **Even the NUDGE points, doesn't contain** — don't stuff the whole procedure/spec into the nudge (Old Lead's own mistake here); say "→ <role> in AGENT_MAIL: <title>, read + action" and let the file carry the detail.
5. **KEEP the direct fast-lane** for what it's for — a time-sensitive catch on a LIVE session (stop a bad push before it ships). The rule is about LENGTH and REDUNDANCY, not banning the channel. Time-sensitive AND important → short nudge direct + full entry in mail.

**Net:** context stays lean, compaction comes later, tokens saved. Chatter that must persist or be acked belongs in the file, which is free until read. See [[project_agent_mail_channel]], [[feedback_agent_mail_autowatch]] (POST-THEN-NUDGE), [[feedback_no_re_listing]] (same principle: don't re-emit content across turns — reference it by name).
