---
name: project_data_visuals_charts
description: "Shared inline-SVG chart module v2_charts.js (WSCChart: sparkline/bars/funnel/stacked/donut, CSP-safe, no external libs). Added visuals to Journal (heatmap), Stats (sparkline), Outreach (funnel), Time Clock (bars), Awaiting Reply (aging bar). Survey of all apps for more."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T09:54:44.023Z
---

**2026-07-25 (DJ: go through all apps, turn data into visuals/graphs where it lends itself).** Surveyed all v2 screens (3 Explore agents) → built the strong wins.

**Shared module `static/owner/v2_charts.js` — `window.WSCChart`** (commit 5c902bb): inline-SVG, theme-aware (CSS vars), NO external libs. Functions: `sparkline(values,{h})`, `bars(items[{label,value,color,sub}],{max,money})`, `funnel(stages[{label,value,color}])`, `stacked(segs[{label,value,color}])`, `donut(slices,{center,sub})`. Injects its own `.wc-*` CSS. Include with `<script src="/static/owner/v2_charts.js?v=1"></script>` after v2_apps.js, then `window.WSCChart.<fn>(...)` returns an SVG/HTML string for innerHTML. **Use this for ALL new charts — don't add chart libs.**

**Visuals shipped (inline, off existing endpoints — no backend change except goals /days earlier):**
- **Journal** (v2_journal.html) — GitHub-style calendar heatmap of entry days over the past year (custom inline, binary present/absent, from /api/journal/list entries[].iso). Reinforces the streak.
- **Stats** (v2_stats.html) — month sparkline of daily booked revenue (WSCChart.sparkline, from /api/stats/month days{}).
- **Outreach** (v2_outreach.html) — customer pipeline FUNNEL: All customers → Done business → Need outreach → Awaiting reply → Reach out today (WSCChart.funnel, from /api/outreach/pipeline: total/done_business/reactivation+reengagement/react_sent+reeng_sent/react_launch+reeng_due).
- **Time Clock** (v2_timeclock.html) — weekly hours bar chart (WSCChart.bars, from /api/payroll/week days[]).
- **Awaiting Reply** (v2_waiting.html) — aging stacked bar fresh≤7/waiting≤21/stale>21 (WSCChart.stacked, from ROWS days_waiting).

**NOT done — remaining opportunities (surveyed, buildable, DJ can greenlight):**
- Shift Review — per-day revenue / $-per-hr bars (from /api/payroll/shift_range rows[]).
- Re-engage Review — flag-mix stacked/donut (replied/you-messaged/auto-only/clean/no-history) from /api/reeng_review/list `counts{}`.
- Command Center — tint the existing month grid cells by job-count density (heatmap) from /api/calendar_jobs.
- Hemet — optional Workiz-coverage donut / lapse-recency histogram.

**Already covered / skipped:** Customer Analytics ALREADY has 9 Chart.js charts and the app has **NO CSP** (verified — CDN scripts load fine), so those render OK. Reactivation already has a Leaflet route map. Pre-Deposit / Weekly Reports (unstructured markdown) / Submitted / HR / Maintenance — not visual. See [[project_capacity_overview_screen]] (the capacity graph that sparked this).
