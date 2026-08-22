---
name: project_outreach_reactivation_upcoming_job
description: Outreach Campaigns "Reactivation" list wrongly showed customers who have a booked upcoming job — classify_customers() bucketed on last-visit only, ignoring x_studio_next_job_date
metadata:
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
---

**Bug (found 2026-07-12, Anne Sandberg):** A customer with a booked FUTURE job (`x_studio_next_job_date` in the future) still appeared on the **Reactivation** tab of the Outreach Campaigns window (`/owner/outreach`, routers/owner/outreach.py). Anne's last completed visit was 2025-03-25 (>12mo) but she had an Oct-2-2026 job booked — she is NOT lapsed, yet showed as a reactivation candidate.

**Root cause:** `classify_customers()` in outreach.py is THE state engine the whole Outreach window + pipeline counts read from. It bucketed every contact purely on `x_studio_last_visit_all_properties`:
```
elif lv < one_year:   buckets['reactivation'].append(id)
```
Its own docstring said the rule was "last service >12 months **/ none upcoming** → Reactivation" but the "none upcoming" half was never coded. So anyone lapsed on last-visit landed in reactivation regardless of a booked future job. (The reactivation Launch branch in `api_outreach_list` also never re-checks next_job_date — it trusts the classifier.)

**Contrast:** the RE-ENGAGEMENT launch path `_reeng_launch_partners()` DID correctly exclude booked customers (`_nj = next_job_date; if _nj and _nj >= tdy: continue  # already booked`). Only reactivation was missing the gate, and it was missing at the classifier root.

**Fix (commit e02686c1):** in `classify_customers()`, added `x_studio_next_job_date` to the search_read fields and gated the reactivation bucket:
```
_nj = str(c.get('x_studio_next_job_date') or '')[:10]
_upcoming = bool(_nj and _nj >= _tdy)
...
elif lv < one_year and not _upcoming:  buckets['reactivation'].append(id)
```
A lapsed-but-booked customer now falls through to maintenance/re-engagement, where the booked-job filter hides them from actionable lists. This also moves them out of the reactivation COUNT into re-engagement (more correct).

**Why:** a customer who already has a future job booked must never be asked to reactivate — it's a bad-look duplicate outreach. **How to apply:** `x_studio_next_job_date` (res.partner, written Phase 3/5, cleared Phase 4 on Done/Canceled) is the "already booked" signal — any list that offers a customer for NEW outreach (reactivation, re-engagement, reminders) must exclude `next_job_date >= today`. classify_customers() is the shared engine; fix bucket logic there, not per-list. See [[project_reactivation_sent_book]] [[project_waiting_screen]].
