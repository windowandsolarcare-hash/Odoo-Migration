---
name: feedback_report_gray_lines
description: Every financial report/P&L emailed to DJ must have a gray separator line under EVERY line item. Phone readability.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

**Every P&L / financial report emailed or shown to DJ must put a light-gray separator line (border-bottom) under EVERY line item row** — not just section totals.

**Why:** DJ reads these on his phone, often with the screen narrow/closed. Without a line between each row, it's hard to track which line item goes with which dollar amount across the gap. (Asked 2026-06-08.)

**How to apply:** In HTML email tables, add `border-bottom:1px solid #cfcfcf` (light gray) to the `<td>`s of every line-item row, with ~7px row padding. Section headers/totals keep their heavier borders. Default emailer: `5_Accounting/pl_2024_2025.py`. Apply the same row-separator treatment to ANY new financial report (balance sheet, cash flow, expense reports, etc.), not just this P&L.
