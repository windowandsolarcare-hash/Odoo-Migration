---
name: project_workiz_lineitem_descriptions_not_migrated
description: Workiz per-LINE-ITEM Descriptions were NOT migrated to Odoo (SO lines carry only product name + price). They ARE recoverable from the full Workiz export JSON. Backfill is viable + planned.
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-21T00:06:47.983Z
---

**Discovered 2026-08-20 (DJ pricing Michael Krauss's pressure wash).** Odoo `sale.order.line` records carry only the **product name + price** — the Workiz per-line **Description** field did NOT come across in the migration. Verified exhaustively on SO 003196 line 5762 ($275 Pressure Wash): read EVERY field + the SO chatter — no description anywhere (line `name`="Pressure Wash", `product_id`=[108,'Pressure Wash']). DJ was surprised (he detailed jobs heavily), so this affects MANY jobs.

**★ THE DATA IS RECOVERABLE — full Workiz export exists.** DJ pulled every job right before Workiz retirement (2026-08-03):
- **`4_Reference_Data/Workiz_Final_Export_2026-08-02/workiz_all_jobs_2026-08-02.json`** (8.7 MB, **3,860 jobs**). Also `4_Reference_Data/Workiz_6Year_Done_History_Master.csv` + older snapshots in z_ARCHIVE_DEPRECATED/2_Migration_Archive.
- **Structure:** top-level = list of jobs. Job keys incl `UUID`, `SerialId` (= old job#), `LineItems` (list), `JobNotes`, `Comments`, `pricing`, etc. Each `LineItems` entry: `Id, Quantity, Price, Cost, Name, Description, Type, ...`. **The `Description` holds the detail** (e.g. Krauss $275 PW = "Concrete in backyard - Move all furniture"; $150="Driveway"; $100="Primary Entry").
- **MATCH KEY:** export `SerialId` (e.g. 3196) ↔ Odoo SO `name` (`003196`, zfill 6), OR export `UUID` ↔ SO `x_studio_x_studio_workiz_uuid`. Both clean.

**★ BACKFILL RUN + COMPLETE 2026-08-20 (DJ greenlit "I want the backfill for sure so we don't lose the data").** Wrote the Workiz `Description` onto a NEW clean field **`sale.order.line.x_line_desc`** (ttype text, store True — created in the Krauss test; NOT the line `name`). Result: **1,819 lines across 1,658 SOs** populated (of 1,669 jobs w/ ≥1 desc). Skipped + logged: 11 SOs whose SerialId has no Odoo SO name, + 14 export lines whose name has junk/typos (`(6.00)`, "Full Servicee"). Script `C:/Users/dj/wk_backfill.py` (`dry`|`write`); **audit CSV `C:/Users/dj/wk_backfill_audit.csv`** (line_id,so_name,line_name,desc) = the reversal key (write x_line_desc='' on those ids to undo).
- **★ MATCH LOGIC THAT WORKED (don't use price):** match export SerialId → Odoo SO `name.zfill(6)`; within a job group lines by **normalized name = `name.split('\n')[0]` lowercased/space-collapsed**, then zip export items → odoo lines **in ORDER** (positional within name-group handles 3× "Pressure Wash"). Price is UNRELIABLE (Krauss Solar line = $5 in export vs $150 in Odoo).
- **★ MIGRATION WAS INCONSISTENT (key discovery):** SOME Odoo lines kept only the product name (Krauss → desc was lost, needed backfill); OTHERS baked the description INTO the line `name` after a newline (`"Windows In & Out - Full Service\nIncludes: Inside…"`) — that messy name-with-desc is the "find/sort problem" DJ wanted to avoid. Backfill wrote the clean export desc to `x_line_desc` for BOTH cases; **left `name` untouched** (don't rewrite names on confirmed SOs w/o DJ approval).
- **DISPLAY (pending DJ decision 2026-08-20):** `x_line_desc` currently shown only on the 💵 by-service Prices screen. DJ wants to decide WHERE else — likely the job-detail Record Payment lines (his screenshot showed names only, no desc). Route to Specialists once decided.

**Feeds:** the new "price history BY SERVICE" customer screen (routed to Specialists 2026-08-20) wants these descriptions — backfill first (or screen reads export). See [[project_customer_brain_job_actions]].
