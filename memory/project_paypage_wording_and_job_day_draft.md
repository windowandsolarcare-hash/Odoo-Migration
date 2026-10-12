---
name: project_paypage_wording_and_job_day_draft
description: "Two customer-facing fixes deployed 2026-10-11: (1) Zelle pay-page wording (payments.py /api/zelle/pay render) — step-1 reword + a 'Please use our email, not a phone number.' line, apostrophes as &#39; HTML entities inside the single-quoted Python strings. (2) specialist_billing.py _zelle_request_text now says the real job day from the SO's date_order (UTC→Pacific) instead of a hardcoded 'today'."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T06:57:28.557Z
---

**DEPLOYED 2026-10-11 to main (DJ "Deploy now" §12 picker in Specialists' session; Audit §15 COMPLETE 6b24066a, Lead confirmed firsthand; Lead QC-GREEN fbb1f7db). Branch `specialists/paypage-wording-datefix` off 80eb18df. 2 Specialists-owned .py files, no route change.**

## Where these customer-facing strings live (the non-obvious part)
- **The Zelle PAY PAGE** (the `wscare.pro/pay/<token>` link customers open) is rendered by **`routers/owner/payments.py`** at **`@router.get('/api/zelle/pay')`** (~line 202) — a SINGLE dynamic Python-string template (Zelle-default view with a "Prefer to pay by card?" `payCard()` toggle). The short `/pay/<token>` link resolves to this one render. The amount is server-authoritative (`so.amount_total`, ignores any client `?amount=`).
- **The payment TEXT DRAFT** "thanks for having us out today…" lives in **`routers/owner/specialist_billing.py` `_zelle_request_text(first, lines, amount, so_id, date_order='')`** — the itemized Zelle/Venmo request texted to the customer. Built in exactly ONE place, `_zelle_request_core` (shared by the owner route + the `/tech` wrapper, and by both preview `send=false` and send). `sms.py` has NO "out today" string (a natural wrong guess — it's here). Grep-confirmed line was the ONLY hardcoded day-reference customer draft in all routers.

## Fix 1 — pay-page wording (payments.py)
Step 1 → "Open your bank&#39;s app and choose **Zelle** (or &#39;Send money&#39;)."; step 2 → "(tap Copy above)"; new line under the Copy button: `'<div class="znote">Please use our email, not a phone number.</div>'` + a `.znote` CSS rule; intro reworded. **Apostrophes/quotes done as HTML entities `&#39;`** so the single-quoted Python literals hold NO apostrophe (zero escaping, wrapper unchanged — Audit's note; the strings sit next to double-quoted HTML attrs + an `onclick="cp(\'...\')"` so flipping the wrapper would collide). Copy button byte-identical; amount/card/already-paid/send paths untouched.

## Fix 2 — real job day from date_order (specialist_billing.py)
Added `date_order` to the SO read; greeting is now `'%s, thanks for having us out%s! Here’s your total:' % (first, day)` where `day` is computed from `date_order` (stored **UTC** → convert to **Pacific** via `datetime.strptime(_dr[:19],'%Y-%m-%d %H:%M:%S').replace(tzinfo=utc).astimezone(_PT).date()`, mirroring the existing pattern ~line 285):
- `_jd >= today_pt()` → `" today"` (today, and folds the near-impossible future date_order — billing only surfaces past jobs).
- past → `" on " + _jd.strftime('%A, %b ') + str(_jd.day)` = "on Friday, Oct 9" (NO `%-d` — not cross-platform; build the day with `str(_jd.day)`).
- missing/unparseable → `""` → "thanks for having us out!" (never wrong).
`today_pt()` returns a `datetime.date`, so the `>=` compare is valid (Lead verified — the feature actually fires, doesn't silently omit). Reads the JOB's date, not the send date → a Sunday-night send for a Friday job says "Friday, Oct 9" (the George Frank case that prompted this). Curly apostrophe in "Here's" preserved. §9: fill-only, DJ reviews + sends every text.

See [[project_stripe_checkout_server_amount_and_pay_link]], [[feedback_times_in_pacific]], [[feedback_no_inventing_customer_lines_hud_confirm]], [[feedback_display_implies_crud_parity]].
