---
name: project_dj_tax_filing_2025
description: "DJ's 2025 tax filing context (self-filed, TurboTax). W&SC + Saunders Printing are BOTH Schedule C sole-props under Daniel J Saunders III's personal 1040. 2025 TurboTax currently shows $14,649 fed / $1,714 CA due — likely overstated because Odoo's business net is missing depreciation/vehicle/home-office/full expenses. Google Drive tax locations + the deduction inputs still needed."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-11T20:17:39.919Z
  originSessionId: c55fb80c-b5c7-4e62-a78d-f46e55b25f48
---

**ENTITY (DJ 2026-10-11):** The legal entity is **Saunders Printing** (sole proprietor, Daniel J Saunders III). **Window & Solar Care is a DBA of Saunders Printing.** BOTH businesses are reported as **Schedule C sole proprietorships on DJ's personal 1040** (two Schedule Cs, same 1040). DJ is **self-filing** via TurboTax (not a CPA this year). In Odoo these are separate companies (W&SC=1, Saunders Printing=3) but for tax they roll up to one person's 1040.

**★ DON'T CONFLATE: DJ also PREPARES his PARENTS' returns** — Daniel Saunders **Jr** & Anita M Saunders (retirees, Married Filing Jointly, income from Social Security / IRA / pension, address 33720 Bell Rd). Their file "TaxReturn2025 MomDad.pdf" (2025 1040-SR, bal due $553) and a "TurboTax Live Premium 2024" scrape (MFJ, total income $41,547, $923 due) are THEIRS, not DJ's. DJ = Daniel J Saunders **III** (address 32569 San Miguelito Dr, Thousand Palms).

**2025 return status (the job):** DJ's own 2025 TurboTax ("Business | Sole Proprietor") currently shows **Federal due $14,649, CA due $1,714**. Deadline ~**Oct 15 2026** (personal 1040 on extension; today 2026-10-11 = ~4 days). Goal: finish the Odoo 2025 books → produce a correct 2025 Schedule C → DJ enters it → the $14,649 should drop.

**★ THE TAX THESIS (why the number is likely too high):** DJ's history shows a MODEST real business net after legit deductions (2023 return: AGI $23,171, taxable $7,457, total tax $4,175). But Odoo's 2025 W&SC P&L shows Net ~$32,803 (Rev $79,877 / Exp $47,074) because Odoo is MISSING the big Schedule C deductions: **vehicle (actual or mileage), depreciation (all 30 fixed-asset accts = $0), home office, health insurance, SEP/retirement, half of SE tax**, and possibly not-fully-categorized expenses. So the Odoo net OVERSTATES taxable business income → inflates the $14,649. Finishing the Schedule C properly is the lever. (Also: Saunders Printing = company 3 has its OWN Schedule C to reconcile.) See [[project_accounting_migration_unfinished]] for the Odoo live state.

**GOOGLE DRIVE — tax locations (owner windowandsolarcare@gmail.com):**
- Folder **"Tax Returns"** id `1ZfdPZa4wGvqZUvhFErXNk29p3UGUZzEm`; **"Tax Info"** id `13VJl85hBPxla_sieu7M-6aQw8KDJHyzw`; **"TurboTax"** id `1fnGgpu_pn7a51VhiQ1ImUFUkeYAsYlMV`.
- DJ's **2023** return PDF = "TaxReturn_Redacted.pdf" id `1EsxWO4ltynra_r9nOGo6Jg2Q3xEbdctN` (parent folder `1kt3jJYknbTvmKf6RM3XPyruok8deKWIF` — DJ's **2024** return should be in/near this folder; LOCATE it next as the Schedule C template).
- **2025 in-progress** scrape = "TurboTax Online 2025" doc id `1QcZX2-3pthEAbovBE2W851WjUWXPMUYmQGn9empIsxc` (banner only: $14,649 / $1,714; no line values).
- These scrape docs are browser captures — the real line detail is in the filed PDFs.

**DRIVE MCP QUIRK:** `mcp__claude_ai_Google_Drive__search_files` ONLY accepts `fullText contains '<term>'` — `name contains`, `'<id>' in parents`, and bare terms all error "Unsupported query field." Use fullText search; to list a folder, fullText-search a distinctive phrase and filter by `parentId` in results.

**★ SENSITIVE:** these files contain SSNs, bank routing/acct numbers, and personal financials. NEVER echo an SSN/account number in chat, NEVER publish or send any of it externally, and redact in any memory. Read-only analysis only; DJ self-files.

**DEDUCTION INPUTS STILL NEEDED FROM DJ (materially change the 2025 number):** business vehicle miles (or actual auto costs) + which method; the QB Fixed Asset List (for depreciation of truck/equipment); home-office sq ft (or % of home); 2025 estimated tax payments already made (fed + CA); self-employed health insurance premiums; any SEP/Solo-401k contribution; and whether 2026 Odoo expenses need completing (QB import stopped ~2026-05-31, so 2026 is NOT a tax concern yet — 2025 is). Accounting prepares DRAFT; DJ enters/files. See [[user_accounting_knowledge]], [[feedback_assistant_use_app_workflow_not_raw_api]].

**★ 2025 DEDUCTION TO-DO (DJ authorized recording 2026-10-11): Danny IT/AI contract labor ~$5,350.** Danny (DJ's son) performed real **AI/IT development work** for W&SC in 2025 that easily equals **$5,350** (the amount Danny already reported as self-employment income on his own 2025 Schedule C). DJ wants to TAKE this as a contract-labor deduction (Schedule C line 11) — **settled by OFFSET against expenses DJ incurred ON DANNY'S BEHALF** (specific offsetting items TBD, to be worked out during tax prep). Cash-basis requires the payment/offset to be real: credit the $5,350 work against a genuine debt Danny owed DJ (advances/bills DJ fronted for him → non-taxable return to DJ = full benefit; NOT rent, which would create offsetting rental income = a wash). ACTION: (1) identify the specific expenses DJ fronted for Danny to offset against, (2) document the barter/offset (dated memo: work performed + debt credited), (3) consider a late 1099-NEC, (4) keep this IT/AI work distinct from Danny's W-2 cleaning role. Don't forget to deal with this on the return. Draft analysis — DJ/CPA decide.