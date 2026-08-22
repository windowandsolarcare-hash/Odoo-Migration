---
name: project_ai_draft_from_conversation
description: "The '✨ Draft from conversation' AI feature — reads a customer's imported Workiz text history and has Claude write a contextual re-engagement/reactivation SMS in Dan's voice that picks up the thread seamlessly. Human-in-the-loop (drafts, never auto-sends). This is the message engine for the Outreach Campaigns window."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6f63b0d4-dd6a-4dd1-aac3-e533a99e7526
---

**Endpoint `POST /api/followup/ai_draft` (reactivation.py ~L874).** DJ's "read the last texts and pick up seamlessly — if they said 'I was on vacation', say 'hope you enjoyed your vacation'" idea IS BUILT and working. Confirmed 2026-07-06.

## What it does
- Resolves property→parent customer, reads their imported **`[workiz-history]` ir.attachment** (the real past SMS transcript, on res.partner), feeds the **last ~5000 chars** to **Claude** (`get_anthropic_client()`, model = `os.environ['CLAUDE_MODEL']` default **`claude-sonnet-4-6`** — could bump to a newer model for sharper drafts).
- Claude writes a SHORT SMS in Dan's voice that CONTINUES the thread. Returns a **draft for DJ to review/edit/send — NEVER auto-sends** (fits [[project_crm_outreach_loop_plan]]'s "I still want to say go" — one-tap approve, never fully hands-off).
- Pulls last Done job's `x_studio_x_studio_x_studio_job_type` → service angle (windows/solar/both) + property address + booking link (`_booking_link` = wscare.pro token).
- `flow='reactivation'` param adds an "it's been OVER A YEAR, acknowledge the gap warmly" note; default `flow='reengage'`.
- **No history → falls back to the static `_build_followup_sms` template** (button still works).

## The system prompt `_AI_DRAFT_SYSTEM` (reactivation.py ~L837) — smart behaviors
- **Anti-false-confirmation guard:** history is PAST record, NOT a live chat, NO upcoming appt — never echo an old "I'll be there at 9:30"/old quote as if current.
- **MODE A — CONTINUE** (recent thread shows they DEFERRED: "on vacation / call me when I'm back / not right now / next month"): do NOT re-pitch; warmly reference their last msg ("hope the trip was great — welcome back!") + a brief "ready whenever you are" bridge → booking block. ← DJ's vacation example, literally coded.
- **MODE B — BREAK THE ICE** (no recent discussion, long gap): ONE light reason — windows=desert dust "dulls the view", solar=dirty panels "cut your output".
- **Voicemail:** if they said they left a voicemail, it can't hear it → warm ack + **`NOTE TO DAN: listen to the voicemail first`** (returned as `heads_up`).
- **Unanswered question:** addresses it directly instead of a generic re-engage.
- **SAFETY:** blocks ONLY on a TRUE opt-out → returns **`DO_NOT_SEND: <reason>`** (endpoint returns `do_not_send:true` + reason; reeng_editor.js:143 shows 🛑 banner + HIDES the launch button). See the 2026-07-13 fix below — a polite "No thank you" is NOT an opt-out.
- Always ends with the verbatim booking block + "— Dan / Text STOP to opt out". First name only, no emojis, no hard-water-spots mention.

