# Claude Code - Project Instructions
**Last Updated:** 2026-08-18
**Migration:** Cursor → Claude Code (permanent)

---

## 🛑 WORKIZ IS RETIRED (went dark 2026-08-03) — READ THIS FIRST

**Workiz no longer exists in the loop. Odoo is the SINGLE SOURCE OF TRUTH for jobs, schedule, status, and payments.** The Workiz API is dead — any call to `api.workiz.com` returns 401/errors, and that is EXPECTED, not an outage. Do NOT raise alarms about "sync being down," and do NOT propose fixes that "duplicate in Workiz," "set status in Workiz," or "sync from Workiz."

- **Everything below in this file that describes Workiz as live is LEGACY** — the Zapier Phases (3/4/5/6), the Workiz API sections, "the schedule" Workiz-status gate, the Workiz status/substatus rules, the reactivation-via-Workiz flow. Kept for history/reference only. Do not act on them as current behavior.
- **What replaced it (all Odoo/app/Twilio-native, already built):** jobs are created directly as Odoo SOs (New Job → `new_job.py`); **duplicate a job = the Odoo-native "Duplicate job" in Customer Brain** (📋 Create as Submitted / 📅 Create & Schedule) — NOT Workiz; scheduling/reschedule is Odoo-native; customer texts go via **Twilio `messaging.send`** (number ported ~2026-07-30).
- **TWO senses of "done" — keep them straight (Portal flagged 2026-08-18):** *service happened* = `x_studio_x_studio_workiz_status == 'Done'` (what the customer portal / history / due-math read); *job closed out* = **PAID IN FULL** (`_execute_payment` writes status Done + spawns the next maintenance SO). A customer who hasn't paid still had their windows cleaned — their portal must still show that visit. Don't let one definition overwrite the other in code.
- **`x_studio_x_studio_workiz_status` is NOT vestigial — it is the LIVE status field** (Odoo-native now, still actively written; only the *name* is legacy). **Rule 2 stands: "Done jobs" = `workiz_status == 'Done'`.** Do NOT "clean it up" as part of Workiz removal. Truly vestigial (history-only): `x_studio_x_studio_workiz_uuid/_link/_tech`. Legacy `if(uuid ...)` UI gates on Odoo-native jobs are a known recurring bug class — don't trust a missing UUID as "not a real job."
- **SO names post-retirement:** new SOs may carry Odoo-default names (`S00192`, `S00218`) alongside the migrated 6-digit form (`003575`) and the new `_next_job_name` YY-counter form (`264938`). **Match SO names EXACTLY — never zero-pad a guess.**
- **Full detail:** memory `project_workiz_retirement.md` + `WORKIZ_RETIREMENT_INVENTORY.md`. Migration is role-by-role; some touchpoints may still be mid-transition — verify against current code, never assume Workiz is live.

---

## ☁️ CLOUD SESSIONS — HOW TO READ YOUR MEMORY (2026-08-22)

**If you are a CLOUD Claude Code session** (running against the GitHub repo on an Anthropic-hosted machine, NOT DJ's local Surface Pro): your memory does NOT auto-load, and the local path `C:\Users\dj\.claude\...\memory\` does NOT exist here. Your full memory lives IN THIS REPO at **`./memory/`** (mirrored from local, kept in lockstep). At session start: read **`memory/MEMORY.md`** (the index + standing rules), then open the relevant **`memory/idx_*.md`** domain shard or `Grep` the `memory/` folder for your topic — same content a local session gets auto-loaded. Also read `3_Documentation/SHARED_MEMORY.md`, and for fleet mail read `saunders-render-app` → `3_Documentation/AGENT_MAIL.md`. When you write a new memory, write it to `./memory/` in THIS repo (a cloud session's commit IS the mirror — no separate push needed).

**Cloud operational facts (found 2026-08-22, verified by cloud-Portal):**
- **`gh` CLI is NOT installed in cloud shells.** Push via the **GitHub MCP Contents API** (same Contents PUT `gh api` does — satisfies the `main` ruleset). The "gh api to main, never git push" rule is unchanged; only the tool differs.
- **★ CORRECTED 2026-09-02 — cloud outbound network is NOT GitHub-only on the current env.** The old claim here (that `wscare.pro`, `wsc-field-assistant.onrender.com`, and `window-solar-care.odoo.com` all 403 at the proxy) has now been **disproven three times** — most recently by the Lead-2 cloud session, which tested it live: a cloud session CAN hit the app, verify by content, and query Odoo. The allowlist was opened back on ~2026-08-22. **So before ANY session tells DJ "I can't smoke-test / can't reach Odoo because I'm in the cloud," it must actually TEST the call first — don't declare the limit from this doc.** (Root cause of the repeat: sessions read this header bullet and not the corrected body — hence the correction is now IN the bullet.) See [[feedback_verify_limits_before_declaring]].

---

## START HERE

**This file is the single source of truth for new sessions.** CLAUDE_CONTEXT.md and MASTER_PROJECT_CONTEXT.md are deep-reference only — do NOT require reading at session start. Everything critical is in this file.

---

## BEHAVIORAL RULES — READ BEFORE DOING ANYTHING

These rules exist because they have been broken before. Each one caused a real problem.

1. **Never guess at Odoo field names OR system formats.** Before using any field, ID format, or system constant: check the ODOO CUSTOM FIELD NAMES table and SYSTEM CONSTANTS table below, then memory files, then query Odoo directly. Never infer formats from training data or patterns — this system has specific formats that differ from Odoo defaults. Examples of past guessing failures: assumed SO names were `S00123` (they are `003575` — 6-digit zero-padded, no prefix); assumed `account.payment` had a `ref` field (it doesn't in Odoo 19); assumed `commercial_partner_id` exists on `sale.order` (it doesn't).

2. **"Done jobs" = `x_studio_x_studio_workiz_status = 'Done'` only.** Never use `state`, `invoice_status`, date filters, or `invoice_ids` as a proxy for job completion.

3. **Emails always via Odoo `mail.mail` JSON-RPC.** Gmail MCP can only create drafts — it cannot send. Pattern: create `mail.mail` record, call `send()`. Returns None = success.

4. **Architecture hard limits — no exceptions:** No new Odoo seats (cost money), no custom models (SaaS blocks without support), one Odoo instance (window-solar-care.odoo.com), all features must scale across businesses.

5. **Read relevant memory files BEFORE acting** — not after something breaks. Before any GitHub deployment: check `feedback_github_deployment_bash.md`. Before using an Odoo field not in the table below: check memory files. Before touching payment/invoice code: check `project_invoice_qty_delivered_gate.md` and `project_phase4a_sync.md`.

6. **GitHub deployment: bash + base64 + temp file. Never PowerShell ConvertTo-Json.** Short version: use `safe_deploy.py` for `dashboard.py` and any file >1000 lines. Use `deploy_to_github.sh` for everything else. Full detail in GITHUB DEPLOYMENT WORKFLOW section below.

7. **Confirmation policy:** Do not ask for confirmation on routine tasks — just do them. Only stop and confirm before irreversible or destructive actions (deleting files/branches, force push, dropping data, actions visible to others).

