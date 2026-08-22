---
name: project_cheryl_role_ai_front_office
description: "DJ decision 2026-08-03: Cheryl leaves real estate entirely and takes the customer/money-facing side of the EXISTING businesses (not a new venture); AI = the front office, Cheryl owns exceptions + approvals. Auth flip is the blocker."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8f0313dc-02cc-482c-833a-0ab0d7a6b313
  modified: 2026-08-03T10:23:29.024Z
---

**DJ decision, 2026-08-03.** Cheryl wants **out of real estate entirely**. DJ's chosen direction:
**not a new venture** — she takes over the **customer-facing and money-facing side of the
businesses he already owns** (reactivation follow-through, quotes, collections, scheduling,
Saunders back office), so he stops being the bottleneck on two businesses instead of becoming the
bottleneck on three. Rejected alternatives (discussed, do not re-pitch without new information):
- **Real estate transaction coordination** — was the best fit for her documented skills, killed by
  "out of real estate entirely."
- **Bookkeeping / back-office service** — viable and matched her profile, but it is a NEW business
  needing 6-9 months to income; DJ chose the existing-businesses route instead.
- **AI front desk / missed-call text-back product** — was set aside because the sales motion is
  cold outbound; ★ RE-OPENED by the 2026-08-03 correction below (she does sell). Remaining real
  objections are unchanged though: crowded category, brutal SMB churn, per-client A2P registration
  pain, and every support call lands on DJ.
- **Growing Saunders Printing** — was set aside on a WRONG premise; see the correction below.
  ★★ **CORRECTED BY DJ 2026-08-03: "Cheryl is good at sales, can pick up the phone."** The 2026-04
  interview note (*"She is NOT focused on lead gen / mass marketing"*) described her PRIORITIES as a
  solo agent serving active clients — it is NOT a statement that she cannot or will not prospect.
  **Do not read that note as "Cheryl won't hunt."** DJ is the authority on this and says she sells
  and will work the phone. This RE-OPENS every option that was rejected for needing a hunter
  (Saunders growth, the AI front-desk product).

**DJ's stated vision:** *"I want AI to be my front office. To handle much of that, and maybe there
is a role for Cheryl in overseeing and approving AI work."*

**★ This is already 80% architected — the Attention Feed IS the AI-front-office pattern.**
Specialists produce work + a draft + a one-tap execute endpoint; a human approves; the HUD renders
the queue. ATTENTION_FEED_CONTRACT hard rule #1 already says customer-facing output is ALWAYS
`kind:approval`. `authz.py` already defines a **`cheryl` role** alongside owner/tech, and Odoo
already carries `x_render_role` (owner/tech/cheryl) + `x_render_business`. The seat was provisioned
before anyone asked for it.

**THE THREE BLOCKERS (handed to the auth-owning session via AGENT_MAIL 2026-08-03):**
1. **`AUTH_ENFORCE=1` is still unset** — auth is in monitor mode, 47 would-block patterns need
   whitelisting first. Until flipped, a "Cheryl login" is decorative: anyone with the URL has
   everything. See [[project_authz_block_b]].
2. **`feed.py` `api_feed_ack` records NO approver identity** (status + timestamp only). Fine with
   one user; unacceptable once two people can approve payments/refunds/customer texts. Add the
   session user at the same time enforcement lands (the cookie is what makes identity available).
3. **The trust dial was never built** — the contract promises duties "graduate to auto" but no
   mechanism exists.

**★ THE DESIGN RULE DJ AGREED TO (most important thing here): the approval queue must SHRINK as
trust grows, not GROW as duties are added.** "Cheryl approves AI work" is only a real job if the AI
escalates **selectively**. Route everything to her and you have not removed labor, you have
relocated it — and approval queues rot: a human facing ~40 near-identical approvals a day stops
reading and starts clicking, producing oversight theater that is *more* dangerous than no review
because everyone then trusts a rubber stamp. Every duty needs a path
**always-ask → ask-when-unusual → did-it-FYI**. A duty that never graduates is not automation, it
is a checklist with extra steps. Early symptom already observed: specialists flagged 2026-07-27
that passive `billing:<so>:waiting` trackers were landing in "Needs you" and inflating it to 13.

**Cheryl's actual job (NOT rubber-stamping):** own the ~10% of exceptions AI escalates; own the
human relationships (the upset customer, the payment plan, the call that shouldn't be a text); be
the second signature on money; and decide when a duty has earned graduation (a risk judgment, which
is the part that does not automate). AI is genuinely good at drafting, chasing, reconciling,
summarizing, routing, scheduling — most of a front office by volume. It is not good at ambiguous
money decisions, relationships, or anything expensive and hard to walk back.

**Also established in the same conversation (Saunders Printing reality check):** print brokering
has no moat (Zoo/4over sell to anyone), the industry is in secular decline, and NBHOF is 100% of
revenue — a contract, not a business. Odoo shows only ~$25.5K ever invoiced, **$13,873 of it
sitting in DRAFT (never posted)** and all 5 posted invoices ($11,636, May 9–Jun 26) showing
**not_paid**, plus **zero vendor bills** so gross margin is literally unknown. The web-to-print
storefront plan in [[project_saunders_printing]] should be considered **killed** — it competes with
Vistaprint/4over-retail on paid acquisition where CAC exceeds lifetime margin. If Saunders is grown
at all, the play is cloning the NBHOF profile (museums, halls of fame, historical societies, minor
league clubs, visitor centers — institutions with gift shops, recurring reorders, no in-house print
buyer). ★ That play needs a hunter — which the 2026-08-03 correction says Cheryl IS, so Saunders
growth is BACK ON THE TABLE and is arguably the strongest option: existing entity, a marquee
reference account (printing for the Baseball Hall of Fame opens museum doors), automation already
built, and the ONLY missing piece was someone to work the phone. Open question DJ raised the same
day: whether FULFILLMENT is allowed — if it is, the better business is "institutional gift-shop
supplier" (postcards, magnets, bookmarks, posters, apparel, mugs) rather than commodity print
brokering: same buyer, same door, better margins, recurring reorders.

**Why:** locks a real business decision plus the reasoning behind three rejected alternatives, and
records the design rule that keeps "AI front office" from becoming a bigger manual queue.
**How to apply:** Cheryl-fronted businesses MAY require outbound sales — she sells and works the
phone (corrected by DJ 2026-08-03; the old interview note is about priorities, not capability). Also
OPEN per DJ 2026-08-03: fulfillment is not necessarily excluded — do not assume a no-fulfillment
constraint without asking. Do NOT add
front-office specialists before the trust dial exists, or the queue grows faster than the help.
Sequence: flip auth → approver identity in feed ack → trust dial → then move duties over one at a
time, each starting at full approval.
