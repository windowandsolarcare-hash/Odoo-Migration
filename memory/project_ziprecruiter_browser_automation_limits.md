---
name: project_ziprecruiter_browser_automation_limits
description: "ZipRecruiter candidate LIST loads fine for claude-in-chrome, but the candidate DETAIL / Full-Application (resume) views HANG the browser automation."
metadata:
  node_type: memory
  type: project
  originSessionId: e3071731-f37a-4440-a358-34be556223c2
  modified: 2026-10-03T07:45:57.592Z
---

Working the ZipRecruiter employer candidate dashboard (ziprecruiter.com/emp/candidates?app_job=...) with the claude-in-chrome tools, 2026-10-02:

- **The candidate LIST view works great.** `get_page_text` on the list returns every applicant's ZR-parsed work-history summary (job titles, employers, dates, years-of-experience, certs, interest tags, "Willing to Relocate"). This is enough to rank candidates on fit without opening individual resumes.
- **The candidate DETAIL view (`&app_contact=<id>`) and the "Full Application" (resume) view HANG the automation.** Both `screenshot` ("Script injection timed out after 5000ms") and `get_page_text` ("Page still loading — waited 45000ms for document_idle") fail — ZR's SPA runs persistent scripts so `document_idle` never fires on those views. Clicking "Full Application" opens a modal on the SAME tab (no new tab), which the tools then can't read.
- A recurring "How are the candidates you've received so far?" survey popup covers the list right side — close it (X ~top-right of the popup) before reading/clicking.

**Why it matters:** don't burn tokens fighting the resume viewer. The list summary is the ranking workhorse.

**REMOTE-SEND LIMIT (2026-10-03):** When DJ is away and the computer screen is off/locked, the Chrome window does NOT render — `computer` screenshots fail with `Cannot take screenshot with 0 width` (resize_window does not fix it). So HR CANNOT safely send candidate messages via computer-use while DJ is away: you can't visually verify the recipient. Also: clicking a card's "Message" button opens a composer the find-tool labels a "BULK message composer" — do NOT blind-send (risk: blasting the 1-person note to all applicants). Only drive ZR sends when DJ is at the machine with the screen ON so each step is visually verifiable. True hands-off auto-outreach = a server-side app flow, not blind browser automation.

**How to apply:** Rank from the LIST `get_page_text`. To read a FULL resume PDF, don't rely on automation — either (a) ask DJ to open "Full Application" and relay/paste it, or (b) use the resume's direct `protected-upload?upload_id=...&filter=pdf` link from the bulk-CSV export (login-gated; may still not text-extract). For "blank" applicants (no parsed work history on the card), the designed fix is the FIRST REACH-OUT message, which asks their experience — their reply places them (see [[project_ziprecruiter_lead_hiring]]). Relates to [[project_hiring_right_fit_not_top_talent]].