8. **Odoo is multi-company — always filter by `company_id`.** Three companies share one Odoo instance: Window and Solar Care (1), Cheryl Johnson REALTOR® (2), Saunders Printing (3). Any financial query (invoices, payments, journal entries, expenses) MUST include `['company_id', '=', 1]` when working on W&SC. Omitting this filter will silently mix in Saunders Printing or Cheryl Johnson data. Confirmed 2026-06-05 when Saunders Printing invoices appeared in W&SC revenue report.
   - **`res.partner` CUSTOMER searches** (any `name ilike` / `phone like` list DJ browses — New Order/New Job pickers, Customer Brain `search_customers`, Vault `search_customer`, payments/customer lookups, etc.) MUST include **`['company_id', 'in', [1, False]]`** — NOT `= 1`. ★ W&SC customers are NOT tagged company 1: they are almost all `company_id = False` (shared/unstamped from the migration); only ~103 are stamped 1, vs ~1566 shared. Cheryl (2) has 314 stamped contacts, Saunders (3) has 1. `= 1` would hide nearly every real W&SC customer; `in [1, False]` keeps W&SC (stamped + shared) and drops Cheryl/Saunders. res.partner is NOT auto-isolated by Odoo (DJ's user has all 3 companies), so EVERY customer-list search needs this leaf. Added 2026-07-03 after Cheryl's clients appeared in the New Order picker. See [[project_new_order_parked_surfacing]].

9. **Repetition is a design smell — STOP and ASK, don't grind. This is the single most important judgment rule.** When a task has you making the SAME change in many places ("update all the V1 pages," "apply this to every page," "roll this format out"), the instant you notice you're on the 2nd–3rd near-identical edit, STOP. Identical code repeated across N files is the loudest possible signal that the thing should be ONE shared source, not N copies. Ask DJ one quick question first — *"this is duplicated across N files; want one shared file they all call, instead of N hardcoded copies?"* A ten-second question beats the alternative every time. **Real incident (2026-07-22):** DJ asked to update all V1 pages to the agreed V2 launcher format; a single session hardcoded the same floating launcher into **34 separate pages** — while just "executing the task" — instead of proposing a shared file. DJ (correctly): *"caught in the rhythm of executing the task instead of seeing the big picture."* See [[feedback_question_when_big_picture_wrong]] and [[project_v2_launcher_duplicated_stale]].
   - This does NOT conflict with rules 10–11 (never remove/rewrite working code; surgical edits only). Those govern *how* to touch existing logic. THIS governs *raising a structural concern before* a large repetitive task. When the big picture looks wrong, the right move is **neither** "mechanically duplicate" **nor** "unilaterally refactor working code" — it is **ASK which one DJ wants.** Executing a task correctly at the line level while the overall structure is wrong is still a failure. Judgment (question the shape of the work) outranks throughput (finish the edits). A quick question is nearly free; damaging or bloating working code across dozens of files is expensive to undo.

10. **WE WORK ON V2 FILES ONLY. Most owner screens were migrated to a "V2" redesign (`static/owner/v2_*.html`), and the V2 file is what DJ's daily launcher actually opens — so the matching legacy non-`v2_` file is DEAD to us unless proven otherwise.** Before editing ANY owner screen: check whether a `v2_<name>.html` twin exists. If it does, edit the **V2** file — editing the legacy twin means DJ won't see your change (burned 2026-07-30: added an "Edit prices" link to `quote.html`, but DJ's launcher opens `v2_quote.html`). Two launchers coexist and this is the tell: the OLD `ql_panel.js` (single-column quick panel) sits on legacy pages; DJ's REGULAR launcher is the v2 **WSCLauncher** (`v2_apps.js`, the 🚀 FAB with **★Favorites / All** tabs) and it links to `/static/owner/v2_*.html`. Known holdout NOT yet on V2: **`field.html`** (the field assistant — big/complicated, deliberately still V1; it has no V2 twin, so it is NOT a legacy file to remove). When in doubt which file a launcher opens, grep `v2_apps.js` for the app's href before assuming. See [[project_two_quote_pages_two_launchers]] and [[project_v2_launcher_duplicated_stale]].

---

## AGENT MAIL — CROSS-SESSION MESSAGES (DJ approved 2026-07-26)

### ★ HYBRID protocol (DJ approved 2026-09-03) — direct message = FAST LANE, mail = SYSTEM OF RECORD
DJ asked why we wait on a 20-min poll when sessions can message each other directly. Both, each for its strength:
- **`SendMessage` (direct)** — instant + event-driven (no polling cost). Use for anything **time-sensitive to a LIVE session** (e.g. catching a reversal before another session ships). Only reaches live sessions; **cloud sessions are one-way** (receive, can't reply back); target by current session name (IDs churn).
- **`AGENT_MAIL.md` (the file)** — the **durable system of record**: survives restarts/offline (role's mail waits until whoever plays that role reads it), **role-addressed** (survives session-ID churn), broadcastable (→ All), carries the **✅ handled-ledger**, DJ-readable audit trail. Reliable catch-all.
- **Time-sensitive AND important → do BOTH** (direct for speed + mail for durability/ledger).
- **The watcher is now the SAFETY NET** (catch offline mail + keep the ledger), not the urgent path — so it no longer needs to poll often. Full detail: memory [[feedback_agent_mail_autowatch]].

Two Claude Code sessions work this project (a lead session and a specialists/PM session).
**At session start AND after finishing any task, read `3_Documentation/AGENT_MAIL.md` in the
saunders-render-app REPO** (fetch via gh api — it lives there because both sessions read that
repo; the local Odoo-Migration copy is just a pointer). Also read that repo's
`3_Documentation/SHARED_MEMORY.md` — the specialists session posts durable notes there.
When you have something for the other session, APPEND an entry there (newest on top) instead of
giving DJ long text to relay — DJ's nudge is the single word "mail" = go check the file. Mark
entries HANDLED when done; prune handled entries older than ~a week. Long-form content still goes
in its own doc (`*_BRIEF.md` / `*_STATUS.md`); mail entries just point to it. Decisions, approvals,
priorities, and anything customer-facing or money-touching still go through DJ.

### ★ AUTO-WATCH — ARM YOUR MAIL WATCHER AT SESSION START (DJ 2026-08-17: kill the manual "mail" relay)
So DJ no longer has to nudge "mail," each session watches its OWN mailbox. **At session start, arm your watcher if it isn't already** (check `CronList`): capture the current `AGENT_MAIL.md` blob sha (Contents API `.sha`, NOT the commit sha) to `/c/Users/dj/agentmail_lastsha_<lead|specialists>.txt`, then `CronCreate` a recurring **20-min** job (`*/20 * * * *`, but OFFSET your minute so sessions don't all fire together — Lead `3,23,43`, Specialists `8,28,48`, Web `13,33,53`, Portal `18,38,58`, Operator `1,21,41`, Design `6,26,46`) — **20-min per DJ's 2026-09-03 decision (was ~15/7; interval raised to cut usage)** — whose prompt: reads that baseline, gets the live `AGENT_MAIL.md` blob sha, and if changed **scans the WHOLE active section for EVERY non-`✅` heading addressed to you** (`→ <your role>`/`Both`/`All`, From≠you) and handles them **OLDEST-FIRST (bottom-up)** — NOT just the newest (with 20-min ticks and several sessions, items pile up and one meant for you can be buried below newer entries for other roles). For each: act + mark `✅`; if `→ DJ` and not `✅`, `PushNotification` DJ a one-line summary. **The `✅` marker is the ledger — an entry is done only when its addressee marks it `✅`; ONLY `✅` entries are pruned (handled + >~1wk); NEVER prune an unhandled entry, so the furthest-back survives until handled.** Push the mark back with **compare-and-swap** (PUT with the sha you read at; 409 → re-read + re-apply). Then store the new sha. **Also: whenever YOU post a `→ DJ` entry, `PushNotification` DJ immediately.** Full protocol: `3_Documentation/AGENT_MAIL_PROTOCOL.md`. (Watcher is session-local — dies on exit, auto-expires 7 days — hence re-arm every session start. A 24/7 version would live in the Render app; not built.) Address every entry `→ Lead|Specialists|Web|All|DJ` and mark `✅` when handled.

**★ SESSION ROSTER (6 roles as of 2026-09-02).** Each session has ONE role + its own watcher baseline file `/c/Users/dj/agentmail_lastsha_<role>.txt` and signs mail with its name. When DJ asks "who are you?", state your role.
- **Lead** — PURE OVERSEER (does NOT hand-write feature code): orchestrates all sessions, owns the DESIGN/specs + cross-stream continuity + brand consistency + the domain/DNS seams, QCs every stream, and runs independent fresh-eyes reviews (throwaway reviewer agents) at each launch gate. **★ ONE live Lead at a time** = the session DJ is interactively driving. (History: an interim Lead covered the 2026-08-30 power outage; on 2026-09-03 DJ confirmed the single live Lead and re-designated the other Lead(local) session as the **Audit** role below.)
- **Audit** — a dedicated independent **fresh-eyes reviewer** (re-designated from the ex-second-Lead on 2026-09-03). Reviews the app / current branch for bugs, regressions, gaps, and stale docs; reports findings **→ Lead** (worst-first) and does NOT fix unless Lead asks. Signs mail `Audit`, watches **→ Audit / → All** (baseline `/c/Users/dj/agentmail_lastsha_audit.txt`), and does NOT act as Lead (no sweeping/QC-marking the Lead mailbox, no directives). This keeps one director (Lead) and one auditor.
- **Specialists** — owns all existing Render APP code incl. `ideas.py` / the Idea Board "brain" (remaining phases) + the Cheryl push layer. Nobody else edits ideas.py.
- **Web** — owns the public marketing website (Odoo website module) at wscare.pro. Touches no app code.
- **Portal** — owns the NEW customer portal (new app files: `routers/owner/portal.py` + its static + magic-link auth). Coordinates with Specialists on additive shared touches (e.g. main.py router registration).
- **Operator** — DJ's execute-only "hands": performs live operations (create/schedule jobs, send confirmations, record payments, add contacts/properties, lookups) STRICTLY via the app's own HTTP endpoints — NEVER codes, plans, builds, or raw-writes Odoo. Charter: `3_Documentation/OPERATOR_CHARTER.md` (app repo). Hands any build/new-endpoint need to **Lead**. See [[feedback_assistant_use_app_workflow_not_raw_api]] + [[project_new_job_via_app_endpoints]].
- **Design** — owns the visual design pieces: creates/edits **design canvases** (postcards, flyers, marketing + social graphics) BY CONVERSATION on the `/design` canvas — always republishing to the SAME artifact URL so DJ's/Cheryl's link never changes — and writes the **Midjourney prompts** for their imagery. Users are **DJ and Cheryl** (Cheryl is non-technical — plain language, never made to learn a tool). NOT a coder, NOT an operator. Charter: `3_Documentation/DESIGN_CHARTER.md` + current-state `3_Documentation/DESIGN_SESSION_HANDOFF_BRIEF.md` (app repo). The **local** Design session is the authoritative actor; if it's live, cloud Design stands down. Key fact: the design canvas CAN produce a true 300-DPI press file (PNG export is 1:1 with artboard px) — this overrides the `/design` skill's "96-DPI proof-only" line.
`→ All` = every role (Lead, Specialists, Web, Portal, Operator, Design, Audit). Keep file ownership clean (one owner per file) — that is how we avoid the collisions we hit on 2026-08-17 (and the two-Lead collision closed 2026-09-03).

**★ ASK DJ DIRECTLY for anything only DJ knows (DJ 2026-08-18).** For information ONLY DJ has — content (reviews to feature, photos), business facts, preferences, account details — **any session asks DJ DIRECTLY: post a `→ DJ` AGENT_MAIL entry AND `PushNotification` him** (it reaches his phone even when it returns "not sent"), and if you're actively in conversation with DJ, just ask him in-chat. DJ answers that session directly. **Do NOT route DJ-only questions through Lead** (no "Lead asks DJ then relays the answer" — that's a needless hop). Lead is for cross-stream seams, architecture, and QC — not a relay for DJ's answers. (Lead may still surface things it notices, but sessions own their own DJ questions.)

**★ NEVER IDLE WAITING ON DJ (DJ 2026-08-18).** DJ is often in the field. If his input is strictly REQUIRED to proceed on a task, ask him directly (→ DJ + push) — then **move on to your other work while you wait.** If the input is something that CAN wait (a nice-to-have, a review, a content piece), **PARK that one item** (note it as "waiting on DJ" in mail) and **keep building everything else.** Never stall the whole workstream on a single DJ answer when there is other work you own. Maximize forward progress; DJ catches up on parked items when he's free.

**★ END-OF-TURN "OVER" STATUS (DJ 2026-08-18) — every session, every turn.** So DJ can tell at a glance which sessions are free to talk to (walkie-talkie "over"), the **VERY LAST LINE of every reply** is a status line:
- Done & idle, ready for DJ → `🟢 <Role> — OVER` (may add a few words, e.g. `🟢 Web — OVER (site done, waiting on your photo pairs)`).
- Still working / a background task is running / you'll produce more without DJ → `🟡 <Role> — working`.
`<Role>` ∈ Lead / Specialists / Web / Portal. DJ scans: **🟢 = channel open, reply to me; 🟡 = still working, stand by.** Put it on EVERY reply from now on (including watcher ticks). It is always the last line.

---

## QUICK REFERENCE

**Project:** Workiz ↔ Odoo sync for Window & Solar Care
**Owner:** DJ Sanders
**Repo:** windowandsolarcare-hash/Odoo-Migration (main only)
**Deploy:** `gh api` to push files - NO git commands

---

## 💳 PAYMENT LOOKUP — "did X pay / how did X pay?" — READ BEFORE ANSWERING

**Never answer a payment question from Odoo alone.** Two documented gaps make Odoo show "unpaid" when the customer actually paid by card. Answering "not paid" without checking Stripe = a WRONG answer (happened 2026-09-02 with Robert Hollenbeck, who had in fact paid $150 by Visa — Stripe charge succeeded, never reconciled to Odoo).

1. **Odoo first, but trust `payment_state` — not just `account.payment`.** Migration-era paid invoices have payment_state='paid'/'in_payment' with ZERO account.payment records (reconciled by bank entry). See `project_paid_without_payment_record`.
2. **If Odoo shows not_paid / no payment record → CHECK STRIPE before concluding "unpaid."** A Stripe card charge can SUCCEED without reconciling to Odoo (success-webhook / abandoned-checkout gap). Search Stripe by **AMOUNT + DATE** (`GET /v1/charges?created[gte]=<epoch>`), NOT by name/email — the billing name may be misspelled and billing email = the BUSINESS email (windowandsolarcare@gmail.com), not the customer's. See `project_stripe_payments_not_reconciled_to_odoo` + `project_stripe_abandoned_checkout_strands_invoice`.
3. **Stripe access:** **Stripe MCP is now connected** (added 2026-09-02 as a claude.ai connector — **READ-ONLY**, LIVE account "Windowandsolarcare"). Tools load as **`mcp__claude_ai_Stripe__*`** in a **new session** (a connector added mid-session isn't visible until a fresh start; run `ToolSearch("stripe")` to load the schemas if they're deferred). Prefer the MCP for payment lookups — it's one call, no key handling. **Fallback (or if the MCP tools aren't present):** live key + direct Stripe REST API (`https://api.stripe.com/v1/...`, `Authorization: Bearer <key>`) — key is in Google Drive **Saunders Vault** → doc "Stripe" and local `C:\Users\dj\_stripe_key_val.txt`; read it FROM THE FILE (don't inline a live `sk_live_` token in a shell command — the classifier blocks it). **Never paste the key in chat or commit it** (GitHub secret-scanning blocks it — see `project_memory_mirror_secret_scanning`; redact secret SHAPES in any memory note). MCP is READ-ONLY by design — any actual money move goes through the app + Operator, never a raw write.
4. **A succeeded Stripe charge with no Odoo payment = a reconciliation gap (money-touching).** Surface to DJ; have **Operator** record the card payment against the invoice (journal: Credit Card, id=20). Likely systemic — flag Specialists to check for other unrecorded card payments.

## KEY VOCABULARY

**"The schedule"** = the Render field assistant daily job list (`wsc-field-assistant.onrender.com`). Gate: SO must have `state in ['sale', 'done']` AND `date_order` = that day. **Submitted jobs are NOT on the schedule** — Phase 3 creates them as draft quotations. A job lands on the schedule when Workiz status is one of: Scheduled / Send Confirmation - Text / Next Appointment - Text / Next Appointment 2 - Text — Phase 4 confirms the SO at that point.

---

## CREDENTIALS

- **Odoo URL:** `https://window-solar-care.odoo.com`
- **Odoo DB:** `window-solar-care`
- **Odoo User ID:** `2`
- **Odoo API Key:** `[ROTATED 2026-08-22 — read from local key file / Render env ODOO_API_KEY, NOT stored in repo]`
- **Workiz API Token:** `[RETIRED — Workiz dead 2026-08-03]`
- **Workiz Auth Secret:** `[RETIRED — Workiz dead 2026-08-03]`
- **GitHub Repo:** `windowandsolarcare-hash/Odoo-Migration` (branch: `main`)

---

## CRITICAL RULES

1. **Zapier:** Code in GitHub. Zapier fetches on every run. Push to main = deploy.
2. **Odoo Server Actions — TWO-STEP DEPLOY:** When fixing a bug in a reactivation script or any Odoo server action, you MUST do BOTH steps: (a) update the local file and push to GitHub, AND (b) write the fixed code directly into the Odoo server action via `ir.actions.server` write API. GitHub is the source of truth for version history, but Odoo runs the code stored in its own database — pushing to GitHub alone does NOT update what Odoo executes. Always patch the live server action immediately after updating the file. Key server action IDs: LAUNCH=563, PREVIEW=559 (DNU). Find others by searching `ir.actions.server` where name ilike the script name.
3. **Odoo Server Actions — code restrictions:** NO imports, NO docstrings, NO env.user.message_post in webhooks, NO hasattr, NO response/result variable names
3. **Odoo Webhook payload:** Often already dict - check `isinstance(payload, str)` before json.loads
4. **Workiz STOP:** Filter on SubStatus (not Status). Status stays "Pending"
5. **Property search:** Use `x_studio_x_studio_record_category` = "Property", NOT type="other"
6. **Testing:** YOU create/cleanup test data via API. User never does manually
7. **Workiz custom field:** Use `type_of_service_2` NOT `type_of_service` — API returns/accepts `type_of_service_2`. Using the wrong name causes Phase 5 to create activities instead of jobs.
8. **Odoo action_confirm resets date_order:** After calling action_confirm() on an SO, always write date_order back. Odoo resets it to datetime.now() internally.
9. **date_order = job START time always.** SO `date_order` is always the Workiz `JobDateTime` (start time) converted to UTC. NEVER use `JobEndDateTime`, `date_deadline`, or any end time for `date_order`. This has been the rule since day one — the schedule, the Render app, and all reporting depend on it.
10. **NEVER comment out or remove existing working code without DJ's explicit approval.** This code was built over months, debugged, and agreed to work. Adding new code is fine. But commenting out, deleting, or disabling any existing logic — even temporarily, even with good intentions — requires DJ to say "yes, remove that." If you believe something should be removed, explain why and ask first. Do not act unilaterally.

11. **Surgical edits only — never rewrite a function to fix one line.** When fixing a bug, change only the specific lines that are broken. Do not rewrite the whole function. Do not restructure surrounding logic. Do not "clean up" while you're in there. A function rewrite is how working code gets accidentally replaced — the new version solves the reported problem but silently drops the working logic that solved a different problem from 3 months ago. If you only need to change one condition, change that condition and nothing else.

12. **localStorage for anything that must survive a page refresh.** The page refreshes constantly — phone screen sleep, app switching, auto-refresh. Any state that gates a user-facing flow (modals, prompts, navigation) MUST be stored in localStorage, not a plain JS variable. A JS variable initialized to `false` is always `false` after a refresh. If you see a gate like `if (_someVariable)` controlling a modal or prompt, verify it's backed by localStorage — if it isn't, that's a bug waiting to happen.

13. **Phone edge cases — code for ALL of these, not just the happy path.** This app runs on a phone in the field. Before shipping any button, fetch, or modal, verify each of the following is handled:
    - **Double-tap:** User taps a button, nothing appears to happen, they tap again. Guard every async button by disabling it on first tap and re-enabling in `finally`. Use a module-level `_pending` flag for modals without a direct button reference.
    - **Fetch timeout:** Never leave a fetch open-ended. Wrap with a 10s timeout (30s for heavy ops). A hanging fetch blocks the user with no feedback.
    - **No signal / signal drops mid-fetch:** If the operation must succeed (clock-in, payment, timer log), save intent to localStorage BEFORE the fetch, then retry on next page load. Never silently lose data because a fetch threw.
    - **Page refresh / app backgrounded:** Any in-progress state must be in localStorage. If the OS kills the webview, the user comes back to a fresh page. JS variables are gone. localStorage is not.
    - **Async init race:** `whoami`, `payroll/status`, and similar boot calls are async. The user may interact before they return. Cache their results in localStorage so the first render is correct without waiting.
    - **Already-completed action replayed on refresh:** Use idempotent keys (e.g. date-keyed localStorage flags) so retrying a queued action on the next load doesn't create duplicates.

---

## ODOO CUSTOM FIELD NAMES (EXACT — CASE SENSITIVE)

| Human Name | Model | Field Name | Notes |
|---|---|---|---|
| Workiz UUID | sale.order | `x_studio_x_studio_workiz_uuid` | Unique key for job lookup |
| Workiz Link | sale.order | `x_studio_x_workiz_link` | |
| Workiz Link | account.move (Invoice) | `x_studio_workiz_job_link` | Different from SO field |
| Workiz Tech | sale.order | `x_studio_x_studio_workiz_tech` | |
| Gate Code | sale.order | `x_studio_x_gate_snapshot` | Snapshot at time of job |
| Gate Code | res.partner | `x_studio_x_gate_code` | Master record |
| Pricing | sale.order | `x_studio_x_studio_pricing_snapshot` | Snapshot |
| Pricing | res.partner | `x_studio_x_pricing` | Master record |
| Job Type | sale.order | `x_studio_x_studio_x_studio_job_type` | |
| Frequency | res.partner | `x_studio_x_frequency` | e.g. "3 Months" |
| Type of Service | res.partner | `x_studio_x_type_of_service` | Written from Workiz type_of_service_2 |
| Alternating | res.partner | `x_studio_x_alternating` | "Yes" or "No" |
| Service Area | res.partner | `x_studio_service_area` | Values: Hemet / Desert / All areas. On the PROPERTY record. NOTE: the twin `x_studio_x_studio_service_area` exists but is EMPTY on all 897 props — do NOT use it. Corrected 2026-06-11. |
| Workiz Client ID | res.partner | `ref` | Stores "1234" (ClientId numeric) |
| Location ID | res.partner | `x_studio_x_studio_location_id` | Workiz serialId / ClientId |
| Record Category | res.partner | `x_studio_x_studio_record_category` | "Property" for property records |
| Last Property Visit | res.partner | `x_studio_x_studio_last_property_visit` | Date of last visit to this property |
| Last Visit All | res.partner | `x_studio_last_visit_all_properties` | Last visit across all properties |
| Active/Lead | res.partner | `x_studio_activelead` | "Do Not Contact" (exact case) |
| SMS Override | sale.order | `x_studio_manual_sms_override` | Reactivation SMS text |
| CRM Activity Log | res.partner | `x_crm_activity_log_ids` | Activity log entries |
| Prices Per Service | res.partner | `x_studio_prices_per_service` | Pricing menu |
| Last Reactivation | res.partner | `x_studio_last_reactivation_sent` | Reactivation cooldown = **365 days** (Reactivation page candidate filter uses `one_year_ago`; SA 563 only WRITES this, never checks it — analytics Reactivate button enforces the 365-day warn+override). Followup flow is a separate 45-day cooldown. "90 days" was stale doc, corrected 2026-06-11. |
| Graveyard UUID | crm.lead | `x_workiz_graveyard_uuid` | |
| Graveyard Link | crm.lead | `x_workiz_graveyard_link` | |
| Historical UUID | crm.lead | `x_historical_workiz_uuid` | |
| Historical Link | crm.lead | `x_studio_x_historical_workiz_link` | |
| Odoo Contact ID | crm.lead | `x_odoo_contact_id` | Linked res.partner ID |
| Workiz Status | sale.order | `x_studio_x_studio_workiz_status` | "Done" = job complete. Filter for Done jobs ONLY with this field |
| Frequency SO | sale.order | `x_studio_x_studio_frequency_so` | Selection: 3/4/6/12 Months, Unknown. Synced from Workiz by SA 955. Dashboard reads this first, falls back to res.partner x_studio_x_frequency |
| Type of Service SO | sale.order | `x_studio_x_studio_type_of_service_so` | Selection: Maintenance / On Request / Unknown (per-job). Only `Maintenance` jobs count as "late/overdue" for due badges — On Request/Unknown are never late. Partner-level equivalent = `x_studio_x_type_of_service`. Verified 2026-06-11 |
| Render Access Code | hr.employee | `x_render_access_code` | 4-digit PIN for Render app login |
| Next Job Date | res.partner | `x_studio_next_job_date` | Next scheduled job date — written by Phase 3/5, cleared by Phase 4 on Done/Canceled |

---

## SYSTEM CONSTANTS (VERIFIED — DO NOT GUESS THESE)

These are facts confirmed by direct API query. Never infer these from patterns or training data.

| Fact | Value | Verified | Notes |
|---|---|---|---|
| Odoo SO name format | 6-digit zero-padded number, NO prefix | 2026-05-20 | e.g. `003575`, `004659`. NOT `S00123`. Query: `sale.order` `name` field |
| Odoo SO sequence | Sequential integers, currently ~4600+ | 2026-05-20 | `str(n).zfill(6)` to normalize any number DJ provides |
| Workiz Job UUID | Long UUID string e.g. `abc-123-def-456` | — | Internal only — DJ never knows/provides this directly |
| Workiz Job Number | Short sequential number shown in Workiz UI | — | Different from Odoo SO number — different sequences |
| Odoo DB name | `window-solar-care` | — | Used in XML-RPC calls |
| Odoo User ID | `2` | — | DJ's user ID for API auth |
| Render app URL | `https://wsc-field-assistant.onrender.com` | — | |
| OwnTracks token | `wsc-ot-2026` | — | OWNTRACKS_SECRET env var |
| mail.activity.type "Follow-up" | ID `15` | 2026-05-28 | Created via API for Phase 5 reminder activities |
| mail.activity.type "To-Do" | ID `4` | — | Personal tasks |
| ir.model sale.order ID | `670` | — | Used in mail.activity res_model_id |
| Render workspace ID | `tea-d78l9fqdbo4c7388n9og` | 2026-06-03 | "Dan's workspace" — use with mcp__render tools, never ask DJ |
| Render main service ID | `srv-d78le0fkijhs738dsli0` | 2026-06-03 | wsc-field-assistant web service |
| Odoo company: Window and Solar Care | `company_id = 1` | 2026-06-05 | Always filter by this for W&SC financial queries |
| Odoo company: Saunders Printing | `company_id = 3` | 2026-06-05 | Separate business — do NOT mix into W&SC reports |
| Odoo company: Cheryl Johnson, REALTOR® | `company_id = 2` | 2026-06-05 | Separate business — do NOT mix into W&SC reports |
| account.journal — Chase Checking | id=6, code=BNK1, type=bank | 2026-06-07 | Where checks deposit. Maps to "Check" bucket in reports |
| account.journal — Check Payments | id=17, code=CHK, type=bank | 2026-06-07 | Also maps to "Check" bucket |
| account.journal — Cash | id=18, code=CASH, type=cash | 2026-06-07 | Maps to "Cash" bucket |
| account.journal — Zelle | id=19, code=ZEL, type=bank | 2026-06-07 | Maps to "Zelle" bucket |
| account.journal — Credit Card | id=20, code=CC, type=bank | 2026-06-07 | Maps to "Credit" bucket |
| account.journal — Venmo | id=29, code=VENMO, type=bank | 2026-06-07 | Maps to "Other" bucket |

**If you need a format not in this table: make an API call to confirm it. Do not guess.**

---

## WORKIZ API ACCESS — HOW TO CALL FROM SCRIPTS

**Workiz GET calls work directly from anywhere** — local machines, Render, Odoo server actions. No IP restriction. No proxy needed.

**Workiz API URL format:**
```
GET:    https://api.workiz.com/api/v1/{TOKEN}/job/get/{UUID}/
UPDATE: https://api.workiz.com/api/v1/{TOKEN}/job/update/{UUID}/
DELETE: https://api.workiz.com/api/v1/{TOKEN}/job/delete/{UUID}/
```
- Token: `[RETIRED — Workiz dead 2026-08-03]`
- Auth Secret: `[RETIRED — Workiz dead 2026-08-03]` — needed for POST/UPDATE/DELETE, **NOT for GET**
- In Odoo server actions: use `requests.get(url)` — `requests` is available in Odoo eval context
- **Rate limit:** ~30 calls before hitting HTTP 429 — sleep 15-30 seconds between batches

---

## WORKIZ API CRITICAL DEFAULTS

These defaults prevent Workiz API validation errors. Always use when field might be empty:

```python
'type_of_service_2': str(value or 'On Request')     # NOT type_of_service, NOT empty string
'frequency':         str(value or 'Unknown')          # NOT empty string
'confirmation_method': str(value or 'Cell Phone')    # NOT empty string
'JobSource':         str(value or 'Referral')         # NOT "Reactivation"
'ok_to_text':        str(value or 'Yes')
```

**Workiz Status vs SubStatus — FUNDAMENTAL:**
Only **Submitted** and **Done** are true top-level Status values that we use. **Everything else lives under Status="Pending" as a SubStatus** — Scheduled, STOP, Lead, Send Confirmation - Text, Next Appointment - Text, Next Appointment 2 - Text, In Progress, Canceled, all of them.
ALWAYS filter on SubStatus, not Status.
When updating SubStatus via the API, the body MUST include the parent Status="Pending" too — otherwise Workiz returns 400 "Could not update sub status with no parent status provided". `workiz_post` in the Render app auto-injects this; if you write Workiz API code in Zapier or Odoo server actions, replicate the rule.

**Workiz API quirks:**
- ClientId: use numeric (e.g. 1040) not "CL-xxx"
- JobDateTime: omit entirely for unscheduled jobs
- All string fields: must be str() — reject None/numbers
- Job create response: returns list `[{UUID: '...'}]` or HTTP 204
- Job GET response: `{"data": [{...job...}]}` — job is inside a list. Always parse: `data = raw['data']; job = data[0] if isinstance(data, list) else data`
- Job GET on deleted job: returns **HTTP 204** (no content), NOT 404. Treat both 204 and 404 as "job is gone"
- type_of_service_2 is the custom field name (NOT type_of_service)

---

## APPROACHES THAT FAILED (DO NOT REPEAT)

| Approach | Error | Fix |
|---|---|---|
| `import urllib.request` in Odoo | forbidden opcode IMPORT_NAME | Odoo blocks ALL imports |
| `exec(code)` from GitHub in Odoo | forbidden opcode | Odoo safe_eval blocks exec |
| Triple-quote docstring in Odoo webhook | Access to forbidden name __doc__ | Use # comments only |
| `env.user.message_post()` in webhook | res.users has no message_post | Remove all logging |
| `json.loads(payload)` when payload is dict | TypeError | `if isinstance(payload, str): payload = json.loads(payload)` |
| `["type", "=", "other"]` for properties | Wrong results | Use `["x_studio_x_studio_record_category", "=", "Property"]` |
| Proxying Workiz GET through Odoo server action | Unnecessary — Workiz allows direct calls from anywhere | Call `requests.get()` directly, no proxy needed |
| Adding `?auth_secret=` to GET URL | auth_secret is NOT required for GET — verified 2026-05-05 | Use `GET /job/get/{UUID}/` with no query params |
| `JobSource = "Reactivation"` | Workiz validation error | Use "Referral" |
| `type_of_service = ""` | Workiz validation error | Use "On Request" |
| `frequency = ""` | Workiz validation error | Use "Unknown" |
| `workiz_job.get('type_of_service')` | Returns None | Use `workiz_job.get('type_of_service_2')` |
| `confirm_sales_order()` then read date_order | Returns current time, not job date | Write date_order back after confirm — Odoo resets it internally |
| `datetime.now()` in Odoo 19 Server Action | 'wrap_module' has no attribute 'now' | Use `datetime.datetime.now()` — datetime is the module in Odoo 19, not the class |
| Server Action via `type="action"` button missing `action = False` | 'Response' object has no attribute 'setdefault' | Always end Server Action code with `action = False` — Odoo 19 tries to use return value as navigation action |
| Using `response = requests.get(...)` in server action | 'Response' object has no attribute 'setdefault' | `response` is a reserved variable in Odoo 19 eval context — rename to `workiz_resp`, `api_resp`, etc. Same applies to `result`. |
| `odoo_rpc('sale.order', 'write', [[id]], {vals})` — 4th kwarg form | `SaleOrder.write() got an unexpected keyword argument 'field_name'` | `write(vals)` is positional. Put vals INSIDE the args list: `odoo_rpc('sale.order', 'write', [[id], {vals}])`. Exception: `message_post` takes real kwargs so 4-arg form is OK there. |
| HTML tags in `message_post` body (`<br/>`, `<p>`, `<strong>`) | Tags display as literal text in chatter | Use plain text with ` \| ` pipe separators — Odoo escapes HTML in both server actions (Odoo 17+) and external JSON-RPC calls. Format: `[YYYY-MM-DD HH:MM:SS] Label: Field: Value \| Field: Value` |
| No green indicator in chatter | N/A — previously thought impossible | Unicode emoji works fine — only HTML is escaped. Use `✅` for success, `⚠️` for warnings, `❌` for failures. DJ prefers `✅` on all completion messages. |
| `PUT /v1/services/{id}/env-vars` with partial list | Wipes ALL env vars not included in payload — 2026-05-14 wiped STRIPE_SECRET_KEY, OWNTRACKS_SECRET, GCAL_1_URL | Always fetch full list first (`GET /env-vars`), merge new values in Python, then PUT the complete merged set. Render has no POST/PATCH for individual vars — PUT is the only write method. |
| Python multi-line `str.replace()` on GitHub-fetched files | All replacements silently fail — files fetched from GitHub via `base64.b64decode` have CRLF (`\r\n`) line endings, so `\n`-based multi-line strings never match | Always call `.replace("\r\n", "\n")` on the decoded content before doing any string replacements. Push the normalized (LF) version — Render/Linux is fine with LF. |

---

## GITHUB DEPLOYMENT WORKFLOW

### 🚫 MANDATORY PRE-PUSH GATES — NO EXCEPTIONS, EVERY FILE, EVERY PUSH

These two are not optional and not "for big files." They are why regressions keep happening (e.g. the Jun-8 stale push that dropped 1,377 lines from field.html, the Apr-30 push that dropped 2,277). Run BOTH before every push:

1. **FETCH THE LIVE FILE FIRST — never edit a local copy you didn't fetch this session.** `gh api .../contents/<path> | base64 -d > <local>`, then edit THAT. The local repo copy is assumed stale. Confirmed 2026-06-10: the field.html on disk was 750 lines behind live. If you skip this, you WILL eventually overwrite newer work.
   - **★ 2026-09-02 — the local app clone `C:\Users\dj\Documents\Business\Saunders Render App` is now an AUTO-SYNCED READ-ONLY MIRROR of `origin/main`.** A SessionStart hook (`.claude/settings.json`) runs `git pull --ff-only origin main` at every session start, so at session start local == live and you can safely GREP/READ it for analysis. It had silently drifted **4 months** (May→Sep 2026: field.html was 2,749 lines behind, dashboard.py ~1,550) because it was a clone nobody pulled — that's why reading local burned two analyses on 2026-09-02. **Still: (a) NEVER edit this clone directly** (edits go via `gh api` fetch→push; a local commit/dirty file breaks `--ff-only` and drift returns — if `git status` shows changes, `git reset --hard origin/main`); **(b) for a PUSH, still re-fetch that one file live** in case it changed mid-session. Reading it is safe at session start; trusting it hours later, or as a push base, is not.
2. **`node --check` on any HTML/JS before pushing; `python -m py_compile` on any .py.** A syntax error or a dangling reference (removed element + leftover `getElementById`) crashes the whole app on load (stuck/error screen). This caught real crashes multiple times — Jun 7 had a cluster of them.

`safe_deploy.py` enforces gate 1's line/byte regression guard automatically — USE IT for field.html / dashboard.py. Gate 2 is on you. (Splitting field.html into modules is the durable third fix — NOT approved yet, do not do it.)

---

**⚠ READ THIS BEFORE EVERY PUSH — 2026-04-30 incident:**

A different Claude Code chat had a stale 3565-line copy of `dashboard.py` and pushed it over the live 5842-line version, wiping out Manage Shifts CRUD, GPS endpoints, Stale SOs, whoami, etc. — 2277 lines of work gone in one push. **This is the single biggest risk in this project.**

**Mandatory before pushing any file > 1000 lines** (especially `dashboard.py`, `field.html`, or anything in `Saunders Render App/`):

1. **Pull the current GitHub version FIRST** — never trust your local copy as up-to-date:
   ```bash
   gh api repos/windowandsolarcare-hash/saunders-render-app/contents/<path> --jq '.content' | base64 -d > /tmp/current.py
   wc -l /tmp/current.py "<your local path>"
   ```
   If the deployed version is significantly larger than your local, **STOP** — your local is stale.

2. **Use `safe_deploy.py`** (saved at `C:\Users\dj\safe_deploy.py`, lives outside the repo) for any push to dashboard.py / large files. It auto-fetches the deployed version and refuses to push if local is >25% smaller or >100 lines shorter:
   ```bash
   python C:/Users/dj/safe_deploy.py \
     --repo windowandsolarcare-hash/saunders-render-app \
     --path routers/owner/dashboard.py \
     --local "C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py" \
     --msg  "2026-04-30 | dashboard.py | what changed"
   ```
   Add `--force` only after you've personally diffed and confirmed the deletions are intentional.

3. **The Render Claude `github_push_file` tool also has the regression guard server-side** (commit `41351838`). Voice-driven pushes refuse if they'd drop >100 lines / >25% bytes unless `acknowledge_regression: true` is passed.

**Use the reliable bash + base64 + temp file approach below. Do NOT use PowerShell ConvertTo-Json (causes "Problems parsing JSON" errors).**

### RECOMMENDED: Use the deploy_to_github.sh script

**Located in:** Both repos (Odoo-Migration and cheryl-real-estate)

**Usage:**
```bash
./deploy_to_github.sh <repo> <file_path> <local_file> <commit_message>
```

**Example:**
```bash
./deploy_to_github.sh \
  windowandsolarcare-hash/Odoo-Migration \
  1_Production_Code/zapier_phase3_FLATTENED_FINAL.py \
  "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\1_Production_Code\zapier_phase3_FLATTENED_FINAL.py" \
  "2026-04-26 | zapier_phase3.py | fixed bug in X"
```

The script handles:
- Reading Windows file paths
- Base64 encoding without line breaks
- JSON payload construction
- GitHub API push via gh CLI
- Error handling and debugging

### FALLBACK: Direct bash command (if script not available)

```bash
repo="windowandsolarcare-hash/Odoo-Migration"
filePath="1_Production_Code/zapier_phase3_FLATTENED_FINAL.py"
localFile="C:\\Users\\dj\\Documents\\Business\\A Window and Solar Care\\Migration to Odoo\\1_Production_Code\\zapier_phase3_FLATTENED_FINAL.py"

base64_content=$(powershell -Command "
\$content = Get-Content '$localFile' -Raw -Encoding UTF8
\$bytes = [System.Text.Encoding]::UTF8.GetBytes(\$content)
\$base64 = [System.Convert]::ToBase64String(\$bytes)
Write-Output \$base64
" 2>/dev/null)

cat > /tmp/gh_payload.json <<EOF
{
  "message": "2026-04-26 | filename | description",
  "content": "$base64_content",
  "branch": "main"
}
EOF

gh api "repos/$repo/contents/$filePath" --method PUT --input /tmp/gh_payload.json
rm /tmp/gh_payload.json
```

### EDITING A DEPLOYED FILE (fetch → edit → push)

**CRITICAL: `/tmp` does NOT persist between separate Bash tool calls.** Each Bash invocation gets a fresh shell. Saving to `/tmp` in call 1 and reading in call 2 always fails with `FileNotFoundError`.

**Working pattern — two calls total:**

**Call 1:** Download + edit + save to a persistent Windows path, all in one pipeline:
```bash
gh api repos/REPO/contents/PATH --jq '.content' | base64 -d | python3 -c "
import sys
content = sys.stdin.read()
content = content.replace('old text', 'new text')
sys.stdout.write(content)
" > /c/Users/dj/edited_file.py && echo "saved \$(wc -l < /c/Users/dj/edited_file.py) lines"
```

**Call 2:** Push from the Windows path (standard push pattern):
```bash
sha=\$(gh api repos/REPO/contents/PATH --jq '.sha')
base64_content=\$(powershell -Command "
\\\$content = Get-Content 'C:/Users/dj/edited_file.py' -Raw -Encoding UTF8
\\\$bytes = [System.Text.Encoding]::UTF8.GetBytes(\\\$content)
[System.Convert]::ToBase64String(\\\$bytes)
" 2>/dev/null)
cat > /c/Users/dj/gh_payload.json << EOF
{"message": "DATE | file | desc", "content": "\$base64_content", "sha": "\$sha", "branch": "main"}
EOF
gh api repos/REPO/contents/PATH --method PUT --input /c/Users/dj/gh_payload.json && echo "pushed"
rm /c/Users/dj/gh_payload.json /c/Users/dj/edited_file.py
```

**Rules:**
- Save intermediate files to `/c/Users/dj/` (Windows filesystem) — this persists between Bash calls
- `/tmp` is fine within a single chained call (`&&`) but never across separate Bash tool invocations
- JSON payload files created with `cat >` in the same call as `gh api --input` are fine

---

### Why this approach (NOT PowerShell ConvertTo-Json)

**Problem with PowerShell ConvertTo-Json:**
- `[System.Convert]::ToBase64String()` adds MIME-style line breaks every 76 characters
- PowerShell escaping of special characters breaks JSON validation
- Result: "Problems parsing JSON" HTTP 400 errors (4-5 retries typical)
- Token waste: 50-100 tokens per failed attempt

**Bash + temp file approach:**
- Handles Windows paths via PowerShell subshell (clean integration)
- Constructs raw JSON string (no escaping issues)
- Temp file avoids shell interpretation
- One-shot success: 99%+ first-try rate

### Notes
- Commit format: `YYYY-MM-DD | filename | description of change`
- Always push to `main` — Zapier watches main only
- For new files: GitHub API creates them automatically (no SHA needed)
- Test the deployment immediately after: verify file size > 0 on GitHub

---

## MEMORY RULE — CRITICAL

**Whenever you discover something new about this project — a field name, an API quirk, a bug root cause, a Workiz/Odoo behavior, a business decision — write a memory file IMMEDIATELY before continuing. Do not wait until end of session or rely on compaction to capture it.**

**EFFICIENCY RULE (2026-04-26):** When you encounter trial-and-error patterns, repetitive errors, or inefficient processes, YOU OWN the responsibility to recognize, solve, document, and save them immediately without waiting for DJ's request. If you do something inefficiently 5 times, that's a signal to document the right way for the next session. Token waste + time waste = your responsibility to prevent. No asking. No waiting. Just save it.

Memory directory (local, auto-loaded): `C:\Users\dj\.claude\projects\C--Users-dj-Documents-Business-A-Window-and-Solar-Care-Migration-to-Odoo\memory\`

Use type `project` for technical facts about how the system behaves. Include **Why:** and **How to apply:** lines.

### ★ MEMORY IS MIRRORED TO GITHUB (2026-08-22) — keep it LIVING
The FULL memory (every `.md` in the local memory dir) is mirrored to **`windowandsolarcare-hash/Odoo-Migration` → `memory/`** on GitHub. **Why:** it was LOCAL-ONLY and unbacked — a Surface Pro drive failure would have wiped 600+ files of accumulated knowledge; the mirror is the backup + makes memory available to cloud/other sessions.
- **When you write OR edit ANY local memory file, ALSO push that individual file to `Odoo-Migration/memory/<same-name>` via `gh api` (Contents PUT, fetch sha first if it exists).** This is IN ADDITION to the SHARED_MEMORY.md dual-write below. Keep the GitHub mirror in lockstep with local — never let them drift.
- Use `gh api` (Contents API), NEVER `git push` — main is protected by a ruleset that rejects direct git pushes (the Contents API is allowed; that's the whole reason for the "gh api, not git" rule).

### ★ WHY MEMORIES MATTER — do not skip this (DJ 2026-08-22)
Every Claude Code session starts BLANK. The only reason a fresh session comes up to speed in minutes — instead of relearning everything — is a strong CLAUDE.md + these memories. **Writing good memories is the single highest-leverage habit in this project; it is what makes each new session immediately valuable.** DJ explicitly reaffirmed this. So: capture discoveries the MOMENT they happen (a field name, a quirk, a decision, a "we agreed to X"), make them self-contained and dated, and never assume "someone will remember" — the next session won't, unless it's in memory. A background agreement that isn't written down does NOT survive. (Reality check found the memory practice only truly began ~March 2026 — the first ~4 months went uncaptured. Don't let that recur.)

### DUAL-WRITE RULE — SHARED MEMORY SYNC

**When writing any local memory file, ALSO update `3_Documentation/SHARED_MEMORY.md` in GitHub.** This file is the shared brain between Claude Code (local) and Render Claude (field assistant on phone). Render Claude loads it on every session start.

- Add key facts to the relevant section in SHARED_MEMORY.md
- Push via `gh api` using the standard deployment script
- Commit message format: `YYYY-MM-DD | SHARED_MEMORY.md | brief description of what was added`

Render Claude can also write to SHARED_MEMORY.md via its `update_shared_memory` tool.

### SESSION START RULE — READ SHARED_MEMORY.md FIRST

**At the start of every Claude Code session, read `3_Documentation/SHARED_MEMORY.md` from the local repo before doing any work.** Render Claude writes facts back to this file in the field — if you skip this read, you miss decisions and fixes that happened since your last session.

The file is already loaded as a system-reminder at session start (see top of this context), but always verify it's current. If you discover it has been updated since the session-reminder was generated, re-read it to get the latest version.

### PROACTIVE SAVES — EVENT-TRIGGERED ONLY

Count-based rules ("every 10 responses") and session-end rules do not work reliably — LLMs have no persistent counter and meta-tasks get squeezed out under task load. These have been removed. Only event-triggered rules follow:

1. **After any API call made to verify something unknown:** If you made an API call because you weren't certain of a format, field name, ID, or system constant — stop immediately after that call and write the result to CLAUDE.md SYSTEM CONSTANTS + SHARED_MEMORY.md before continuing. Do not finish the task first. Write it now.

2. **After discovering any field name, API behavior, or system quirk not already in CLAUDE.md:** Write it to memory and SHARED_MEMORY.md before the next tool call. The moment of discovery is the trigger — not the end of session.

3. **After any bug fix that reveals a non-obvious system behavior:** Write the root cause and fix pattern to memory immediately. "We got burned by X" entries in CLAUDE.md exist because they were written at the moment of discovery.

### PROJECT-SCOPED SHARED MEMORY

Each project has its own SHARED_MEMORY.md. This project's file is `3_Documentation/SHARED_MEMORY.md` in repo `windowandsolarcare-hash/Odoo-Migration`.

When DJ starts a new project, Render Claude's `GITHUB_REPO` and `SHARED_MEMORY_PATH` env vars are updated to point to the new project's file — no code change needed. Never merge content from different projects into the same file.

---

## CODE MODIFICATION WORKFLOW

1. Read the current local version first
2. Make the requested changes
3. Save locally
4. Push to GitHub main using deployment script above
5. Confirm to user: what changed, file name, that it's on GitHub main
6. Zapier auto-fetches latest code on next trigger (NO manual Zapier update needed)

---

## PLATFORM MIGRATION RULE

**When migrating code between platforms (Zapier → Odoo, Odoo → Zapier, etc.):**

**NEVER:**
- Simplify, optimize, or "clean up" existing code
- Strip down features, logging, or field mappings
- Remove ANY functionality that exists in the original

**ALWAYS:**
- Copy ALL functionality exactly (1:1 functional duplicate)
- Only change what's technically required for the new platform

**Why:** This code represents months of development. Every detail exists for a reason.

---

## TESTING WORKFLOW

**YOU create and cleanup ALL test data via API. User never manually creates/deletes.**

1. Make code changes locally → push to GitHub main
2. YOU create test data via API (Workiz: `test_create_workiz_job.py` / Odoo: JSON-RPC)
3. Trigger/monitor Zapier
4. Verify results
5. YOU cleanup test data via API

Scripts: `2_Testing_Tools/test_create_workiz_job.py`, `test_cleanup_workiz_job.py`, `test_cleanup_odoo_data.py`

---

## PHASE STATUS

| Phase | Purpose | Trigger | File |
|---|---|---|---|
| 1 | Historical Migration | One-time (complete) | N/A |
| 2 | Reactivation Engine | Odoo Server Action (manual) | ODOO_REACTIVATION_*.py |
| 2B | STOP Compliance | Workiz → Odoo direct webhook | odoo_webhook_stop_handler.py |
| 3 | New Job Creation | Workiz webhook → Zapier | zapier_phase3_FLATTENED_FINAL.py |
| 4 | Job Status Updates | Zapier polling (5 min) | zapier_phase4_FLATTENED_FINAL.py |
| 5 | Auto Job Scheduling | Phase 6 webhook trigger | zapier_phase5_FLATTENED_FINAL.py |
| 6 | Payment Sync | Odoo webhook → Zapier | zapier_phase6_FLATTENED_FINAL.py |

**STOP webhook URL:** `https://window-solar-care.odoo.com/web/hook/f64d0bc1-54fd-45a1-b645-0dcae6ae1728`

---

## PAIRED CHANGES — DO BOTH OR NEITHER

These are changes that always require updating TWO places. Missing one breaks something silently.

| Trigger | File 1 | File 2 | Notes |
|---|---|---|---|
| ~~Calendly event types~~ | — | — | **Calendly RETIRED 2026-07-19** — never emit calendly.com links. All booking links = `wscare.pro/c/<token>` (make_token in routers/booking.py) or `wscare.pro/book` fallback. See memory `project_calendly_retired.md` |
| Change /api/hemet/* behavior | `routers/owner/hemet.py` | `routers/owner/dashboard.py` (~line 8530+, its own copy of the hemet endpoints) | dashboard.py registers FIRST and SHADOWS hemet.py — patching hemet.py alone does nothing (burned 2026-07-19) |
| Change the field VOICE assistant (`/owner/ask` — tools, SYSTEM_PROMPT, `_agent_loop`, the voice text-draft tool, Think-hard deep mode) | `routers/owner/dashboard.py` (the LIVE `/ask` — EDIT HERE) | `routers/owner/field.py` (its `/ask` twin is DEAD) | main.py includes dashboard FIRST, so **dashboard.py serves `/owner/ask` and field.py's copy does nothing** (burned 2026-08-19 — a whole voice-tool + deep-mode build landed in field.py with zero effect). Voice-assistant changes go in **dashboard.py**. Note: dashboard.py's `/ask` is still the pre-Workiz-retirement version (live Workiz tools + "WORKIZ FACTS" + an override "WORKIZ RETIRED" block on top); full cleanup pending — do NOT strip the still-live `workiz_status` FIELD in that cleanup. |

**★ Route-shadowing rule (2026-08-19):** two routers registered under the same prefix can define the same path; the one included FIRST in `main.py` wins and the later one is a silent dead twin (hit us on `/api/hemet/*` and `/owner/ask`). Two defenses: (1) before editing OR reviewing any endpoint, confirm which file actually SERVES it (grep the path across the repo; late-registered routers — e.g. portal.py at main.py:292 — are the at-risk profile). (2) When adding a route to a late-registered router, **feature-namespace the path** (`/portal/...`, `/p/...`) instead of a generic one (`/ask`, `/api/job`, `/api/customers`) — collisions only happen on generic paths, so namespacing makes shadowing impossible by construction. **`anthropic` SDK stays pinned at `==0.122.0`** — 0.123/0.124 stamp `tool_use.toolset_name`, which the API 400-rejects (affects every session's Claude calls).
| ANY field **voice assistant** change (tools, prompt, model routing, `_agent_loop`, `run_agent`) | `routers/owner/dashboard.py` (the LIVE `/ask`) | `routers/owner/field.py` (DEAD twin — do NOT edit for voice) | Both define `@router.post('/ask')`; main.py includes dashboard FIRST under `/owner`, so **dashboard.py serves `/owner/ask`, field.py's twin is shadowed/dead**. Burned hours 2026-08-19 building the voice text tool + deep mode in field.py with zero effect. Edit dashboard.py. See memory `project_voice_ask_lives_in_dashboard.md` |

---

## 🧱 INFRASTRUCTURE / ENVIRONMENT GOTCHAS (not business logic — check these BEFORE building)

These are environment traps that silently waste hours; they recur unless recorded. Pre-flight a new endpoint/feature against them.

- **Shadowed routes:** before building on any `/owner/*` route, confirm which file actually serves it — grep the repo for duplicate `@router.post('/<path>')` defs and check `main.py` include order (first `include_router` under a prefix wins). dashboard.py shadows BOTH hemet.py and field.py. (2026-08-19)
- **Pin critical Python deps:** `requirements.txt` was unpinned, so a Render rebuild pulled `anthropic` 0.123/0.124 (released 2026-08-19) which stamps `tool_use.toolset_name` onto tool-use blocks → API 400 `Extra inputs are not permitted` on every tool call. Pinned `anthropic==0.122.0`. **Leave pinned; bump deliberately + test, never let it float.** (2026-08-19)
- **Voice tool-card HTML is ESCAPED by the client renderers:** the voice pages (`v2_voice.html` `renderAnswer`, `field.html` `addHistory`/`addVmHistory`) run answers through `esc()`/`linkify` — so a tool that returns an `<a href>` card shows as literal HTML text unless the renderer special-cases it (like the maps/`navigate_to` button). Relative links (`/static/...`) aren't linkified either. Add a per-renderer branch that extracts the URL into a real button. (2026-08-19)
- **Odoo rate-limits (HTTP 429):** aggressive testing (rapid curls) + background dashboard polling overloads `window-solar-care.odoo.com/jsonrpc` → 429s that make unrelated flows fail intermittently. Space out test calls; don't loop-hammer Odoo. (2026-08-19)
- **On this stack HTTP 200 ≠ success:** Odoo serves a `placeholder.png`/error page on permission denial with a 200; verify route/permission changes by CONTENT (body bytes/type), never status code alone. (2026-08-19)

---

## KNOWN FIXES & BEHAVIORS (CHANGELOG)

| Date | File | What | Why |
|---|---|---|---|
| 2026-06-09 | ql_panel.js | Mobile Customers overlay starts at `top:36px` (was `inset:0`) | **Clock-in bar = fixed, top:0, 36px, max z-index. ANY full-screen `position:fixed` overlay on an owner page MUST start at `top:36px`, never `inset:0`/`top:0`, or the bar covers its header.** Bar's body-padding/`#app`-shrink offset only protects normal-flow content, not fixed overlays. See [[project_clockin_bar_customer_overlay]] |
| 2026-06-09 | reactivation.py/html, field.py | Reactivation "Sent" tab — book a customer who replied directly (not Calendly): suggested slots (find_next_opening direct), convert graveyard Workiz job in place, close CRM → Won | crm.lead stages: 5=Attempt1-Sent, 4=Won, 6=Lost. See [[project_reactivation_sent_book]] |
| 2026-05-28 | phase3, phase4 | All task creation/sync/removal commented out | Tasks obsolete — field assistant gate is SO state in ['sale','done'], not tasks |
| 2026-05-28 | phase3 | Creates Follow-up activity (type 15) on SO for Phase 5 Submitted jobs | Reminds DJ to add tech+items in Workiz; auto-closed by Phase 4 on SO confirm |
| 2026-04-01 | phase4 | `confirm_sales_order()` writes date_order back after confirm | Odoo action_confirm() resets date_order to now() internally |
| 2026-04-01 | phase4, phase5 | Read `type_of_service_2` not `type_of_service` | Workiz API returns custom field as type_of_service_2 |
| 2026-04-01 | phase5 | New job payload uses `type_of_service_2` | Write path must match read path |
| 2026-04-01 | phase5 | Added `ok_to_text` and `confirmation_method` to new job payload | Fields were missing from new maintenance jobs |
| 2026-03-19 | phase4 | Property search uses `x_studio_x_studio_record_category` | type="other" returned wrong results |
| 2026-03-19 | reactivation | Fixed PostalCode strip non-digits | Workiz sometimes sends "93117-1234" format |
| 2026-03-19 | reactivation | Fixed last_date_cleaned year (0025 → 2025) | Raw year was 2-digit, needed +2000 |

---

## CONVERSATION ADDITIONS (March–April 2026)

- **STOP Odoo webhook:** URL above — Workiz must send here directly
- **Reactivation CRM Activity:** `{campaign} | {date} | Job #{so_name} | {primary_service}` for x_name; x_description = actual SMS text
- **Contact link on SO:** Related field `partner_shipping_id.parent_id` in Odoo Studio
- **Add-on pricing:** base_price < $70 = no inflation, no $85 floor
- **Phase 5 next date:** Use completed job's JobDateTime, not datetime.now()
- **Phase 5 last_date_cleaned:** Populate on new maintenance jobs
- **Orphaned future jobs:** Leave alone (no auto-delete)
- **Graveyard job:** Always create new (don't reuse existing future job)

---

## CODEBASE ORGANIZATION

- **1_Production_Code/** — Active scripts running the business
- **2_Testing_Tools/** — API test scripts
- **3_Documentation/** — Active manuals
- **4_Reference_Data/** — CSVs and mappings
- **z_ARCHIVE_DEPRECATED/** — Old files

---

## ODOO HTML FIELD COLOR PATTERN (DJ uses this frequently)

To show colored status indicators on Odoo form fields:

1. **Field must be `ttype: html`** (not char — char cannot render HTML)
2. **Add to view as `readonly="True"`** so the rich text editor never appears
3. **Write Bootstrap classes** — these survive Odoo's HTML sanitizer (inline `style=` gets stripped):

```python
'<span class="text-success"><b>OK - details</b></span>'    # green
'<span class="text-danger"><b>MISMATCH - details</b></span>'  # red
'<span class="text-warning"><b>PENDING - details</b></span>'  # orange
'<span class="text-info"><b>INFO - details</b></span>'        # blue
```

**To create a new HTML field via API:**
- Get model ID: search `ir.model` where `model = 'sale.order'` → ID **670**
- Create: `ir.model.fields` create with `ttype: html, store: true`
- If field already exists as char: remove from all views first → unlink → recreate → re-add
- Studio SO form view ID = **1385** (`Odoo Studio: sale.order.form customization`)

---

## COMMUNICATION STYLE

- Be concise — DJ is experienced, skip basic explanations
- Always confirm what branch you committed to
- If something fails, explain exactly why and give the fix
- Never ask "would you like me to..." for things clearly part of the task — just do them
- When done: short summary of what changed, where it lives, next step

---

## REFERENCE FILES (deep detail only, not required reading)

- `CLAUDE_CONTEXT.md` - Phase-by-phase detail, API patterns
- `MASTER_PROJECT_CONTEXT.md` - Extended field mappings, API syntax examples
- `3_Documentation/BUSINESS_WORKFLOW.md` - Business processes
