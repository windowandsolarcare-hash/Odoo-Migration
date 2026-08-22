---
name: Planning constraints filter
description: Always filter architecture suggestions through DJ's four constraints before presenting them
type: feedback
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
Before suggesting any architecture, model, tool, or approach, run it through these four filters first. If it fails any of them, don't suggest it — find an alternative that passes all four.

**The four filters:**
1. **No new Odoo seats** — res.users records cost money, never suggest them for app users
2. **No custom Odoo models** — SaaS platform blocks them without support approval, last resort only
3. **One Odoo instance** — everything runs on window-solar-care.odoo.com, no spinning up new instances until growth demands it
4. **Scale across businesses** — DJ may offer this platform to other businesses (fiduciary, real estate, etc.), so solutions must work beyond W&SC

**Why:** DJ is building a scalable multi-business platform on a constrained budget. Textbook "best practice" answers (res.users, custom models, separate Odoo instances) are wrong for his situation. The right answer is the most practical one given real constraints.

**How to apply:** When planning anything — login systems, data models, integrations — run the suggestion through all four filters silently before presenting it. If you catch yourself about to suggest something that fails a filter, find the alternative first.
