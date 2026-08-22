---
name: project_morningnews_specialist
description: "Morning weather + national news card, LIVE 2026-07-27: routers/owner/specialist_morningnews.py. Daily attention card 'morningnews:<date>' (source=briefing so it groups under the HUD info/briefings pill) → /owner/api/morningnews/view: today's Hemet weather with a window-day read + top US national headlines. Weather=open-meteo, news=Google News RSS (both free, no key). Fires from cron daily_sync."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-27T10:43:34.590Z
---

**2026-07-27 — DJ: "morning news briefing... weather and real national news."** The app already had a MORNING BRIEFING (lead's `briefing.py`, ~6:30 AM push + HUD cards: today's jobs/$, My Day load, what needs OK, journal prompt) — but business-only. This adds the weather + news DJ wanted.

`routers/owner/specialist_morningnews.py` (registered main.py, cron hook in daily_sync). Endpoints: `GET /api/morningnews/data` (JSON), `GET /api/morningnews/view` (themed page: weather block + headlines, header/Back/launcher), `POST /api/morningnews/prepare` (manual fire). `run_morning_trigger()` submits ONE `morningnews:<date>` attention card, **source='briefing'** (groups under the info/briefings pill), urgency glance, expires next-day 1pm.

- **Weather** `_weather()`: open-meteo (free, no key) for Hemet base coords `_LAT,_LON = 33.7475,-116.9719`; current temp + daily hi/lo/wind/precip%. **Window-day read** (DJ works outdoors): 'Good window day' (clear, low wind, low rain) / 'Windy — mind the ladder' (wind≥20) / 'Rain in play — plan around it' (pop≥40 or rain codes) / 'Workable'.
- **News** `_news()`: Google News RSS top stories US (`news.google.com/rss?hl=en-US&gl=US&ceid=US:en`), regex-parsed top 6 {title, link, source}. Real national headlines (CNBC/AP/CNN/etc). Both guarded — one failing never breaks the card.

**Contract rule #0 (lead, DJ 2026-07-27):** card TITLE = stable/generic ("☀️ Morning weather & national news"), NO volatile data; weather + top story live in `why_now`. Same rule retro-applied same day to billing:review ("Past-due jobs to collect") + reschedule:review ("Jobs to reschedule") — customer names+amounts in why_now, dollars/badge carry the volatile numbers. Rule: anything that can change (counts, $) must NOT be in a card title.

Verified live: 74° Clear / Good window day + 6 real headlines. See [[project_digest_specialist]] (weekly), [[project_operating_system_vision]], [[project_attention_feed_contract]].
