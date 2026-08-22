---
name: project_settings_screen
description: "One Settings screen for business variables that change periodically (DJ's ask 2026-08-06). Config-backed (ir.config_parameter), each knob LIVE with a safe default. Frame + first two knobs shipped: Quiet hours + Days off. More (cooldowns, pricing, hours, forwarding #) to be wired one at a time."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T19:22:31.601Z
---

**DJ (2026-08-06):** wants ONE screen listing the important business variables that change periodically, instead of hardcoding them. Agreed architecture + built the frame + first two knobs.

## Architecture (the rule for adding more)
- **Screen:** `static/owner/v2_settings.html` (⚙️ Settings; launcher entry added to `v2_apps.js` → `/static/owner/v2_settings.html`). Served static like the other v2 screens.
- **Store:** every knob = an `ir.config_parameter` key. Code that consumes it reads the param **at runtime with the current hardcoded value as the fallback default** — so a blank/bad value NEVER breaks behaviour, and no redeploy is needed to change a value.
- **API (myday.py):** `GET /api/settings/get` (returns all current values), `POST /api/settings/quiet {start,end}`, `POST /api/settings/dayoff {date,off}`. Helper `_cfg_get(key,default)`. Secrets/keys deliberately NOT here (stay in Render env).
- **To add a knob:** (1) add the `ir.config_parameter` read (with default fallback) at the CONSUMER site, (2) add get/save to the settings API, (3) add the UI section. Only put a knob on the screen once it actually takes effect — no dead knobs.

## Knobs shipped
1. **Quiet hours** — keys `wsc.quiet.start` (allow-from, morning, default 8) / `wsc.quiet.end` (hold-from, evening, default 20). **Wired in `messaging.py`**: new `_quiet_bounds()` reads the params (falls back to the `QUIET_START_HOUR=8`/`QUIET_END_HOUR=20` constants if unset/invalid); `in_quiet_hours()` and `_next_window_start()` now use it. Validation: `0<=start<end<=24`. (Cosmetic follow-up: some UI strings still say "releases 8:00 AM" hardcoded — update if DJ changes it.)
2. **Days off** — key `wsc.capacity.overrides` (JSON dict date→capacity; per-date `<=0` = day off). This is the SAME store `shared.is_day_off()` already reads AND the **Work Hours screen** (`v2_workhours.html`) writes — single source of truth, my screen is the consolidated view. Settings shows only upcoming (`>= today`) dates with cap<=0. (Verified: DJ's existing 2026-08-06/07 Mexico days already appear.)

## Roadmap (candidate knobs, NOT yet wired — do one at a time, carefully; the last 3 touch shared/specialist code)
- Reactivation cooldown (365d) / follow-up cooldown (45d)
- Pricing rules ($85 floor / $70 no-inflation threshold)
- Business/working hours + working days; default appointment length
- Owner forwarding number (inbound-call ring target); from-email; service areas
- (Voicemail sweep time is EXCLUDED — it's a Render dashboard cron, not an app value.)

See [[project_day_off_capacity_block]] [[project_voicemail_to_vault.md]] and messaging quiet-hours hold logic.
