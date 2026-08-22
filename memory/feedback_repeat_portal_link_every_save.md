---
name: feedback_repeat_portal_link_every_save
description: "EVERY \"Portal — OVER\" sign-off must carry the picker link as a tappable markdown link — not just after saves. Bare/backticked URLs don't tap on DJ's phone."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-20T13:24:40.179Z
---

DJ, 2026-08-20, in two steps:
1. *"Repeat the portal link every time you save portal — and please make it a link not text."*
2. **Escalated same day: "Every time you say Portal — Over, I need you to include: Picker — find
   any customer: wscare.pro/owner/portal-links"**

**The rule (current):** the **Portal session's `🟢/🟡 Portal — OVER` status line is ALWAYS
accompanied by the picker link** — every single reply, including bare watcher ticks and
"mail: no change" turns. Not only after a deploy. Format:

```
Picker — find any customer: [wscare.pro/owner/portal-links](https://wscare.pro/owner/portal-links)
```

**Format matters as much as presence:** use a **markdown anchor** `[text](url)`. A bare URL or a
`backticked` one does not render as tappable on his phone, and tappable is the entire point.

After a deploy that touched the portal, ALSO re-paste a live example so he can eyeball the change
without searching — e.g. Blair Becker `https://wscare.pro/p/23046-617fb0ac9d`.

**Why:** he reviews on a phone between jobs. If the link isn't in the message he's looking at, he
has to scroll back to find it, and in practice that means he doesn't check the work at all. He
asked twice — treat it as non-negotiable, not a nicety.

Related: [[project_customer_portal]], [[feedback_always_paste_preview_link]], [[feedback_over_status_line]]