## Wiring
- UI = **"✨ Draft from conversation"** button in the shared **WSCReeng** widget (`reeng_editor.js` `draft()` L133 → posts to `ai_draft`). Handles `do_not_send` (🛑 don't send), `heads_up` (📞 note), else fills the editable Text-to-send box. Used wherever WSCReeng renders (My Day, field job menu, activities, reactivation).
- Returns: `{ok, sms_text, source:'ai'|'template', used_history, heads_up, do_not_send, reason}`.

## ★ DATE/RECENCY FIX (2026-07-07 — was a real bug)
The `ai_draft` user_msg originally passed the history with NO today's-date / last-service-date context → the AI treated the customer's LAST message as if it just arrived, even when it was a year old and already resolved by a completed job. E.g. Barbara Cameron (23013): her last "text" was a Jul-2025 voicemail that led to a Jul-10-2025 service; a year later the draft wrongly opened "thanks for calling — so glad you reached out!" **FIX:** ai_draft now prepends `date_context` = "Today is {today}. Their last COMPLETED service was {date} ({N months ago}). ★ JUDGE RECENCY BY THESE DATES … a call/message from months ago followed by a completed service is RESOLVED history, not a live request; don't say 'welcome back'/'thanks for calling' unless the LAST message is genuinely recent AND unaddressed." (last_service from the last Done SO's `date_order`.) Verified: Barbara's draft flipped to correct break-the-ice "it's been about a year since I cleaned your windows…". **Lesson: any AI that reasons over historical records MUST be given today's date + record dates, or it can't judge recency.**

## ★ LOCATION-AWARE MESSAGES (2026-07-08 — Hemet ≠ desert)
DJ caught a **Hemet** customer's re-engagement text saying "out here the desert dust piles on fast." Hemet/inland is NOT the Coachella Valley desert. FIX (reactivation.py): (1) `_build_followup_sms` picks the grime reason by area — desert customers keep "desert dust piles on fast"; Hemet/inland get "dust and water spots build up faster than you'd think." (2) ROOT CAUSE: the AI fallback called `_build_followup_sms(city='')` → defaulted to desert. Builder now RESOLVES city from the **PROPERTY** (`res.partner` child, `city` else `x_studio_service_area`) via `contact_id` when the caller passes none — city lives on the property, not the customer. (3) AI draft gets a `LOCATION:` note in user_msg + `_AI_DRAFT_SYSTEM` no longer forces "desert dust" (only if the location note says desert). Hemet detection = city contains hemet/san jacinto/valle vista/menifee/winchester/homeland. Verified: Trish (Hemet)=no desert; Adam Ruelas (Indio)=keeps desert. ★ Service area field = `x_studio_service_area` (the twin `x_studio_x_studio_service_area` is EMPTY — don't read it).

## ★ TONE: WARM, NOT SALESY (2026-07-08)
DJ on the standard `_build_followup_sms` template: "too salesy." He LOVES the AI-draft tone (warm, humble, low-pressure). Rewrote the 4 template variants to match: ONE light location-aware nudge, close with **"Whenever you're ready, I'd love to…"**. DROPPED: "easy to let slide", "dulls the view / looking dingy", "costing you a little every month", "Let's get them crystal clear again" (problem-selling + pushy CTA). Rule for any outreach copy: humble + low-pressure, at most one gentle reason, never sell the problem or push the close.

## ★ EXACT WORDING (2026-07-08 — DJ's final line edits, applies to Render Claude drafts too)
DJ dictated 4 wording fixes; BOTH the static template (`_build_followup_sms`, all 4 svc variants) AND the AI-draft booking block (`_AI_DRAFT_SYSTEM`) now use them. **Render Claude / the ✨ Draft-from-conversation AI must come back with messages that follow these — do NOT regress to the old phrasing:**
- "it's been **too long** since I…" → "it's been **a while** since I…"
- DROP the "**, and honestly that's on me.**" clause entirely (was on every variant).
- CTA header "**Grab a time here:**" → "**Schedule a time online:**"
- reply line "…and I'll **lock it in**." → "…and I'll **schedule it**."
Verified live on Trish (23589): "…it's been a while since I cleaned your windows at 8305 Bogey Ave. They're probably due for a refresh by now. Whenever you're ready, I'd love to get them looking great again. / Schedule a time online: {link} / Or just reply with a day that works and I'll schedule it."

## ★ AI DRAFT keeps slipping banned phrases → DETERMINISTIC FILTER (2026-07-09)
DJ flagged a reactivation AI draft (Dot Gallahan 23605) that STILL said "way too long, that's on me!" even after the template + prompt were fixed. TWO causes in the AI path: (1) `_AI_DRAFT_SYSTEM` MODE-B literally said `"that's on me" and "easy to let slide" are fine here`; (2) the reactivation-flow note (`reactivation_note`, ai_draft ~L964) literally instructed `Acknowledge the longer gap warmly (it's been way too long)`. Both fixed to say "a while" / forbid the phrases. **BUT the model still slipped ~1-in-2** (e.g. "that's on me for not staying in touch sooner!"). ★ LESSON: a system-prompt "don't say X" is NOT reliable for a phrase this natural to the persona — you must ALSO enforce it deterministically. Added **`_scrub_wording(t)`** (reactivation.py, applied to the `out` of `/api/followup/ai_draft` before return): regex-strips "too long"/"way too long" (→ "a while") and removes the "that's on me" self-blame clause while KEEPING the sentence's terminal punctuation (so grammar survives). Plus a top-of-prompt `BANNED PHRASES` line. Verified: 4/4 drafts clean + grammatical + short. If DJ bans another phrase, add it to BOTH the prompt AND `_scrub_wording`.

## ★ "No thank you" ≠ opt-out (2026-07-13 — DJ business rule)
DJ hit a red **🛑 Don't send — "Customer explicitly said No thank you… this is a clear opt-out"** banner on Edith Grossi and pushed back: a polite decline is NOT an opt-out. His actual model: he tells customers "I'll text you in 6 months — if the windows look fine to you, just say no thank you, and I'll text again in another 3-4 months." So "No thank you" = *not this cycle*, and these customers SHOULD keep getting re-engaged. ROOT CAUSE: the `_AI_DRAFT_SYSTEM` SAFETY line said block if the customer "**clearly does not want contact**" — too broad; the model read "No thank you" as that. FIX (reactivation.py `_AI_DRAFT_SYSTEM`, commit df7319d): SAFETY now blocks (`DO_NOT_SEND`) ONLY for a TRUE opt-out — DECEASED, texted STOP, or an explicit "never contact me again / stop contacting me / take me off your list / lose my number / leave me alone." Polite declines ("No thank you", "not right now", "not this time", "we're good this time", "maybe later", "the windows look fine") are explicitly listed as NOT opt-outs → write the normal SMS; "when in doubt, WRITE the SMS, do not block." ★ RULE: a real opt-out requires explicit never-contact language or STOP — declining one appointment never counts. (True STOPs are the 17 blacklisted — see [[project_stop_optout_true_count]].)

## ★ OPEN: CHANNEL-AWARENESS (call-only customers) — DJ flag 2026-07-07
Barbara is a PHONE customer — her entire text history is transcribed VOICEMAILS ("give me a call, I'm home"); she never types a real text (she does receive confirmation texts but replies by calling). The `x_studio_x_studio_ok_to_text` field exists on res.partner but is BLANK on 761/762 contacts (only 1 'Yes') — useless as a filter (same blank-contact-field trap as maintenance/frequency); nothing usable on sale.order either. So a text-only re-engagement flow aims the wrong channel at callers. PROPOSED (not built): (a) teach ai_draft to detect call-only patterns (all inbound = voicemails/call-me, no real text replies) → return a "CALL, don't text" flag → route to a 📞 Call task instead of a text; (b) a manual "call only" switch DJ can set. DJ's immediate concern was the DATES bug (fixed above); the channel routing is still open — decide whether to build.

## Snooze reflected in the customer brain (2026-07-07)
The customer-brain Outreach strip reads `GET /api/outreach/timeline` (reactivation.py) — SEPARATE from the Outreach-window lists. It now reads `x_snooze_until`: a snoozed customer shows **state='snoozed', 'Snoozed until <date>'** (icon ⏰ in field.html `_OUT_STATE_ICON`) instead of "Due to reach out". Priority: dnc > snoozed > booked > waiting > deferred > due. RULE: any new outreach filter (snooze/DNC/etc.) must be added to BOTH the window lists AND this timeline endpoint or the customer card drifts out of sync (this exact bug: Alona snoozed until Oct still showed "🔴 Due to reach out" on her card).

## Role in the CRM
This is the **message-generation engine for the "Outreach Campaigns" window** ([[project_crm_outreach_loop_plan]]) — it produces the "here's the exact text about to go out" that DJ reviews in show-me-everything mode, for BOTH re-engagement and reactivation. Nothing to rebuild; wire it straight in. See [[project_reengagement_logic]], [[project_reengagement_vs_reactivation]].
