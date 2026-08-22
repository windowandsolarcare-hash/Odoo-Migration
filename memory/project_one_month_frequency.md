---
name: project_one_month_frequency
description: "1 Month" is now a valid maintenance frequency (DJ has monthly customers). Added to the SO selection field + the 2 hardcoded job-detail dropdowns; next-date math already handles any "N Month".
metadata:
  type: project
---

**DJ (2026-08-13):** has a few monthly customers; frequency choices were 3/4/6/12 Months. Added **"1 Month"**.

**What "frequency" is stored in (verified):**
- `sale.order.x_studio_x_studio_frequency_so` = **Selection** (field id 15538). Values now: **1 Month**, 3 Months, 4 Months, 6 Months, 12 Months, Unknown (reordered, 1 Month first). Add a value via `ir.model.fields.selection` create (field_id=15538, value+name).
- `res.partner.x_studio_x_frequency` (property master) = **char** (free text) — any string works, no selection to edit.
- `create_next_maintenance_so` (new_job.py) reads freq via `re.search(r'(\d+)\s*(month|week)')` → **"1 Month" → +30 days** automatically. No code change needed for the date math.

**NOW DJ-EDITABLE via Settings (2026-08-13, centralized — no more hardcoding):** frequency options are managed on the ⚙️ Settings page (v2_settings.html "🔁 Maintenance frequencies" — add/remove). **Single source of truth = the Odoo SELECTION values** on field 15538 (so any offered value is always a valid SO write). Helpers in `shared.py`: `get_frequency_options()` / `add_frequency_option()` / `remove_frequency_option()`. Add creates the `ir.model.fields.selection` value; remove unlinks it (existing records keep their stored string). API in myday.py: `/api/settings/get` returns `frequencies`; `GET /api/settings/frequencies`; `POST /api/settings/frequency {action,value}` (validates value = "N Month(s)/Week(s)" or "Unknown"). **All pickers read it live:** brain.py `_EDIT_SELECT` loop overrides Frequency with `get_frequency_options()`; dashboard.py so_full uses local `_freq_options()` (self-contained file); v2_new_job.html `loadStatic` fetches `/api/settings/frequencies`. Settings is now a launcher **favorite** (v2_apps.js `fav:true`). So DJ adds "2 Months"/"6 Weeks" himself and it appears everywhere — no code. Commits: shared d7ad9bb, myday 6e0b045, brain 3942f2d, dashboard 65f8f1f, v2_settings 78e72e8, v2_new_job 2aa1a90, v2_apps 7f8c4b3.

**Norman Woodel switched to monthly (his example):** property 24116 (3586 Date Palm Trail) `x_studio_x_frequency` = "1 Month"; his next job SO 17563 (264947) moved from Nov 11 → **Sep 13** (one month out) + `x_studio_x_studio_frequency_so` = "1 Month". Next time it's done → +1 month picks up automatically. Related: [[project_paywatch_auto_tip]].
