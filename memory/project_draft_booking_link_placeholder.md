---
name: project_draft_booking_link_placeholder
description: "AI-drafted customer replies wrote a literal \"[booking tool link]\" placeholder that would send as-is (no auto-substitution). Fixed on the Follow-ups screen by filling the real wscare.pro/c/<token> link."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T15:21:05.588Z
---

**Bug (2026-08-07, DJ hit live):** The Follow-ups "Needs action" screen (followups.py) drafts a reply (via the shared AI drafter `_draft_reply`/`_inbox_brain` in sms.py) that offers online booking, but the model was never handed a real link — so it wrote a literal **`[booking tool link]`** placeholder. Nothing substitutes it on send (Send via Twilio posts the textarea text verbatim), so tapping Send would text the words "[booking tool link]".

**Fix (followups.py):** new `_fill_booking_link(text, pid, phone)` + regex `_BOOKLINK_PH` (`\[[^\]]*\b(book|schedul|link)\w*\b[^\]]*\]`). Resolves the customer's contact (pid or `_resolve_pid(phone)`) → **`https://wscare.pro/c/<make_token(cid)>`** and swaps the placeholder for the REAL personalized link. Applied at the draft render (`elif draft:` branch) so DJ SEES the actual URL. Also hardened `POST /owner/api/ai/rewrite`: if the input had a `wscare.pro/c/` link and the rewrite dropped it / re-added a placeholder, the real URL is put back. (The screen is server-rendered; the card DJ was looking at was drawn before the fix → he must reload to see the filled link.)

**Still open (source-level, shared):** `_draft_reply`/`_inbox_brain` (sms.py) still EMIT the placeholder because the drafter isn't given the link — so the **inbox** (v2_inbox rewriteReply, same `/api/ai/rewrite`) can show the same placeholder in its initial draft (the rewrite guardrail preserves an existing link but the first draft's placeholder isn't filled there). Durable fix = hand `_draft_reply` the real link + "use this EXACT link, never a placeholder" (like `ai_sched_message`'s link guardrail). Flagged to lead. Personalized booking link canon: `make_token(contact_id)` → `wscare.pro/c/<token>` (booking.py; Calendly retired). See [[project_wsc_sendbox_shared]].
