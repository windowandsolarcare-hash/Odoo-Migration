---
name: project_workiz_tech_not_api_settable
description: "The Workiz tech/Team assignment on a job CANNOT be set via the Workiz API (per DJ 2026-06-09). Must be done in the Workiz UI. Affects any \"schedule a job\" automation."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

**Fact (per DJ, 2026-06-09):** You cannot assign the **tech (Team)** on a Workiz job via the Workiz API. It has to be done in the Workiz UI.

**Why it matters:** Scheduling a job needs 3 things on the Workiz job — **tech, line items, status**. Status IS settable via API (`workiz_update` SubStatus + Status="Pending"). Tech is NOT. So DJ has to open the Workiz job anyway to set the tech.

**Implication for the scheduling-flow design discussion (2026-06-09):** Because DJ must enter the Workiz UI for the tech regardless, the cleaner approach is to **drop him straight into the Workiz job** (deep link) where he does tech + line items + status himself — rather than building a voice/API status-picker that doesn't save him the trip. This is a TEMPORARY bridge anyway: all of this goes away when Workiz is removed and the Render detail screen becomes editable ([[project_workiz_exit_field_editability]]).

Workiz job deep link format: `https://app.workiz.com/root/job/{uuid}/` (main page has status + team + items); items page is `https://app.workiz.com/root/job/{uuid}/items`.

DISCUSSION ONLY so far — nothing built. [[project_phase5_activity_flow]]
