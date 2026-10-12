---
name: feedback_archive_statements_on_pull
description: "★ Whenever Accounting retrieves bank/credit-card statements or exports (CSV/PDF), SAVE them to a durable, organized, retrievable location — never leave them only in chat or the messy Downloads folder — so future sessions reuse instead of re-pulling. DJ 2026-10-12. Candidate yearly archive routine."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T18:51:49.168Z
---

**DJ 2026-10-12.** Anytime we go out and retrieve statements/exports (bank CSV, credit-card PDFs, activity downloads via computer-use), they must be **saved somewhere we can quickly retrieve them again** — NOT just left in the chat, and NOT just sitting in `Downloads`. Store them in an organized archive so the next session doesn't have to log in and pull them all over again.

**Why:** re-pulling is slow, token-heavy, and needs DJ to log in each time; the online window is limited anyway (Amex/Chase only keep ~24 months of activity online — older is PDF-only). Capturing them once, filed, preserves the data permanently and makes every future session instant.

**How to apply:**
- On every statement/export pull, COPY the files into an organized folder: `C:/Users/dj/Documents/Business/Financial_Statements/<Business>/<Account>/<Year>/` (e.g. Saunders_Printing/Amex_11003/2024/2024-12-27.pdf; .../Chase_8356/...activity.csv). Established 2026-10-12 with the first Saunders pull.
- For true CROSS-SESSION durability (cloud/other roles), also push to a Google **Drive** "Financial Statements" folder (Drive is reachable by any session with the connector) — local folder is the fast local mirror.
- Name files clearly (account + period). Note which statements are PDF-only (pre-24-months) vs CSV.
- This belongs in the **Accounting boot pack** (`saunders-render-app/3_Documentation/roles/ACCOUNTING.md`) so every future Accounting spin-up follows it.

**Candidate routine (DJ musing, not firm):** a **YEARLY** (not monthly) archive pass — log in to each bank/card once a year and pull/file that year's statements before they age off the online window. Monthly is overkill/hassle; yearly fits the 24-month retention. Login required (DJ does it; computer-use reads + files). Revisit with DJ before scheduling. See [[project_saunders_qb2010_export_findings]], [[project_wsc_odoo_opening_balances]].
