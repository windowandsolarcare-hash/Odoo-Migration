---
name: project_inbox_brain_and_job_buttons
description: "Inbox thread has two jump buttons — 🧠 Brain (Customer Brain pre-filtered to this customer, for general research) + 📋 Their current job (jumps to the most-current SO detail). Both client-side, reuse existing deep-links."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-15T14:23:05.178Z
---

**DJ 2026-08-14:** reading a customer's inbox thread, their message is often either a general question (→ research all their jobs) or about their current job (→ jump to it). Wanted two buttons.

**Built (v2_inbox.html, commit 6ce8c1d) — a `#jumpRow` at the top of the thread body (always visible):**
- **🧠 Brain — all jobs** (`openBrain`): `location.href = /static/owner/v2_customers.html?cust_q=<name>&cust_pid=<partner_id>` → opens the **Customer Brain pre-filtered to this customer** (the `cust_q`/`cust_pid` deep-link params v2_customers.html already reads, L1063). Not the generic brain.
- **📋 Their current job** (`openCurrentJob`): `GET /api/followups/job_link?phone=<CUR.norm>` → `{ok, so_id}` (soonest-upcoming-else-most-recent = "most current") → `location.href = /static/owner/v2_field.html?open_so=<so_id>`. No job → shows a note in `sendNote`.

**Reuse, no new backend:** the conv (`CUR`) already carries `partner_id` (thread endpoint returns it, sms.py L1305) + `norm` (phone) + `name`. Brain deep-link = existing `cust_q`/`cust_pid` params. Job resolver = existing `followups.followups_job_link` (phone→so_id). Sits next to the existing intent-row (📅 Booking / ✅ Confirm / 💬 Reply). See [[reference_customer_brain_deeplink]], [[project_followups_job_detail_button]], [[project_inbox_intent_buttons]].

**★ CONSOLIDATED into ONE ⚡ Actions menu (DJ 2026-08-14, commits wsc_thread 1fc5a82 / v2_inbox 8d21cbb):** DJ didn't want scattered bottom buttons ("I'm gonna add more and more") — wants ONE "Actions" button → a menu of everything, and the top jump-row was invisible anyway (thread auto-scrolls past it). So: **`WSCThread.openMenu(items)`** = shared bottom-sheet ([{icon,label,run}]); `goBrain(pid,name)`/`goJob(norm)` are now DIRECT-arg. The **inbox** replaced its intent-row (Booking/Confirm/Reply) + the top jump-row with ONE `⚡ Actions` button → `openInboxActions()` → openMenu of 5 (Booking link / Confirm / Suggest reply / 🧠 Brain / 📋 Current job). The **WSCThread modal** got an `⚡ Actions` button in its header → `openModalActions()` (Brain + Current job). Adding a future action = one line in the item list. `WSCThread.jumpRow` was removed (superseded by openMenu). Below is the earlier (superseded) jump-row build.

**SHARED across EVERY text-thread surface (DJ 2026-08-14, commits wsc_thread 41fc5a3 / v2_inbox e5c80bc):** the buttons now live in the ONE shared texting component `wsc_thread.js` — `WSCThread.jumpRow(pid, name, norm)` returns the HTML; `WSCThread.goBrain(btn)` / `goJob(btn)` handle taps (read data-attrs, so they work off-modal too). Injected into the WSCThread MODAL shell (so **job detail `openTexts` + Customer Brain `openTexts` get them automatically**), and **v2_inbox now calls `WSCThread.jumpRow(...)`** instead of its own copy (removed the inbox-local openBrain/openCurrentJob). So anywhere a text thread appears — inbox (incl. opened from a HUD needs-reply card, which deep-links to v2_inbox?c=), job-detail texts, Customer-Brain texts — the same two buttons show. HUD path was already covered (needs-reply cards open v2_inbox). See [[project_shared_text_thread_component]].
