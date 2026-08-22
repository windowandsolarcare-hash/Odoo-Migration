---
name: QuickBooks MCP — Capabilities, Limitations, and Setup Status
description: What the QB MCP can and cannot do, and the current profile configuration for Window & Solar Care
type: reference
originSessionId: d77fc6bd-119f-4192-b2c8-a8592257d2b6
---
## MCP Tools Available (~8 total)
- `company-info` — returns company name and industry
- `profit-loss-quickbooks-account` — generates P&L report from QB data
- `cash-flow-quickbooks-account` — generates cash flow report
- `profit-loss-generator` — generates P&L from a provided CSV (not QB account)
- `cash-flow-generator` — generates cash flow from provided CSV
- `quickbooks-transaction-import` — imports transactions INTO QB
- `quickbooks-profile-info-update` — updates QB company profile (industry, state, name)
- `benchmarking-against-industry` — compares to industry benchmarks
- `benchmarking-quickbooks-account` — benchmarks from QB account data
- `industry-recommendation` — suggests industry classification

## What It CAN Do
- Pull P&L summary totals by category (income, expenses, net)
- Pull cash flow report
- Show monthly breakdown columns
- Import new transactions into QB
- Read company name and industry

## What It CANNOT Do (important limitations)
- Cannot retrieve individual transaction records — no list of invoices, no line-by-line payments, no customer names per transaction
- Cannot edit or delete existing QB transactions
- Cannot pull balance sheet
- Cannot access vendor lists, customer lists, or chart of accounts
- Cannot reconcile
- Cannot drill down into a category to see constituent transactions
- The P&L response is a 276K character JSON of monthly rollup columns — not transaction rows

## Current Profile Configuration (already set — do not re-set)
- **Company Name:** Window & Solar Care ✓
- **Industry:** Services to buildings and dwellings ✓
- **NAICS Code:** 561790 ✓
- **State:** CA ✓
- Set on 2026-04-15 — this persists in the QB MCP account

**Note:** The `profit-loss-quickbooks-account` tool requires `company-info` to be called first in each session to establish the connection before it will work.

## QB Financial Summary (pulled 2026-04-15, period 2020–2026)
- Total Income: $390,935
- Total Expenses: $214,159
- Net Operating Income: $176,759

## Why We're NOT Using QB MCP for the Migration
The MCP cannot export individual transactions. The actual Transaction Detail by Account CSV (downloaded directly from QB) is far more useful — it has 16,777 individual transaction rows going back to 2019. That CSV is the source of truth for expense history, not the MCP.

## QB MCP Use Cases Going Forward
Essentially none after Odoo accounting is live. Odoo will be the financial system of record. QB MCP may be useful occasionally for a quick sanity check during the migration transition period only.
