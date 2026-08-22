---
name: feedback_email_draft_first_always
description: "ALWAYS create emails as Gmail DRAFTS for DJ to review and send himself — never send directly, even when he says \"yes/send\"."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

**Rule (DJ, 2026-06-24):** Every email I prepare goes to **Gmail Drafts first**. DJ reviews it and hits send himself. **Do NOT send directly via SMTP**, even if DJ replies "yes" or "send it" to a "want me to send this?" question — treat that as approval to PREPARE THE DRAFT, not to transmit.

Context: I sent a clarification to the insurance broker (Ana) directly via SMTP because DJ answered "Yes" to "Want me to send that clarification to Ana?". He liked the email but corrected the workflow: *"I didn't think you would ever send an e-mail without it going through draft first… from now on, maybe everything goes draft and I send it after I look it over."*

**Why:** DJ wants final eyes on anything leaving his name/business before it goes out. Outbound email is irreversible and customer/vendor-facing. A draft costs nothing and keeps him in control.

**How to apply:**
- Build drafts via IMAP APPEND to `"[Gmail]/Drafts"` (the working pattern: login windowandsolarcare@gmail.com + app password, set In-Reply-To/References from the thread's latest Message-ID to keep it threaded, attach files, append with `\\Draft` flag). Run the script from a clean dir (NOT C:\Users\dj — local `calendar.py` shadows stdlib imaplib).
- Tell DJ the draft is in Drafts and quote the body so he can review before sending.
- The ONLY time to actually send is if DJ explicitly says "send it directly / don't draft it / send without a draft." Default = draft.
- Same applies to Odoo `mail.mail` and any other send path — prepare, don't transmit, unless explicitly told.
