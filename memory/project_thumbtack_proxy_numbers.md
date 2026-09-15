---
name: project_thumbtack_proxy_numbers
description: "★ AUTHORITATIVE Thumbtack rules (DJ 2026-09-12, do not re-debate). TT gives only NAME + CITY (no real contact); the lead phone is a TT PROXY that routes THROUGH Thumbtack (our registered Twilio reaches it). REFUND: only if the customer contacts NO pro within 72h; ANY reply to ANY pro kills it; AND including YOUR phone number in a response within the first 72h forfeits the refund. After 72h + engaged: get the real phone+address, then real number becomes primary (TT proxy → secondary)."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-12T06:01:59.080Z
---

**★ DJ stated these as AUTHORITATIVE on 2026-09-12 and asked they be documented so they are NOT re-debated. They ALTER how we respond to Thumbtack leads.** (Supersedes/refines the Aug-21 notes below.)

## How Thumbtack works now (the rules that govern our reply flow)
1. **TT gives only the customer's NAME + CITY — no real contact info.** The phone that arrives on the lead is a **Thumbtack PROXY number** (masked, pooled — Alabama 256-area pattern, e.g. jo raff `256-663-5812`, Bob Lis `256-645-4462` — NOT the customer's real cell). Thumbtack wants **all correspondence through their platform.**
2. **The proxy routes THROUGH Thumbtack** — and our app's Twilio number is **registered to the Thumbtack account**, so `messaging.send` to the proxy DOES reach the customer and their replies thread back. So "text the lead number → it goes through TT" is CORRECT. (Don't repeat the 2026-09-11 mistake of calling it the customer's real cell / a direct off-platform text — it's the proxy.)
3. **REFUND rules (why the reply wording matters):**
   - Thumbtack refunds the lead fee **only if the customer contacts NO pro within 72h.** The customer just has to reply to **ONE** pro (any pro, incl. a competitor) and **no refund is available to anyone.**
   - **★ If YOU include your phone number in ANY response within the first 72 hours, the refund is OFF the table** — permanently, for that lead. So **within the first 72h, our reply must contain NO phone number** (and don't push off-platform / don't ask for their real number before they've engaged — same forfeiture risk).
4. **After 72h, if the customer has reached out:** the goal is to get their **REAL phone number + address**, then move correspondence to the real number.
5. **System data model:** when a lead is created, the **TT proxy number is PRIMARY** (the phone on the record). **When the customer gives their real number, the real number takes over and the TT proxy moves to SECOND position.**

## What this means for the build (correction to the 2026-09-11 TT reply flow)
- The Claude-drafted reply → text is right, and it goes THROUGH TT via the proxy. BUT:
- **★ WITHIN 72h the reply must NOT include the WSC phone-number signature** (the Twilio funnel auto-appends Dan/Window & Solar Care/phone — that phone in the body would FORFEIT the refund). The Thumbtack-reply send path must **strip the phone/signature during the 72h window**, and the draft itself must not include a number or ask to go off-platform.
- After 72h + engagement: capture real phone+address; swap real→primary, proxy→secondary.

## Still-true operational facts (from 2026-08-21, DJ-corrected)
- EMAIL is separate — the proxy is text/call only; a real EMAIL is still needed for email pay-links/invoices.
- Proxy numbers are **pooled + recycled** (Twilio-masking) — "permanent WHILE the Thumbtack account is ACTIVE," not forever. If DJ pauses/cancels Thumbtack, proxies stop routing and get reassigned. ⇒ the proxy is a free channel we don't OWN. **Before ever winding down Thumbtack, sweep to capture REAL phone+email for all TT customers** so none go dark. This is the reason to convert TT leads to our own contact info over time.
- Reference: Bob Lis person 27192 / property 27193, proxy `2566454462`. jo raff (2026-09-11) proxy `2566635812`, Yucca Valley 92284, window cleaning.

Related: [[project_thumbtack_lead_webhook]] (Phase 1/2 webhook), [[project_thumbtack_automation]], [[feedback_dj_operating_instincts]] (reply tone).

## ★ THE 3-STEP REPLY WORKFLOW (DJ 2026-09-15, AUTHORITATIVE — put in a note; CHANGES our first-reply flow)
DJ clarified the correct Thumbtack contact sequence:
1. **FIRST/INITIAL contact MUST go through THUMBTACK'S OWN APP** (thumbtack.com/pro/messages), NOT our system. ★ WHY (DJ "just learned this"): Thumbtack runs a **RESPONSE TIMER** — a reply sent through OUR system does NOT trigger/satisfy their timer, so Thumbtack keeps nagging "get back to this person." The first **in-app** response is what stops their clock. So on a new lead our app must **NUDGE DJ to respond IN THUMBTACK first** (primary action = "Respond in Thumbtack"), NOT auto-send the first text via our proxy send-path. ★ This CORRECTS the earlier build where the first draft could send via /owner/api/thumbtack/reply — that send does NOT satisfy the TT timer.
2. **AFTER the initial in-app contact:** DJ can run correspondence through OUR app via the **PROXY** number (messaging.send to the proxy threads back through Thumbtack) — this is where our two-way inbox channel matters.
3. **THEN convince the customer to give their REAL phone + address** → from that point schedule through our system to the real number (real→primary, proxy→secondary). Everything flows through our system after that.

## ★ THE GAP (DJ 2026-09-15) — webhook fires on the new lead then DIES
The webhook launches on the NEW LEAD (NegotiationCreated) and there's "no further connection" — verified: 5/5 raw_log entries are NegotiationCreated, ZERO message/reply events; and Ann Cates's reply ("her husband responded") is NOT on our side — it's stranded in the Thumbtack app. DJ expects a TEXT to also reach our app (via the proxy) opening the two-way channel. TO CLOSE: (a) check the TT webhook config (leads-only vs +messages), (b) verify inbound proxy SMS threads into our inbox, (c) build capture of TT MESSAGE events → our inbox (step 2), while step-1 nudges "Respond in Thumbtack." NOTE: "Kate" = **Ann Cates** (surname ≈ "Kate's"), proxy 2566638203, lead 453.
