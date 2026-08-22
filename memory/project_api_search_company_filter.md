---
name: project_api_search_company_filter
description: "Universal home search /api/search now filters company_id in [1,False]; why Cheryl contacts weren't actually the cause"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

`/api/search` (dashboard.py ~7305, the home "Saunders Business Group" universal customer search → Customer Brain) was MISSING the `['company_id', 'in', [1, False]]` leaf that its sibling searches (dashboard.py 402/411) have. Added 2026-07-11 (commit 0f4c8f9) to the base name/street/city domain + the phone fallback (`_pdom`) + the SO-number lookup (`company_id = 1`). This was NOT a regression from my session — the base domain was byte-identical at 73a64d2f (before my session); it just never had the filter.

★ **Nuance:** adding the filter changed nothing VISIBLE, because **no Cheryl (company 2) contact has a Workiz `ref`**, and the search already required `['ref', '!=', False]` — so company-2 contacts were already excluded. What DJ saw as "Cheryl customers" (e.g. "Active Window Products, Los Angeles") are actually **unstamped `company_id=False` contacts** with a Workiz ref, matching the query via mid-word substring (name ilike 'rod' hits "p**ROD**ucts"). The company filter keeps `False`, so those strays still show. To hide them would need either stamping them to a company or word-boundary matching — not done.

**★ Two DIFFERENT customer searches — keep both filtered:** (1) HOME universal search = `/api/search` (dashboard.py) — requires `ref != False`, so applicants never showed. (2) **New Order → Existing customer picker = `/api/intake/search`** (new_job.py) — had the company filter but NO customer-signal, so job APPLICANTS leaked in. Fixed 2026-07-11 (commit ad91f53): added `'|', ['ref','!=',False], ['child_ids','!=',False]` — a real customer has a Workiz ClientId (ref) OR ≥1 property child; drops Indeed/hiring applicants + stray imports. Francisco Rodríguez (2 records, ids 27037/26990, created by DJ May 2026, one `@indeedemail.com`, 0 SOs/leads/props) was the trigger. ★ Applicant/stray contacts get created as res.partner company_id=1 with no ref/category/property — filter customer pickers on `ref OR child_ids`, not just company_id.

**WORD-START matching (commit 40f6b2d, 2026-07-11):** DJ asked to match word-STARTS not substrings. `api_search` token_groups now use `_wordstart(field,t)` = `['|', [field,'=ilike',t+'%'], [field,'ilike',' '+t]]` per name/street/city — field starts with the token OR a later word does. So "rod" → Rodgers/Rodriguez/Rodine/Rod Becky Hahn but NOT mid-word "p**ROD**ucts" (his vendor Active Window Products no longer surfaces on "rod"). Verified live. (Active Window Products = a legit W&SC VENDOR, company_id=False — DJ doesn't care if it shows, that wasn't his complaint; the substring noise was.)

★ The weird "search shows A/B alphabetical names that don't match the query" DJ screenshotted was a **transient during a deploy** (app mid-restart), NOT a backend bug — `api_search` returns `[]` for len(q)<2 and always AND's the token domain otherwise; live it correctly returns the substring matches. See [[project_duplicate_and_reschedule_fixes]] (Render ~3-4 cycle propagation lag). dashboard.py verified intact (12864 lines, all 35 key endpoints present) — the scheduler.py struggle touched scheduler.py, not dashboard search.
