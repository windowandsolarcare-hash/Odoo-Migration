---
name: project_thumbtack_automation
description: Thumbtack lead automation plan — Thumbtack HAS a partner-gated Pro API (leads + two-way messaging); built-in auto-responder is the quick win; computer-use (Claude in Chrome) to configure it.
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-19T00:09:44.782Z
---

**DJ wants to stop hand-dealing with Thumbtack leads.** Researched 2026-08-18. Two paths:

**1. Quick win (do first): built-in Thumbtack auto-responder.** Pro app → Settings → Auto responses. A templated first message that fires instantly (speed-to-lead against the other pros). Dumb — same text to everyone, can't quote the actual price. **Plan: set it up via computer-use** (Claude in Chrome) when DJ is at his desk + logged into Thumbtack — I screenshot each screen, read on-screen instructions, click/type to fill the auto-responder(s). DJ watches; needs desktop Chrome + Thumbtack login + grant extension permission on thumbtack.com.

**2. Durable win: Thumbtack Pro API (it EXISTS).** Thumbtack launched a **Pro API** — partner-gated **OAuth 2.0 REST**, at developers.thumbtack.com. The **Leads/Negotiations API is webhook-based** and does exactly what we need: **real-time lead delivery + two-way messaging** (read the lead AND reply back INTO the Thumbtack thread programmatically). Delivers name/email/phone/custom form fields (e.g. panel count). This is BETTER than parsing lead emails and BETTER than texting from DJ's phone: reply stays on-platform → **no phone number, no A2P/10DLC setup needed** for the Thumbtack side (which was DJ's exact concern). **Catch: partner-gated — must APPLY/get approved; aimed at CRM/tool partners, so whether a solo pro qualifies is the open question to verify at developers.thumbtack.com.** If approved → build an auto-quoter: lead webhook → AI reads panel count → sends the right tier price → posts to thread (DJ approves or auto-send).

**Why NOT text from DJ's own phone/app:** (a) A2P consent basis differs — his campaign was approved on the website opt-in checkbox, NOT Thumbtack leads; (b) Thumbtack prefers on-platform comms. Keep Thumbtack replies inside Thumbtack.

**Solar quote tiers (from the $125 lead):** 11–20 panels = $125. (Confirm full tier table with DJ before automating.)

**Status:** parked until DJ is at desk (computer-use setup of built-in auto-responder). API access application = not started. See [[project_twilio_a2p_and_entity.md]].
