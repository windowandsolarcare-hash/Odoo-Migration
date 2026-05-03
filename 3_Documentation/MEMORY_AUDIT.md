# WSC Claude Memory Audit
**Generated:** 2026-05-03  |  **Total memory files:** 106

This document aggregates everything Claude uses as memory context for this project.
Sources: this file (local memories) + CLAUDE.md + SHARED_MEMORY.md (both in GitHub).

---

## External Sources (GitHub)

- **CLAUDE.md** — Project instructions, critical rules, field names, workflow: `windowandsolarcare-hash/Odoo-Migration/CLAUDE.md`
- **SHARED_MEMORY.md** — Session summaries shared with Render Claude: `windowandsolarcare-hash/Odoo-Migration/3_Documentation/SHARED_MEMORY.md`

---

## User Profile
*2 file(s)*

### DJ Accounting Knowledge & Preferences
`user_accounting_knowledge.md`
> DJ's accounting background, comfort level, and how Claude should handle accounting tasks for him

DJ likes accounting conceptually but is not an accountant. Specific comfort levels:

- **P&L** — comfortable. Understands income, expenses, categories, what drives profit.
- **Balance sheet** — less confident. Understands it exists and roughly what's on it but not comfortable managing it himself.
- **Double-entry accounting** — does not want to deal with it at all. Never had an accountant to ask. Has made do in QB but found journal entries and reconciliation tedious and confusing.

**How Claude should handle accounting for DJ:**

- DJ describes financial events in plain English ("I sold the truck for $7,000", "a customer got a refund", "I paid off the loan")
- Claude translates to correct accounting treatment and executes all transactions in Odoo directly
- Claude never makes DJ think about debits, credits, or which accounts to touch
- If Claude needs a factual answer DJ would know (e.g. "what did you originally pay for that truck?") Claude asks — otherwise just handles it
- Claude should briefly explain what it did and why in plain English after doing it, so DJ builds understanding over time without being overwhelmed

**DJ wants Claude to be his on-call accountant** — available any time, handles anything from simple categorization questions to complex asset disposal or loan payoff journal entries.

**Specific scenarios DJ mentioned:**
- Customer refund — doesn't do these but wouldn't know how to handle one if it happened
- Selling a vehicle — removing asset from books, recognizing gain/loss
- Loan payoff — zeroing out liability
- Owner draws — moving money from business to personal

All of these: DJ describes it, Claude handles it completely in Odoo.

---

### DJ User Profile
`user_profile.md`
> DJ's full name, business identity, and how he goes by — critical for documents, emails, signatures

# DJ's Identity

- **Full legal name:** Dan Saunders
- **Goes by:** DJ
- **Business name:** Window & Solar Care (main), Saunders Business Group (umbrella / multi-business)
- **Email:** windowandsolarcare@gmail.com

## How to apply
- In documents, PDFs, emails, and signatures: always use **Dan Saunders** — never "DJ Sanders" or any other variation
- In conversation and casual references: DJ is fine
- Business umbrella brand: Saunders Business Group
- All print/art/commercial business: Saunders Printing

---

## Feedback (How Claude Should Behave)
*19 file(s)*

### Activity notes are self-contained — never link to local memory files
`feedback_activity_notes_self_contained.md`
> When creating an Odoo mail.activity that future-you (or future-Claude) needs to act on, embed the relevant runbook content directly in the HTML note. Don't rely on links to local memory files — file:// URLs are blocked by browsers, and DJ reads activities on his phone where the dev machine isn't reachable.

When creating a `mail.activity` whose purpose is to remind future-DJ (or instruct future-Claude) to do something, the activity's `note` field should be **self-contained**. Embed the runbook content directly. Never rely on the reader being able to follow a link to a local Claude memory file.

**Why:** 2026-04-29 — DJ asked whether activity #66 (preselect coverage check reminder) should link to its memory file or just be a note. Reality: memory files live on DJ's local dev machine in `~/.claude/projects/.../memory/`. They're not URL-addressable from a browser, especially not from his phone where he reads activities. `file://` URLs are blocked by Chrome/Edge/Safari when the page itself came from http/https. Pushing every memory file to GitHub introduces duplication-rot and requires GitHub mobile login. The clean answer is to keep memory files for Claude's eyes only and put the human-readable runbook directly in the activity note.

**How to apply:**

When asked to create a future-self reminder activity, use this structure for the `note`:

```html
<p><b>Why this exists:</b> Short context for future-DJ on what triggered this reminder.</p>
<p><b>What to do when this surfaces:</b> Numbered/bulleted action steps.</p>
<p><b>Pass criteria:</b> How to know we're done.</p>
<p><b>Code locations:</b> File paths + key function names. Don't link.</p>
<p><b>Claude memory:</b> Name the memory file (e.g. <code>project_xyz.md</code>) so when DJ shows the activity to Claude, Claude knows where to dig for the deeper template/query/script. Don't try to make it a URL — just name it.</p>
```

This keeps:
- DJ informed on his phone (full context in the note, no links to chase).
- Claude pointed at the deeper memory file for the exact query/template/code on the desktop side.
- One source of truth: the memory file for internals, the activity note for the action.

**When NOT to apply:** Routine activities created by automated flows (reactivation SMS, follow-up SMS, Phase 5 maintenance scheduling) don't need a runbook — they're handled by their existing automation, and DJ rarely needs to read them. This rule applies only when *Claude itself* is creating an activity as a deferred reminder for itself or DJ.

**If DJ ever wants a real clickable link in an activity note:** the practical option is a Render endpoint behind the existing access code that serves runbook markdown — e.g., add `static/owner/runbooks/{slug}.md` to the saunders-render-app repo and serve via `/owner/runbook/{slug}`. Don't try GitHub URLs (mobile auth friction). Don't try file:// URLs (browsers block).

---

## Anything that IS a URL — make it a real `<a href>` link

DJ's rule (2026-04-29): "memory is not a link, but I want other info that has a URL to be self to link. Link it, not copy and paste."

When the activity note references content that lives at a real URL — Workiz job, Odoo record, Calendly booking, GitHub file, public docs, Render dashboard, anything with `https://` — write it as a proper HTML anchor in the note, not as plain text:

✅ `<a href="https://app.workiz.com/jobs/...">Open Workiz job</a>`
✅ `<a href="https://window-solar-care.odoo.com/odoo/sales/15885">SO 003917 in Odoo</a>`
❌ `See https://app.workiz.com/jobs/... for details`  ← forces copy-paste

The Activities detail modal already strips HTML and linkifies URLs in `note_full`, but writing real `<a>` tags lets you control the link **text** (e.g., "Open Workiz job" instead of the raw 80-char URL) and is more reliable than relying on linkify regex.

**Combined rule:**
- **Memory files** (local, Claude-only) → embed the content directly, name the file for Claude's lookup, no link.
- **Anything with a public URL** → real `<a href="...">` anchor with descriptive text, never copy-paste-style plain URL.

**Activity-note authoring checklist:**
1. Embed runbook content directly (Why / What to do / Pass criteria / Code locations / Memory file name).
2. For any external resource (Workiz, Odoo, Calendly, GitHub, etc.), write it as `<a href="URL">Descriptive text</a>`.
3. Never paste a raw URL as text and expect DJ to long-press → copy.

---

### Chatter message formatting standard
`feedback_chatter_format.md`
> All Odoo chatter messages must use pipe-separated plain text — no HTML tags

Use pipe-separated plain text for all `message_post` body values. Never use HTML tags (`<br/>`, `<p>`, `<strong>`, etc.).

**Why:** Odoo escapes HTML tags in chatter in two scenarios: (1) external JSON-RPC calls from Zapier always escape HTML; (2) Odoo 17+ server actions also escape HTML unless you use `Markup`, which requires an import that safe_eval blocks. Plain text with `|` separators looks clean and works everywhere.

**How to apply:**
```python
# CORRECT — works from both server actions and Zapier JSON-RPC
record.message_post(body='[2026-04-02 07:58:13] Synced from Workiz: Job Type: Maintenance | Tech: Dan Saunders | Workiz Status: Pending / Scheduled')

# WRONG — tags show as literal text
record.message_post(body='<p><strong>Synced</strong></p><br/>Job Type: Maintenance')
```

Format pattern: `[YYYY-MM-DD HH:MM:SS] Action label: Field: Value | Field: Value | Field: Value`

**Unicode emoji DOES work in chatter** — only HTML tags are escaped, not Unicode characters. Use emoji for status indicators:
```python
record.message_post(body='✅ COMPLETE: https://...')   # green checkmark
record.message_post(body='🔔 Follow-Up Activity Created | ...')
record.message_post(body='⚠️ WARNING: ...')
record.message_post(body='❌ FAILED: ...')
```
DJ prefers `✅` for completion messages. Use it on all success/completion `message_post` calls.

---

### Confirmation policy
`feedback_confirmation_policy.md`
> When to ask DJ for confirmation vs. just do it

Never ask for confirmation or approval. Just do the work end-to-end and report what was done when finished.

DJ does not know code and has no opinion on implementation details. As long as the work matches what was discussed, just do it.

This includes:
- File reads, writes, edits
- GitHub pushes to main
- API calls to Odoo and Workiz
- Test data creation and cleanup
- Code changes that implement agreed-upon behavior

Only stop and ask if:
- Something is genuinely ambiguous about WHAT to build (not how)
- An action is irreversible and destructive (e.g., deleting production customer data)

**Why:** DJ wants to walk away and come back to find it done. Every approval prompt is friction that defeats the purpose.
**How to apply:** Complete the full task, then give a brief summary of what was done. No mid-task check-ins.

---

### Definition of DONE jobs
`feedback_done_jobs_definition.md`
> When DJ says "Done jobs" he means x_studio_x_studio_workiz_status = 'Done' on sale.order

When DJ says "Done jobs" or "completed jobs" he always means **`x_studio_x_studio_workiz_status = 'Done'`** on `sale.order`.

**Why:** That field stores the Workiz job status synced to Odoo. Historic jobs (Phase 1 migration) and current jobs (Phase 3/4) all have this field populated. Invoice-based proxies are WRONG — historic jobs were never invoiced through Odoo.

**How to apply:**
- Filter: `['x_studio_x_studio_workiz_status', '=', 'Done']` on `sale.order`
- Never use `state='done'`, `invoice_status='invoiced'`, or `invoice_ids != False` as a proxy for Done
- Never use `date_order < now` alone — that picks up future-scheduled and pending jobs
- `amount_total` is the correct field for job value (sum of line items)

---

### Send emails via Odoo mail server
`feedback_email_via_odoo.md`
> Use Odoo mail.mail JSON-RPC to send emails — not Gmail MCP (Gmail MCP can only draft, not send)

Always send emails via Odoo's mail server using `mail.mail` JSON-RPC, not the Gmail MCP.

**Why:** Gmail MCP can only create drafts, not send. Odoo has a configured outbound mail server and can send directly.

**How to apply:**
```python
mail_id = rpc('mail.mail', 'create', [{
    'subject': '...',
    'body_html': '<p>...</p>',
    'email_to': 'windowandsolarcare@gmail.com',
    'auto_delete': True,
}])
rpc('mail.mail', 'send', [[mail_id]])
# auto_delete=True means the record disappears after send — that's expected/success
# send() returns no result key in JSON-RPC response — that's normal, not an error
```

**Why:** DJ confirmed this is the standard approach going forward (2026-04-19).

---

### GitHub deployment from Claude Code bash environment
`feedback_github_deploy_from_bash.md`
> Claude Code runs in bash on Windows — use powershell -Command wrapper to deploy to GitHub, not raw bash or Python

When deploying files to GitHub from Claude Code, the **preferred method** is direct bash using gh CLI and base64. PowerShell wrapper also works but sometimes fails with CLR errors.

**Why:** gh CLI is accessible from bash directly. Direct bash is faster and more reliable than PowerShell wrapper.

**Preferred (bash directly):**
```bash
SHA=$(gh api "repos/windowandsolarcare-hash/Odoo-Migration/contents/PATH/file.py" --jq '.sha') && CONTENT=$(base64 -w 0 "/c/Users/dj/Documents/Business/A Window and Solar Care/Migration to Odoo/PATH/file.py") && echo "{\"message\":\"DATE | file | desc\",\"content\":\"$CONTENT\",\"sha\":\"$SHA\",\"branch\":\"main\"}" | gh api "repos/windowandsolarcare-hash/Odoo-Migration/contents/PATH/file.py" --method PUT --input - --jq '.commit.sha' && echo "PUSHED"
```

**Fallback (PowerShell wrapper):**
```bash
powershell -Command "\$repo='windowandsolarcare-hash/Odoo-Migration'; \$filePath='PATH/file.py'; \$sha=(gh api \"repos/\$repo/contents/\$filePath\" --jq '.sha').Trim(); ..."
```

For Odoo server action 955 specifically: use Python xmlrpc.client (write a deploy_955.py script, run with `python deploy_955.py`, delete after).

---

### Use Python for GitHub deploy when the bash+powershell pipeline chokes
`feedback_github_deploy_python_fallback.md`
> CLAUDE.md says use deploy_to_github.sh (bash + powershell base64). It works MOST of the time but occasionally returns "Problems parsing JSON" HTTP 400. When that happens, fall back to a small Python script that does base64+JSON natively. No retry loop — just switch tools.

CLAUDE.md prescribes a bash+powershell+base64 pipeline for pushing files to GitHub via the GH API. It works most of the time. Occasionally it returns **"Problems parsing JSON" HTTP 400** — particularly on larger files (300+ lines) and files with lots of nested quotes/special characters. PowerShell's `[System.Convert]::ToBase64String` reliably introduces line breaks that break the JSON payload despite the heredoc approach.

**Why:** 2026-04-29 — pushing `quote.html` (a single 700-line HTML file with embedded JS) failed via the bash script. The Python fallback succeeded on the first try.

**How to apply:**

When `deploy_to_github.sh` (or the inline bash+powershell pattern in CLAUDE.md) returns `"Problems parsing JSON" HTTP 400`, do not retry the same command. Instead, use this Python pattern:

```python
import base64, json, subprocess, tempfile, os

REPO = 'windowandsolarcare-hash/saunders-render-app'

def deploy(path_in_repo, local_path, msg):
    with open(local_path, 'rb') as f: data = f.read()
    content_b64 = base64.b64encode(data).decode('ascii')
    try:
        sha = subprocess.check_output(
            ['gh','api',f'repos/{REPO}/contents/{path_in_repo}','--jq','.sha'],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        sha = ''  # new file
    payload = {"message": msg, "content": content_b64, "branch": "main"}
    if sha: payload["sha"] = sha
    fd, tmp = tempfile.mkstemp(suffix='.json', text=True)
    with os.fdopen(fd, 'w') as f: json.dump(payload, f)
    r = subprocess.run(
        ['gh','api',f'repos/{REPO}/contents/{path_in_repo}','--method','PUT','--input',tmp],
        capture_output=True, text=True)
    os.unlink(tmp)
    if r.returncode == 0:
        print('OK', json.loads(r.stdout)['commit']['sha'][:8])
    else:
        print('FAIL', r.stderr[:300])
```

**Why this works:** Python's `base64.b64encode()` returns a single line with no MIME-style breaks. `json.dump()` produces valid escaping. `tempfile.mkstemp` gives a real Windows-friendly path (avoids the `/tmp/...` issue when called from PowerShell-spawned bash).

**Important:**
- This is a fallback, not the default. Stick with the bash script for normal use — it's documented in CLAUDE.md and easier to understand.
- If a file fails twice via bash, switch to Python without trying a third time. Token-wasting retry loops are explicitly called out in `feedback_proactive_inefficiency_capture.md`.
- For multi-file deploys, factor a `deploy()` helper and call it once per file. Don't loop bash and Python separately.

**Related memory:**
- `feedback_github_deployment_bash.md` — the canonical bash approach
- `feedback_proactive_inefficiency_capture.md` — don't retry-loop, switch tools

---

### GitHub Deployment — Bash Approach (Not PowerShell)
`feedback_github_deployment_bash.md`
> Reliable bash + base64 + temp file method for GitHub deployments. PowerShell ConvertTo-Json causes "Problems parsing JSON" errors (4-5 retries typical). Use the deploy_to_github.sh script for all future file pushes.

## Rule

**Always use bash + base64 + temp file approach for GitHub deployments. NEVER use PowerShell ConvertTo-Json.**

## Why

**PowerShell ConvertTo-Json failures:**
1. `[System.Convert]::ToBase64String()` adds MIME-style line breaks every 76 characters by default
2. PowerShell escapes special characters in JSON payloads in ways that break validation
3. Result: HTTP 400 "Problems parsing JSON" errors
4. Typical failure pattern: 4-5 retry attempts before switching methods
5. Token cost: 50-100 tokens wasted per failed attempt

**Why bash approach works:**
- Handles Windows file paths cleanly via PowerShell subshell (read only, no escaping)
- Constructs raw JSON string in temp file (no shell interpretation)
- Base64 encoding stays inline without extra newlines
- One-shot success rate: 99%+
- Token cost: ~1 call, always succeeds

## How to Apply

**Use the deploy_to_github.sh script** (in both repos: Odoo-Migration and cheryl-real-estate)

```bash
./deploy_to_github.sh \
  windowandsolarcare-hash/Odoo-Migration \
  1_Production_Code/zapier_phase3_FLATTENED_FINAL.py \
  "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\1_Production_Code\zapier_phase3_FLATTENED_FINAL.py" \
  "2026-04-26 | zapier_phase3.py | fixed bug"
```

**Or use the fallback bash command directly:**

```bash
repo="windowandsolarcare-hash/Odoo-Migration"
filePath="1_Production_Code/zapier_phase3.py"
localFile="C:\\Users\\dj\\Documents\\Business\\A Window and Solar Care\\Migration to Odoo\\1_Production_Code\\zapier_phase3.py"

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

**Never use:**
```powershell
# ❌ DO NOT USE — causes "Problems parsing JSON" errors
$payload | ConvertTo-Json | gh api "repos/$repo/contents/$filePath" --method PUT --input -
```

## When to Update

- When deploying any file to GitHub (Zapier scripts, documentation, etc.)
- The script is self-contained and idempotent
- No SHA lookup needed for new files (GitHub API auto-handles)
- For existing files, the script fetches SHA automatically if needed

## Related Decisions

- Script location: Both repos (windowandsolarcare-hash/Odoo-Migration and cheryl-real-estate)
- CLAUDE.md updated: 2026-04-26 with full documentation and fallback command
- This feedback applies to ALL future sessions and projects

---

### Local Saunders Render App copy may lag deployed code — diff before pushing
`feedback_local_vs_deployed_drift.md`
> 2026-04-27 — pushed local dashboard.py and unintentionally regressed two prior Workiz quirk fixes (commits 7cbd848 + 405a31d) because the local file was older than what was running on Render. Diff before deploy.

When editing `C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py` (or any file in that repo), the local copy may be stale relative to what's deployed. This bit me on 2026-04-27: I deployed follow-up endpoints, and the deploy overwrote two earlier `workiz_post` fixes (UUID auto-inject for update/delete, and Status="Pending" auto-inject when SubStatus present) because my local file pre-dated those commits.

**Why:** the dashboard.py at `C:\Users\dj\AppData\Local\Temp\deployed_dashboard.py` is a snapshot pulled FROM Render at some point. The repo working copy is at `C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py`. They drift independently. The temp file got updated when those Workiz fixes happened (or when DJ pulled fresh from Render); the repo working copy didn't.

**How to apply:**

Before deploying any change to that repo, run a fast sanity check:

```bash
gh api repos/windowandsolarcare-hash/saunders-render-app/contents/routers/owner/dashboard.py --jq '.content' | base64 -d > /tmp/remote_dashboard.py
diff /tmp/remote_dashboard.py "C:/Users/dj/Documents/Business/Saunders Render App/routers/owner/dashboard.py" | head -200
```

If the diff shows changes you don't recognize as your own work — STOP. Either:
1. Pull the remote version into the local working copy first, then layer your edits on top
2. Or pinpoint exactly which lines have drifted and reapply the fix as part of your push

**Specific fixes that exist in the deployed code and could be lost on a sloppy push** (verify these before deploying any dashboard.py change):
- `workiz_post()` should auto-inject `UUID`/`ID` for job/update and job/delete endpoints (regex match on URL path)
- `workiz_post()` should auto-inject `Status="Pending"` when `SubStatus` is in body
- `_sessions` history is persisted to Odoo `ir.config_parameter` under `render.session.{id}` (not just in-memory)

If you're unsure whether the local file has the fix, grep for the regex `^def workiz_post` and look for the lines `re.match(r'^job/(update|delete)/...` and `if 'SubStatus' in data and 'Status' not in data`. Both should be present.

**Token cost of this rule:** ~5 seconds to run the diff. Cost of getting it wrong: 30+ minutes to re-diagnose a bug we already fixed.

---

### Never remove or comment out working code without DJ approval
`feedback_never_remove_working_code.md`
> Commenting out or deleting existing working code requires DJ's explicit approval first — adding code is fine, removing is not

NEVER comment out, delete, or disable existing working code without DJ's explicit approval first.

**Why:** This codebase was built over months, debugged, and agreed to work. Every line exists for a reason that may not be obvious in the moment. Removing code unilaterally — even with good intentions, even "temporarily" — can silently break things that took significant effort to get right. The `update_sales_order_date` calls in Phase 3 were commented out with a plausible-sounding reason ("date_order now set at creation time") that turned out to be wrong, causing a recurring date bug.

**How to apply:** Adding new code, new features, new logging = fine, do it. But if you think existing code should be removed or commented out, STOP — explain to DJ why you think it should be removed and wait for explicit approval before touching it. If in doubt, leave it in and add a comment explaining the concern instead of removing it.

---

### No guessing on Odoo field names
`feedback_no_guessing_on_fields.md`
> Never guess at Odoo field names. Verify in CLAUDE.md field table, memory files, or by querying Odoo directly before using any field.

Never guess at Odoo field names — not for sale.order, res.partner, or any model.

**Why:** DJ introduced `commercial_partner_id` on sale.order without verifying it exists. Field was invalid — broke the live stale SOs endpoint immediately after deploy. This codebase took months to build and bad field guesses cause real outages.

**How to apply:**
1. Check CLAUDE.md field table first
2. Check memory files (project_*.md) for known fields
3. If not found: query Odoo via JSON-RPC (`search_read` with the field, or `fields_get`) before writing any code
4. Never assume a field exists because it "should" exist in standard Odoo — this instance has heavy customization and some standard fields are absent (e.g. `account.payment` has no `ref` field in Odoo 19)

---

### Don't re-print tables/lists/buckets across responses — use a working file
`feedback_no_re_listing.md`
> When work involves a list/table that spans multiple turns (SO triage, payment scans, batch reviews), write it to a file once and reference it. Re-printing forces DJ to scroll back through compacted history to find the canonical version, and each repeat tends to drop detail.

When a task involves a list, table, or bucketed data that we'll revisit across multiple turns (SO triage lists, payment scans, batch deletions, line-item reviews, etc.):

1. **Write the data to a working file** — typically under `4_Reference_Data/` with a date-stamped name (e.g. `so_triage_apr27.md`)
2. **Update the file as items are resolved** — not the chat
3. **In chat, reference the file by name** — don't re-paste the table
4. **Chat replies stay terse** — decisions and actions only

**Why:** DJ flagged this on 2026-04-27 — *"why do you keep repeating your answers... each additional repeat is missing some part. so i have to go all the way up to the first response (find it). then come back down to type next response. very confusing and time consuming."* Lossy compaction over a long session makes the problem compound: each re-print may drop a column or summarize a bucket, so the user no longer trusts any single copy as canonical. They end up scrolling far back to find the original, which kills flow.

**How to apply:**
- Triggers: any time I'm about to print a list of >5 items that we'll act on across turns. SOs, contacts, jobs, accounts, anything.
- The first time, dump it to a file and tell DJ the path. Every subsequent turn, reference the file (e.g. "Bucket 1a in `so_triage_apr27.md`") and avoid re-printing.
- One exception: a final "here's what got done" recap at the end of a triage session is fine — that's a closeout, not a working reference.
- This is independent of `feedback_save_filter.md` (memory writes) and `feedback_chatter_format.md` (Odoo chatter formatting). Different surface, same principle: write once, reference forever.

Related: this is also why `MEMORY.md` is an index — same principle at the meta level (memory files exist so chats don't keep re-deriving the same facts).

---

### Odoo HTML field color technique
`feedback_odoo_html_field_colors.md`
> How to create colored status indicators in Odoo form fields using HTML field type + Bootstrap classes

Use an HTML field type (not char) with Bootstrap CSS classes to display colored text in Odoo form views. DJ likes this pattern and wants to use it more.

**Why:** Char fields cannot render HTML. HTML fields with Bootstrap classes survive Odoo's sanitizer (inline `style="color:red"` gets stripped, but `class="text-danger"` works). The field must be `readonly="True"` in the view so users don't see the rich text editor.

**How to apply — full recipe:**

**Step 1: Create the HTML field via API**
```bash
curl -X POST "https://window-solar-care.odoo.com/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"service":"object","method":"execute_kw","args":["window-solar-care",2,"API_KEY","ir.model.fields","create",[{"model_id":<MODEL_ID>,"name":"x_studio_my_flag","field_description":"My Flag","ttype":"html","store":true}]]}}'
```
Get model_id first: search `ir.model` where `model = 'sale.order'` → ID 670.

**Step 2: Add to form view as readonly**
```xml
<field name="x_studio_my_flag" readonly="True" string="My Flag"/>
```

**Step 3: Write colored HTML from server action or Phase code**
```python
# Green
'<span class="text-success"><b>OK - details here</b></span>'

# Red
'<span class="text-danger"><b>MISMATCH - details here</b></span>'

# Orange/warning
'<span class="text-warning"><b>PENDING - details here</b></span>'

# Blue/info
'<span class="text-info"><b>INFO - details here</b></span>'
```

**Bootstrap color classes available in Odoo:**
- `text-success` → green
- `text-danger` → red
- `text-warning` → orange/yellow
- `text-info` → blue
- `text-muted` → grey

**Important gotchas:**
- If field already exists as char: must remove from all views first, then unlink field, then recreate as html, then re-add to views
- Odoo blocks deleting fields that are still in views — error: "Cannot rename/delete fields that are still present in views"
- Find which views reference the field: search `ir.ui.view` where arch_db contains the field name
- Remove field from view arch_db → delete field → create as html → re-add to view
- Sale.order model ID = 670 (for this Odoo instance)
- Studio customization view ID = 1385 (sale.order Studio form customization)

---

### odoo_rpc write() positional vs kwargs — CRITICAL
`feedback_odoo_rpc_write_pattern.md`
> odoo_rpc 4th arg is kwargs, not positional. write(vals) needs vals INSIDE args list or it crashes with "unexpected keyword argument"

`write(vals)` takes `vals` as a positional argument, NOT a keyword argument. The `odoo_rpc` function signature is:

```python
def odoo_rpc(model, method, args, kwargs=None):
    # kwargs is passed as **kwargs to the Odoo method
```

**WRONG — passes vals as **kwargs, causes TypeError:**
```python
odoo_rpc('sale.order', 'write', [[so_id]], {'field': value})
#                                ^^^^^^^^  ^^^^^^^^^^^^^^^^
#                                args      kwargs — WRONG for write()
```

**RIGHT — vals inside the args list as the second positional arg:**
```python
odoo_rpc('sale.order', 'write', [[so_id], {'field': value}])
#                                ^^^^^^^^^^^^^^^^^^^^^^^^
#                                args includes both id list AND vals dict
```

**Why:** Odoo's `write(self, vals)` signature makes `vals` a positional argument. When passed as `**kwargs`, Python raises `TypeError: SaleOrder.write() got an unexpected keyword argument 'field_name'`.

**How to apply:** Any time you write `odoo_rpc(..., 'write', ...)`, the values dict MUST be the second element inside the args list. This applies to `write` on any model (`sale.order`, `sale.order.line`, `res.partner`, `account.move`, etc.).

**Exception — methods that DO take keyword args (4-arg form is correct):**
- `message_post(body=..., subject=...)` — keyword args, so `odoo_rpc(..., 'message_post', [[id]], {'body': text})` is fine
- `search_read(domain, fields=..., limit=...)` — keyword args OK

**Discovered:** 2026-05-02 — `_sync_so_with_workiz()` had 4 broken write calls. Error: `SaleOrder.write() got an unexpected keyword argument 'date_order'`. Fixed commit `17d277ee`.

---

### Planning constraints filter
`feedback_planning_constraints.md`
> Always filter architecture suggestions through DJ's four constraints before presenting them

Before suggesting any architecture, model, tool, or approach, run it through these four filters first. If it fails any of them, don't suggest it — find an alternative that passes all four.

**The four filters:**
1. **No new Odoo seats** — res.users records cost money, never suggest them for app users
2. **No custom Odoo models** — SaaS platform blocks them without support approval, last resort only
3. **One Odoo instance** — everything runs on window-solar-care.odoo.com, no spinning up new instances until growth demands it
4. **Scale across businesses** — DJ may offer this platform to other businesses (fiduciary, real estate, etc.), so solutions must work beyond W&SC

**Why:** DJ is building a scalable multi-business platform on a constrained budget. Textbook "best practice" answers (res.users, custom models, separate Odoo instances) are wrong for his situation. The right answer is the most practical one given real constraints.

**How to apply:** When planning anything — login systems, data models, integrations — run the suggestion through all four filters silently before presenting it. If you catch yourself about to suggest something that fails a filter, find the alternative first.

---

### Proactive Inefficiency Capture — I Own This
`feedback_proactive_inefficiency_capture.md`
> When I discover trial-and-error patterns, repetitive failures, or inefficient processes, I MUST document and save them immediately without waiting for DJ's request. This is my responsibility, not his job to ask.

## Rule

**When I encounter trial-and-error, repetitive errors, or inefficient patterns, I own the responsibility to:**
1. **Recognize it** — "I just did this same thing 5 times differently"
2. **Solve it** — "Here's the working approach"
3. **Document it immediately** — Don't wait for DJ to ask
4. **Save to memory** — Both local (memory/) and shared (SHARED_MEMORY.md)
5. **Update CLAUDE.md** — So CLAUDE.md becomes the canonical playbook

**No asking. No waiting for end of session. No "should I save this?" Just do it.**

## Why

**Token efficiency:** Today's GitHub deployment cost 50-100 wasted tokens across 4-5 failed PowerShell attempts. That repeats across future sessions = 100+ tokens wasted per future deployment cycle.

**Time efficiency:** Next time I or any chat hits the same problem, I grab the documented solution instead of experimenting again.

**Trust:** DJ shouldn't have to ask. If I discover something useful, saving it is part of my job, not an optional task.

## How to Recognize Patterns Worth Saving

| Pattern | Example | Save As |
|---|---|---|
| Trial-and-error loop | Tried 5 PowerShell approaches, bash worked | Feedback (how to do it right) |
| Repeated process | "I always do X, Y, Z when deploying" | Reference (playbook) or feedback (rule) |
| Bug with root cause | "PowerShell line breaks cause JSON errors" | Project (technical fact) + feedback (rule) |
| Process blocker removed | "Deploy script eliminates SHA lookup headache" | Project (improvement) |
| Cross-session pattern | "This will help Render Claude too" | SHARED_MEMORY.md addition |

## When to Save

- **During session:** The moment I recognize a pattern worth saving (don't wait for end)
- **Immediately after solving:** Before moving to the next task
- **No threshold:** If I think a future chat would benefit, it's worth saving. Better to over-document than under-document.

## What Gets Saved Where

- **Technical facts** (bugs, API quirks, behaviors) → `project_*.md` with **Why:** and **How to apply:**
- **Process rules** (do this, not that) → `feedback_*.md` with rule + why + how to apply
- **Across-chat knowledge** (affects Render Claude, future projects) → Also add to SHARED_MEMORY.md
- **Project playbook** (canonical approach) → Update CLAUDE.md section

## Example: Today's GitHub Deployment

- ✅ Recognized: 5 PowerShell failures, bash worked
- ✅ Solved: bash + base64 + temp file approach
- ✅ Documented: feedback_github_deployment_bash.md (local)
- ✅ Shared: SHARED_MEMORY.md (Render Claude sees it next session)
- ✅ Canonical: CLAUDE.md (GitHub deployment section rewritten)
- ✅ Script: deploy_to_github.sh (both repos, copy-paste ready)

Result: Next time, no trial-and-error. Just use the script.

## DJ's Authority

DJ doesn't need to approve or ask for this. If I see inefficiency, I fix and document it. If he disagrees with what I saved, he can tell me and I adjust. But the default is: **I own the responsibility to make future sessions faster.**

---

### Regression guard for GitHub pushes — never push from a stale local copy
`feedback_regression_guard_pushes.md`
> 2026-04-30 incident — another Claude Code chat had a 3565-line copy of dashboard.py and pushed it over the live 5842-line version, wiping 2277 lines (Manage Shifts CRUD, GPS endpoints, Stale SOs, whoami, todos/reactivate). Two guards now exist: (1) safe_deploy.py at C:\Users\dj\safe_deploy.py refuses local-smaller-than-deployed pushes; (2) Render Claude's github_push_file tool refuses voice pushes that drop >100 lines or >25% bytes unless acknowledge_regression:true. Use safe_deploy.py for ALL pushes to dashboard.py and other large files.

**Why:** A different Claude Code chat regressed dashboard.py from 5842 lines to 3565 lines in one push. The other chat had been editing what it thought was the current file but was actually a stale snapshot. The push silently wiped Manage Shifts (Danny couldn't see his shifts), GPS endpoints, Stale SOs page, and more. DJ noticed only when "Error: Load Failed" came back. Restoration took ~15 minutes plus an emergency redeploy.

**How to apply:**

1. **Before editing any large file (>1000 lines) in `Saunders Render App/`** — pull the current GitHub version FIRST and compare to local:
   ```bash
   gh api repos/windowandsolarcare-hash/saunders-render-app/contents/<path> --jq '.content' | base64 -d > /tmp/current
   wc -l /tmp/current "<local path>"
   ```
   If GitHub version is significantly larger than local, your local is stale — refresh from GitHub before editing.

2. **Push via `safe_deploy.py`** instead of one-off scripts. Located at `C:\Users\dj\safe_deploy.py`. It does the freshness check automatically and refuses to push if local is >25% smaller or >100 lines shorter than deployed.

   ```bash
   python C:/Users/dj/safe_deploy.py \
     --repo  windowandsolarcare-hash/saunders-render-app \
     --path  routers/owner/dashboard.py \
     --local "C:\\Users\\dj\\Documents\\Business\\Saunders Render App\\routers\\owner\\dashboard.py" \
     --msg   "2026-04-30 | dashboard.py | what changed"
   ```
   Add `--force` only after personally diffing and confirming the deletions are intentional.

3. **Render Claude's `github_push_file` tool** has the same guard server-side (commit `41351838`). Voice-driven pushes refuse if they drop >100 lines or >25% bytes unless `acknowledge_regression: true` is in the call. So even if a voice command tries to push a stale version, it'll be blocked with a clear message.

**Files / commits:**
- `C:\Users\dj\safe_deploy.py` — local deploy helper (added 2026-04-30)
- `Saunders Render App/routers/owner/dashboard.py` — github_push_file with guard (commit 41351838)
- `CLAUDE.md` updated 2026-04-30 with mandatory pre-push checklist

**Override semantics:** When the guard fires, the calling code should:
- DIFF locally and verify the deletions are intentional
- Then re-call with `--force` (CLI) or `acknowledge_regression: true` (Render Claude tool)
- Never bypass blindly — that's how we lost 2277 lines

**Related memory:**
- `feedback_local_vs_deployed_drift.md` — the original observation (2026-04-27) that local Saunders Render App copies can lag deployed
- `feedback_github_deployment_bash.md` — the bash+base64 deploy approach
- `feedback_github_deploy_python_fallback.md` — Python fallback when bash chokes on large files

---

### SHARED_MEMORY save filter — save at the right time, not all the time
`feedback_save_filter.md`
> DJ wants me to keep auto-saving (he doesn't want to invoke a skill). But filter what goes into SHARED_MEMORY so it doesn't bloat Render Claude's context.

DJ confirmed 2026-04-26 that he wants me to keep auto-saving discoveries to SHARED_MEMORY (per the dual-write rule in CLAUDE.md). He does NOT want a `/save` slash command he has to invoke. The behavior is mine to own.

**His one ask:** be deliberate about WHEN — save at the right time, not all the time.

**Why:** SHARED_MEMORY loads into Render Claude's context every session. Bigger file = bigger system prompt = more tokens per query = costs DJ money. Same cost concern that came up with API-key spend.

**The filter to apply before each SHARED_MEMORY write:**

GOES IN:
- Workiz/Odoo API quirks Render Claude calls against (UUID-in-body, SubStatus parent, defaults required)
- Field name conventions, field defaults
- Status models, business rules DJ explicitly stated
- Tool semantic changes Render Claude needs to know (new tool exists, tool now copies extra fields)

STAYS OUT (local memory only):
- Implementation architecture (where session history lives, internal helpers)
- Why-we-fixed-it commit history (git log covers this)
- My debugging notes
- Things already in SHARED_MEMORY (don't duplicate)
- Things already in Render Claude's system prompt (don't restate)

**The test question:** "Does Render Claude need to know this AT RUNTIME to behave correctly?" If no, it's local memory only.

**Volume calibration:** typical days produce 1–2 SHARED_MEMORY-worthy discoveries. A day with 5+ is unusual (today 2026-04-26 was that — five Workiz fixes in a row). When volume is high, it should be because the DAY had many genuine discoveries, not because I'm dual-writing aggressively.

**If DJ ever asks "why are you saving so much?":** lead with the cause (today's discoveries) rather than jumping to "let me change the behavior." He may just want the explanation, not a fix.

**How to apply:** Before pushing any SHARED_MEMORY edit, run the filter mentally. If a candidate fails the filter, save it as local-only and skip the dual-write. Don't ask DJ — own the judgment.

---

### How to send email with PDF attachment via Odoo JSON-RPC
`feedback_send_email_with_attachment.md`
> Exact pattern for creating and sending an email with a file attachment through Odoo mail.mail using JSON-RPC (not XML-RPC)

# Sending Email with Attachment via Odoo

Use JSON-RPC (not XML-RPC — XML-RPC fails because `send` returns None which can't be marshaled).

**Why:** XML-RPC raises `TypeError: cannot marshal None` when `mail.mail.send()` returns None. JSON-RPC handles None gracefully.

**How to apply:** Use this pattern any time you need to send an email with or without an attachment from a local Python script.

```python
import requests, base64

ODOO_URL = 'https://window-solar-care.odoo.com'
ODOO_DB = 'window-solar-care'
ODOO_USER_ID = 2
ODOO_API_KEY = '7e92006fd5c71e4fab97261d834f2e6004b61dc6'

def rpc(model, method, args, kwargs=None):
    payload = {
        'jsonrpc': '2.0', 'method': 'call', 'id': 1,
        'params': {
            'service': 'object', 'method': 'execute_kw',
            'args': [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args, kwargs or {}]
        }
    }
    r = requests.post(f'{ODOO_URL}/jsonrpc', json=payload)
    result = r.json()
    if 'error' in result:
        raise Exception(result['error']['data']['message'])
    return result.get('result')  # use .get() — send() returns None, that's normal

# Read and base64-encode the file
with open(r'C:\path\to\file.pdf', 'rb') as f:
    file_data = base64.b64encode(f.read()).decode()

# Create the mail record with attachment inline
mail_id = rpc('mail.mail', 'create', [{
    'subject': 'Your subject here',
    'email_to': 'recipient@example.com',
    'email_from': 'windowandsolarcare@gmail.com',
    'body_html': '<p>HTML body here</p>',
    'attachment_ids': [(0, 0, {
        'name': 'Filename.pdf',
        'datas': file_data,
        'mimetype': 'application/pdf',
    })],
}])

# Send it — returns None, that's expected
rpc('mail.mail', 'send', [[mail_id]])
```

**Verification:** After sending, Odoo deletes the mail record from the queue. If `search_read` for that mail_id returns None, the email was sent successfully — not an error.

**PDF generation:** Use `reportlab` (already installed). Generate the PDF locally, then attach via the pattern above.

---

## Project Knowledge
*76 file(s)*

### Odoo 19 server action reserved variable names
`feedback_odoo_reserved_variable_names.md`
> response and result are reserved in Odoo 19 server action eval context — never use them as local variable names

In Odoo 19 server actions, the eval context treats certain variable names as special return values, just like `action`:

- `response` — if set, Odoo uses it as the HTTP response (causes `'Response' object has no attribute 'setdefault'` error)
- `result` — potentially also captured

**Why:** Using `response = requests.get(...)` overwrites Odoo's internal response variable, causing the requests.Response object to be returned as the action result, which crashes `clean_action()`.

**How to apply:** In ALL server action code, never use `response` or `result` as local variable names. Use `workiz_resp`, `workiz_data`, `api_resp`, `api_result`, or similar prefixed names instead.

---

### account.payment has no 'ref' field in Odoo 19 — use 'memo'
`project_account_payment_no_ref_field.md`
> 2026-04-28 — Schedule endpoint broke ("No jobs today") because new code queried account.payment.ref which doesn't exist. Use memo for the customer-facing reference instead. Also: wrap any new helper that touches a less-trafficked model in try/except so a schema mismatch can never block the main page from rendering.

In this Odoo 19 instance, `account.payment` does NOT have a `ref` field. Reading it raises `ValueError: Invalid field 'ref' on 'account.payment'`. The only customer-visible reference field is `memo` — that's where `account.payment.register` writes the `communication` value from `record_check_payment`.

**Why:** Caused a "No jobs today" outage on 2026-04-28 — the new last-payment-method preselect added an `account.payment.search_read` with `fields=['memo', 'ref']`. The exception bubbled out of `_last_payment_method_by_partner` and broke `tool_schedule` for the field assistant.

**How to apply:**
- For Zelle/Venmo memo detection, the only field to read is `memo`.
- Don't assume Odoo classics like `ref` exist — query `ir.model.fields` first if uncertain.
- More importantly: **any auxiliary lookup that decorates a primary response (preselects, badges, hints) should be wrapped in try/except.** The primary endpoint must keep working even if the side-trip fails. Pattern:

```python
def _safe_decorator(...):
    if not inputs: return {}
    try:
        # actual lookup
        return result
    except Exception:
        return {}  # graceful degradation — the main feature still works
```

Applied to `_last_payment_method_by_partner` after this incident.

---

### Activities module — full reference (Render app /owner/activities)
`project_activities_module.md`
> Comprehensive guide to the Activities module: 4th hub card, To-Dos + Follow-Up flow, all endpoints, data flow, gotchas, and rules for safe changes. Read this BEFORE editing anything related to /owner/activities, /api/todos, /api/followup/*, or activities.html.

# Activities Module — Read this before editing

This module is small in code volume but has subtle data-flow rules. Future chats keep getting it wrong because they assume it works like Field Assistant. It doesn't.

## What it is

The 4th hub card on `/owner/`. Standalone page at `/owner/activities`. Currently houses two things:
- **Open** sub-tab — to-do list (mail.activity records assigned to DJ)
- **Done** sub-tab — recently completed activities (last 30 days)

It is **intended to grow** — DJ said "a whole bunch of other things will go here." Don't refactor it as a single-purpose to-do screen. Treat it as a generic admin/activities hub.

The To-Dos used to live in the right panel of Field Assistant (`field.html`). That tab + dispatcher entry was removed when this module was built (2026-04-27). Dead modal HTML/JS may still be in `field.html` — it's intentionally left there as a safety belt; do **NOT** clean it up unless DJ explicitly asks.

## Files (canonical paths)

| File | Role |
|---|---|
| `Saunders Render App/routers/owner/dashboard.py` | All backend endpoints |
| `Saunders Render App/static/owner/activities.html` | The page (Open/Done tabs, follow-up modal) |
| `Saunders Render App/static/owner/index.html` | Hub card (4th tile, emerald `--card-activities #10b981`) |
| `Saunders Render App/static/owner/field.html` | Field Assistant — to-do tab REMOVED here. Don't touch unless asked |

Repo: `windowandsolarcare-hash/saunders-render-app` (NOT the Odoo-Migration repo).

## Endpoints (all in dashboard.py)

| Method + Path | Purpose | Notes |
|---|---|---|
| `GET /activities` | Serves `activities.html` | Just file read, no auth at server level — page itself reads `localStorage.wsc_ac` and bounces to `/owner/` if missing |
| `GET /api/todos` | Open to-dos for the Open tab | Optimized 2026-04-27: batched partner reads + 60d window. `TODOS_USE_LEGACY` flag rolls back |
| `GET /api/todos/done` | Last 30d archived activities for Done tab | Reads `active=False` with `active_test:False` context. Pulls `x_followup_workiz_uuid` to render the Workiz pill |
| `POST /api/followup/preview` | Builds SMS text + cooldown info — read-only | NEVER writes to Odoo or Workiz. Front-end shows the result in the modal so DJ can edit before sending |
| `POST /api/followup/launch` | Actually sends the text via Workiz | Heavy: Odoo reads + Workiz job-create + Workiz substatus update + Odoo writes + chatter post + activity archive |
| `POST /api/followup/markdone` | Close to-do without sending | For when DJ handled the follow-up another way |

## Constants (top of follow-up section, ~line 3236)

```python
FOLLOWUP_COOLDOWN_DAYS = 45
FOLLOWUP_SUBSTATUS     = 'Follow Up Trigger'   # parent Status="Pending"
FOLLOWUP_JOB_TYPE      = 'Follow Up Lead'

# /api/todos optimization flags (~line 2456)
TODOS_USE_LEGACY = False
TODOS_DEADLINE_WINDOW_DAYS = 0   # 0 disables the date filter; was 60 but hid 29 of 31 todos
```

## SMS template — single edit point

`_build_followup_sms(first_name, property_addr, last_visit_str, frequency, city, full_name, street)` at ~line 3241 in dashboard.py. **This is the only place to edit follow-up SMS wording.** It also embeds the Calendly URL with city-based slug (same map reactivation uses: pmsg, rm, pd, iw, indlaq, ht, gb fallback).

## The Follow-Up flow — what actually happens on /api/followup/launch

This is where future chats get confused. The flow is:

1. Re-validate contact (cooldown, blacklist, Do Not Contact) — front-end values are NEVER trusted
2. Find a source Workiz UUID by searching latest sale.order with `x_studio_x_studio_workiz_uuid != False` for this partner OR any of their Property children (via `partner_shipping_id`)
3. `workiz_get(job/get/{source_uuid}/)` — pull the source job
4. Validate phone (≥10 digits) and PostalCode (5 digits) from the source
5. Build a NEW Workiz job payload with:
   - `JobType = 'Follow Up Lead'`
   - **No JobDateTime** (unscheduled — important; this is why job/all/ won't find it later)
   - `information_to_remember = sms_text` (Workiz automation reads this field on substatus change)
6. `workiz_post('job/create/', payload)` — get back new UUID
7. `time.sleep(3)` race-condition workaround (same as reactivation)
8. `workiz_post('job/update/{new_uuid}/', {'SubStatus': 'Follow Up Trigger'})` — this fires the Workiz automation that sends the SMS
9. Post chatter to **the contact** (not the SO): `📨 Text sent · Workiz job link · SubStatus: ...`
10. Write `x_studio_last_followup_sent = today` on res.partner (cooldown anchor)
11. Archive the to-do **manually**: `mail.activity.write({'active': False, 'date_done': today, 'x_followup_workiz_uuid': new_uuid})`

### CRITICAL — DO NOT call `mail.activity.action_done()` on follow-up activities

Odoo auto-generates "Call done" in chatter when you call `action_done()` on an activity whose type is "Call" — and our follow-up activities use the Call type. That message is misleading because we just sent a TEXT, not made a call. The launch endpoint deliberately uses `write({active: False, date_done: ...})` instead. Only the `markdone` endpoint (when DJ presses "Mark Done" without sending) uses `action_done`, with `unlink` as a fallback.

If you "fix" this to call action_done, you reintroduce the "Call done" chatter bug DJ already flagged once. Don't.

## Workiz POST body quirks (handled by `workiz_post` helper)

These are auto-injected — you don't need to remember them, but you should know they exist:
- `UUID` is required in the body for `job/update/{UUID}/` (URL alone is not enough — 400 otherwise)
- `ID` is required in the body for `job/delete/{UUID}/`
- `Status='Pending'` must be sent alongside any `SubStatus` (otherwise 400 "Could not update sub status with no parent status provided")
- `auth_secret` must be in the JSON body for POST endpoints (URL works only for GET)

The helper handles all of these. **If you ever rewrite or replace `workiz_post`, preserve these auto-injections** or send fails. Drift between local and deployed `dashboard.py` regressed these once already (see `feedback_local_vs_deployed_drift.md`).

## Custom Odoo fields used

| Field | Model | Type | ID | Purpose |
|---|---|---|---|---|
| `x_studio_last_followup_sent` | `res.partner` | date | 20151 | 45-day cooldown anchor. Cleared = eligible. Today = blocked |
| `x_followup_workiz_uuid` | `mail.activity` | char | 20154 | Stamped on launch so the Done tab can rebuild the Workiz link |

## Data resolution — the partner_id rule (where chats get this wrong)

A `mail.activity` can be linked to `res.partner` OR `sale.order`. The follow-up flow needs the **contact** partner, NOT a Property record. Resolution rules:

- `res_model = 'res.partner'` and the partner has `x_studio_x_studio_record_category = 'Property'` → walk up to `parent_id`. Otherwise use `res_id` directly.
- `res_model = 'sale.order'` → read SO's `partner_id`, then apply the same Property→parent walk to that.
- `res_model` is anything else (e.g. `hr.employee`) → `partner_id` stays `None`.

`/api/todos` has this baked in. If you write a new endpoint that operates on activities, replicate it.

## /api/todos performance notes

Pre-optimization (legacy): one search_read for activities (limit 30) + one read for SOs + **one separate read.partner per row inside the loop**. With 30 activities that's 30+ sequential round-trips at ~150ms each ≈ 4-5s total.

Post-optimization (2026-04-27, current default): batched into:
- 1 search_read for activities (with `date_deadline` window filter)
- 1 read for all sale.orders referenced
- 1 read for ALL res.partners referenced (collected from both res.partner activities and SO partner_ids)

Rollback path: flip `TODOS_USE_LEGACY = True` and redeploy. The legacy function is preserved verbatim as `_api_todos_legacy()` below the new one.

**Date window currently DISABLED** (`TODOS_DEADLINE_WINDOW_DAYS = 0`) because DJ has ~29 of 31 to-dos scheduled >60d out, and the filter was hiding them. Set to a non-zero value (e.g. 90, 180) to re-enable the cut. The batched-reads optimization is the real perf win and stays on regardless. Undated activities (`date_deadline = False`) are always included when the filter is active.

## activities.html structure

- Header with WSC/Saunders branding, emerald accent
- Two sub-tabs at top: Open / Done (`#sub-open`, `#sub-done`, JS `showSubTab(name)`)
- Open tab: card list per to-do — clicking a card opens follow-up modal OR detail modal (see routing below)
- Done tab: card list with Workiz pill (rendered if `workiz_uuid` exists)
- **Two modals share the `.fu-*` CSS classes:**
  - **Follow-up modal** (`#followup-modal`): editable textarea with SMS, Send + Mark Done + Cancel buttons. Default for all to-dos.
  - **Detail modal** (`#detail-modal`): plain read-only view of the full activity (customer, type, date, full note). Close + Mark Done buttons only. NO SMS path. Used for Calendly bookings + any other non-followup activity.
- localStorage.wsc_ac for access code persistence (same pattern as field.html / reactivation.html)
- After successful Send: 3000ms pause, then `closeFollowupModal(); loadOpen(); showSubTab('done');` so DJ visually sees the activity move

### Modal routing rule (added 2026-04-27)

`isCalendlyTodo(t)` checks if `summary` or `type` contains "calendly" (case-insensitive). Card click routes:
- **Calendly to-do** → `openDetailModal(cardEl)` — shows full activity contents from `note_full`. Mark Done via `/api/followup/markdone`.
- **Anything else** → `openFollowupModal(cardEl)` — existing flow.

The frontend caches the loaded `/api/todos` response in `openTodosById` so the detail modal can read `note_full` without a second fetch.

If you add a new "this is not a follow-up" activity type in the future, extend `isCalendlyTodo` (rename if needed — it's just the routing predicate).

### note vs note_full

`/api/todos` returns BOTH:
- `note` — first 120 chars of the cleaned text (used for the small preview line on the card)
- `note_full` — full text with HTML stripped, paragraph/line breaks preserved

Stripping done by `_strip_activity_html()` helper in dashboard.py: converts `</p>` → `\n\n`, `<br>` → `\n`, strips remaining tags, decodes basic HTML entities. The detail modal renders `note_full` inside `<div class="dt-note">` which uses `white-space: pre-wrap` to preserve the breaks.

If you need to add a new sub-tab or section to Activities (DJ said "a whole bunch of other things"), add it as a sibling sub-tab — do not bury it inside Open/Done.

## What DJ still has to do on the Workiz side (one-time setup)

1. Create SubStatus value `Follow Up Trigger` in Workiz (under parent Status `Pending`)
2. Create a Workiz automation that fires when a job's SubStatus changes to `Follow Up Trigger`, sending the contents of the `information_to_remember` field as an SMS to the customer

Without those, the launch endpoint will create a Workiz job and set the substatus successfully, but no text will actually go out.

## Phase 3 / Phase 4 interaction

Phase 3's graveyard skip filter was extended on 2026-04-27 (commit `ed24c02e` in Odoo-Migration repo) from `JobType="Reactivation Lead"` to `("Reactivation Lead", "Follow Up Lead")`. This stops Follow-Up jobs from triggering SO creation in Odoo. Phase 4 didn't need changes — it delegates to Phase 3 for missing SOs.

If you ever add a new "trigger-only" Workiz JobType, extend that tuple too. File: `Migration to Odoo/1_Production_Code/zapier_phase3_FLATTENED_FINAL.py`.

## Architectural pivot — why this is NOT an Odoo server action

Reactivation runs out of Odoo Server Actions 562/563 because reactivation was originally triggered FROM the Odoo Studio UI. Follow-Up's trigger surface is the Render app — there is no reason to round-trip through Odoo. Everything lives in `dashboard.py`. DJ explicitly endorsed this.

**Future:** reactivation should eventually be ported to the same pure-Render pattern. Not in scope right now, but if you find yourself adding new server actions for a Render-triggered flow, stop and reconsider.

## Common ways future chats break this

1. **Calling `action_done()` on follow-up activities** → "Call done" chatter regression. Use `write({active: False, date_done: today})`.
2. **Using `job/all/` to verify a follow-up was created** → returns nothing because the job is unscheduled. Use `job/get/{UUID}/` directly. (See `project_workiz_job_all_quirk.md`.)
3. **Forgetting `Status='Pending'` when setting SubStatus** → 400 from Workiz. The `workiz_post` helper auto-injects it; don't rewrite that helper without preserving the rule.
4. **Looking up partner_id without the Property→parent walk** → follow-up gets sent to the property record's chatter (often blank), not the contact.
5. **Local dashboard.py drifting from deployed** → diff before pushing, or you'll regress the UUID + Status auto-injection. (See `feedback_local_vs_deployed_drift.md`.)
6. **Cleaning up "dead" code in field.html** (the old to-do modal/CSS/JS that was moved to activities.html) → DJ left it intentionally. Don't touch.
7. **Refactoring activities.html into a single-purpose to-do screen** → DJ wants this page to grow. Keep it modular.

## How to test the flow end-to-end

1. Pick a contact (e.g. Bev Hartin, partner 23629)
2. Clear cooldown: `res.partner.write([id], {'x_studio_last_followup_sent': False})`
3. Create a `mail.activity`: `res_model_id=90` (res.partner), `res_model='res.partner'`, `res_id=<partner>`, `activity_type_id=2` (Call), `summary='Follow up text'`, `user_id=2`, `date_deadline=today`
4. Open `/owner/activities`, Open tab — the to-do should appear
5. Click it → modal with SMS preview
6. Edit if needed → Send → wait 3s → activity should appear in Done tab with Workiz pill
7. Verify: contact chatter should have "📨 Text sent · Workiz job link · SubStatus: Follow Up Trigger"

## Field Assistant additions layered on top of Activities (2026-04-28)

Several field-assistant changes added today that share infrastructure with the activities module:

- **Tag pill next to dollar amount** is now the SO's real `tag_ids` (OK, CF, etc. — resolved through `crm.tag`), not service words. `_resolve_so_tag_names()` helper batches the lookup.
- **Subtitle (`Window` / `Solar` / `Combo`)** is computed by `_service_labels_by_so()`. **Source of truth = JobType**, not order lines — by design. The order-line analysis is run too, and when it disagrees with JobType, an orange `⚠` is rendered next to the subtitle. This deliberately surfaces data hygiene issues (e.g. JobType says "Outside Windows and Screens" but the SO has both Solar + Window order lines → ⚠ tells DJ to fix the JobType). DJ explicitly chose this over auto-correcting the display.
- **"Combination" was renamed to "Combo"** — shorter on the card.
- **Zero-value `sale.order.line` rows are skipped** in the order-line analysis. Odoo blocks hard-delete of order lines on confirmed SOs; DJ's workflow zeroes qty+price as soft-delete. See `project_so_lines_zero_means_deleted.md`.
- **Pay button is greyed and reads `✓ Already Paid`** when the SO has any posted invoice with `payment_state in ('paid', 'in_payment')`. Logic in `_paid_status_by_so()`. Becomes active again automatically if DJ deletes the payment in Odoo (next schedule refresh re-evaluates).
- **Pay button preselects the method** (Check/Cash/Zelle/Venmo/Credit) based on the customer's most recent `account.payment`. Method detection: `payment_method_line_id` 8=check, 7=credit, 6=cash/zelle/venmo (disambiguated by the `memo` field — "Zelle" or "Venmo" substring → that, else cash). Walks Property → parent Contact since payments live on contacts. See `project_account_payment_no_ref_field.md` (account.payment has NO `ref` field — only `memo`).
- **`openJob()` now fully resets payment section state** — button text, disabled flag, memo input — so a previous job's `✅ Paid` doesn't carry over into the next.
- **`/api/job/append_note` endpoint added** (was missing — the three-dots "Add Workiz Note" was a frontend-only stub returning 404). Reads existing `JobNotes` from Workiz, prepends `[YYYY-MM-DD HH:MM] [Render] <note>`, writes back. Newest note on top.
- **`/api/todos` performance fix** — partner lookups are now batched into 2-3 calls instead of 30+ sequential ones. `TODOS_USE_LEGACY` flag for one-line rollback. Date window filter is currently DISABLED (`TODOS_DEADLINE_WINDOW_DAYS = 0`) because DJ's activities skew far into the future.
- **Detail modal for Calendly bookings** — when a to-do's summary or type contains "calendly," tapping opens a plain detail modal showing the full activity contents (HTML stripped to plain text by `_strip_activity_html`, anchor URLs preserved + frontend `linkify()` makes them clickable). No SMS path. Mark Done uses `/api/followup/markdone`.

## Voice-driven activity creation (planned, not built)

**Goal:** DJ talks into the field assistant, the system creates the right kind of activity automatically. Generalizable to other businesses (W&SC + Cheryl + future).

**Design agreed 2026-04-28:**

- One mic button on /owner/field (probably floating) and on /owner/activities
- Whisper transcribes → small LLM call parses into structured fields:
  - **Customer** (matched against Odoo contacts; AI handles fuzzy match for typos like "Hamm" vs "Ham")
  - **When** (`"in two months"` → ISO date)
  - **Type** (dropdown — explicit confirm, no auto-pick. Surprises = bad)
  - **Draft message** (if SMS-type, AI writes first pass; DJ edits)
- Preview card pops up with all four fields editable. Confirm → save → lands in /owner/activities Open tab with due date.
- **Two starter activity types:**
  1. **`scheduled_sms`** ("prep now, send later") — the SMS body is stored alongside the activity. Cron fires it on the due date through Workiz.
  2. **`reminder`** — just surfaces in /owner/activities on the due date for DJ to act on. No auto-fire.
- Activity catalog (`ACTIVITIES = {...}`) lives in code, not in Workiz/Odoo config. New types = code change. Easy.
- All scheduled-SMS firings reuse the existing follow-up Workiz substatus + automation pattern (one substatus, one automation, dynamic message via `information_to_remember`). New jobs each fire so the "Workiz automation only fires once per status" limit doesn't matter.
- **Render cron** (mcp__render__create_cron_job) runs daily, queries Odoo for activities due today with type `scheduled_sms`, fires each via the same code path as immediate fires, marks the activity done. Daily resolution is fine for service comms; can go hourly if precision matters later.
- **Twilio approval SMS (separate channel for DJ-to-system messaging):** DJ gets a personal Twilio number. When the system needs DJ's approval (e.g. "send this text to Bud now?"), it texts him. He replies Y/N/tomorrow/etc. — Twilio webhook hits Render, Render acts. Twilio is for DJ approval flow; customer-facing SMS still goes through Workiz. Cost is trivial (~$2-3/mo). DJ has not yet set up the Twilio account — needs sign-up + payment card himself.
- **Failure handling:** if Workiz is unreachable when the cron tries to fire, alert DJ (push or email — TBD) rather than silently slip.
- **Generalizability:** same UX (mic → Whisper → LLM parse → preview → save) works for any business; only the activity catalog and SMS templates differ per business.

**Decisions made:**
- Type dropdown is editable in preview, NOT auto-picked — user always confirms explicitly.
- Draft message stored at activity creation time (not regenerated at fire time) — DJ wrote it while context was fresh.
- One Workiz substatus + one automation across all activity types (simpler than per-type substatuses).

**Open / not-yet-built:**
- DJ needs to create the Twilio account.
- Activity catalog content — start with 2-3 types as proof, then add the rest.
- Whether scheduled fires need approval SMS to DJ before they go out, or fire silently. Open question.
- 2-month follow-ups for Bud Piraino + Gary Marsalone (today's "skipped solar" cases) — not yet scheduled. Will be the first real test of the system once built.

## Related memories (cross-references)

- `project_followup_flow.md` — original architectural notes from when this was built
- `project_workiz_job_all_quirk.md` — why job/all/ won't find these jobs
- `project_workiz_substatus_needs_status.md` — the Pending parent Status rule
- `project_workiz_update_needs_uuid_in_body.md` — UUID-in-body rule
- `project_so_unlink_needs_cancel.md` — odoo_write auto-cancel (used elsewhere but related to SO cleanup)
- `feedback_local_vs_deployed_drift.md` — diff-before-pushing rule
- `feedback_never_remove_working_code.md` — don't clean up dead code without DJ
- `session_apr27_summary.md` — full context of when this was built

---

### Activities tab — sections + type filter + search + snooze (v2 2026-04-29)
`project_activities_org_v2.md`
> Organization layer DJ asked for after the activities list became "an out-of-control inbox". Open sub-tab now has search bar with X clear, type filter (All/Follow-Ups/To-Dos), 4 date-based collapsible sections (Overdue/Today/This Week/Later), and a Snooze row in the detail modal with 4 chips (+1d/+3d/+1wk/+1mo).

**READ when editing /owner/activities open-list rendering or detail-modal action area.**

## What's there

The Open sub-tab of `/owner/activities` (`activities.html`) renders a filtered, grouped list:

```
[Search bar with X clear]
[All] [Follow-Ups] [To-Dos]              ← type filter pills

🔴 Overdue (3)              ▾
  [activity card]
  [activity card]
🟠 Today (2)                ▾
  [activity card]
🔵 This Week (4)            ▾
  ...
⚪ Later (12)               ▾
  ...
```

All sections start expanded. Tapping a section header collapses/expands it; the choice persists for the rest of the browser session (in-memory `_collapsedSections` Set, not localStorage).

## Detail modal Snooze row

Added between the body and the action row:

```
SNOOZE: [+1 day] [+3 days] [+1 week] [+1 month]
[Close] [Open Follow-Up Editor →] [Mark Done]
```

Tap a snooze chip → calls `/api/todos/snooze` with `{activity_id, days}` → backend bumps `date_deadline` by N days → modal closes → list reloads.

## Backend endpoint

`POST /owner/api/todos/snooze`
- Body: `{activity_id: int, days: int (positive)}`
- Reads current `date_deadline`. If it's in the past, **clamps to today** before adding (so a 30-day-overdue activity snoozed 1 week becomes 1 week from today, not 23 days from yesterday).
- Returns `{ok: true, date_deadline: 'YYYY-MM-DD'}`.

## Frontend state

```javascript
let _allTodos = [];                // full list from /api/todos
let _searchQuery = '';             // current search text
let _typeFilter = 'all';           // 'all' | 'followup' | 'todo'
const _collapsedSections = new Set();  // section keys collapsed by user
```

`renderOpen()` is called whenever filter state changes. It filters `_allTodos` through `passesFilters(t)` then groups by date proximity via `classifyBucket(t, today, weekEnd)`.

## Type filter logic

- `all` — no filter
- `followup` — only those where `isFollowupTodo(t)` returns true (partner_id set + summary/type contains "follow up", "follow-up", "followup", "reactivation", or "reach out")
- `todo` — everything else

The `isFollowupTodo()` predicate is the same one that surfaces the "Open Follow-Up Editor" button in the detail modal — so toggling "Follow-Ups" shows exactly the activities that have that button.

## Search filter

Case-insensitive substring match across `summary` + `record` + `type` + `note`. Empty search = no filter.

## Date-based bucket classification

```javascript
function classifyBucket(t, today, weekEnd) {
  if (!t.date) return 'later';
  if (t.date < today)   return 'overdue';
  if (t.date === today) return 'today';
  if (t.date <= weekEnd) return 'week';
  return 'later';
}
```

`weekEnd = today + 7 days` (calendar days). Activities with no date_deadline land in 'later'.

## Filter bar hides on Done sub-tab

`showSubTab(which)` toggles `#todo-filter-bar` visibility based on `which === 'open'`. The filter bar is only meaningful for open activities.

## When adding new activity types or filters

Add the predicate alongside `isFollowupTodo(t)`. If you add a new pill (e.g. "Calendly"), add a `data-type` value, the predicate match in `passesFilters`, and a button in the type-pills div. Don't refactor the whole bucket structure — sections are date-based and the type pills are orthogonal.

## Related memory

- `project_activities_module.md` — broader Activities module reference (READ FIRST)
- `project_activities_unified_flow.md` — detail-first routing pattern (the reason snooze chips live IN the detail modal, not on the cards)
- `feedback_activity_notes_self_contained.md` — note-authoring rule
- `session_apr29_summary.md` — context for why this was built

---

### Activities UI — unified detail-first flow with automation buttons inside
`project_activities_unified_flow.md`
> 2026-04-29 — Every activity opens the detail modal first (shows ALL fields). Specialized automations (follow-up SMS, future voice-activity types) surface as buttons INSIDE the detail modal, not as separate routing paths. This keeps a consistent "see everything, then choose what to do" pattern.

Every to-do/activity in `/owner/activities` opens the **detail modal first**, regardless of type. The detail modal shows every populated field of the `mail.activity` record — Summary, Type, Due, Linked-to record, res_model, res_id, Activity ID, full note (HTML stripped, anchors preserved as text + frontend linkified).

Specialized automations are buttons **inside** the detail modal, not separate routing destinations.

**Why:** Earlier design routed activities through different modals based on a card-level predicate (Calendly → detail, everything else → follow-up). DJ's complaint on 2026-04-29: a generic to-do (his preselect coverage reminder, activity #66) routed to the follow-up modal which hid the actual note text and presented the SMS-send UI that didn't apply. The fix DJ asked for: *"display everything for all activities so I have a full understanding of the activity. then a button for the automation."*

**How to apply:**

When adding a new specialized activity flow (e.g., voice-driven `scheduled_sms`, `reminder`, future automation types):

1. **Don't** add a new top-level routing branch in `loadOpen()`. The card always opens the detail modal.
2. **Do** add a button to the detail modal's `.fu-actions` area, hidden by default with `style="display:none"`.
3. In `openDetailModal()`, show that button only when the activity matches the trigger (e.g., `isFollowupTodo(t)`, `isScheduledSmsTodo(t)`, etc.).
4. The button's click handler should bridge into the specialized modal — synthesize the data attributes the specialized modal expects and call its `open*Modal()` function. Pattern:
   ```javascript
   function detailOpenFollowup() {
     if (!dtActivityId) return;
     const t = openTodosById[dtActivityId] || {};
     const stub = document.createElement('div');
     stub.dataset.actid = String(dtActivityId);
     stub.dataset.pid   = String(t.partner_id || '');
     stub.dataset.name  = String(t.record || t.summary || '');
     closeDetailModal();
     openFollowupModal(stub);
   }
   ```
5. Inside the specialized modal, the existing Send + Mark Done buttons keep working as before — no changes needed there.

**Predicate functions** (top of activities.html `<script>` block):
- `isCalendlyTodo(t)` — summary/type contains "calendly". Currently no extra button needed (note covers it).
- `isFollowupTodo(t)` — `partner_id` set AND summary/type contains "follow up", "follow-up", "followup", "reactivation", or "reach out". Surfaces the "Send Follow-Up SMS →" button.
- Add new predicates here for future activity types.

**Detail modal field list** (in `openDetailModal()`): Summary, Type, Due, Linked to (`record`), Model (`res_model`), Record ID (`res_id`), Activity ID, then the full note. Any populated field → row; missing → skipped. If a future activity type adds new fields to `/api/todos`, just add a `fieldRow(...)` line.

**Files:**
- `Saunders Render App/static/owner/activities.html` — UI + routing
- `Saunders Render App/routers/owner/dashboard.py` `/api/todos` — what fields the frontend sees

**Related memories:**
- `project_activities_module.md` — broader Activities module reference (READ FIRST when editing this area)
- `project_followup_flow.md` — follow-up SMS flow internals
- `session_apr28_29_summary.md` — earlier design decisions for voice-driven activity creation

---

### Active Window Products vendor setup in Odoo + ordering rules
`project_awp_vendor_setup.md`
> 2026-04-29 — DJ's primary screen-frame supplier. Vendor partner 26936, Customer ID 55145, Tax Exempt (resale fiscal position id 5). Order emails go to BOTH Jaime Gutierrez + Valerie Campos. 33 frame products imported with vendor pricing.

**READ when creating POs to Active Window Products, editing AWP vendor, or building the voice-driven PO tool.**

## DJ's names for this vendor — match all of these

DJ refers to this vendor as any of: **Active**, **AWP**, **Active Window**, or **Active Window Products**. All should resolve to partner 26936. The vendor record's `x_aliases` field lists these explicitly: `"Active, AWP, Active Window, Active Window Products"`.

When parsing voice/chat, match on:
1. The partner's `name` field
2. The partner's `x_aliases` field (split on comma, strip)
3. Substring match — "active" or "awp" anywhere in DJ's text → this vendor

The same alias pattern should be applied to other vendors as we add them (Precision, etc.) by populating their `x_aliases` field.

## Vendor record

- **Partner ID:** 26936
- **Name:** Active Window Products
- **Address:** 5431 San Fernando Road West, Los Angeles, CA 90039
- **Phone:** (323) 245-5185 · Fax: (818) 246-5188
- **AWP Customer ID:** `55145` (stored in `ref` field)
- **Tax status:** Tax Exempt (resale) — `property_account_position_id` = fiscal position id 5 ("Resale - Tax Exempt"). Future POs auto-skip sales tax.
- **Supplier rank:** 1

## Default PO email template — `x_default_po_template_id`

A custom many2one field `x_default_po_template_id` on `res.partner` points to `mail.template`. AWP's value is set to template **id 49 "AWP Order Request"** — DJ's preferred Part No / Qty / Est. Price format with both Jaime + Valerie on TO.

Future PO-sending tools (Render Claude voice tool, scripts, automations) should read `partner.x_default_po_template_id`; if set, use that template. If empty, fall back to standard "Purchase: Purchase Order" (id 47).

This pattern is reusable for other vendors — set their `x_default_po_template_id` to a vendor-specific template and the tool picks it automatically.

## Order email rule — TO BOTH

When sending a PO email to AWP, recipients are **Jaime + Valerie** (both on TO line). The parent partner's `email` field is set to a comma-separated string so Odoo's "Send by Email" button does this automatically:

```
j.gutierrez@activewindowproducts.com, v.campos@activewindowproducts.com
```

Both are also followers (`message_partner_ids`) of the AWP partner record (children 26937 + 26938).

## Child contacts

- **Jaime Gutierrez** (id 26937) — Sales / Order Contact — `j.gutierrez@activewindowproducts.com`
  - Direct ordering contact. Replies within 20-30 min during business hours.
  - Format DJ uses: Part No / Qty / Est. Price table.
- **Valerie Campos** (id 26938) — Customer Service Manager — `v.campos@activewindowproducts.com` · (323) 245-5185
  - Sends price-increase letters, holiday schedules.
  - Send detailed-invoice requests to her — Jaime's accounting team only sends totals.

## Order template (DJ's historical format)

Subject: `Order Request - <description>`

```
Please process the following order:

Part No    Qty    Est. Price
1017AL     100    $1.017
1213M      40     $0.21

Total: ~$110.10

Thank you,
Dan
```

Then Jaime adds it to the next delivery (Friday delivery is the standard cycle).

## Products imported (2026-04-29)

33 frame products were created with vendor pricing (`product.supplierinfo` linked to AWP):

| SKU pattern | Product | Mill price | Color price | Finishes |
|---|---|---|---|---|
| AWP-1017{X} | 5/16" Aluminum Screen Frame .020 | $0.855/ft | $1.017/ft | AD/AL/BL/G/M/T/W/Z |
| AWP-1010{X} | 5/16" Aluminum Lip Frame .025 | $1.344/ft | $1.650/ft | AD/AL/BL/G/M/T/W/Z |
| AWP-1025{X} | 1"×5/16" Aluminum Screen Frame .025 | — | $1.510/ft | AD/AL/BL/W/Z |
| AWP-1019{X} | 3/8" Aluminum Slider Frame .025 | $1.104/ft | $1.280/ft | AD/AL/BL/G/M/T/W/Z |
| AWP-1005{X} | 3/8" Aluminum Slider Frame .020 | $0.852/ft | $0.987/ft | G/M/W/Z |

UOM = ft (id 20). Bundle/carton sizes + matching corner SKU + spline size in each product description.

**Not yet imported:** corners (1213M, 1210M, 1225M, etc.), splines, screen cloth, hardware, full screen-door catalog (Sec 11). Add when needed.

## Sample existing PO

- **P00002** — 100 ft of AWP-1017AL (5/16" Almond) @ $1.017/ft = $101.70 — draft state, awaiting confirmation
- View: https://window-solar-care.odoo.com/odoo/purchase/1

## When building the voice PO tool

Follow the rule above:
1. Search vendor by name → AWP partner 26936
2. Search products by part code → AWP-{sku}
3. Apply Resale fiscal position automatically (it's already set on partner — POs inherit it on create)
4. Default email recipients = both Jaime + Valerie (parent email already comma-separated)
5. Generate email body in the Order Request format above
6. Show DJ a preview before sending — voice misrecognition on quantities is expensive

## Related memory

- `reference_supplier_pricing.md` — paths to AWP price-list PDFs in Documents folder
- `feedback_proactive_inefficiency_capture.md` — preview-first pattern for ordering tools
- `project_quote_tool.md` — companion (customer quotes vs. supplier POs)

---

### Calendly MCP — connected via claude.ai
`project_calendly_mcp.md`
> Calendly MCP is connected through claude.ai connector (NOT local config) and is authorized

Calendly MCP is connected and authorized via the **claude.ai connector** (same method as Gmail, Google Calendar, Zapier). It shows up as `claude.ai Calendly` in `/mcp`.

**How it was set up (2026-04-12):**
- Local config entry (`https://mcp.calendly.com/mcp`) was removed — it caused OAuth failures ("No client info found", "SDK auth error: hNH") because Calendly's MCP doesn't support dynamic client registration from local config
- Added via claude.ai → Settings → Integrations → Calendly → OAuth approved in browser
- Now shows as `claude.ai calendly · ✔ connected` in `/mcp`

**Why local config failed:** Calendly's auth server requires pre-registered OAuth client credentials. Claude Code's local MCP OAuth uses dynamic client registration which Calendly doesn't support. The claude.ai proxy handles this correctly.

**Correct URL (FYI):** `https://mcp.calendly.com` (no `/mcp` suffix) — but irrelevant now since it's connected via claude.ai.

**Confirmed working 2026-04-12:** Listed events, got current user (Window & Solar Care / windowandsolarcare@gmail.com). Tools are live and authorized.

**Why:** DJ wants Claude Code to manage Calendly — view/change availability, event types, booking links, meetings.

**How to apply:** Tools load as `mcp__claude_ai_calendly__*` (lowercase). Use `get_current_user` first to get the user URI, then pass it to `meetings-list_events` etc. No special setup needed — just start a new chat.

---

### Cheryl Real Estate Interview Infrastructure (2026-04-24)
`project_cheryl_interview_infrastructure.md`
> 20-question behavioral interview template, interview day guide, Whisper transcription setup on Windows, folder structure for recording/analysis

## Overview
Built complete infrastructure for capturing Cheryl's real estate business operations via structured 60-minute video interview. Designed to understand deal workflow (pre-interview through post-close), extract beyond-audio insights (screenshots, documents), and transcribe via OpenAI Whisper v20250625 on Windows.

**Why:** Rich qualitative data beats incomplete quantitative surveys. Video captures non-verbal cues, hesitations, alternative workarounds. Whisper avoids cost/privacy of cloud transcription APIs.

## Interview Design

### 20-Question Template
**File:** `3_Documentation/INTERVIEW.md` in local Cheryl repo

**Structure:** Deal walkthrough framed in three time windows:
1. **Pre-Close Phase** (3 questions)
   - How do leads come in? (source, volume, conversion %)
   - How do you qualify leads? (criteria, quick-reject signals)
   - What's the initial client conversation? (what docs exchanged, typical duration)

2. **During-Deal Phase** (6 questions)
   - How many tasks live in your current workflow? (CRM, spreadsheet, email tracking)
   - How do you coordinate with agents / title companies / lenders? (tools, handoff points)
   - What milestones do you track? (inspection, appraisal, clear-to-close, etc.)
   - What goes wrong most often? (blockers, rework, timeline slips)
   - How do you handle extensions / renegotiations?
   - How do clients get updates? (frequency, channel)

3. **Post-Close Phase** (2 questions)
   - What happens after close? (follow-ups, nurture, referral capture)
   - How do you celebrate / acknowledge deals? (systems, timing)

4. **System & Tools Stack** (4 questions)
   - Current CRM / system(s) - what do you like / hate?
   - Contact database - how do you organize? (tags, segments, notes)
   - Document storage - folders, naming convention?
   - Integration desires - what would save you the most time?

5. **Operational Questions** (5 questions)
   - Team size / structure?
   - Busiest season / slow season?
   - Do you do commercial or residential (or both)?
   - Geographic focus?
   - Biggest untapped opportunity (if money/time were unlimited)?

### Why This Structure
- Opens with lead gen + qualification (foundation, no tech bias)
- Deep dives into actual workflow (reveals hidden steps, duplicate entry, bottlenecks)
- Avoids pitching Odoo (let her describe what she needs first)
- Captures pain points naturally (what goes wrong > what works great)
- Ends with aspirational vision (what she wishes for) — good signal for priorities

## Interview Day Execution

### Pre-Interview Brief
**File:** `3_Documentation/INTERVIEW_DAY_GUIDE.md`

Covers:
- **Setup:** Camera position (eye level), mic placement, lighting
- **Consent:** Record the video and permission to use in analysis (not sharing externally without approval)
- **Framing:** "This is a design interview, not an interrogation. I'm here to understand your world."
- **Redirection:** If she pitches ideas or vents frustrations → acknowledge, note it, redirect to the 20 questions
- **Pacing:** 3 min per question target; 60 min total with buffer
- **Beyond-Audio:** Ask for screenshots of current system, sample client email, deal doc samples during relevant questions
- **Debrief:** After recording, 5-min verbal debrief (hypothesis before vs. after, surprises)

### Recording & Transcription Pipeline

**Whisper Setup (Windows):**
- Tool: OpenAI Whisper v20250625 CLI
- Models: small (484 MB) + medium (1.53 GB), both cached locally at `~/.cache/huggingface/...`
- Installation: `pip install openai-whisper==20250625`
- Env var: `PYTHONIOENCODING=utf-8` (required on Windows 3.14, prevents Unicode errors)
- Command: `whisper input.m4a --model medium --output_format vtt --output_dir output/`

**Why Whisper:**
- No cloud API calls (privacy, cost)
- Accurate (~95%) on English-language speech
- Runs offline on Windows GPU (fast; ~15 min to transcribe 60-min interview)
- Outputs VTT (webvtt) for timestamps + text

### Folder Structure (Per Interview)

```
4_Reference_Data/interviews/[CHERYL_DATE]/
├── debrief.md                 # 7-point post-interview checklist
├── hypothesis_before.txt      # What I thought about her workflow (pre-interview)
├── hypothesis_after.txt       # What I learned (post-interview, post-transcribe)
├── audio_notes.md             # Key phrases, timestamps, quotes to pull
├── Cheryl_Interview_[DATE].m4a # Raw video
├── Cheryl_Interview_[DATE].vtt # Whisper transcript with timestamps
├── screenshots/               # PNG/JPG of her current system
├── documents/                 # Sample client contracts, emails, PDFs
└── ANALYSIS.md               # Synthesis (not required, optional deeper analysis)
```

### Debrief Checklist (7 Points)
1. **Biggest surprise** — something you didn't expect
2. **Biggest pain point** — where she expressed most frustration
3. **Biggest opportunity** — gap between current + aspirational
4. **Who is she** — role title, how long in real estate, size of portfolio
5. **Her world** — residential / commercial, single-family / multi, geographic focus
6. **Tech stack** — current CRM, storage, integrations
7. **Next action** — what does she want to do with this analysis?

## Implementation

**Local Tools Installed:**
- `C:\Users\dj\bin\ffmpeg.exe` — media conversion (ffmpeg.com → download "essentials" build)
- `C:\Users\dj\bin\ffprobe.exe` — media inspection (bundled with ffmpeg)
- `whisper.exe` v20250625 — transcription (pip installs to `~/.local/bin/` on Windows)
- Models cached: `~/.cache/huggingface/hub/models--openai--whisper-*.../...` (~2 GB total)

**Persistent Env Vars (set once):**
```powershell
[Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'User')
```

**End-to-End Test (2026-04-22):**
- Recorded 3-min test video (iPhone camera)
- Transcribed with `whisper test.m4a --model small`
- Output: VTT file with timestamps, accurate transcription
- Time: ~30 seconds for 3-min video on GPU

## How to Apply

**Before Interview:**
1. Set up camera + mic (phone on tripod OK)
2. Review 20-question template + circle topics most relevant to Cheryl
3. Print `INTERVIEW_DAY_GUIDE.md` for reference
4. Create interview folder: `4_Reference_Data/interviews/cheryl_[DATE]/`
5. Write hypothesis_before.txt (what you think you'll learn)

**During Interview:**
1. Record video (iPhone voice memo → export as .m4a, or use camera app)
2. Ask the 20 questions (can skip 1-2 if time constrained)
3. Capture screenshots (ask her to show you her current CRM, send them as files after)
4. Note timestamps for key phrases (side notes during interview)
5. Verbal debrief immediately after (5 min, capture hypothesis_after.txt)

**After Interview:**
1. Transcribe: `whisper interview.m4a --model medium --output_format vtt --output_dir output/`
2. Read transcript, extract key quotes to audio_notes.md with timestamps
3. Write ANALYSIS.md (if deeper synthesis needed)
4. Upload to GitHub (Cheryl repo, not W&SC repo)

## Known Behaviors

- **Whisper hallucination:** Sometimes repeats phrases or adds text not in audio. Review transcript manually.
- **Background noise:** Whisper handles it well but loud noise may reduce accuracy. Test at interview location.
- **Privacy:** Whisper stays local; no audio sent to cloud. Can delete raw video after transcription.
- **Timestamp precision:** VTT output has 1-second precision. Sufficient for finding soundbites.

## Current Status (2026-04-22)
✅ Template created
✅ Interview guide created
✅ Folder structure established
✅ Whisper setup tested end-to-end
✅ Models cached locally
⏳ **Waiting on:** Scheduling interview with Cheryl (when is she available?)

## Reference Docs
- OpenAI Whisper: https://github.com/openai/whisper
- ffmpeg documentation: https://ffmpeg.org/documentation.html
- WebVTT spec: https://www.w3.org/TR/webvtt/

---

### Cheryl Interview Template Refinements (2026-04-26)
`project_cheryl_interview_refinements.md`
> 8 template improvements based on transcript analysis; 60→90 min interview; identifies gaps between MODELS_SPEC and Cheryl's actual workflow

## What Was Done

**Analyzed two Cheryl interview transcripts** and refined the 20-question template with 8 improvements:

### New Questions Added
1. **Q5.5 — Pre-Contract Communication Strategy** (~6 min)
   - What info does she WANT to send clients between qualification and contract?
   - Cheryl emphasized this is a major pain point (clients confused, she repeats herself, no system)

2. **Q18.5 — Automation & Triggers** (~4 min)
   - What communications should auto-send at the right moment?
   - Cheryl talked extensively about automation: "here's what you should know per stage"

3. **Q18.7 — Broker & System Portability** (~2 min)
   - What survives a broker change, what gets left behind?
   - She said "I still have stuff with old pictures, old broker information" — major pain

### Questions Revised
- **Q2** — Changed from time allocation → client segmentation (pre-qualified, active, past clients) + priority gaps
- **Q17** — Added follow-up about proof/audit trail of communications (critical for escrow compliance)
- **Q18** — Added depth: "What pain point does it solve? Which would you delete first?"
- **Q19** — Added specificity: if "dashboard" is the magic feature, get her to sketch it directly

### Metadata Updated
- **Duration:** 60 min → **75–90 min** (added 12 min of new material; can trim Q7 by 2–3 min if time-constrained)
- **Section headers:** Updated to reflect new timing allocations
- **Emphasis:** Added note that template probes deeper on 5 unmet needs (segmentation, communication, personalization, automation, portability)

**File:** `windowandsolarcare-hash/cheryl-real-estate` | `3_Documentation/INTERVIEW.md`
**Pushed:** 2026-04-26 | commit `60015bcb5a06f9185b81bcc51d69ef69c5ac7ead`

## Key Findings from Transcript Analysis

### Cheryl's Top Pain Points (in order of emphasis)
1. **Pre-contract communication cadence** — clients don't know what to expect, she sends same info multiple times
2. **Tool fragmentation** — 7–8 tools doing overlapping things (CRM, MLS, forms, texting, etc.)
3. **Personalized follow-up** — wants to send smart reminders (solar maintenance, home value updates, property-feature-based outreach)
4. **System churn on broker switch** — data and workflows don't port when she changes brokers
5. **Communication proof/audit trail** — needs documented evidence of what was sent when (escrow compliance)

### Workflow Themes Cheryl Emphasized
- **Deal stages matter:** pre-contract, under-contract, close, post-close have very different communication needs
- **Automation via triggers:** wants system to send right message at right time based on stage
- **Client segmentation:** "serve current clients first, then expand" — active deals ≠ past clients ≠ prospects
- **Data persistence:** wants to carry client history, preferences, notes across broker changes

## Gap: MODELS_SPEC vs. Cheryl's Reality

**MODELS_SPEC.md status:** DRAFT, built 2026-04-20 from contract samples + domain knowledge, NOT from Cheryl's workflow

### What MODELS_SPEC Has (✓ aligned)
- Transaction/Opportunity/Property structure (correct)
- Deal stages + state transitions (correct)
- Contact tracking (lenders, escrow, title, etc.) (correct)
- Checklist attachment at stage level (correct)

### What MODELS_SPEC Lacks (gaps to fill after full interview)
- **Cadence/communication templates** — no fields for pre-contract message sequence
- **Personalization data** — no structured fields for client preference data that drives smart sends
- **Automation rules/triggers** — no model for "send message X when deal reaches stage Y"
- **Tool integrations** — no mention of MLS sync, texting platform, calendar integrations
- **Broker/portability metadata** — no fields to mark "this stays, this goes" during broker transitions

### Next Step
After Cheryl completes the full refined interview, add fields to MODELS_SPEC:
- `x_cheryl_communication_template` model (pre-contract, in-contract, post-close sequences)
- `x_cheryl_personalization_field_id` (solar, lot size, school district, etc.) on Transaction + Property
- `x_cheryl_automation_rule` (trigger-based message sends)
- Metadata on key integrations (MLS, texting, calendar)

## How to Apply

**When to run refined interview:**
- Use the updated `INTERVIEW.md` as-is for Cheryl's next session (75–90 min allocation)
- New questions will surface the communication/automation/personalization workflows we couldn't see before
- Capture her answers inline in a fork: `INTERVIEW_CHERYL_[DATE].md`

**After interview:**
1. Extract data shape from her answers (template fields, cadence rules, personalization triggers)
2. Propose additions to MODELS_SPEC
3. Build new models for communication + automation
4. Test with her live workflow

## Files
- `3_Documentation/INTERVIEW.md` — the refined template (live on main)
- `MODELS_SPEC.md` — existing spec (needs field additions post-interview)

---

### Cheryl Project — Interview to Plan Workflow (Best Practice Approach)
`project_cheryl_interview_to_plan_workflow.md`
> Three-phase workflow for Cheryl's real estate system: (1) Interview gathers current workflow, (2) Plan shows best-practice benchmarks vs. current state with gap analysis, (3) DJ approves the approach. NOT "sell best practice in interview" but "show best practice in plan for approval."

## The Workflow

### Phase 1: Interview (Gather Data — Current State Only)
**What happens:** Refined 29-question interview template walks through her real deal workflow, pain points, tools, what she wants.

**What we're collecting:** 
- How she actually works now
- Where it hurts (Q14: "what would you pay to outsource?")
- What she aspires to (Q19: "magic feature?")
- Business metrics (volume, close ratio, revenue mix)
- Adoption readiness (Q23: how she learns, what makes tools stick)

**What we're NOT doing:** Selling best practices in the interview. No "top 1% agents do X" comparisons. Just listen and gather.

**Output:** Interview answers captured in `INTERVIEW_CHERYL_[DATE].md` (fork of template with her answers inline)

---

### Phase 2: Plan (Show Best Practice vs. Current State)
**What happens (AFTER interview):** Claude researches real estate best practices, builds a proposal showing:

**Structure:**
1. **Current State Summary** (from her interview)
   - How she works now (deal flow, tools, team, metrics)
   - Top 3 pain points she mentioned
   - What she aspires to

2. **Best-Practice Benchmarks** (real estate industry standards)
   - Lead follow-up cadence (daily hot, weekly warm)
   - Referral generation system (ask at close, track sphere, nurture)
   - Communication templates (pre-contract, in-contract, post-close sequences)
   - Automation triggers (milestone-based sends)
   - Metrics tracked (close ratio, days-on-market, CAC, LTV, referral %)
   - Past-client revenue (typically 40-60% for top agents)
   - Time allocation (highest-value activities vs. admin)

3. **Gap Analysis** (Current vs. Best Practice)
   - Where she aligns with best practice (keep/strengthen)
   - Where she has significant gaps (opportunities for improvement)
   - What's blocking her from best practice (time, knowledge, tooling, discipline)

4. **Proposed System Architecture**
   - How we'll close the gaps
   - What we'll automate vs. what stays personal
   - What data/tools/workflows we'll build
   - Timeline and phases

**Output:** Proposal document (PDF or Google Doc) ready for DJ + Cheryl review and approval

---

### Phase 3: Approval & Refinement
**What happens:** DJ and Cheryl review the plan together.

**Outcomes:**
- Cheryl sees best practice + where she is vs. that (no surprises)
- Cheryl approves the approach (or asks for adjustments)
- We have explicit buy-in on "we're building a best-practice system, not just automating what you do now"
- Scope and priorities are locked in before we build

---

## Why This Workflow

| Mistake | Why It's Bad | Our Approach |
|---|---|---|
| Sell best practice IN interview | Feels preachy, defensive, wastes interview time | Gather data first, show best practice in plan with context |
| Build system to her current workflow | Locks in her inefficiencies | Build to best practice, she approves before we build |
| No explicit discussion of best practice | She might expect automation of status quo | Plan shows "here's best practice, here's the gap, here's how we close it" |
| Scope creep later | "Why didn't you include X from best practice?" | Approved plan = locked scope |

## When to Apply This

**Timing:**
- Interview: 2026-04-26 or later (when Cheryl is ready, 75–120 min)
- Post-interview: Claude builds best-practice proposal (1–2 days)
- Review: DJ + Cheryl discuss, approve, iterate (scheduled with Cheryl)
- Build: Only after written plan approval

**Key Decision Point:** Before Claude writes ANY code or builds ANY system, there must be an approved plan that shows:
✅ Current state
✅ Best-practice benchmarks
✅ Gap analysis
✅ Proposed architecture
✅ DJ + Cheryl sign-off

---

## What "Best Practice" Means Here

Real estate best practices (sourced from industry studies, top-agent playbooks, automation platforms):

1. **Lead Management** — Systematic follow-up (hot: daily, warm: weekly, cold: monthly)
2. **Referral Generation** — Ask at close, track source, nurture sphere (should be 40–60% of revenue for mature agents)
3. **Communication Cadence** — Pre-contract weekly, in-contract milestone-triggered, post-close nurture schedule
4. **Automation** — Trigger-based messages (inspection day, appraisal complete, 30-day post-close, anniversary, market update)
5. **Metrics** — Close ratio, days-on-market, cost per lead, lifetime value by source, referral attribution
6. **Data** — Centralized contact DB, complete transaction history, preference tracking, searchable communication logs
7. **Checklists** — Stage-based workflows to prevent dropped balls
8. **Time Allocation** — Top agents spend 60%+ on highest-value activities (client calls, negotiations, referral cultivation), 40% or less on admin

---

## Files Involved

- `3_Documentation/INTERVIEW_BEST_PRACTICES.md` — The 29-question template (workflow-focused, not best-practice-focused)
- `INTERVIEW_CHERYL_[DATE].md` — Cheryl's interview answers (will be created during interview)
- `CHERYL_PROPOSAL_BEST_PRACTICE_[DATE].md` — The plan showing current vs. best practice (will be created post-interview)
- `MODELS_SPEC.md` — Will be updated based on best-practice system requirements (not interview answers)

---

## Key Principle

**Interview = Data gathering. Plan = Best practice presentation & approval. Build = Execute approved plan.**

Don't mix them. The interview doesn't need to sell best practice — the plan does, with context and data to back it up.

---

### Cheryl Real Estate Assistant — Full Plan
`project_cheryl_real_estate.md`
> Complete plan for Cheryl's real estate assistant app — client pipeline, stage checklists, property dossiers, MLS integration, accounting

# Cheryl Real Estate Assistant

**Decided:** 2026-04-18
**Status:** Planning complete. Build plan sent to Cheryl 2026-04-19. Waiting on: stage checklists, business name, CRMLS API access.
**Cheryl's email:** markethouses@gmail.com
**Current tools she pays for:** Lofty ($20/mo), Elevated Marketing (CRM+website), Homes.com/HomeSnap ($40/mo) — ~$150/mo she wants to replace
**Key tool to recreate:** Lofty — has leads, opportunities, transactions, tasks, appointments, listings
**MLS:** CRMLS — has InfoSparks access through MLS dues (good sign for Spark API)
**Recording reviewed:** C:\Users\dj\Downloads\Cheryl Real Estate_original.txt (13 min conversation)

---

## WHO CHERYL IS

Real estate agent, solo proprietor (possible S-Corp in future). Very knowledgeable — gives clients a lot of information at every stage. Her problem: same high-quality info delivered verbally to many clients gets blurry. Loses track of what was said, what was sent, what paperwork was given. Wants a system to make her consistent and documented.

She is NOT focused on lead gen / mass marketing. Her priority is serving active clients at the highest level. CRM campaigns are secondary.

---

## THE 5 THINGS SHE NEEDS

### 1. Client Stage Tracker
Full real estate journey tracked per client:
- Introduction → Needs Assessment → Property Search → Offer → Contract → Escrow → Pre-Close → Close → Post-Close → Follow-up
- Each client has a current stage
- Moving to new stage auto-triggers checklist + prompts

### 2. Stage-Based Checklists + Prompts (KEY FEATURE)
- Each stage has items: things to do, discuss, send, give
- System prompts her for each item
- **Three options per item:**
  - **"I Did It"** → logs: Cheryl completed, timestamp
  - **"Claude Did It"** → Claude executes it (sends email, generates doc, posts note) then logs it
  - **"N/A"** → logs: skipped, moves on
- Every item has a resolution + timestamp — full audit trail
- Never wondering "did I cover that with this client?"

### 3. Property Showing Dossier
- Enter MLS# → system pulls all property data automatically
- She adds: photos from showing, voice notes, written notes, viable/not viable + why
- Per-client property history — shows if property was shown before + prior notes
- All in one place before she walks in the door
- When showing is scheduled → property data auto-populates

### 4. Document + Communication Log
- What did I send this client? When?
- Log of every conversation, document sent, disclosure given
- Searchable — "what was that thing I told them about escrow?"

### 5. Post-Close Resource Library
- Pre-written guides on common post-close questions (mortgage vs HOI, property tax notices, HOA, etc.)
- Pull up and send instantly
- "We discussed this — here's the link" capability

---

## MLS INTEGRATION

**Key question still open:** What MLS is she on? Southern California = likely CRMLS (California Regional MLS).
- CRMLS has Spark API
- Requires API credentials through her broker
- If she has API access: enter MLS# → all listing data downloads automatically
- If website access only: manual copy or web scrape workaround

**Need to find out:** Does her broker/MLS give her API access?

---

## ACCOUNTING

- Solo proprietor now, possible S-Corp future
- Starting fresh in Odoo — no migration needed
- Expense categories typical for RE agent: MLS fees, marketing, auto, E&O insurance, office, splits/referrals
- Claude handles all accounting same as DJ — she describes it in plain English

**Still need from Cheryl:**
1. What expense categories does she have?
2. Any open invoices / commissions currently owed?
3. Business bank account — separate or personal?
4. Business name as it appears on tax return

---

## TECHNICAL PLATFORM

- Odoo multi-company: "Cheryl Real Estate" as second company under DJ's instance
- Clients = Odoo CRM contacts with custom stage field
- Properties = linked records per client
- Checklists = Odoo activities/tasks auto-generated by stage
- Photos/docs = Odoo attachments (ir.attachment)
- Her screen = custom Render interface at /cheryl route

---

## STILL NEEDED BEFORE BUILDING

1. Her business name (to create Odoo company)
2. Which MLS + API access type
3. Her stage-by-stage checklist — what are the 5-10 things she does at each stage? This is the backbone of the whole system.
4. Her accounting setup answers (4 questions above)

---

## PHASE PROGRESSION (login/access)

Phase 1: Render only — Cheryl uses access code, never sees Odoo
Phase 2: Render primary + her own Odoo login under DJ's account
Phase 3: Her own Odoo account — I migrate everything

---

### Cheryl Project Split Into Its Own Repo
`project_cheryl_repo_split.md`
> 2026-04-20 Cheryl real estate code moved from W&SC Migration repo into its own local folder + GitHub repo + SHARED_MEMORY

# Cheryl Project Split — 2026-04-20

Cheryl's real estate project was broken off from the W&SC Migration codebase into its own fully independent repo.

**Why:** Keep W&SC migration code clean. Cheryl is a separate business with no Workiz/Zapier — mixing them created confusion. Also prepares for per-business Render voice boxes (DJ → W&SC memory, Cheryl → her own memory).

**How to apply:**
- **Local:** `C:\Users\dj\Documents\Business\A Cheryl Real Estate\` (parallel to W&SC). Has its own CLAUDE.md, SHARED_MEMORY.md, PLAN.md, and folder skeleton (1_Production_Code, 2_Testing_Tools, 3_Documentation, 4_Reference_Data).
- **GitHub:** `windowandsolarcare-hash/cheryl-real-estate` (private, DJ is owner). Same `gh api` deployment pattern as W&SC.
- **Render:** no new service — Cheryl's voice box will live at `/cheryl/` route inside existing `saunders-render-app`. Role→repo mapping for SHARED_MEMORY sync to be added when the voice box is built (role `cheryl` → `cheryl-real-estate` repo, roles `owner`/`tech` → `Odoo-Migration` repo).
- **W&SC SHARED_MEMORY.md:** Cheryl section replaced with a 4-line pointer. Don't duplicate Cheryl content back into W&SC.
- **When working on Cheryl's project:** `cd` into `A Cheryl Real Estate` folder first — her CLAUDE.md and SHARED_MEMORY.md load there, not W&SC's.

**Deployment gotcha discovered:** The PowerShell-based `gh api` deploy script in W&SC's CLAUDE.md has an escaping issue when fetching the SHA of files in subfolders (404s even though file exists). Workaround: use Python subprocess to call `gh api` directly — works reliably. Pattern:
```python
sha = subprocess.check_output(['gh','api',f'repos/{repo}/contents/{path}?ref=main','--jq','.sha'], text=True).strip()
subprocess.run(['gh','api',f'repos/{repo}/contents/{path}','--method','PUT','--input','-'], input=json.dumps(payload), text=True)
```

---

### Claude Code Remote Control auto-start setup
`project_claude_remote_control.md`
> Claude Code Remote Control is configured to auto-start at login so DJ can control it from his Galaxy Z Fold 5 via the Claude mobile app

Claude Code Remote Control is set up for auto-start on DJ's Windows 11 machine. Set up 2026-04-20.

**Components:**
- Scheduled task: `ClaudeRemoteControl` (registered via PowerShell `Register-ScheduledTask`, not schtasks — schtasks returned Access Denied)
- Startup script: `C:\Users\dj\start-claude-remote.bat` — 30s timeout, cd to Migration to Odoo folder, launch `claude.exe remote-control --name "WSC-Auto"`
- Session name visible in Claude app: `WSC-Auto`
- Trigger: At user logon (user-scoped, no admin needed)
- Claude CLI location: `C:\Users\dj\.local\bin\claude.exe` (native Windows binary, not a bash script)

**Why:** DJ wanted to control Claude Code from his phone while on the road. Remote Control is the official Claude Code feature — gives full local environment access (files, MCP servers, configs) via Claude mobile app or browser.

**How to apply:**
- If DJ reports remote control isn't working: check Task Manager for `claude.exe`, verify `ANTHROPIC_API_KEY` env var is NOT set (it blocks remote control, requires OAuth via `claude auth login`), check the scheduled task state with `Get-ScheduledTask -TaskName 'ClaudeRemoteControl'`
- To test manually: `powershell -Command "Start-ScheduledTask -TaskName 'ClaudeRemoteControl'"`
- To disable/remove: `powershell -Command "Unregister-ScheduledTask -TaskName 'ClaudeRemoteControl' -Confirm:\$false"` and delete the .bat file
- Push notifications enabled via `/config` inside Claude Code → "Push when Claude decides" (Claude mobile app, signed in with windowandsolarcare@gmail.com)
- Task runs hidden — no visible terminal. Verify it started via Claude app session list, not by looking for a window.
- Requires Claude Code v2.1.110+ (DJ has 2.1.114 as of setup date)

**Gotchas discovered during setup:**
- `schtasks /create` from Git Bash mangles `/` flags — use `cmd.exe //c "schtasks..."` or PowerShell's Register-ScheduledTask instead
- `schtasks /create` returned "Access is denied" even for user-scoped tasks — PowerShell's `Register-ScheduledTask` with `-LogonType Interactive -RunLevel Limited` worked without admin
- If machine sleeps, session pauses — DJ must wake the PC before connecting from the road (future: consider wake-on-LAN if this becomes a pain point)

---

### Render clock-in writes to hr.attendance, not ir.config_parameter
`project_clockin_uses_hr_attendance.md`
> Live Render timeclock stores shifts in Odoo's built-in hr.attendance model, contradicting the local app.py/dashboard.py code which references payroll.* config parameters

The Render app's clock-in/out system stores data in Odoo's built-in `hr.attendance` model — NOT in `ir.config_parameter` under `payroll.clockin.{id}` / `payroll.shifts.{id}` keys as the local code in `5_Mobile_Interface/app.py` and `Saunders Render App/routers/owner/dashboard.py` suggests.

Verified 2026-04-24: queried `hr.attendance` and found 15 records matching DJ's screenshot (Dan Saunders emp_id=1, Danny Saunders emp_id=2). Queried `ir.config_parameter` for `payroll.*` and found zero rows.

Key fields on `hr.attendance`:
- `employee_id` — [id, name] tuple
- `check_in` — UTC datetime string
- `check_out` — UTC datetime string (False if still clocked in)
- `worked_hours` — float

The screenshot showed an admin "+ Add Shift / Week of / raw" UI with edit buttons and weekly groupings — this UI does NOT exist in either local codebase. It must live in a newer/separate payroll admin page (possibly deployed on Render but not yet pulled down locally, or in a sibling repo not yet surveyed).

**Why:** Local code is stale. Before editing clock-in/out logic, pull the deployed version from GitHub or the running Render service. Don't assume ir.config_parameter is the storage.

**How to apply:** When asked about clock-in/out data, query `hr.attendance` first (filter by `employee_id` and date range on `check_in`). Remember DJ emp_id=1, Danny emp_id=2. Times are UTC — convert to Pacific for display. Before editing the clock-in code path, verify the live source — check GitHub repos `windowandsolarcare-hash/Odoo-Migration` and `windowandsolarcare-hash/saunders-render-app` for the currently deployed version and look for the "Add Shift" admin UI.

**CRITICAL: ignore Odoo's `worked_hours` field.** The deployed app (`saunders-render-app/routers/owner/dashboard.py` lines 2638–2642) computes hours from raw `check_in`/`check_out` timestamps and applies `_round_quarter_hour_neutral()` (FLSA 7-min rule) at display time only. Odoo auto-populates `worked_hours` with calendar-based break deductions (e.g., 8 wall-clock hours → `worked_hours = 7.0` due to a 1-hour lunch deduction) but the UI/Gusto export both bypass this. When creating attendance records via API for DJ to use, DO NOT try to compensate for the lunch deduction by extending check_out — the wall-clock duration is what shows. Verified 2026-04-26 by creating 3 × 15:00→23:00 UTC shifts (worked_hours=7.0 each); they display as 8.00h in Manage Shifts.

---

### Credit card at-door payment flow
`project_credit_card_payment_flow.md`
> How credit card payments taken at the door in Workiz are handled differently in Phase 6

When Dan collects a credit card payment at the job site, Workiz records it immediately but does NOT auto-mark the job Done. This is the ONLY scenario where `JobAmountDue = 0` AND `Status != Done`.

**Why:** Credit card is collected in Workiz app on site. All other payment types (check, cash, Zelle) go through Odoo first — Phase 6 posts the payment to Workiz AND marks Done. Credit card is the reverse: payment already in Workiz, needs to flow to Odoo.

**How to apply:**

Detection in Odoo: "Sync from Workiz" server action (ID 955) checks `JobAmountDue == 0` AND `Status != Done` → sets `x_studio_pricing_mismatch` to **yellow** (`bg-warning text-dark`) "Credit Card Payment Received - Invoice in Odoo using Credit method".

DJ workflow:
1. Hit Sync from Workiz → sees yellow warning
2. Create invoice in Odoo, register payment using **"Credit"** method (account.payment.method.line ID 7)
3. Phase 6 fires, sees `workiz_type = "credit"` (derived from Odoo payment method, NOT Workiz) → **skips** addPayment to Workiz (already there) → marks job Done → flips field to green → triggers Phase 5

Phase 6 change: single `if workiz_type == "credit": skip addPayment` block around the Workiz POST. Everything else (mark Done, Phase 5 trigger) unchanged.

**Key field:** `x_studio_pricing_mismatch` on `sale.order` (HTML field)
- Yellow (`bg-warning text-dark`): credit card received, not yet invoiced in Odoo
- Green (`text-success`): fully processed — set by Phase 6 after marking Done
- Red (`text-danger`): pricing mismatch between Workiz and Odoo totals

---

### Daily Sync Monitor — CronCreate job + self-renewal
`project_daily_sync_monitor.md`
> Self-renewing CronCreate job that reviews the daily Workiz sync log and alerts DJ. Recreate immediately at session start if not running.

## What it does
A Claude CronCreate job (`17 4 * * *` — 4:17am daily local time) that:
1. Calls `monitor_tick` to get the sync log + increment a day counter stored in Odoo
2. Analyzes the log for errors, rate-limit hits, or stale timestamps
3. Emails DJ at windowandsolarcare@gmail.com if anything needs attention
4. At day 5, recreates itself (same prompt) and resets the counter — runs indefinitely

## How to restart (if session closed and job is gone)

**ALWAYS CHECK FIRST — do not blindly create a duplicate.**

### Step 1: Check if a job is already running in another session
Call (read-only, no side effects):
```
GET https://wsc-field-assistant.onrender.com/api/cron/daily_sync_log?token=wsc-daily-sync-2026
```
Response includes `created_at` — the ISO timestamp of when the last CronCreate job was stamped.

**Decision logic:**
- `created_at` is within the last 5 days → **SKIP. A job is likely still running in another session. Do not create.**
- `created_at` is older than 5 days, or null → **CREATE the job** (see Step 2)

### Step 2: Create the job (only if needed)
```
CronCreate:
  cron: "17 4 * * *"
  recurring: true
  durable: true
  prompt: (see PROMPT TEMPLATE below)
```

### Step 3: Stamp the creation date immediately after creating
```
GET https://wsc-field-assistant.onrender.com/api/cron/monitor_tick?token=wsc-daily-sync-2026&stamp=1
```
This writes today's UTC timestamp to Odoo so any OTHER session that checks will see "recent" and skip.

**Why this works:** Every session checks `created_at` before creating. Every new cron stamps the date after creating. If two sessions race, the second one sees a fresh date and skips. No duplicates.

## Endpoints used (all need token: wsc-daily-sync-2026)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/cron/monitor_tick` | GET | Increment day counter + return sync log. Add `?reset=1` to reset to 0 |
| `/api/cron/notify` | POST | Send alert email to DJ. Body: `{subject, message}` |
| `/api/cron/daily_sync_log` | GET | Read current sync log without incrementing counter |

Base URL: `https://wsc-field-assistant.onrender.com`

## Day counter
Stored in Odoo `ir.config_parameter` key `render.sync_monitor_day`.
Read/write via `monitor_tick` endpoint. Reset by appending `?reset=1`.

## Auto-email (no Claude needed)
`_run_daily_sync()` in dashboard.py ALWAYS sends a brief summary email after every sync run (even clean runs). Subject: `WSC Daily Sync — ✅ Clean | X updated, 0 errors`. This is independent of the CronCreate job.

## PROMPT TEMPLATE (copy verbatim to recreate the CronCreate job)

```
WSC DAILY SYNC MONITOR — self-renewing agent

## What you are
You review the WSC Odoo/Workiz daily sync log every morning and alert DJ if anything needs attention. You also keep yourself alive past the 7-day session limit by recreating the job when you get close to expiry.

---

## STEP 1 — Tick the day counter and get the log (one call)

Use WebFetch to GET:
  https://wsc-field-assistant.onrender.com/api/cron/monitor_tick?token=wsc-daily-sync-2026

Response shape: { "ok": true, "day": N, "log": { "run_at": "...", "total": X, "synced": X, "skipped": X, "errors": X, "rate_limit_hits": X, "error_details": [...] } }

Note the `day` value — you'll need it in Step 4.

---

## STEP 2 — Analyze the log

Flag problems (send alert) if ANY of:
- errors > 0
- rate_limit_hits > 2
- log.run_at is more than 26 hours ago (cron stopped firing)
- log is null and day > 1 (sync never ran)

Healthy → no email needed.

---

## STEP 3 — Send alert if needed

Use WebFetch to POST https://wsc-field-assistant.onrender.com/api/cron/notify?token=wsc-daily-sync-2026
Content-Type: application/json
Body: { "subject": "WSC Sync Alert — [brief status]", "message": "[your analysis]" }

Keep message tight: 1-line summary, bullet list of problem SOs (max 10), one recommendation at the end.

---

## STEP 4 — Self-renewal (only if day >= 5)

This job expires after 7 days. At day 5, recreate it so it runs forever.

4a) Call the CronCreate tool with these exact parameters:
  - cron: "17 4 * * *"
  - recurring: true
  - durable: true
  - prompt: [copy the ENTIRE text of this prompt verbatim, from "WSC DAILY SYNC MONITOR" through the end of Step 5]

4b) Reset the day counter — use WebFetch to GET:
  https://wsc-field-assistant.onrender.com/api/cron/monitor_tick?token=wsc-daily-sync-2026&reset=1

4c) Output: "Renewed — fresh 7-day job created, counter reset to 0."

---

## STEP 5 — Always output a one-line status

"Day N | Processed X SOs | Updated Y | Errors Z | Rate-limit hits W | [Healthy / Alert sent / Renewed]"

That one line is your only required output when everything is fine.
```

---

### SO date_order is always the job START time
`project_date_order_is_start_time.md`
> date_order on sale.order always = Workiz JobDateTime (start) in UTC — never end time, never date_deadline

SO `date_order` is always set to the Workiz `JobDateTime` (start time) converted to UTC. This has been the rule since the beginning of the project.

**Why:** The schedule display, the Render field assistant app, and all date-based reporting rely on `date_order` being the start time. Using the end time causes jobs to appear at the wrong time slot.

**How to apply:** Whenever writing `date_order` on a sale.order — whether in Phase 3, Phase 4, a manual fix, or any other context — always use `JobDateTime` → `convert_pacific_to_utc()`. NEVER use `JobEndDateTime`, task `date_deadline`, task `planned_date_end`, or any other end-time field.

Workiz fields:
- Start time: `JobDateTime` → maps to SO `date_order` and task `planned_date_begin`
- End time: `JobEndDateTime` → maps to task `date_deadline` / `date_end` only

---

### duplicate_workiz_job tool fix — copies ServiceArea and sets last_date_cleaned
`project_duplicate_job_fields_fix.md`
> 2026-04-26 fix to Render Field Assistant's duplicate_workiz_job tool — was missing ServiceArea copy and last_date_cleaned set

The `duplicate_workiz_job` tool in `saunders-render-app/routers/owner/dashboard.py` (around line 1040) was missing two fields when constructing the Workiz job-create payload:

1. `ServiceArea` — never copied from the source job
2. `last_date_cleaned` — never set on the new job

Fixed 2026-04-26 (commit a6ae157):
- Copy `ServiceArea` from source: `payload['ServiceArea'] = str(job.get('ServiceArea') or job.get('service_area'))`
- Set `last_date_cleaned` on new job to source job's `JobDateTime[:10]` — when the source job ran, that was the customer's most recent cleaning, so the duplicate inherits that as the "last cleaned" date

The tool's description says "Copies all fields" — but the implementation didn't actually copy all fields. Render Claude trusted the description and produced jobs missing ServiceArea and last_date_cleaned.

**Why:** Tool descriptions are agent-facing contracts. If a tool says "copies all fields," its implementation MUST do that — agents can't be expected to re-verify every payload field, and adding "remember to also pass ServiceArea" instructions to the system prompt is a fragile workaround. Fix the tool, not the prompt.

**How to apply:** When auditing other "copy from source" tools (`create_workiz_job`, future variants), check that the payload actually copies every field promised by the description. The two known business-critical fields that often get forgotten: `ServiceArea` and `last_date_cleaned`. Workiz API uses `ServiceArea` (PascalCase, system field) and `last_date_cleaned` (snake_case, custom field) — different casing conventions.

---

### Follow-Up flow — pure Render, no Odoo server actions
`project_followup_flow.md`
> 2026-04-27 — DJ asked for parallel-to-reactivation follow-up flow. Built entirely in Render Python. Mirrors reactivation's Workiz-side mechanism (information_to_remember + SubStatus trigger) but no Odoo SAs.

Built 2026-04-27. Lives in `routers/owner/dashboard.py` + `static/owner/field.html` in `windowandsolarcare-hash/saunders-render-app`.

**Architectural decision:** moved away from the reactivation pattern of Odoo server actions (SA 562 Preview / SA 563 Launch). DJ explicitly questioned whether server actions still earn their keep now that Render exists. They don't — the trigger is in Render, the UI is in Render, the SMS template can be a Python function. Server actions only earn their keep when the trigger lives *inside* Odoo (cron, button on form view, automated rule).

**Why this matters for future work:** when reactivation needs maintenance, consider porting SA 562/563 into Render endpoints too. Then the two-step Odoo-deploy pain (CLAUDE.md rule #2) for reactivation goes away. Don't touch reactivation reactively — only when reactivation work is already in scope.

## Workiz-side mechanism (cribbed from reactivation)

The SMS text travels through Workiz, not through SMS provider APIs directly:
1. Render creates a Workiz job with custom field `information_to_remember` = the SMS body
2. After 3-second pause (Workiz commit race), Render updates job's SubStatus
3. Workiz automation fires on the SubStatus change and sends SMS using `information_to_remember`

**Reactivation uses SubStatus = "API SMS Test Trigger".**
**Follow-up uses SubStatus = "Follow Up Trigger"** (DJ created this in Workiz).

Both ride parent Status="Pending". `workiz_post()` auto-injects `Status="Pending"` whenever `SubStatus` is in body — see `project_workiz_substatus_needs_status.md`.

## Endpoints

- `GET /owner/api/todos` — extended to return `id`, `res_model`, `res_id`, `partner_id`. Resolves partner_id by walking up from Property → Contact when needed; resolves SO-linked activities by reading `partner_id` on the SO and walking up.
- `POST /owner/api/followup/preview` — read-only. Builds SMS from Python template, returns history + cooldown status. Does NOT write to Odoo.
- `POST /owner/api/followup/launch` — clones latest Workiz job for contact, fires SubStatus, writes `x_studio_last_followup_sent`, marks `mail.activity` done.
- `POST /owner/api/followup/markdone` — closes to-do without sending (when DJ handled it another way).

## Cooldown

- Field: `x_studio_last_followup_sent` on `res.partner` (date, id=20151, created 2026-04-27)
- Days: 45
- Enforced on `/launch` (blocking, returns ok:false). Preview only warns.
- Reactivation cooldown is 90 days via `x_studio_last_reactivation_sent` — different field, independent counter.

## SMS template

In `_build_followup_sms()` in `dashboard.py`. DJ said wording is a starter and he'll iterate. To change copy: edit one Python function, push, live in 2 min. No Odoo Studio editing.

Calendly slug-by-city map is duplicated from reactivation PREVIEW script (`ODOO_REACTIVATION_PREVIEW.py` lines 124-139). If reactivation's slug map changes, follow-up's must change too — or refactor both to share.

## UI

- To-do cards in field.html become clickable when `partner_id` is set (i.e., resolvable to a contact). Cards without a partner stay read-only.
- Tap → bottom-sheet modal (`#followup-modal`) styled like the existing voice modal. Three buttons: Cancel / Mark Done (no send) / Send Follow-Up.
- Send button is disabled when cooldown warning fires.

## What DJ has to do in Workiz

1. Create new SubStatus "Follow Up Trigger" under parent Status "Pending"
2. Set up Workiz automation on that SubStatus that sends SMS using `information_to_remember` field — same as the reactivation automation, just on a different SubStatus

Until DJ does step 2, the launch endpoint will create the job and set the SubStatus, but no SMS will go out.

## Why: Knowing this saves time when

- Someone asks "why doesn't follow-up use SA 600 like I expected?" — answer: deliberate architectural shift, not an oversight.
- Someone asks "does follow-up share fields with reactivation?" — answer: shares `information_to_remember` and parent Status="Pending", but uses its own cooldown field and own SubStatus.
- A new follow-up template wording request comes in: edit `_build_followup_sms()` and deploy. Don't touch any Odoo server action.

## How to apply

- Bug reports against follow-up: check Render logs first, not Odoo chatter — the code path is pure Python.
- Calendly link broken? Same root cause as reactivation (the slug map). Fix in both places or refactor.
- "Cooldown is wrong" → adjust `FOLLOWUP_COOLDOWN_DAYS` constant at top of the follow-up section.
- "SubStatus name is different now" → adjust `FOLLOWUP_SUBSTATUS` constant. Don't hardcode it in JS.

---

### GPS-driven timesheet autofill — Phase 1 (data collection) shipped 2026-04-30
`project_gps_timesheet_autofill.md`
> Foundation for replacing manual per-task timer with GPS-derived per-person timesheet entries. Phase 1 collects pings while employees are clocked in. New x_gps_ping Studio model. Endpoint /api/payroll/gps_ping. timeclock.html watchPosition with 5-min/100m throttle. Per-person model — both DJ and Danny ping independently when riding together; auto-fill (Phase 3) creates one timesheet line per employee per matched stop.

**READ when extending the GPS logger, building the cluster/match algorithm (Phase 2), or wiring auto-fill (Phase 3).**

## Why this exists

DJ + Danny don't want to start/stop a timer per task — they just want to clock in once at start of day and have per-task hours filled in automatically based on where the phone was. Bonus: when DJ misses a timer toggle, the GPS data corrects the timesheet retroactively.

## Phase 1 (this build) — Data collection

Storage model: **x_gps_ping** (Odoo Studio, model_id=1024)

| Field | Type | Notes |
|---|---|---|
| `x_employee_id` | m2o → hr.employee | Required. ondelete=cascade. |
| `x_timestamp_utc` | Datetime | Required. UTC. |
| `x_lat` | Float | Required. |
| `x_lng` | Float | Required. |
| `x_accuracy_m` | Float | Optional — meters. From browser's GeolocationPositionError.accuracy. |
| `x_shift_id` | Char | Synthesized "{emp_id}:{check_in_utc_iso}" — same format as `_shift_id()` in dashboard.py for the Manage Shifts UI. Empty string if employee not currently clocked in. |
| `x_active_so_id` | m2o → sale.order | Optional — what the employee thinks they're working on, if any. |
| `x_active_task_id` | m2o → project.task | Optional — same. |

ACL: Administrator group has full read/write/create/unlink. Internal User group has read+create. Render's API user (UID=2) writes via JSON-RPC.

## Endpoint

`POST /owner/api/payroll/gps_ping`
- Body: `{employee_id, lat, lng, accuracy?, active_so_id?, active_task_id?}`
- Server tags the ping with the current shift_id by reading `payroll.clockin.{emp_id}` from ir.config_parameter
- Returns `{ok: true, ping_id, shift_id}`

## Frontend behavior (timeclock.html)

- `startGpsTracking()` is called from `updateClockUI()` whenever `clockedIn=true`. `stopGpsTracking()` is called when `clockedIn=false`.
- Uses `navigator.geolocation.watchPosition({enableHighAccuracy: false, maximumAge: 30000, timeout: 60000})`.
- Throttle: a position is converted into a ping only if **both** of these are true:
  - 5 minutes have passed since last ping, OR
  - the phone has moved more than 100m since last ping
  
  (Implemented as: skip if elapsed<5min AND moved<100m. So either condition can fire a ping.)
- Status indicator (`#gps-status`) below the CLOCK OUT button shows last ping time + accuracy. Hidden when not tracking.
- On geolocation error → red status with the error message. No retry — just informative.

## Two-person scenario (DJ + Danny on one truck)

Each phone runs its own GPS watcher with its own employee_id. Pings are stored per-employee. Phase 3 auto-fill will create separate timesheet entries per employee on the same matched task → correct for payroll (Danny gets paid hourly, both per-person hours visible) and project costing (2 person-hours visible on a 1-hour job).

## Limitations to remember (and address in Phase 4)

1. **Foreground only.** Web `watchPosition` only fires when the page is visible/focused. If Danny closes the tab or his phone screen sleeps, no pings during that gap. Phase 4 may add a TWA/Bubblewrap wrapper or PWA Wake Lock to mitigate.
2. **No backfill if forgot to clock in.** GPS only logs while the JS knows employee is clocked in. If DJ forgets to clock in, no pings → no auto-fill that day.
3. **Indoor accuracy** drifts to ±30m. Cluster algorithm in Phase 2 will tolerate this.
4. **Quarter-hour rounding** applied at Phase 3 (matches existing payroll FLSA rule).

## Phase roadmap (open tasks)

- **Phase 1** ✅ shipped commit `38c3030a` (this) + `466c97d1` (timeclock.html) + Studio model creation
- **Phase 2** (task #39): cluster algorithm + match to res.partner addresses + read-only "stops timeline"
- **Phase 3** (task #40): auto-write account.analytic.line per stop, manual review UI, drive-time allocation
- **Phase 4** (task #41): mileage logs, native Android wrapper for background GPS

## Files involved

- `static/owner/gps_tracker.js` — **shared module** (added 2026-04-30 commit 3e46318b). Exposes `window.WSC_GPS.start(employeeId)`, `.stop()`, `.isActive()`. Throttle constants + haversine + watchPosition all in here. Both timeclock.html and field.html load it via `<script src="/static/owner/gps_tracker.js">`.
- `routers/owner/dashboard.py`:
  - `/api/payroll/gps_ping` endpoint (POST) — stores ping in x_gps_ping
  - `/api/whoami` (GET) — resolves access_code → {type, name, employeeId} for field.html
- `static/owner/timeclock.html` — calls `WSC_GPS.start()` from `updateClockUI()` when clockedIn=true; `WSC_GPS.stop()` when false. Status indicator div: `#gps-status` near the CLOCK OUT button.
- `static/owner/field.html` — `initGpsWatcherFromAccessCode()` runs from `boot()`. Resolves employee_id via `/api/whoami`, then polls `/api/payroll/status` every 60s + on `visibilitychange` to start/stop the watcher based on the same source-of-truth clock state. Status indicator is a fixed top-right badge so it doesn't conflict with the page layout.
- Odoo Studio model: `x_gps_ping` (id 1024), 8 fields all stored

## Multiple-tab behavior

If both timeclock.html and field.html are open in different tabs while clocked in, BOTH will fire pings. The Phase 2 cluster algorithm absorbs duplicates within tolerance, so this is harmless (just extra DB rows). No coordination is implemented because the cost is low.

## Validation / smoke test (already done)

Created + deleted a test ping via the Studio model creation script. Endpoint not yet hit from a real browser — that happens when DJ or Danny next clocks in.

## Browser permission flow

First clock-in after deploy will prompt: "wsc-field-assistant.onrender.com wants to use your location." DJ/Danny tap Allow. Permission persists across sessions until manually revoked or browser data wiped.

---

### Gusto Integration Status (2026-04-24)
`project_gusto_integration_status.md`
> CSV export endpoint partially complete; blockers = Gusto CSV format confirmation, button scope fix, Playwright selector calibration

## Current State

### What's Done
✅ Render endpoint `/api/payroll/gusto_export` created
  - Fetches hr.attendance for date range
  - Applies quarter-hour rounding + CA 4-hour reporting-time pay minimum
  - Outputs CSV with columns: Employee Name, Date, Hours
  - Example: `Dan Saunders,2026-04-20,4.75`

✅ Download CSV button in Manage Shifts UI
  - Green button (#10b981), placed in gusto-export section
  - Currently wired to export single employee (whoever is selected in employee picker)
  - File downloads as attachment

✅ Playwright skeleton created
  - Path: `saunders-render-app/scripts/gusto_upload.py`
  - 110 lines, handles: browser launch, login, file upload, confirmation
  - Uses env vars: GUSTO_EMAIL, GUSTO_PASSWORD
  - Outputs screenshot on success
  - **Selectors are TODOs** (need calibration)

### What's Blocked

#### Blocker 1: Gusto CSV Format - INFORMATION NEEDED
**Status:** Waiting on DJ confirmation

Gusto's "Smart Import" feature claims to auto-match columns, but exact expected format unknown.

Current export: `Employee Name, Date, Hours`

**Possible requirements:**
- Does Gusto need `Employee Email` instead of/in addition to name?
- Does Gusto need separate columns for Overtime, Regular Time, PTO?
- Does Gusto need date in specific format (MM/DD/YYYY vs YYYY-MM-DD)?
- Are hours expected as decimal (4.75) or minutes (285)?

**How to Resolve:**
1. DJ logs into Gusto account
2. Goes to Time Tracking → Import
3. Downloads CSV template or sample file
4. Provides first row (headers) and 1-2 sample rows
5. We update `/api/payroll/gusto_export` endpoint to match exact format

**Impact:** Without correct format, Playwright upload fails or imports incorrectly (wrong hours recorded).

#### Blocker 2: Download Button Scope - CODE FIX PENDING
**Status:** Ready to fix once Gusto format is confirmed

Current bug:
```javascript
// Current behavior: exports only selected employee
const empId = currentSmEmpId();  // returns selected employee
window.location.href = `/api/payroll/gusto_export?start_date=${start}&end_date=${end}&employee_id=${empId}`;
```

Should be:
```javascript
// Fixed behavior: exports ALL employees, ignores picker
window.location.href = `/api/payroll/gusto_export?start_date=${start}&end_date=${end}`;
// Endpoint default: if employee_id omitted, query all active hr.employee records
```

**Backend logic (unchanged):**
```python
def gusto_export():
    emp_id = request.args.get('employee_id')  # optional param
    if emp_id:
        employees = [int(emp_id)]  # single employee
    else:
        # All active employees
        employees = [e['id'] for e in odoo_rpc('hr.employee', 'search_read', 
            [[['active', '=', True]]], {'fields': ['id']})]
    
    # Rest of logic fetches hr.attendance for all in list, groups by employee + date
```

**Why:** Gusto expects one CSV with all employees for batch Smart Import. Separate exports per employee is inefficient.

**Fix effort:** 2 lines of JavaScript + 3 lines of backend logic.

#### Blocker 3: Playwright Selector Calibration - USER ACTION REQUIRED
**Status:** Skeleton ready, selectors are TODOs

Current skeleton:
```python
# TODO: fill in selectors via playwright codegen
async def login(page):
    await page.goto('https://app.gusto.com/login')
    # await page.fill('[TODO_EMAIL_SELECTOR]', email)
    # await page.fill('[TODO_PASSWORD_SELECTOR]', password)
    # await page.click('[TODO_LOGIN_BUTTON_SELECTOR]')

async def upload_csv(page, csv_path):
    # await page.goto('[TODO_IMPORT_PAGE_URL]')
    # await page.fill('[TODO_FILE_INPUT_SELECTOR]', csv_path)
    # await page.click('[TODO_CONFIRM_BUTTON_SELECTOR]')
```

**How to Calibrate:**
1. Install Playwright: `pip install playwright && playwright install chromium`
2. Set env vars: `setx GUSTO_EMAIL "email@gusto.com" && setx GUSTO_PASSWORD "password"`
3. Run codegen: `playwright codegen https://app.gusto.com/login`
4. Browser opens, user logs in → import flow → selects file → imports
5. Codegen auto-generates selector code; copy into `gusto_upload.py`

**Why:** Selectors are account + UI-version specific. User's account interface may differ from mine. Codegen records the exact path through their UI.

**Effort:** ~10 minutes to walk through once; one-time setup.

**Usage (After Calibration):**
```bash
python scripts/gusto_upload.py "/path/to/wsc_hours_2026-04-20_to_2026-05-03.csv"
# User approves 2FA on phone; script finishes upload
```

## Implementation Checklist

```
[ ] DJ downloads Gusto CSV template (or sample import file)
[ ] DJ provides column headers + sample row
[ ] Claude updates /api/payroll/gusto_export endpoint (column names)
[ ] Claude fixes Download CSV button (omit employee_id, query all)
[ ] Claude deploys both changes to main
[ ] DJ installs Playwright deps (pip install playwright && playwright install chromium)
[ ] DJ runs playwright codegen + walks through login/import
[ ] DJ provides selectors (copy/paste from codegen output)
[ ] Claude updates gusto_upload.py with real selectors
[ ] Claude deploys to main
[ ] At next pay period: DJ runs gusto_upload.py, approves 2FA, done
```

## How to Apply

**Until blockers are resolved:**
- Continue using manual clock in/out on Render
- Manage Shifts UI is ready for edits + retroactive adds
- CSV export button works but exports only one employee (not useful yet)

**After Gusto format confirmed + code fixed:**
- Download CSV → all employees + all hours for date range
- Send to Gusto via button (opens CSV) or manually

**After Playwright calibrated:**
- Fully automated: `python scripts/gusto_upload.py "path.csv"` + 2FA approval = done

## Known Gotchas

- **Gusto Smart Import may have rate limits.** If uploading frequently, watch for throttling.
- **Gusto deletes prior data on import.** Each upload overwrites that pay period (good for corrections, bad if you double-submit).
- **2FA may block headless automation.** Playwright script will pause and wait for user approval — phone gets push notification.
- **CSV format mismatch = silent failure.** Gusto may accept the file but map columns wrong (hours go to OT, names become notes, etc.). Always spot-check first import in Gusto UI.

## Email References
- Gusto support email: none yet (DJ to provide if needed)
- Playwright docs: https://playwright.dev/python/

## Related Files
- `/api/payroll/gusto_export` endpoint — saunders-render-app/routers/owner/dashboard.py (lines 2900–2951)
- Download CSV button — saunders-render-app/static/owner/timeclock.html (exportGusto function)
- Playwright script — saunders-render-app/scripts/gusto_upload.py

---

### Invoice wizard refuses when qty_delivered=0 — must force-deliver SO lines before invoicing
`project_invoice_qty_delivered_gate.md`
> 2026-04-30 — Odoo's sale.advance.payment.inv wizard fails with "No items available to invoice" when SO lines have qty_delivered < product_uom_qty AND the product invoicing policy is 'delivery' or service_policy is 'delivered_timesheet'. Surfaced collecting Zelle for Betsy Justice via Render Claude. Fix: write qty_delivered=product_uom_qty on real lines (qty>0, price>0) BEFORE calling create_invoices. Helper `_force_lines_deliverable(so_id)` lives in Saunders Render App/routers/owner/dashboard.py and is called by both record_check_payment and _execute_payment.

**READ when editing any code that creates an invoice from a sale.order.**

## The gate

Odoo's `sale.advance.payment.inv.create_invoices()` wizard (Odoo 19) raises `UserError("Cannot create an invoice. No items are available to invoice.")` when **every** non-deleted SO line has `qty_to_invoice <= 0`.

`qty_to_invoice` is computed from the product's invoicing policy:

| Product type | invoicing policy | What gates `qty_to_invoice` |
|---|---|---|
| Storable / consumable | `order` (Ordered Quantities / Prepaid) | `product_uom_qty - qty_invoiced` (always available once SO confirmed) |
| Storable / consumable | `delivery` (Delivered Quantities) | `qty_delivered - qty_invoiced` (requires stock delivery or manual write) |
| Service | `service_policy='ordered_prepaid'` | Same as `order` above |
| Service | `service_policy='delivered_manual'` | Same as `delivery` — set `qty_delivered` manually |
| Service | `service_policy='delivered_timesheet'` | Sums hours from `account.analytic.line` (timesheets) for the linked task |
| Service | `service_policy='delivered_milestone'` | Requires milestone reached |

Most W&SC service products are `delivered_timesheet` or `delivered_manual`. If DJ collects payment **before** logging timesheets / before marking the FSM task done, `qty_delivered=0` on every line, `qty_to_invoice=0`, wizard refuses.

## The fix (already deployed 2026-04-30, commit 3f80c1d5)

Helper `_force_lines_deliverable(so_id)` in `Saunders Render App/routers/owner/dashboard.py`:

```python
lines = sale.order.line.search_read(domain, fields=['id', 'product_uom_qty', 'qty_delivered', 'price_unit'])
for ln in lines:
    if qty > 0 and price > 0 and delivered < qty:
        write({'qty_delivered': qty})
```

Called BEFORE `sale.advance.payment.inv.create_invoices` in both invoice paths:
1. `record_check_payment` tool (Render Claude voice flow) — line ~1300
2. `_execute_payment` (`/api/payment` field-assistant flow) — line ~2740

## Rules going forward

- **Never call `sale.advance.payment.inv.create_invoices` without first ensuring qty_delivered ≥ qty_ordered on the lines you want invoiced.** Always either (a) call `_force_lines_deliverable` first, or (b) verify timesheets are logged.
- **Soft-delete pattern compatibility** — DJ uses `qty=0 + price=0` to "delete" lines on confirmed SOs. The helper skips these (filters on `qty > 0 AND price > 0`) so it doesn't accidentally revive them.
- **Idempotent** — running it twice writes the same value the second time. Safe to call on every invoice attempt.
- **Future task→delivered hook compatibility** — if DJ marks the FSM task done after invoicing, Odoo's industry_fsm_sale module sets `qty_delivered=qty_ordered`. Same value we already wrote, no conflict.
- **Phase 6 / Zapier paths** — if any future Zapier code creates invoices from Odoo, replicate this pattern. Phase 6 currently goes Odoo→Workiz only (payment sync), not invoice creation, so it's not affected.

## What surfaced this

DJ tried "Zelle from Betsy Justice" via Render Claude. `record_check_payment` ran, fetched SO, found no draft invoice, called `create_invoices` → wizard threw the UserError. Bug existed silently in `_execute_payment` too — never triggered because most field-assistant payments happen after timesheets are logged.

## Related memory

- `project_so_lines_zero_means_deleted.md` — the qty=0/price=0 soft-delete pattern the helper respects
- `project_phase6_tech_gate.md` — payment-sync direction (Odoo→Workiz, not the other way)
- `feedback_done_jobs_definition.md` — "Done" = `x_studio_x_studio_workiz_status='Done'`, NOT invoice/payment state (relevant if you're tempted to gate this on Done status)

---

### Multi-Business Architecture Plan
`project_multi_business_architecture.md`
> Full plan for expanding DJ's Odoo/Render platform to multiple businesses and users — Cheryl real estate, payroll, artwork eCommerce

# Multi-Business Architecture

**Decided:** 2026-04-18
**Updated:** 2026-04-19
**Status:** Scaffold LIVE. Login system built. saunders-render-app repo live on Render.

---

## MASTER ARCHITECTURE

```
One Render Service (existing, paid plan)
    ├── Login/routing screen → routes by user/access code
    ├── DJ    → W&SC field assistant (current app, already live)
    ├── Danny → Payroll clock-in/out (planned)
    ├── Cheryl → Real estate assistant (planned)
    └── [future users/businesses]

One Odoo Instance (existing subscription, full package)
    ├── Company: Window & Solar Care (existing)
    ├── Company: Cheryl Real Estate (planned - multi-company)
    ├── Company: Artwork / AI Prints (planned - multi-company)
    └── Company: Saunders Printing (planned - multi-company)

Odoo Website (included in full package)
    ├── W&SC marketing site (planned)
    ├── Cheryl real estate site (planned)
    └── Saunders Printing storefront (planned — primary eCommerce)
```

---

## ODOO MULTI-COMPANY SETUP

- Odoo natively supports multiple companies in one instance
- Each company has completely separate: chart of accounts, P&L, invoices, bank accounts, tax settings
- One login, switch between companies from top menu
- DO NOT touch existing `x_studio_x_studio_record_category` field — build a NEW field for business type tagging

---

## CHERYL — 3-PHASE LOGIN PROGRESSION

**Phase 1:** Render only — Odoo is invisible backend. Cheryl uses her own access code on Render. No Odoo user needed. No extra cost.

**Phase 2:** Render primary + her own Odoo login under DJ's account. She can access Odoo directly if needed. Still DJ's subscription, added user.

**Phase 3:** Her own Odoo account entirely. I migrate all her data (contacts, accounting, history, documents). Update Render env vars to point to her new Odoo URL. Clean separation.

Transition between phases: any time, DJ's call, I handle it.

---

## ODOO WEBSITE MODULE

DJ has full Odoo package including Website module. Plan:
- Build W&SC website in Odoo (marketing + booking)
- Build Cheryl's real estate website in Odoo
- All landing pages through Odoo
- eCommerce when ready (already included in plan)
- Key advantage: lead forms → Odoo CRM automatically, no Zapier

Odoo supports MULTIPLE websites from one instance — one per business/company.

---

## PAYROLL TRACKER

**Workers:** DJ + Danny, both hourly
**Stack:** Render screen for clock-in/out → Odoo timesheets (account.analytic.line)
**Payroll processing:** Stay on Gusto for now. Odoo tracks hours, DJ manually enters into Gusto. Future: switch to Odoo payroll if Claude can automate enough.
**Access:** Danny sees only his own hours. DJ sees everything (both workers, weekly totals, what's owed).
**Status:** Ready to build. No blockers.

---

## ARTWORK / eCOMMERCE BUSINESS

**Concept:** AI artwork using Midjourney → sell on Etsy + Shopify/Odoo

**API access:**
- Midjourney: NO official API. Use manually. Workarounds exist but against ToS.
- Etsy: ✅ Official API — create/update listings, manage orders, upload images
- Shopify: ✅ Excellent API — full store automation
- Alternative art generation: DALL-E 3 or Stable Diffusion have real APIs Claude can call

**Platforms:**
- Etsy = marketplace traffic/discovery
- Shopify OR Odoo eCommerce = branded store, higher margin
- Sync inventory between platforms, manage in Odoo

**Claude's role after art is approved:**
1. Resize/optimize images for each platform
2. Write title, description, tags (SEO)
3. Create listing on Etsy + Shopify/Odoo simultaneously
4. Set pricing, categories, shipping
5. Order comes in → log, update inventory, trigger fulfillment

**Status:** Green-lighted as future project. Not started. Revisit when other priorities are done.

---

## BUILD PRIORITY ORDER

1. W&SC accounting migration (QB → Odoo) — waiting on DJ's file exports
2. Cheryl Odoo company setup — need her business name
3. Cheryl real estate Render screen — need MLS info + stage checklist
4. Cheryl accounting setup — need her expense categories + bank info
5. DJ + Danny payroll tracker — ready to build anytime
6. Artwork eCommerce — future, after above complete
7. Saunders Printing — web-to-print site, Odoo eCommerce, Stripe, file prep automation
8. W&SC website in Odoo — future
9. Cheryl website in Odoo — future

## BUSINESSES SUMMARY

| Business | Status | Platform | Notes |
|---|---|---|---|
| Window & Solar Care | LIVE | Render + Odoo | Field assistant, full automation |
| Cheryl Real Estate | Planning | Render + Odoo multi-company | Need info from Cheryl |
| Artwork / AI Prints | Green-lighted | Odoo + Etsy/Shopify APIs | Flux/DALL-E 3, Printify fulfillment |
| Saunders Printing | Green-lighted | Odoo Website + Stripe | Web-to-print, DJ prints/ships |
| Payroll (DJ+Danny) | Ready to build | Render + Odoo timesheets | No blockers |

---

### Next Job Date field - COMPLETE
`project_next_job_date_field.md`
> New res.partner field x_studio_next_job_date to exclude contacts with future scheduled jobs from reactivation filter

Add a Date field `x_studio_next_job_date` to `res.partner` so the reactivation filter can exclude customers who already have a future job scheduled.

**Why:** Kevin Hile (SO 003912, Apr 23 2026) appeared in the reactivation candidate filter even though he already has a job coming up. Need a way to automatically exclude these customers without manual tagging.

**How to apply:** This work is NOT done yet. Pick it up at the start of the next session.

## Steps remaining (in order):

1. ~~**Create field via Odoo API**~~ — DONE. `x_studio_next_job_date`, ttype `date`, field ID 18764 on `res.partner` (model ID 90)
2. ~~**Add to contact form view**~~ — DONE. View ID 728, placed below `x_studio_last_reactivation_sent`
3. ~~**Phase 3**~~ — DONE. Calls `write_next_job_date_to_contact(contact_id, job_datetime)` at end of paths A, B, C
4. ~~**Phase 4**~~ — DONE. Calls `clear_next_job_date_on_contact(contact_id)` when status is Done or Canceled
5. ~~**Phase 5**~~ — DONE. Calls `write_next_job_date_to_contact(contact_id, scheduled_datetime)` after successful job creation
6. ~~**Reactivation filter**~~ — DONE. DJ needs to add to filter: "Next Job Date is not set" OR "Next Job Date is before today". Backfill script run 2026-04-02, populated 48 contacts. Field `x_studio_x_studio_workiz_status` used as filter (not just state='sale') — only SOs with scheduling statuses count.

## Context:
- Reactivation filter lives on `res.partner` in Odoo (custom filter DJ built)
- Current filter already has: exclude Dan Saunders/Window & Solar Care, Record Category = Contact, Last Visit All Properties < 01/01/2025, Last Reactivation Sent < date, Active/Lead = Active, Has Solar/Window Service
- The new condition slots in alongside those existing rules

---

### Odoo Accounting Migration Plan
`project_odoo_accounting_migration.md`
> Complete plan to migrate DJ's financials from QuickBooks into Odoo accounting — revenue from Odoo/Workiz, expenses from QB CSV, opening balances from real accounts

# Odoo Accounting Migration — Full Detail

**Created:** 2026-04-15
**Status:** Planning complete, not yet started. DJ is in thinking/prep stage only.

---

## BACKGROUND & CONTEXT

DJ runs Window & Solar Care as a solo/contractor service business. He is migrating away from QuickBooks Online and Workiz, moving everything into Odoo. The accounting migration is a separate phase from the operational migration (Workiz→Odoo sync) which is already running.

### How the current system works (important for context)
- All jobs are managed in Workiz
- When DJ marks a job Done and invoices the customer in Workiz, Workiz auto-syncs the invoice AND payment to QuickBooks via a built-in integration
- In QB: invoice hits Sales + Accounts Receivable; payment hits AR + Undeposited Funds
- When Chase bank transactions come in (linked to QB), DJ matches the deposit → zeroes Undeposited Funds → credits Checking
- Expenses also come in from Chase bank feed and DJ categorizes them in QB

### Problems with current system
- Workiz→QB sync has duplicate/orphaned payment issues — sometimes creates extra invoices or payments in QB that have no matching bank transaction, leaving them permanently open
- DJ has not categorized all 2025 and 2026 expenses yet
- DJ has not fully reconciled QB and does not want to — it's too tedious
- Workiz is being phased out — the Workiz→Odoo phases (3,4,5,6) are already handling new jobs

### Why the migration approach works without reconciling QB
Because we are using **real account balances** (logged into actual Chase/credit card/loan accounts on cutover day) as opening entries in Odoo. This makes QB's internal reconciliation state irrelevant. Whatever QB says is offset by the truth from the actual bank.

---

## THE THREE DATA SOURCES

### 1. Odoo SOs (Sales Orders)
- Every job ever synced from Workiz exists as an SO in Odoo
- SO name format: Workiz Job ID zero-padded to 6 digits. Example: Workiz job 4265 = Odoo SO name `004265`
- Each SO has: customer, service date (date_order), line items, amounts, Workiz UUID, payment method info
- SOs with Workiz status "Done" are completed paid jobs — these need invoices created

### 2. Workiz Payment CSVs (6 files, one per year)
- Downloaded from Workiz Reports → Payment Report
- Workiz only allows one year at a time — DJ downloads 6 separate files
- File naming convention: `Workiz_Payments_YYYY.csv`
- Stored in: `C:\Users\dj\Downloads\`
- Sample file already reviewed: `Payment report - 04-15-2026.csv`
- Columns confirmed: Job ID, Document, Payment type, Status, Amount, Service Fee, Net, Tips, Technician, Client name, Transaction method, Card, Payment date, Payment time, Collected by, Description, Job type, Job status, Confirmation code
- **Join key:** Workiz Job ID (e.g. 4265) → Odoo SO name (e.g. 004265) by zero-padding to 6 digits
- Payment types seen: Check, Credit charge — need to map to Odoo payment journals
- Contains exact payment date, amount, and method per job — this is authoritative

### 3. QuickBooks Transaction Detail CSV
- Already downloaded: `C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail by Account.csv`
- Date range: January 1, 2019 – April 15, 2026
- Size: 17,335 rows, 16,777 actual transactions
- **Transaction type breakdown:**
  - Expense: 6,318 rows ← THIS is what we need from QB
  - Invoice: 4,131 rows ← SKIP — Odoo SOs are better source
  - Payment: 3,222 rows ← SKIP — Workiz CSVs are better source
  - Deposit: 2,575 rows ← handled by bank feed matching in Odoo
  - Journal Entry: 266 rows ← review individually, some may be needed
  - Credit Card Payment: 164 rows ← may need for balance sheet
  - Transfer: 60 rows ← between accounts, handle with opening balances
  - Check: 4 rows
- **Account sections in the file (balance sheet accounts seen):**
  - TOTAL BUS CHK (9008) — Chase checking account
  - Undeposited Funds
  - Discover (credit card)
  - Discover II
  - Shop Your Way - Mastercard
  - Thank You Card
  - CRV Loan (deleted)
  - Ford Transit 250 2019 Loan
  - Notes Payable - Saunders Printing
  - Toyota Loan
  - Van Shelving Loan
  - Opening Balance Equity
  - Owner's Investment
  - Owner's Pay & Personal Expenses
  - Discounts given
  - Services (revenue)
- **Expense categories confirmed in QB:**
  - Advertising & Marketing (EDDM Post Cards, Herald Mag, Lead Generation)
  - Bank Charges & Fees (Credit Processing Fees)
  - Car & Truck (Auto Insurance, Fuel, Vehicle Maintenance and Repair)
  - Contractors
  - Dues & Subscriptions
  - Employee Benefits
  - Equipment Purchase
  - Equipment Rental
  - Insurance
  - Interest Paid
  - Job Supplies
  - Meals & Entertainment
  - Office Supplies & Software (Scheduling Software, Software - Other)
  - Other Business Expenses
  - Rent & Lease
  - Repairs & Maintenance
  - Supplies & Materials - Not Job Specific (Screens)
  - Taxes & Licenses
  - Travel
  - Uncategorized Expense
  - Utilities
- **This file must be re-exported AFTER DJ categorizes 2025/2026 expenses** so the newly categorized items are included

### 4. QuickBooks Fixed Asset List (not yet exported)
- QB tracks vehicles and equipment separately with depreciation schedules
- Must be exported from QB: Reports → Fixed Asset List
- Contains: asset name, purchase date, purchase price, current book value (after depreciation)
- Needed for the balance sheet — vehicles/equipment show up as assets in Odoo

---

## DECISIONS ALREADY MADE (do not re-litigate these)

1. **No QB reconciliation** — DJ is not reconciling QB before migration. Opening balances from real accounts make it unnecessary.

2. **No QB customer balance / open invoices report** — Not needed. All customers pay at the door. There is no AR. Odoo already knows who paid from the Workiz payment CSVs.

3. **No QB deposit matching** — Not needed. Matching deposits to QB invoices produces data we're throwing away. Skip it entirely.

4. **Revenue source = Odoo + Workiz, NOT QuickBooks** — Odoo SOs have more detail (service type, line items, job date, customer) than QB invoices ever had. QB invoice rows are ignored during import.

5. **Expense source = QB Transaction Detail CSV** — QB is the only place expenses ever lived. This is the one thing QB has that Odoo doesn't.

6. **Opening balances from real accounts** — On cutover day, DJ logs into Chase, each credit card, and each loan account and reads the actual balance. These become opening journal entries in Odoo. Claude handles all double-entry.

7. **Workiz→QB sync problems are irrelevant** — The duplicate/orphaned payment issues in QB don't matter. Our new system bypasses Workiz→QB entirely and drives invoicing from Workiz payment CSVs directly.

8. **DJ does not want to do anything manually in Odoo accounting setup** — Claude handles all journal entries, chart of accounts, opening balances, scripts. DJ supplies numbers and files.

---

## PHASE-BY-PHASE PLAN

### PHASE 1 — QuickBooks Cleanup (DJ does this, no Claude involvement)
**Purpose:** Get expense history accurate before final export

Steps:
1. Open QuickBooks Online
2. Go to Banking → Review (or Transactions → Banking)
3. For every uncategorized expense in 2025 and 2026: assign the correct expense category
4. Do NOT match deposits to invoices — waste of time
5. Do NOT reconcile — not needed
6. When done: re-export Transaction Detail by Account CSV (same report, full date range 2019–today)
7. Save new file as: `C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail FINAL.csv`

**Why this matters:** The 6,318 expense rows in the CSV will have "Uncategorized Expense" for anything not categorized. If we import those into Odoo they're useless. Do the categorization once in QB, then export and never go back.

---

### PHASE 2 — Gather All Source Files (DJ does this)
**Purpose:** Collect everything Claude needs before touching Odoo

Files to collect:
1. **QB Transaction Detail CSV** — re-export after Phase 1 (replaces current file)
2. **QB Fixed Asset List** — QB → Reports → Fixed Asset List → export CSV
3. **6x Workiz Payment CSVs** — Workiz → Reports → Payment Report, one per year:
   - `Workiz_Payments_2021.csv` (or earliest year available)
   - `Workiz_Payments_2022.csv`
   - `Workiz_Payments_2023.csv`
   - `Workiz_Payments_2024.csv`
   - `Workiz_Payments_2025.csv`
   - `Workiz_Payments_2026.csv`
   - Drop all in `C:\Users\dj\Downloads\`

When all files are in Downloads, tell Claude and provide the exact filenames.

---

### PHASE 3 — Choose Cutover Date & Gather Real Account Balances (DJ does this)
**Purpose:** Establish the opening state of every balance sheet account

DJ picks a cutover date (recommendation: first of a month, e.g. June 1, 2026).

On that date, DJ logs into each account and records the actual balance:

| Account | Institution | Balance Needed |
|---|---|---|
| Chase Checking (9008) | chase.com | Ending balance on cutover date |
| Discover Card | discover.com | Statement balance |
| Discover II | discover.com | Statement balance |
| Shop Your Way Mastercard | | Statement balance |
| Thank You Card | | Statement balance |
| Ford Transit 250 2019 Loan | Lender | Remaining payoff balance |
| Toyota Loan | Lender | Remaining payoff balance |
| Van Shelving Loan | Lender | Remaining payoff balance |
| Notes Payable — Saunders Printing | Own records | Amount still owed |
| Owner's Equity | Calculated | Assets minus Liabilities (Claude calculates) |

DJ gives these numbers to Claude. Claude enters them as opening journal entries. All entries offset to "Opening Balance Equity" account (standard accounting practice). Claude then zeros Opening Balance Equity into Retained Earnings.

---

### PHASE 4 — Odoo Accounting Setup (Claude does this via API)
**Purpose:** Configure Odoo's accounting module to receive data

Steps Claude handles:
1. **Chart of Accounts** — create/map all QB expense categories to Odoo accounts
   - Use QB category names exactly so historical imports match
   - Key accounts: all expense categories listed above + AR, AP, Checking, Undeposited Funds, each credit card, each loan, Owner's Equity
2. **Payment Journals** — create journals for:
   - Check
   - Cash
   - Credit Card (generic)
   - Zelle (used for some payments)
   - Bank (Chase) — connected to bank feed
3. **Opening Balance Journal Entries** — one entry per account using Phase 3 numbers
4. **Fixed Assets** — enter each vehicle/equipment from QB Fixed Asset List
   - Asset name, purchase date, original cost, accumulated depreciation, current book value
5. **Bank Feed Connection** — DJ connects Chase to Odoo (requires DJ's Chase login, cannot be done by Claude)
   - In Odoo: Accounting → Configuration → Add Bank Account → connect Chase
   - After connected, transactions flow in automatically — same as QB

---

### PHASE 5 — Bulk Invoice Creation + Payment Application (Claude builds and runs script)
**Purpose:** Create invoices for all 6 years of completed jobs and apply payments

**Script logic:**
1. Query Odoo for all SOs where:
   - Workiz status (x_studio_workiz_status or equivalent field) = "Done"
   - No invoice yet exists (invoice_ids is empty)
2. For each SO:
   - Call `action_confirm()` if SO is still in draft (write date_order back after — Odoo resets it)
   - Create invoice: `sale.order` → `_create_invoices()` method
   - Post (confirm) the invoice: `action_post()`
3. Load all 6 Workiz payment CSV files, combine into one lookup table keyed by Job ID
4. For each invoice:
   - Zero-pad the SO name to get Job ID (e.g. `004265` → `4265`)
   - Look up matching payment row in Workiz CSV
   - If found: create payment in Odoo with correct amount, date, method
   - Apply payment to invoice (reconcile)
   - If not found: leave invoice open (these become flagged for review)
5. Report: how many invoices created, how many paid, how many left open

**Payment method mapping (Workiz → Odoo journal):**
- "Check" → Check journal
- "Credit charge" → Credit Card journal
- "Cash" → Cash journal
- "Zelle" → Zelle journal
- anything else → flag for review

**Important technical notes:**
- SO name join: Workiz Job ID is integer in CSV (e.g. 4265.0) → strip .0 → zero-pad to 6 digits → match SO name
- date_order on SO must be preserved — always write back after action_confirm()
- Invoice date = payment date from Workiz CSV (not today's date)
- Do NOT use `response` or `result` as variable names in any Odoo server action (reserved)
- Run in batches to avoid timeouts — 50 SOs at a time with error handling

---

### PHASE 6 — Import Historical Expenses from QB (Claude builds and runs script)
**Purpose:** Get 6 years of expense history into Odoo so P&L is complete

**Script logic:**
1. Read the final QB Transaction Detail CSV
2. For each row where Transaction type = "Expense":
   - Parse: date, vendor name (Name column), category (Split column), amount (negative = expense)
   - Create vendor bill in Odoo (`account.move` with move_type = `in_invoice`)
   - Set: partner (vendor name), invoice_date, account (mapped from QB category), amount
   - Post the bill
3. For Journal Entry rows: review list first, Claude presents them to DJ for decision on which to import
4. Skip: Invoice, Payment, Deposit, Transfer rows — handled by other phases or bank feed

**QB category → Odoo account mapping (to build during Phase 4):**
- Advertising & Marketing → Marketing/Advertising expense account
- Car & Truck → Vehicle expense account
- Bank Charges & Fees → Bank fees account
- etc. (full mapping built when chart of accounts is created in Phase 4)

**Volume:** ~6,318 expense rows. Will run in batches.

---

### PHASE 7 — Go Live (DJ switches from QB to Odoo for daily work)
**Purpose:** Stop using QB, start using Odoo for everything

Steps:
1. Chase bank feed now connected to Odoo (from Phase 4)
2. Transactions come in daily — DJ matches them in Odoo instead of QB
   - Deposits → match to invoices/payments sitting in Undeposited Funds (same as QB)
   - Expenses → categorize vendor/category (same as QB, Odoo learns over time)
3. New invoices → created automatically by Zapier Phase 6 (already running)
4. Stop logging into QuickBooks

---

### PHASE 8 — Validate (Claude checks, DJ confirms)
**Purpose:** Sanity check that the numbers make sense

1. Claude pulls P&L from Odoo for 2024 → compares income/expense totals to QB P&L for same period
2. Claude checks balance sheet → verifies cash, credit card, loan balances match real accounts
3. Any discrepancy → Claude creates an adjusting journal entry to correct it
4. DJ confirms the numbers look right

---

## WHAT DJ DOES vs. WHAT CLAUDE DOES

| Task | Who |
|---|---|
| Categorize 2025/2026 expenses in QB | DJ |
| Re-export QB Transaction Detail CSV (after categorizing) | DJ |
| Export QB Fixed Asset List | DJ |
| Download 6 Workiz payment CSVs (one per year) | DJ |
| Pick cutover date | DJ |
| Look up real account balances on cutover date | DJ |
| Connect Chase bank feed to Odoo | DJ (requires Chase login) |
| Daily: match deposits & categorize expenses in Odoo | DJ |
| Chart of accounts setup in Odoo | Claude |
| Payment journal setup in Odoo | Claude |
| Opening balance journal entries | Claude |
| Fixed asset entries | Claude |
| Bulk invoice creation script | Claude |
| Payment application from Workiz CSVs | Claude |
| Expense import script from QB CSV | Claude |
| All double-entry accounting | Claude |
| Validation and adjusting entries | Claude |

---

## POST-MIGRATION AUTOMATIONS TO BUILD (after books are live)

All of these were agreed upon on 2026-04-15. Build after accounting migration is complete.

1. **Nightly bank reconciliation script** — pulls new Chase transactions, matches deposits to invoices one-to-one (DJ deposits checks one at a time via phone — always 1:1), categorizes expenses by vendor name rules, flags unknowns for DJ review
2. **Monthly P&L email** — runs last day of every month via scheduled trigger:
   - Pulls P&L from Odoo API
   - Formats clean summary (revenue, expenses, net income, vs. prior month %)
   - Claude adds written commentary flagging anything unusual (expense spikes, revenue drops)
   - Includes one-click deep link to Odoo P&L with dates pre-filled: `https://window-solar-care.odoo.com/odoo/accounting/reports/profit-and-loss?date_from=YYYY-MM-01&date_to=YYYY-MM-DD`
   - Attaches PDF for records
   - Sends to windowandsolarcare@gmail.com via Gmail MCP
   - Creates activity in Odoo: "Monthly P&L ready — [link]"
3. **Weekly cash summary** — every Monday morning: checking balance, what came in, what went out that week
4. **Vendor categorization rules** — built once, run forever. New unknown vendors flagged to DJ, DJ confirms category once, never asked again.

---

## THINGS STILL TO DECIDE

- [ ] **Cutover date** — what date to go live on Odoo accounting?
- [ ] **How far back to import expenses** — all the way to 2019, or just 2024 forward?
- [ ] **Fixed assets** — full depreciation schedules or just current book value as a lump?
- [ ] **Journal entries from QB** — which of the 266 journal entry rows are needed vs. skip?

---

## QUICKBOOKS FINANCIAL SUMMARY (for reference)
Pulled via QuickBooks MCP on 2026-04-15, period 2020–2026:
- Total Income: $390,935
- Total Expenses: $214,159
- Net Operating Income: $176,759
- Revenue breakdown: Services $341,992 | Sales $40,118 | Unapplied Cash $8,433 | Tips $588
- Top expense categories: Car & Truck $47,493 | Supplies & Materials $39,885 | Office/Software $36,883 | Meals $11,462 | Utilities $11,489 | Advertising $19,855 | Interest $9,556 | Rent $15,843

---

## FILE LOCATIONS

| File | Location |
|---|---|
| This migration plan (detailed) | `C:\Users\dj\.claude\projects\...\memory\project_odoo_accounting_migration.md` |
| Migration checklist (for DJ) | `C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\3_Documentation\Odoo_Accounting_Migration_Plan.md` |
| QB Transaction Detail CSV (current) | `C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail by Account.csv` |
| Workiz Payment sample (2026) | `C:\Users\dj\Downloads\Payment report - 04-15-2026.csv` |
| Workiz 6-year master job data | `C:\Users\dj\Downloads\Workiz_6Year_Absolute_Master_FINAL.csv` |

---

## HOW TO RESUME THIS IN A NEW SESSION

Just tell Claude "I want to work on the accounting migration" — Claude will find this memory file automatically and have full context. No special phrase needed.

## DJ'S CHECKLIST DOCUMENT — WHERE TO FIND IT

DJ has a human-readable checklist version of this plan saved here:

**`C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\3_Documentation\Odoo_Accounting_Migration_Plan.md`**

If DJ asks "where is the accounting migration document?" or "where did we save that plan?" — point him to that path. It can be opened in any text editor, Notepad, VS Code, etc. Claude can also open and read it directly.

---

### Odoo action_confirm resets date_order to current time
`project_odoo_action_confirm_resets_date_order.md`
> Calling action_confirm() on a sale.order resets date_order to datetime.now() — must write it back immediately after confirming

Odoo's `action_confirm()` internally resets `date_order` to the current timestamp as part of its confirmation logic.

**Why:** When Phase 4 confirms an existing draft SO (e.g. user changes job status to Pending Scheduled on a job whose SO was previously created but never confirmed), `date_order` gets overwritten with the current time instead of the Workiz JobDateTime. First observed on SO 004253 (2026-04-01). Does not affect new SO creation because the date is set in the creation payload before confirm runs in the same transaction.

**How to apply:** After any `action_confirm()` call on an existing SO, immediately do a separate `write` call to restore `date_order` to the correct UTC value. In Phase 4, `confirm_sales_order(so_id, date_order_utc=...)` now does this automatically — always pass the date when calling it.

---

### Odoo customer names sometimes differ from how DJ pronounces them
`project_odoo_name_typos.md`
> Real example — DJ refers to customer as "Jon Hamm" but Odoo has him stored as "John Ham". Search must handle this fuzziness.

DJ's mental model of a customer's name doesn't always match what's stored in Odoo. Real example discovered 2026-04-27:

- DJ says: "Jon Hamm"
- Odoo stored: "John Ham" (partner_id 23052)

This is a data-entry quirk — the original creation likely had a typo, and DJ didn't notice (or did but the record stuck). It's not a bug in DJ's memory, and it's not worth fixing the data (might break Workiz sync history). Search has to handle it.

**Why:** Plain `ilike "Jon Hamm"` doesn't match "John Ham" — the substring isn't there. Even per-word `ilike "Jon"` doesn't match "John" because "Jon" isn't a substring of "John" (the `h` is between `o` and `n`).

**How to apply:**
- `tool_search_customers` in `saunders-render-app/routers/owner/dashboard.py` now does progressive fuzzy: full → AND words → AND with last-char truncation (Hamm→Ham, Jon→Jo) → OR fallback. The `>=3` threshold for truncation is the key — handles both trailing-letter typos and interior-letter substring failures.
- When debugging "Render Claude can't find X", first check Odoo for variant spellings: `name ilike '<part of name>'` with a short prefix.
- If a typo causes ongoing confusion, fix the contact name in Odoo (and verify Workiz sync still works) — but only when the customer's actual job records are stable.
- DON'T add Levenshtein/trigram unless we see real cases the truncation logic misses. Premature optimization.

---

### Odoo has no fuzzy/similar search operator — only ilike substring
`project_odoo_no_fuzzy_operator.md`
> DJ asked if there's a "fuzzy LIKE" command. Answer: no. Manual truncation+OR is the available solution. PostgreSQL pg_trgm exists but isn't exposed through Odoo's domain RPC.

DJ asked 2026-04-27 whether Odoo has a fuzzy/similar search operator (something more relaxed than `ilike`). Honest answer: **no**.

Available domain operators on `res.partner.search_read` (and other models):
- `=`, `!=` — exact equality
- `like`, `ilike` — case-(in)sensitive substring (auto-wrapped with `%`)
- `=like`, `=ilike` — same but no auto-wrap (provide your own `%`/`_` wildcards)
- `not like`, `not ilike`
- `in`, `not in`
- `child_of`, `parent_of`, `=?`

None of these do edit-distance, phonetic, or trigram matching. They're all literal substring or pattern.

**True fuzzy options that exist but aren't accessible via Odoo's RPC domain:**
- PostgreSQL `pg_trgm` (trigram similarity) — needs raw SQL
- Levenshtein/edit-distance — same
- Soundex/Metaphone — same

**The `=ilike` skeleton trick** (e.g. `=ilike 'J%n%H%m%'` to match "John Ham") works but produces lots of false positives ("Joan Hamilton", "Johnathan Bingham", etc.). Not worth it.

**Why:** Knowing this saves time when someone asks "can't we just use the fuzzy command?" — there isn't one. Don't go hunting for it.

**How to apply:**
- If a user asks for fuzzy search, the answer is: build it manually (truncation + OR conditions) like `tool_search_customers` does, OR build a custom Render endpoint that pulls names and scores them with Python `difflib.get_close_matches`.
- For the W&SC project, current truncation logic in `tool_search_customers` handles ~90% of typos. Don't add server-side fuzzy without concrete failing cases.
- Odoo server actions block imports, so `difflib` etc. can't run there. The fuzzy endpoint would have to live on Render (Python full library access).

---

### Odoo native upsell activity from Field Service timer
`project_odoo_upsell_activity.md`
> Odoo auto-creates "Upsell" To-Do activity on SO when timer hours exceed ordered quantity — needs to be disabled

When DJ stops the Field Service timer and logged hours exceed the ordered quantity (e.g. 1.25h logged vs 1.00 unit sold), Odoo automatically creates a mail.activity on the SO: "Upsell {SO} for customer {NAME}, {address}".

This is 100% native Odoo Field Service behavior — not in any of our code.

**Why it fires:** Service products track delivery by timesheets. Hours logged > qty ordered triggers Odoo's built-in upsell detection.

**How to apply:** This does NOT apply to DJ's business (flat-rate services, not hourly billing). The timer is for personal tracking only. Need to disable in Odoo → Field Service → Configuration → Settings — look for "Upsell" or "Timesheets" toggle. NOT YET DISABLED as of 2026-04-10 — DJ needs to find and turn off the setting.

---

### Payment sync Render Claude tools
`project_payment_sync_tools.md`
> sync_so_verify + process_payment_with_sync tools for voice-driven payment flow

## What They Do

**2026-05-01:** Two Render Claude tools added for payment flow integration.

### sync_so_verify
- **Purpose:** Verification only — report what sync changed before accepting payment
- **Input:** so_identifier (SO ID, SO name, Workiz UUID, or customer name)
- **Output:** Detailed sync report (fields changed, lines matched, status)
- **Triggers:** User says "sync Fred Jones open job" or "sync SO-12345"
- **Resolves identifiers:** Customer name → finds open invoiceable SO → grabs UUID automatically

### process_payment_with_sync
- **Purpose:** Full transaction — sync first, then process payment
- **Input:** so_identifier, amount, date (defaults to today if omitted)
- **Flow:** (1) sync all fields + line items, (2) create invoice, (3) record payment
- **Auto-fix:** If sync detects mismatches, runs cancel→draft→update→confirm before invoicing
- **Output:** Sync report + invoice confirmation + payment receipt
- **Triggers:** User says "process payment for Fred Jones" or "I received $150 from [customer]"

## Natural Language Resolution

Both tools support identifier resolution:
1. Try numeric SO ID
2. Try SO name (e.g., "SO-2024-001")
3. Try Workiz UUID
4. **Try customer name** — searches res.partner by name, finds their most recent open invoiceable SO (state in [sale, done] AND invoice_status='to invoice')

**Result:** User can say "sync Fred Jones" without knowing the SO ID or UUID — the tool finds everything automatically.

## Implementation Details

**Endpoints:**
- `POST /owner/api/sync_so_verify` — verification only
- `POST /owner/api/process_payment_with_sync` — full payment + sync

**Helper function:**
- `_find_so_by_identifier(identifier: str)` — resolves SO by ID/name/UUID/customer name

**Sync logic:**
Uses Phase 4A `_sync_so_with_workiz(so_id)` which:
- Compares 10+ fields (status, tech, gate, pricing, notes, job type, lead source, date_order, tags)
- Compares line items as (name, qty, price) tuples
- Only runs cancel→draft→confirm if differences found (early-exit optimization)
- Returns {'ok': bool, 'synced': bool, 'message': str, 'fields_updated': int}

## Voice Scripts

**Sync verification:**
- "Sync Fred Jones open job"
- "Sync SO-12345"
- "Check if the sync matches for [customer]"

**Payment processing:**
- "Process payment for Fred Jones"
- "I received $150 from [customer]"
- "Accept payment for [customer] on [date]"

## Commits
- First push (endpoints only): cd8a16a
- Tool registration: 73ed4ac
- Natural language resolution: ff7829c

---

### Payroll hr.attendance Retrofit (2026-04-24)
`project_payroll_hr_attendance_retrofit.md`
> Complete migration from JSON blobs to hr.attendance model with quarter-hour rounding, CA reporting-time pay, Gusto export, Manage Shifts UI, and Playwright automation

## Overview
Completed major payroll system overhaul: replaced fragile ir.config_parameter JSON storage with Odoo native hr.attendance model. Added comprehensive Manage Shifts UI on Render, Gusto CSV export endpoint, and Playwright automation skeleton for recurring uploads.

**Why:** JSON blobs have 90-day rolling deletion, no audit trail, no filtering, can't sync with payroll providers. hr.attendance is infinite-history, chatter-audited, native Odoo model designed for timesheets.

## Data Model
- **Storage:** Odoo hr.attendance (check_in, check_out, employee_id, worked_hours auto-computed)
- **Calendar:** "W&SC Field Work" (24/7, no lunch break deduction) assigned to DJ (emp 1) and Danny (emp 2)
- **Employees:** DJ=1, Danny=2 in hr.employee
- **Project:** "Payroll" (ID 3, separate from job timer entries)

## Hours Calculation Rules

### Quarter-Hour Rounding (FLSA-Compliant)
- Raw hours: `(check_out - check_in).total_seconds() / 3600`
- Rounding rule: round-half-up at 7.5-min boundary → nearest 0.25
- Formula: `math.floor(hours * 4 + 0.5) / 4`
- Apply at DISPLAY/EXPORT time only, NOT stored
- Example: 4.8253 hours → 4.75 hours (7.5 mins rounds down)

**Why:** FLSA requires rounding to nearest 0.25h. 7-minute neutral rule avoids bias (1-7 min down, 8-15 min up). Storage is raw to preserve audit trail.

### California Reporting-Time Pay (4-Hour Minimum)
- If employee called in and sent home early, minimum 4 hours paid
- Stored as boolean flag `x_reporting_time_pay` on shift (toggle in Manage Shifts UI)
- Export applies minimum: `max(rounded_hours, 4.0)` if flag=true

## Render App Changes (saunders-render-app/routers/owner/dashboard.py)

### New Helper Functions
```python
def _round_quarter_hour_neutral(hours):
    """Quarter-hour rounding to nearest 0.25, FLSA-compliant."""
    if hours <= 0:
        return 0.0
    return math.floor(hours * 4 + 0.5) / 4

def _raw_hours(check_in_str, check_out_str):
    """Raw hours from check_in/check_out timestamps (YYYY-MM-DD HH:MM:SS)."""
    # Returns 0 if either is None/empty; no rounding

def _open_attendance_for(emp_id):
    """Return currently-open hr.attendance for emp_id (check_out IS NULL)."""
    # Used for current shift tracking

def _attendances_in_pt_range(emp_id, start_pt_date, end_pt_date):
    """Return hr.attendance rows in PT date range [start_pt_date, end_pt_date)."""
    # Converts PT boundaries to UTC for Odoo query
```

### New Endpoints

**GET /api/payroll/shifts**
- List shifts for date range (Pacific time)
- Params: employee_id, start_date (YYYY-MM-DD), end_date
- Returns: list of {shift_id, check_in_pt, check_out_pt, raw_hours, rounded_hours, reporting_time_pay}

**POST /api/payroll/shift/update**
- Edit existing shift (check_in, check_out, reporting_time_pay)
- Body: {shift_id, check_in_pt?, check_out_pt?, reporting_time_pay?}
- Validates: check_out > check_in
- Returns: updated shift dict

**POST /api/payroll/shift/create**
- Retroactive shift add (for backfills, corrections)
- Body: {employee_id, check_in_pt, check_out_pt, reporting_time_pay?}
- Returns: new shift dict

**POST /api/payroll/shift/delete**
- Hard delete shift
- Body: {shift_id}
- Returns: {ok: true, deleted_id}

**GET /api/payroll/gusto_export**
- CSV export with daily hour rollups, all active employees
- Params: start_date, end_date, employee_id (optional; omit for all)
- Returns: CSV file (Content-Disposition: attachment)
- Columns: Employee Name, Date, Hours
- Applies: quarter-hour rounding + reporting-time 4h minimum
- Example row: `Dan Saunders,2026-04-20,4.75`

## Frontend UI Changes (timeclock.html)

### Manage Shifts Button & Panel
- Button: light blue (#60a5fa), white text, 13px padding, 15px font, 600 weight, 8px border-radius
- Opens hidden shifts-panel with employee select (owner only), date range pickers
- "＋ Add Shift" button
- shifts-list with day headers and shift rows

### Shift Row Display
- Time: check_in_pt → check_out_pt (Pacific time, 12-hour format with AM/PM)
- Raw hours: gray text (informational only)
- Rounded hours: bold, primary color
- Reporting-time badge: orange pill if flag=true
- Edit button: pencil icon
- Open-flag indicator: amber pill if shift still open (check_out=null)

### Shift Modal (Edit/Add)
- shift-in/shift-out: datetime-local inputs (Pacific time)
- shift-rtp: checkbox for reporting-time pay with explanation text
- Buttons: Cancel, Delete (edit only), Save
- Validation: check_out > check_in, show error hint if invalid

### Gusto Export Section
- Info block: "Download hours for Gusto Smart Import"
- "⬇ Download CSV" button (#10b981 green)
- Exports ALL active employees (ignores employee picker)
- Applies rounding + reporting-time pay

**Why:** Gusto expects one CSV with all employees for "Smart Import" feature. Separate exports per employee is inefficient.

## JavaScript Functions
- `showShiftManager()` - switches to panel, loads employees, sets date range to this week
- `loadShiftList()` - fetches /api/payroll/shifts for selected employee/date range
- `renderShifts(shifts)` - groups by date, renders day headers + shift rows
- `openShiftModal(shift)` - edit (shift provided) or add (shift=null)
- `saveShiftModal()` - POST /shift/update or /shift/create
- `deleteCurrentShift()` - confirmation dialog → POST /shift/delete
- `exportGusto()` - sets window.location.href to trigger CSV download (all employees)

## Playwright Automation (scripts/gusto_upload.py)

### Status
Skeleton created (110 lines), NOT YET TESTED. Needs selector calibration before first use.

### Setup Steps
```bash
pip install playwright
playwright install chromium
setx GUSTO_EMAIL "your-email@gusto.com"
setx GUSTO_PASSWORD "your-password"
```

### Flow
1. Read CSV path from argv[1]
2. Launch browser (Chromium)
3. Navigate to https://app.gusto.com/login
4. Enter email/password (env vars)
5. Navigate to Time Tracking → Import
6. Upload CSV file
7. Confirm import
8. Screenshot + exit

### Calibration
User must run:
```bash
playwright codegen https://app.gusto.com/login
```
Then walk through real login + import flow, copy selectors back into script.

**Why:** Selectors are account-specific and change with Gusto UI updates. Codegen captures them automatically by recording actual interactions.

### Usage (After Calibration)
```bash
python scripts/gusto_upload.py "path/to/wsc_hours_2026-04-20_to_2026-05-03.csv"
```

User approves 2FA prompt on phone. Script handles everything else.

## Migration Execution

### Script
`migrate_payroll_to_hr_attendance.py` (local, already executed)

### Results
- 3 shifts migrated for DJ (4/20: 4.83h, 4/21: 5.83h, 4/22: 3.10h)
- 0 shifts for Danny (only test clicks in old JSON system)
- 4 ir.config_parameter rows deleted (payroll.clockin.1, payroll.clockin.2, payroll.shifts.1, payroll.shifts.2)
- Backup: `payroll_json_backup_2026-04-23.json` saved locally

### Calendar Assignment
"W&SC Field Work" calendar (24/7, no lunch) assigned to both DJ and Danny to avoid Odoo's auto-deduction of break time from worked_hours.

## Documentation Created

### For Danny
- `docs/timeclock_usage_for_danny.md` (105 lines)
- Covers: daily clock in/out, fixing mistakes via Manage Shifts, understanding rounding, reporting-time pay, next steps
- Attached to Odoo Activity #52 on Danny's employee record (due 2026-04-25)

### For DJ (Punch List)
- `docs/timeclock_rollout_punch_list.md` (99 lines)
- 5 remaining action items with descriptions
- Attached to Odoo Activity #53 on DJ's record (due 2026-04-30)

### Odoo Activities
- Activity #52: "Train Danny on time clock — doc attached + backfilled shifts" (hr.employee id 2, due 2026-04-25)
- Activity #53: "Time Clock Rollout — Remaining Actions" (hr.employee id 1, due 2026-04-30, with all 3 docs linked)

## Gusto Integration Status

### CSV Format - TBD
- Currently exports: Employee Name, Date, Hours (rounded)
- Gusto has "Smart Import" feature that claims to auto-match columns
- **Blocker:** Need to confirm Gusto's exact expected columns/headers. User to download template from their Gusto account or test export.
- May need to add: Employee Email (if name is insufficient), or separate Overtime/Time Off columns if Gusto requires categorization

### Button Behavior - TO BE FIXED
- Current: exports one employee at a time (whoever is selected in employee picker)
- Should be: ignore employee picker, always export all active employees in one CSV
- Gusto expects all employees in single CSV for "Smart Import" batch processing
- Fix needed: update exportGusto() JS function to omit employee_id param

### Playwright Readiness - BLOCKED ON USER
- Skeleton ready
- User must run: pip install playwright, playwright install chromium, setx env vars
- User must run: playwright codegen and capture selectors
- After selector calibration: ready for first pay-period upload

## How to Apply

**Editing a shift:** Click Manage Shifts → select employee → click date → click shift row → pencil → change times → Save
**Adding retroactive shift:** Click Manage Shifts → select employee → "＋ Add Shift" → fill times + reporting-time flag → Save
**Exporting to Gusto:** Click Manage Shifts → date range → "⬇ Download CSV" → uploads to Gusto Smart Import (after calibration)

**If timeclock looks wrong:** Check that both DJ and Danny have "W&SC Field Work" calendar assigned (not default calendar). Default calendar deducts 1h lunch even for short shifts.

## Known Quirks

- **Odoo worked_hours field is ignored.** We compute hours ourselves from check_in/check_out to avoid calendar-based deductions.
- **Raw hours are stored, rounding applied at display/export.** This preserves audit trail and allows rounding rules to change without recalculating history.
- **Reporting-time pay is a toggle, not auto-calculated.** DJ must manually mark shifts as RTP in Manage Shifts UI. No rule to auto-detect "called in and sent home."
- **Gusto upload is fully manual after Playwright is calibrated.** No cron job; DJ runs it once per pay period.

---

### Payroll Tracker — DJ + Danny
`project_payroll_tracker.md`
> Plan for clock-in/out payroll tracking for DJ and Danny via Render, storing hours in Odoo, syncing to Gusto

# Payroll Tracker

**Decided:** 2026-04-18
**Status:** Ready to build. No blockers.

---

## REQUIREMENTS

- **Workers:** DJ + Danny, both hourly
- **Clock in/out:** Via Render app (their own screen/route)
- **Storage:** Odoo timesheets (account.analytic.line) — same model the timer already uses
- **Payroll processing:** Gusto for now. Odoo tracks hours, DJ manually enters into Gusto.
- **Future:** Switch to Odoo payroll completely if Claude can automate enough of it

---

## ACCESS / PERMISSIONS

- Danny: sees only his own hours, clock in/out for himself only
- DJ: sees everything — both workers, daily hours, weekly totals, what's owed to each

---

## RENDER SCREEN (Danny's view)

- Simple clock in / clock out button
- Shows today's hours running
- Shows week total
- No other access

---

## RENDER SCREEN (DJ's view — within existing app or new tab)

- Both workers side by side
- Hours per day this week
- Weekly total hours each
- Dollar amount owed at their hourly rate
- Status: currently clocked in or out

---

## ODOO STORAGE

- Uses existing account.analytic.line (timesheet) model
- Each entry: employee, date, hours, description "[Payroll] Clock in/out"
- Separate from job timer entries (those use task_id, payroll entries use employee_id only)
- Project: create a "Payroll" project in Odoo to house these entries

---

## GUSTO SYNC (for now)

- Manual: DJ runs weekly report from Render, enters hours into Gusto
- Future: Gusto has API — could automate hours submission when ready

---

## HOURLY RATES

- Store as Render env vars (DANNY_RATE, DJ_RATE) — easy to update without code change
- Never hardcoded

---

## BUILD ORDER

1. Create Payroll project in Odoo
2. Add Danny as employee in Odoo (if not already)
3. Build /danny and /payroll-admin routes in Render app
4. Clock in/out API endpoints in app.py
5. DJ's payroll summary view

---

### Pending - review Cursor chat history for lost solutions
`project_pending_cursor_history_review.md`
> DJ needs to share old Cursor session history so we can extract historical bug fixes and failed approaches into CLAUDE.md — raise this at the start of the next session

DJ has Cursor chat history from before the Claude Code migration (pre 2026-03-19) that likely contains previously discovered solutions — things like Odoo safe_eval quirks, Workiz API behaviors, field name corrections — that were never formally captured.

**Why:** We rediscovered two known-pattern errors in this session (datetime.datetime.now() and action=False) that were probably solved before. Getting the Cursor history reviewed would prevent future sessions from hitting these again.

**How to apply:** At the start of the next session, remind DJ: "When you have time, can we go through your Cursor chat history to pull out any past bug fixes or failed approaches we haven't captured yet?" Don't push if DJ is busy — it's a when-you-have-time task, not urgent.

---

### Pending Discussion — Auto-sync Workiz before Payment button
`project_pending_sync_before_payment.md`
> REMIND DJ to discuss running the Workiz sync server action automatically (with small lag) before the payment button fires, so SO data is fresh

# Pending Discussion — Run Workiz Sync Before Payment Button

**Raised:** 2026-04-20 (DJ, mid-field)

**The idea:** Before the Payment button in the Field Assistant triggers Phase 6 / invoice flow, auto-run the existing "Sync with Workiz" server action against that SO so the Odoo data (tech assignment, amounts, any Workiz-side edits) is guaranteed fresh. A slight lag / brief spinner may be needed to let the sync complete before the invoice step kicks off.

**Why it matters:** Today's Jose Merelies case (SO 17113, 2026-04-20) hit the Phase 6 tech gate — no tech assigned on the SO, Workiz had none either. DJ had to manually assign tech in Workiz, sync the SO, then re-invoice. An auto-sync before payment would have caught the blank-tech state (and potentially fixed it if Workiz was updated on his phone before tapping Payment), or at least failed with a clearer message before an invoice was already created.

**Open questions for the discussion:**
- Where does the sync hook in — Render app side (before calling the Odoo payment endpoint) or Odoo side (as a pre-step inside Phase 6 / server action)?
- How much lag is acceptable? Workiz API calls can 429; need to rate-limit.
- Do we always sync, or only when the SO hasn't been synced in the last N minutes?
- What do we do if sync fails? Block the payment, or warn and proceed?

**How to apply:** When DJ says "let's talk about that sync thing" or similar, open this discussion. Don't build until we decide the where/how. Related memory: `project_phase6_tech_gate.md`.

---

### Phase 4 missing task backfill
`project_phase4_missing_task_backfill.md`
> Phase 4 skips task sync when confirmed SO has 0 tasks — needs backfill path to create tasks directly via API

Phase 4 task sync (function `sync_tasks_from_so_and_job`) only UPDATES existing tasks. When it finds `tasks_found=0` on a confirmed SO, it logs "No tasks found linked to this SO's order lines (sale_line_id in line_ids). Task sync skipped." and returns early.

**Root cause of gap:** Tasks are normally created by Odoo's `action_confirm()`. If an SO was created confirmed (historical import, Phase 4 delegation with skip_confirm) without tasks, they never get created.

**Example:** Dianne Hourscht SO 003918 / UUID F7NBU3. Created Feb 12 2026, confirmed, no tasks ever created. Phase 4B ran Apr 4 2026, found 0 tasks, skipped.

**Fix implemented 2026-04-04:** In Phase 4, after `sync_tasks_from_so_and_job` finds `task_ids=[]` on a confirmed SO in a scheduling status, a backfill path runs:
- Get the SO's order line IDs
- For each order line, create a `project.task` directly via Odoo API with:
  - `name`: "{CustomerName} - {City}" (same format Phase 3 uses)
  - `project_id`: DEFAULT_PROJECT_ID (2)
  - `sale_line_id`: order_line_id (this is what links task to SO for future Phase 4 sync)
  - `user_ids`: tech from Workiz job if available
  - `date_deadline`: job datetime UTC
- Log "[OK] Backfilled N task(s) for confirmed SO with no existing tasks"

**Why not cancel/draft/confirm cycle:** Risk of failing if SO has invoice/payment linked.

**How to apply:** Next session, add backfill block in Phase 4 immediately after the early return at line ~330 where tasks_found=0. Only trigger when SO state='sale' (confirmed) AND is_task_trigger_status() is True.

---

### Phase 4 / sync_action_955 task re-entry bug
`project_phase4_task_reentry_bug.md`
> When Workiz substatus cycles Scheduled → "Next Appointment X - Text" → back to Scheduled, the Planned project.task gets deleted on the outbound trip but isn't recreated on return — Field Assistant shows no timer

**Root cause:** Phase 4 and/or sync_action_955 delete Planned project.tasks when a Workiz job transitions out of Scheduled (into "Next Appointment - Text", "Next Appointment 2 - Text", etc.). When the job cycles back to Scheduled, the task is never recreated. The SO's cached `tasks_count` stays at 1, which fools any "has task?" check that uses the cached field instead of actually querying project.task.

**Symptom:** DJ opens a job in Field Service Assistant, sees no task, can't start the timer. SO looks fine on paper — tasks_count shows 1 — but project.task for that sale_order_id is empty.

**Case confirmed 2026-04-20:** SO 15916 (Barbra Balser, Apr 20 3:30 PM job). Chatter showed substatus went Scheduled → "Next Appointment - Text" → "Next Appointment 2 - Text" → back to Scheduled on Apr 17. Task was deleted, never recreated. Fix today: manually recreated as task 297, linked to order line 17478. Modeled on Ruby Weaver's task (same service type, same tech, stage 17 Planned).

**Sweep 2026-04-20:** 4 active-future SOs have `tasks_count > 0` but zero actual tasks:
- SO 17116, 17117 (Naresh Bellara test jobs, May 5) — skip, no tech assigned
- SO 15857 (Lanny & Sue Lund, May 12) — expected, Phase 4 deletes tasks on Submitted before confirmation
- **SO 17066 (Wayne Geringer, Aug 20 2026)** — same bug as Balser, reactivation orphan, needs task recreated before that date

**Why it matters:** Timer won't start without a task. Every reactivation-cycled job is a potential silent orphan.

**How to apply:** 
- When DJ reports "no task" on a recently-reactivated SO, first check: `env['project.task'].search([('sale_order_id', '=', SO_ID)])`. If empty but `tasks_count > 0`, this bug.
- Short-term fix: recreate the task modeled on a peer job (same tech, same service, stage 17 Planned), link to the correct order line via `x_sale_order_line_id`.
- Long-term fix (NOT BUILT): in whatever server action / Zapier step handles "Scheduled" status entry, add logic: if SO has no project.task for its sale_order_id, call the task creation routine (same one used at initial Schedule). Candidates: sync_action_955, Phase 4's status-change branch. Needs a read of those files to locate the exact insertion point.

Related memory: `project_task_deletion_stage_filter.md` — the outbound deletion side is already stage-gated (only New/Planned, not In Progress/Done). The gap is purely on the return trip.

---

### Phase 4A comprehensive Workiz sync
`project_phase4a_sync.md`
> Full SO field sync before payment (stale SO + Field Assistant) — all Workiz fields checked

**ENHANCED 2026-05-01 (v2 — comprehensive)**

## What
Phase 4A is a comprehensive pre-payment sync function (`_sync_so_with_workiz()`) that ensures Odoo SOs match Workiz job data **completely** before accepting payment.

**v1:** Line-count only  
**v2 (CURRENT):** Full field sync — 10+ fields + line items

## Fields synced from Workiz → Odoo
- `x_studio_x_studio_workiz_status` (SubStatus)
- `x_studio_x_studio_workiz_tech` (Team member names)
- `x_studio_x_gate_snapshot` (Gate code)
- `x_studio_x_studio_pricing_snapshot` (Pricing snapshot)
- `x_studio_x_studio_notes_snapshot1` (JobNotes)
- `x_studio_x_studio_x_studio_job_type` (Job type)
- `x_studio_x_studio_lead_source` (JobSource)
- `date_order` (JobDateTime UTC)
- `tag_ids` (Tags)
- `order_line` (Line items: product ID, qty, price, description)

## How it works
1. Fetches SO with all Workiz fields + line items
2. Fetches Workiz job data
3. Compares each field (status, tech, gate, pricing, notes, job type, source, date, tags)
4. **Compares line items** by (name, qty, price) tuples — not just count
   - Handles "customer changes mind at door" scenario: Inside+Outside → Outside only
   - Detects qty or price changes
5. If any mismatch found:
   - **If SO confirmed (state='sale'):** cancel → draft → delete unmatched lines → re-confirm
   - **If SO draft:** just write field updates
6. Restores date_order after confirm (Odoo resets it)
7. Returns {'ok': bool, 'synced': bool, 'message': str, 'fields_updated': int}

**Early exit:** If all fields match AND line items match exactly → skip cancel/confirm (no disruption)

## Integration points
- **Function:** `_sync_so_with_workiz(so_id)` (line 4782)
- **Endpoint 1:** `/api/record_zelle_payment` (stale SO) — **BLOCKING**: fails payment if sync fails
- **Endpoint 2:** `/api/payment` via `_execute_payment()` (Field Assistant) — **NON-BLOCKING**: logs error but proceeds
- Both called **before** invoice creation

## Edge cases
- No Workiz UUID: skips (ok=True, synced=False)
- Workiz job missing: skips gracefully
- Workiz fetch fails: blocks payment (stale) or logs warning (Field Assistant)
- Line deletion fails: blocks payment
- DateTime conversion fails: silently skips (non-blocking)

**v2 rationale:** User requirement for low-frequency operations (like accepting payment) — "ensure EVERYTHING is synchronized, not just line counts."

## Phase 4 vs Phase 4A Logic

**The sync logic is identical.** Both check the same 10+ fields + compare line items the same way (tuple-based sets).

**Differences:**
- **Phase 4** (Workiz status changes): Field sync + task creation/deletion + full job lifecycle management
- **Phase 4A** (Before payment): Field sync only (verify + auto-fix), no task operations

**Trigger distinction:**
- Phase 4: Triggered by Workiz webhook (status change or job update)
- Phase 4A: Triggered before payment acceptance (manual via Render Claude tool or stale SO endpoint)

---

### Phase 6 tech gate — check SO before any action
`project_phase6_tech_gate.md`
> Phase 6 gates on x_studio_x_studio_workiz_tech at start — blocks entire run if no tech assigned

Phase 6 checks `x_studio_x_studio_workiz_tech` on the SO as step 2 (right after finding the SO), before posting payment or touching Workiz. If empty, returns error immediately.

Error message: "SO {name} has no technician assigned. Assign tech in Workiz, run Sync on the SO in Odoo, then re-invoice."

**Why:** Workiz rejects Mark Done with "Must assign technician" if no tech is on the job. Better to catch it at the Odoo level before any payment is posted (avoids needing to delete/recreate invoice).

**How to apply:** If Phase 6 fails with no-tech error: assign tech in Workiz → run Sync from Workiz button on SO → re-invoice. No need to delete old invoice.

---

### Phase 3/4/5 Flowcharts (2026-04-24)
`project_phase_flowcharts.md`
> SVG + PNG flowcharts for Workiz→Zapier→Odoo automation phases with narrative markdown explaining routing logic and date field handling

## Location
`3_Documentation/phase_diagrams/` in GitHub repo windowandsolarcare-hash/Odoo-Migration

Files per phase: `.md` (narrative), `.mmd` (Mermaid source), `.svg` (infinite-scale rendering), `.png` (3200px wide, mobile-readable)

**Why:** Diagrams make automation flow visible to non-technical stakeholders. SVG + PNG covers desktop (zoom) + mobile (readable at 3200px).

## Phase 3 - New Job Creation
**Trigger:** Workiz webhook sends new job (Status=Submitted)
**Path:** Workiz → Zapier HTTP request → Odoo sale.order + tasks

### Flow Routing
1. New job received with Workiz UUID
2. **Path A (New Customer):** Workiz ClientId not found in Odoo → create new res.partner + SO
3. **Path B (Existing Customer, New Property):** ClientId exists, property (partner_shipping_id) not found → reuse contact, create new property partner
4. **Path C (Existing Customer, Existing Property):** Both exist → reuse both

### Key Date Handling
- `date_order` on SO = Workiz `JobDateTime` (start time, UTC) — **never end time**
- `x_studio_next_job_date` on contact = copy of date_order for reactivation tracking
- Task created with deadline = date_order + 3 hours buffer (scheduling)

### Fields Created on SO
- `x_studio_x_studio_workiz_uuid` = job UUID (lookup key)
- `x_studio_x_workiz_link` = link to Workiz job
- `x_studio_x_studio_workiz_status` = "Submitted"
- `x_studio_x_studio_workiz_tech` = Workiz tech assignment
- `x_studio_x_gate_snapshot` = gate code at creation time
- `x_studio_x_studio_pricing_snapshot` = pricing at creation time

### Custom Fields Required for Validation
- `type_of_service_2` = Workiz custom field (NOT type_of_service) — required, default "On Request"
- `frequency` = required, default "Unknown"
- `confirmation_method` = required, default "Cell Phone"
- `JobSource` = required, always "Referral"

**Why:** If any of these are empty string, Workiz API rejects the record on Phase 5 (create new job for next visit).

## Phase 4 - Job Status Updates
**Trigger:** Zapier polling (every 5 minutes)
**Path:** Odoo query → Workiz API → update Odoo fields + tasks

### Polling Logic
1. Find all SO where `x_studio_x_studio_workiz_status` != "Done" (incomplete jobs)
2. For each SO, fetch Workiz job by UUID
3. Compare `SubStatus` in Workiz to current Odoo status
4. Update task stage and SO fields

### Task Lifecycle (Phase 4 + Phase 5)
- `New` (16) → `Planned` (17): Phase 4 first sync, stays until job scheduled in Workiz
- `Planned` (17) → `In Progress` (18): Field Assistant starts timer (Render app)
- `In Progress` → `Done` (19): Field Assistant stops timer + photos
- `Done` → (archive): Phase 4 skips; field manual only

**Deletion Rule:** Only delete tasks in New(16) or Planned(17) on Submitted status. Protect In Progress(18) and Done(19) — never auto-delete active/completed work.

### SubStatus Routing
- `Scheduled`, `STOP`, `Lead` → task stays Planned
- `Next Appointment X - Text` (after Calendly confirmation) → task stays Planned
- `In Progress` → task moves to In Progress (if Field Assistant hasn't started)
- `Done` → task moves to Done, SO status updated
- `Canceled` → task deleted if safe (New/Planned only)

### Critical Bug: Task Re-Entry
**Symptom:** Task deleted on Workiz substatus exit from Scheduled, NOT recreated on return
**Example:** Workiz cycle: Scheduled → Next Appointment - Text → back to Scheduled = task deleted, not recreated
**Impact:** SO shows tasks_count=1 but no task exists; Field Assistant shows no timer
**Status:** Bug found + diagnosed (Phase 4 logic, task cache expires). Permanent fix not yet built.
**Workaround:** Manual task creation in Odoo (task 297 on SO 15916).

### next_job_date Clearing
- Phase 4 clears `x_studio_next_job_date` on property partner when SO status = "Done"
- If future job exists, it should be re-written by Phase 5 (see below)
- If no future job, date stays null until reactivation triggers

**Why:** Reactivation screen uses next_job_date to plan outreach. Stale dates block campaigns.

## Phase 5 - Auto Job Scheduling
**Trigger:** Phase 6 webhook payload (payment recorded) or manual Phase 5 run
**Path:** Completed SO → Workiz API (create new job for next visit)

### Load-Bearing Path
1. Query completed SO (workiz_status="Done", frequency != "One Time")
2. Calculate next visit date: last_completed_date + frequency interval
3. Fetch last_date_cleaned from current job (Workiz field)
4. **Create new job** in Workiz for next visit with:
   - JobDateTime = calculated next visit date (start of business day)
   - last_date_cleaned = copy from completed job (preserve history)
   - All other fields (type_of_service_2, frequency, pricing, etc.) = copy from completed SO snapshot fields

### Field Mapping (Completed SO → New Workiz Job)
- Service type: `x_studio_x_type_of_service` (from property partner)
- Frequency: `x_studio_x_frequency` (from property partner)
- Type of service: `x_studio_x_studio_x_studio_job_type` (from SO snapshot)
- Gate code: `x_studio_x_gate_code` (from property partner, NOT snapshot)
- Pricing: `x_studio_x_pricing` (from property partner, NOT snapshot)
- Phone: contact phone (from res.partner, required)
- Address: contact address (required)

**Why:** Some fields should update dynamically (pricing, gate code) even if SO snapshot is stale. Others must preserve snapshot from original job date (initial pricing offered).

### New Job Validation
All Workiz API defaults must be applied:
```
type_of_service_2: str(value or 'On Request')
frequency: str(value or 'Unknown')
confirmation_method: str(value or 'Cell Phone')
JobSource: str(value or 'Referral')
ok_to_text: str(value or 'Yes')
```

If any is empty string, Workiz validation rejects the POST.

### next_job_date Write (Phase 5A)
After new job created in Workiz:
- Write `x_studio_next_job_date` on property partner = new job's JobDateTime
- Enables reactivation screen to show "Next scheduled: [date]" as visual confirmation

**Why:** Reactivation team uses this date to avoid scheduling duplicate jobs.

### last_date_cleaned Population (Phase 5B)
When creating new maintenance job:
- Populate `last_date_cleaned` from completed job
- Format: Workiz date field (YYYY-MM-DD or timestamp)
- Enables technician to track service history without jumping between jobs

### Orphaned Future Jobs
- **Rule:** Leave alone. Do NOT auto-delete.
- **Example:** SO 17066 (Wayne Geringer, Aug 20 2026) has a future job but Phase 4 task sync deleted the Odoo task and won't recreate it.
- **Workaround:** Manual task creation in Odoo; keep Workiz job intact for continuity.

## Graveyard Job Creation (Special Case)
When SO marked "Do Not Contact" (x_studio_activelead = "Do Not Contact"):
- **Always create new graveyard job** instead of reusing future job
- DO NOT update/overwrite existing future job
- Create separate crm.lead record with Workiz link for audit

**Why:** Graveyard = inactive but trackable; preserve original job in case status changes back.

## How to Apply

**Debugging a job flow issue:**
1. Find SO in Odoo → check `x_studio_x_studio_workiz_uuid` (Phase 3 key)
2. Fetch Workiz job by UUID → check JobDateTime + SubStatus (Phase 4/5 keys)
3. Check SO `date_order` matches Workiz JobDateTime (if mismatch, Phase 1 error)
4. Check task stage vs Workiz status (if wrong, Phase 4 sync issue)
5. Check `x_studio_next_job_date` populated (if blank, Phase 5 didn't complete)

**Adding custom logic:**
- Phase 3: add conditions before Path A/B/C routing
- Phase 4: add SubStatus handlers before task sync
- Phase 5: add field mappings before Workiz POST, but always apply validation defaults

## Files Generated
- `phase3_flow.md` — narrative explanation of new job creation, all paths
- `phase3_flow.mmd` — Mermaid source (Flowchart syntax with shapes)
- `phase3_flow.svg` — infinite-scale vector rendering
- `phase3_flow.png` — 3200px wide raster (mobile-readable)
- Same 4 files for Phase 4 and Phase 5

## Rendering Notes
- Mermaid `%%init%%` block sets fontSize to 14px (larger than default for readability)
- PNG rendered at `-w 3200` pixels wide (verified readable on phone with pinch-zoom)
- SVG supports browser pinch-zoom + pan (infinite scale)
- Phase 5A identified as critical load-bearing path (next_job_date writes) — verify on every new feature

---

### After accounting migration phase 4-5, verify payment preselect coverage
`project_preselect_coverage_check.md`
> Pending follow-up — once historical Workiz payment CSVs land in Odoo's account.payment, run a coverage check on the field assistant's last-payment preselect. Today most customers default to "Check" because Odoo has almost no payment history.

When the Odoo accounting migration phases 4-5 complete (Workiz Payment CSV imports populating `account.payment`), run a coverage check on the field assistant payment preselect.

**Why:** As of 2026-04-29, the preselect logic in `_last_payment_method_by_partner` (Saunders Render App/routers/owner/dashboard.py:2624) is correct and verified end-to-end (Gary Marsalone partner 24153 → contact 23031 → Zelle, confirmed via direct Odoo query). But almost every customer falls through to the 'check' default because there are virtually no `account.payment` records in Odoo yet — only a handful from invoices DJ has processed through Odoo. The fix is the accounting migration, not the code. DJ confirmed "Path A" (wait for migration, no Workiz API fallback).

**How to apply:**

When DJ mentions completing accounting migration phase 4 or 5 (the Workiz CSV import phases — see `project_odoo_accounting_migration.md`), proactively offer to run this check:

```python
# Coverage report — % of upcoming-schedule customers that now have an account.payment
sos = odoo_rpc('sale.order','search_read',
    [[['date_order','>=', today_iso + ' 00:00:00'],
      ['date_order','<=', plus_14d_iso + ' 23:59:59'],
      ['state','in',['sale','done']]]],
    {'fields':['partner_id']})
partner_ids = list({s['partner_id'][0] for s in sos if s.get('partner_id')})
result = _last_payment_method_by_partner(partner_ids)
print(f"Coverage: {len(result)}/{len(partner_ids)} ({100*len(result)//max(1,len(partner_ids))}%)")
print("Methods:", Counter(result.values()))
```

If coverage is < 70%, investigate why (memo parsing? walk Property→Contact failing for some? PML IDs changed?).

If coverage is healthy (≥70%), no action needed — preselect is now doing its job in production.

**Related:**
- `project_odoo_accounting_migration.md` — phase status
- `project_account_payment_no_ref_field.md` — the schema gotcha that caused the original outage
- `session_apr28_29_summary.md` — original preselect implementation context

---

### Property partners may NOT contain the customer's name — search must walk Contact↔Property
`project_property_partner_naming_quirk.md`
> 2026-04-30 — DJ has Property res.partner records named two different ways: "Customer Name, address" (e.g. "Betsy Justice, 255 E Avenida Granada") AND just the address ("47446 Rabat Dr"). A partner-name search for "betsy" misses the second pattern. Surfaced when Render Claude charged the wrong Betsy SO. Any code finding all of a customer's SOs MUST resolve the Contact, then enumerate child_ids — never rely on name-matching across properties.

**READ when writing code that finds all of a customer's records (SOs, tasks, properties).**

## The data shape

DJ's Odoo customers are modeled as:

- **Contact** (res.partner with `x_studio_x_studio_record_category='Contact'`, `parent_id=False`, has `ref` = Workiz ClientId)
- **Property children** (res.partner with `x_studio_x_studio_record_category='Property'`, `parent_id=Contact.id`)

Property names are **inconsistent**:

| Property record | Name | Notes |
|---|---|---|
| id 26574 | `"Betsy Justice, 255 E Avenida Granada"` | "old style" — name + address |
| id 24957 | `"47446 Rabat Dr"` | "new style" — address only |

Both belong to the SAME contact (Betsy Justice, id 23238).

## Why it bites

A query like `name ilike "betsy"` returns the contact + the old-style property, but **misses** the address-only property. Any code that uses partner-name search to enumerate a customer's records will silently lose data.

Real incident (2026-04-30): Render Claude was asked to "Collect $170 from Betsy Justice." It found 1 SO via partner-name walk (the March 26 SO @ 255 Avenida, $0, empty) and tried to invoice that — failing with "No items available to invoice." The actual target SO ($170 @ 47446 Rabat Dr, April 3) was invisible because Property 24957's name doesn't contain "Betsy".

## Rule going forward

Always resolve via `parent_id`, never via name pattern:

```python
# Given any partner_id (could be Contact OR Property)
rec = odoo_rpc('res.partner', 'read', [[partner_id]],
    {'fields': ['parent_id', 'child_ids']})[0]
related = {partner_id}
contact_id = rec['parent_id'][0] if rec.get('parent_id') else partner_id
related.add(contact_id)
contact = odoo_rpc('res.partner', 'read', [[contact_id]], {'fields': ['child_ids']})[0]
related.update(contact.get('child_ids') or [])
# `related` now contains the contact + all properties — search SOs across that set
```

The helper `_find_invoiceable_sos_for_partner(partner_id)` in
`Saunders Render App/routers/owner/dashboard.py` (added 2026-04-30, commit 0e6726af) does this.

## Search by Workiz ClientId is more reliable

Every Contact has `ref` = Workiz ClientId (e.g. Betsy = `1417`). If you have a Workiz job and want to find the related Odoo Contact, search by `ref` — bypasses the naming inconsistency entirely.

```python
contact = rpc('res.partner', 'search_read',
    [[['ref', '=', str(workiz_client_id)]]],
    {'fields': ['id', 'child_ids']})
```

## Related memory

- `project_so_lines_zero_means_deleted.md` — DJ's qty=0/price=0 soft-delete pattern (also relevant to which SO is "real")
- `project_invoice_qty_delivered_gate.md` — invoice wizard gate (separate issue, doesn't fix this)
- `project_render_claude_tools.md` (and `reference_render_claude_write_tools.md`) — `record_check_payment` v2 now does the partner walk + multi-SO disambiguation + tip detection

---

### Window Quote Tool — full reference
`project_quote_tool.md`
> 2026-04-29 — DJ replaced the AppSheets "Our Pricing" tool with /owner/quote (and /tech/quote) on Saunders Render App. Saves quotes as Odoo sale.orders with 3 watermarks (client_order_ref, job_type=Quote, QUOTE ONLY tag). Picks from schedule = updates existing Workiz-linked SO; walk-up = creates new partner + SO.

**READ THIS FIRST when editing /owner/quote, /tech/quote, /api/quote/*, or anything related to window-quoting.**

## What it is

Replacement for DJ's AppSheets "Our Pricing" tool. Mobile-first quote calculator with auto-save to Odoo. DJ uses it on a doorstep with a customer; backend stores everything as a draft `sale.order` (or updates an existing Workiz-linked one).

## Files

- `Saunders Render App/static/owner/quote.html` — single-file UI for both owner and tech (role detected via URL path)
- `Saunders Render App/routers/owner/dashboard.py` — endpoints: `/api/quote/save`, `/api/quote/update`, `/api/quote/get`, `/api/quote/list`
- `Saunders Render App/routers/tech/jobs.py` — `/tech/quote` route mirrors the same HTML
- `Saunders Render App/static/owner/index.html` + `static/tech/index.html` — orange "💲 Window Quote" tile on both dashboards

## Pricing model (rates per unit, in `dashboard.py`)

```python
QUOTE_RATES = {
    'reg_panes':      7,    # Regular Panes
    'over_panes':     8,    # Oversized Panes
    'ss_panes':       9,    # Second Story Panes
    'reg_sliders':   25,    # Regular Sliders
    'over_sliders':  30,    # Oversized Sliders
    'triple_sliders':35,    # Triple Sliders
}
```

## Modifiers

- **Mode** (radio):
  - `in_out` (default) — uses Odoo product **141** "Windows In & Out - Full Service"
  - `outside` — total ÷ 2 × 1.10, uses Odoo product **103** "Outside Windows And Screens"
- **Difficulty** (3 buttons):
  - `standard` ×1.00
  - `hard` ×1.15
  - `very_hard` ×1.30
- Total formula: `sum(count × rate)` → if outside, ÷2 × 1.10 → × difficulty multiplier → round to 2dp

## Watermarks (the 3 signals that mark an SO as a quote)

Applied by `_apply_quote_watermark()`:

1. `client_order_ref` = `'🔶 QUOTE ONLY'` — visible at top of SO form
2. `x_studio_x_studio_x_studio_job_type` = `'Quote'` — selection field, valid value
3. `tag_ids` += "QUOTE ONLY" tag (orange, color 2) — auto-created on first quote save

Phase 4 will eventually clear these on conversion (task #16, not built yet — DJ removes manually for now).

## Save flow — two paths

**Path A: Picked from schedule (so_id present)**
- `_replace_quote_line(so_id, line_create_tuple)` — soft-deletes existing lines (qty=0, price=0; can't unlink on confirmed SOs per `project_so_lines_zero_means_deleted.md`)
- Adds the new quote line with the marker `[Render Quote Tool]` in description
- Patches partner contact details (street/phone/name) if changed
- Applies watermarks
- Returns existing `so_id` and partner_id from the SO

**Path B: Walk-up (no so_id)**
- Auto-creates `res.partner` from name + street + phone
- Creates fresh draft `sale.order` with the quote line
- Applies watermarks
- Returns new `so_id` and partner_id

## Edit flow — `/api/quote/get` + `/api/quote/update`

Saved Quotes panel lists active quote SOs. Tap one → fetches `/api/quote/get?so_id=N` → returns full `{name, address, phone, counts, mode, difficulty, total, partner_id}`. Form fills, Save button switches to "Update Quote" → calls `/api/quote/update` which patches the existing line + partner contact fields. State doesn't matter (works on draft AND confirmed SOs).

## Round-trip data preservation

Quote line description has format:

```
[Render Quote Tool]
2× Regular Panes ($7) · 3× Oversized Panes ($8)
Mode: Windows In & Out
Difficulty: Standard (+0%)
__QUOTE_JSON__:{"counts":{"reg_panes":2,...},"mode":"in_out","difficulty":"standard"}
```

The trailing `__QUOTE_JSON__:` blob lets `/api/quote/get` reconstruct the form state on load. There's a legacy fallback parser (`_parse_quote_json_from_line`) that re-extracts counts/mode/difficulty from the human-readable text for quotes saved before the blob existed.

## Saved Quotes filter — IMPORTANT

`/api/quote/list` filters by `client_order_ref = '🔶 QUOTE ONLY'` (the watermark text, only set by this tool, cleared by Phase 4 on conversion). **DO NOT** filter by `job_type='Quote'` alone — that catches every historical Workiz Quote-type job that Phase 3 imported (was 18 SOs going back to 2022 on 2026-04-29 when the bug was caught and fixed in commit `755d9617`).

The watermark filter:
- ✅ Catches both walk-up draft SOs and updated Workiz-linked confirmed SOs (state=sale) — both get the watermark applied by `_apply_quote_watermark`
- ✅ Excludes pre-Render-tool Workiz quotes (they have `job_type='Quote'` but no watermark)
- ✅ Auto-drops accepted quotes when Phase 4 clears the watermark on conversion

- **Owner role** (URL `/owner/quote`): no limit, sees every active Render-tool quote
- **Tech role** (URL `/tech/quote`): `limit=1`, just their most recent. **Caveat:** filtering by `create_uid` doesn't truly partition because every Render-driven RPC runs as ODOO_USER_ID=2. So tech sees the latest globally, not their own. Real per-tech filtering needs PIN-based auth on save (deferred).

## "Pick from schedule" flow

- "📅 Pick from scheduled jobs" button at the top of the customer block
- Modal lists upcoming jobs from `/api/upcoming` — name, time, address, phone
- Tap → fills name/address/phone (autofills via partner_shipping display name + walks Property→parent for phone) + sets `linkedSoId` + `linkedPartnerId` + shows green banner
- Save uses `linkedSoId` → triggers Path A (update existing SO)
- ✕ on banner OR typing in name/address fields clears the linkage → falls back to Path B (walk-up)

## Address autocomplete

Google Places Autocomplete (New) — see `reference_google_cloud_apis.md`. Key embedded in HTML; restricted to `wsc-field-assistant.onrender.com/*`. Biased to Palm Springs (lat 33.83, lon -116.54), filtered to US.

## UX details DJ asked for

- Two-row stacked counter layout (label+subtotal on top, [−] count [+] on bottom) — tested overflow on phones, fits cleanly
- 5-second undo grace was a separate feature DJ asked for in the activities flow, not directly in quote — but could apply if needed
- Save Quote button is **disabled** until name + address + total > 0 (validateSaveButton called from every input + counter change + mode/difficulty pill click)
- Haptic vibration (12ms) on +/- and 8ms on mode/difficulty pill taps (Android only — iOS Safari blocks Vibration API)

## Architecture decisions (locked)

1. **Quote save = update existing SO when from schedule, create new when walk-up** — DJ's pivot 2026-04-29 to leverage existing Phase 3/4 infrastructure rather than running a parallel SO-creation path.
2. **Soft-delete (zero qty + price) for existing lines** instead of unlink — Odoo blocks unlinking on confirmed SOs.
3. **Three watermark signals** because each surfaces in a different Odoo view (SO form top / dashboard filters / list pills).
4. **`Quote` is an existing valid job_type** — already in the selection list. Don't need to add a new one.
5. **No new custom Odoo fields** — uses built-in `client_order_ref`, existing job_type selection, and crm.tag (auto-creates "QUOTE ONLY" tag if missing).

## Future work (parked as activities #67, #68, #69 due today, plus Render task list)

- **Task #16 / Activity #67** — Phase 4 auto-clear watermarks when Workiz substatus leaves Quote. Modify `zapier_phase4_FLATTENED_FINAL.py` in Odoo-Migration repo. Set job_type from product mapping: 141→"Windows Inside & Outside Plus Screens", 103→"Outside Windows and Screens". Clear `client_order_ref` and remove QUOTE ONLY tag.
- **Task #17 / Activity #68** — Workiz "Quote" substatus + automation webhook → Render endpoint, replaces Phase 3 polling for instant sync. Pattern matches existing STOP webhook (`odoo_webhook_stop_handler.py` in Odoo-Migration). Blocked on DJ creating the substatus.
- **Task #18 / Activity #69** — "Push to Workiz" button on accepted quotes — writes line-item breakdown to Workiz JobNotes (or custom field — DJ to confirm). Uses existing `workiz_post`/JobNotes append-prepend pattern. Pair with #67.
- **Tech-specific saved-quotes filter** — needs PIN-based auth on save endpoint to capture creator's hr.employee ID. Currently all Render writes show as user_id=2.

## Common pitfalls

- **Don't forget the `_apply_quote_watermark` call** after save / update — without it, the SO won't show in the Saved Quotes list.
- **Don't try to unlink existing lines on a confirmed SO** — `_replace_quote_line` already handles the soft-delete pattern correctly.
- **Don't re-use the customer's "QUOTE ONLY" tag** — the helper handles get-or-create. Multiple tags with the same name break filtering.
- **The SO state doesn't matter for the list** — filter is on job_type only. So Path A SOs (state='sale') and Path B SOs (state='draft') both appear.
- **"Pick from schedule" only shows the next 14 days from /api/upcoming.** If DJ created a Quote-substatus job further out, it won't appear until it's within window.

## Related memory

- `reference_google_cloud_apis.md` — API key + project info
- `project_so_lines_zero_means_deleted.md` — why we soft-delete instead of unlink
- `feedback_activity_notes_self_contained.md` — pattern for activities #67-69 notes
- `project_workiz_substatus_needs_status.md` — Workiz API quirk for the future webhook work

---

### Reactivation Attempt 2 Design
`project_reactivation_attempt2.md`
> Planned but not yet built — Attempt 2 follow-up text for non-responders to Attempt 1

Attempt 2 follow-up SMS for reactivation non-responders. Design agreed, not yet built.

**Why:** People who didn't respond to Attempt 1 (pricing given) need a closing nudge. They didn't STOP, just didn't reply.

**Trigger:** 40 days after x_studio_last_reactivation_sent on res.partner
**Cadence:** Daily automated run — picks up anyone hitting 40-day mark that day
**Stage:** Move CRM opp from "Attempt 1 - Sent" (ID 5) to new "Attempt 2 - Sent" stage
**After Attempt 2:** TBD — DJ to decide, nothing automated yet

**How to apply:** When DJ says "build Attempt 2", create: new CRM stage, daily Odoo server action (or Zapier schedule), SMS text focused on closing (pricing already seen, now nudge to book). Use x_studio_last_reactivation_sent + 40 days as filter.

---

### Reactivation Screen — April 19 2026 State
`project_reactivation_screen_apr19.md`
> Full state of reactivation.html and related app.py endpoints as of 2026-04-19

# Reactivation Screen — 2026-04-19

## FILES
- `5_Mobile_Interface/static/reactivation.html` — full UI
- `5_Mobile_Interface/app.py` — endpoints listed below

---

## VIEWS (3 total, single-page)

### view-list — Candidates List
- Loads from `GET /api/reactivation/candidates?service=all|window|solar&city=...`
- **Name search**: full-width input at top, filters locally (no API call), instant, X clears, auto-clears on back
- **Service pills**: All / Window / Solar (server-side filter)
- **City input**: debounced 600ms, server-side filter
- Each card: customer name, city, tags (Service, Last Visit, Est $, Freq)
- Count shows filtered total
- Tap card → openCandidate(partner_id) → view-preview

### view-preview — Preview & Launch
**Header card:** customer name, city, service/last visit/est/freq tags

**Property & Contact details card** (purple left-border):
- Fields: Service Type, Last Property Visit, Pricing Note (amber), Last Reactivation Sent
- Prices Per Service block (pre-wrapped text below rows)
- Pills at bottom: 🏠 View Property (green → Odoo contact), 👤 View Contact (orange → Odoo contact), 📋 All SOs (gray → view-so-list)
- Data source: property record (x_studio_x_pricing, x_studio_prices_per_service, x_studio_x_studio_last_property_visit, x_studio_x_type_of_service) + contact record (x_studio_last_reactivation_sent)

**Job History card** (blue left-border):
- Shows total Done job count + last 2 Done jobs
- Done = x_studio_x_studio_workiz_status = 'Done' on sale.order — NEVER invoice-based
- Per job: Most Recent / 2nd Most Recent label, Date, Property, Job Type, Total Value ($, green), Frequency, Pricing Note, Pricing Snapshot (labeled)
- Per job pills: 🔧 Workiz (blue), 🟣 Odoo SO (purple)

**SMS section:** generated by SA 562, editable textarea, char count

**Launch › button:** disabled until SMS loads. Opens confirm bottom sheet:
- Title: "Send Reactivation?"
- Shows customer name + "This will send an SMS and create a graveyard job in Workiz."
- Buttons: Cancel / Send It
- Tap outside sheet = cancel

### view-so-list — All Sales Orders
- Loaded on demand via `GET /api/reactivation/so_list?partner_id=X`
- Same candidate-card style as view-list
- Per card: SO name, property (cand-city), status tag (color coded), date tag, job type tag, $ amount tag
- Status colors: Done=green, Canceled=red, In Progress=blue, other=amber
- Tapping card opens SO in Odoo directly (target=_blank)
- Back arrow returns to view-preview

---

## app.py ENDPOINTS (reactivation)

| Endpoint | Method | Purpose |
|---|---|---|
| /api/reactivation/candidates | GET | Candidate list (service, city filters) |
| /api/reactivation/preview | POST | Run SA 562, return SMS + job history + prop details |
| /api/reactivation/so_list | GET | All SOs for a partner (new 2026-04-19) |
| /api/reactivation/launch | POST | Fire reactivation SMS + create graveyard job |

### preview endpoint returns:
- sms, workiz_link, job_count, last_jobs, prop_id
- prop_details: {pricing_note, prices_per_service, last_property_visit, type_of_service, last_reactivation_sent}
- last_jobs[]: {so_name, so_id, workiz_link, date, property, job_type, pricing_snap, total, frequency, pricing_note}

---

## KEY RULES
- Done jobs filter: x_studio_x_studio_workiz_status = 'Done' — NEVER use invoice_status or state
- Property fields read from partner_shipping_id of the SO (not the contact)
- Contact fields (frequency, last_reactivation_sent) read from parent partner_id
- openCandidate() uses partner_id lookup (not array index) — safe with name filter

---

### Customer Re-engagement flow (formerly "Follow-Up") — terminology rename 2026-04-30
`project_reengagement_flow.md`
> 2026-04-30 — Renamed Phase 5's customer cycle reminder from "Follow-up" to "Re-engagement" so DJ's voice "follow up with my uncle" stops colliding with the customer-SMS path. Phase 5 still creates project.task records (Odoo To-do app) named "Re-engagement: {customer} — {service}". The legacy 30 mail.activity records still match the SMS predicate via "follow up"/"reactivation"/"reach out" keywords. Voice "follow up" → create_todo (personal project.task, optional partner_id anchor).

**READ when editing Phase 5, the create_todo tool, the Activities SMS predicate, or the Render Claude system prompt around todos.**

## Why the rename

DJ uses "follow up" constantly in personal speech ("follow up with my uncle", "remind me to follow up with the dentist"). The same word was used by:
- Phase 5's project.task title: `"Follow-up: Customer — Service"`
- create_todo's project.task title: `"[Render] Follow-up: Customer"`
- Render Claude's tool description ("create a follow-up to-do")

Result: voice trigger ambiguity → Render Claude was asking too many CLARIFY questions, sometimes routing personal todos through customer-anchor logic.

**Rename**: Phase 5's customer-cycle-overdue flow is now **"Re-engagement"**. Personal voice todos use whatever DJ said as the title (no fixed prefix).

## Current architecture (post-rename)

| Trigger | Tool / Code path | Storage | Title pattern | SMS button? |
|---|---|---|---|---|
| Phase 5 fires (job done with frequency) | `zapier_phase5_FLATTENED_FINAL.py::create_followup_activity` | `project.task` (project_id=False) anchored to res.partner | `Re-engagement: {customer} — {service}` | No (predicate excludes source='task') |
| DJ voice: "follow up with X" / "remind me to Y" | Render Claude `create_todo` tool | `project.task` (project_id=False) anchored to partner_id (if customer named) or no partner | DJ's actual phrase, e.g. `"call uncle Bob"` | No |
| Phase 5's "On Demand" path (manual invoice, no Workiz job) | Same `create_followup_activity` (via `create_ondemand_followup`) | `project.task` | `Re-engagement: ...` | No |
| ~30 LEGACY records (pre-rename Phase 5) | `mail.activity` records still in DB | `mail.activity` | `Follow-up: {customer}` | **Yes** (predicate matches) |

## SMS button (`isFollowupTodo` predicate in activities.html)

Matches now: `re-engagement`, `reengagement` (new), PLUS legacy `follow up`, `follow-up`, `followup`, `reactivation`, `reach out`. The legacy keywords stay because the ~30 historical mail.activity records still need the SMS button. **Predicate also requires `source='activity'`** — project.task records never match regardless of title.

## Render Claude system prompt rule (commit 1645e679)

Added explicit terminology rule:
- "follow up with X" / "remind me to Y" / "note to self" / "add a task" → ALWAYS `create_todo`
- Pass `partner_id` only if X is a real customer (silent search_customers check first)
- Default `days=7` if unspecified; map "tomorrow"/"next week"/etc to integers
- DO NOT ask "personal or customer?" — search silently and decide
- "Re-engagement" is reserved for Phase 5's automated flow — NOT voice-triggerable

## Chatter breadcrumbs (already in Phase 5 — preserved through rename)

Phase 5 posts a chatter mail.message on the linked SO when it creates a Re-engagement task:
> `[Phase 5] Re-engagement Task created | Customer: X | Due: Y | Task: <url>`

For "On Demand" path (no SO, just an invoice), it posts on the invoice instead:
> `[Phase 5] Re-engagement Task created | Customer: X | Due: Y | Task: <url>`

## Files touched in the rename

| File | Repo | Change |
|---|---|---|
| `zapier_phase5_FLATTENED_FINAL.py` | windowandsolarcare-hash/Odoo-Migration | Title `Follow-up: ...` → `Re-engagement: ...`; chatter prefix `[Phase 5]` |
| `routers/owner/dashboard.py` | windowandsolarcare-hash/saunders-render-app | `create_todo`: drop `[Render] Follow-up:` prefix, accept personal todos (partner_id optional), better description; system prompt terminology rule |
| `static/owner/activities.html` | windowandsolarcare-hash/saunders-render-app | `isFollowupTodo()` matches `re-engagement` + legacy keywords |

## DJ's manual step (one-time)

Rename Workiz SubStatus from `"Follow Up Trigger"` to `"Re-engagement Trigger"` in Workiz UI. Phase 5 only reads the rendered activity title, not this SubStatus, so the rename is cosmetic for Workiz. Optional but consistent.

## Task #25 — closed as obsolete

Pre-rename, there was a pending task to "Extend SMS Follow-Up flow to project.task records." After the rename:
- The SMS flow stays bound to the legacy ~30 mail.activity records (uses `x_followup_workiz_uuid` field)
- Future Phase 5 records are project.tasks → never qualify for SMS button
- Personal voice todos are project.tasks → never qualify for SMS button

So extending SMS to project.task is no longer needed. The split is now clean:
- `mail.activity` = legacy SMS records only
- `project.task` = customer cycle reminders (Phase 5) + personal voice todos (create_todo) — neither uses SMS

## Related memory

- `project_followup_flow.md` — original Follow-Up flow doc (pre-rename, kept for history)
- `project_todo_models_in_odoo.md` — mail.activity vs project.task distinction
- `reference_render_claude_write_tools.md` — write tool catalog (create_todo entry)
- `feedback_no_re_listing.md` — DJ communication style

---

### Render App — April 18 2026 State
`project_render_app_apr18.md`
> Current state of app.py and index.html as of 2026-04-18 — all features, tools, recent changes

# Render App Current State — 2026-04-18

---

## RECENT CHANGES (this session)

### app.py
- `api_upcoming`: now fetches `project.task` records for upcoming SOs → adds `task_names` list to each job → enables Solar/Window service type on future day rows
- `api_upcoming`: extended from 10 → 14 calendar days (guarantees 10 work days Mon-Fri)
- `_render_timer_stop`: log description now includes PT start + end times: `[Render Timer] 1234 Main St | 8:15 AM – 10:32 AM`
- `POST /api/attachment`: new endpoint — accepts base64 image, creates ir.attachment on SO in Odoo. Params: access_code, so_id, filename, content_type, data
- `tool_github_list_dir`: new tool for Render Claude — lists files/dirs in GitHub repo. Empty path = root. Returns dirs as [folder/] and files with sizes.

### index.html
- Future day rows now use `job-name-wrap` div (fixes dollar amount right-justification)
- Solar/Window service type subtitle now shows on future day rows (from task_names)
- `.job-svc` font size: 11px → 13px
- Saved request library: localStorage `wsc_saved_qs`, max 15 recent + unlimited starred. Tap to reuse, ☆ to pin. Shows below Send button in Command tab.
- Timer stop: GPS timeout 5s → 2s. `_timerStopping` guard prevents double-tap. Button disables immediately on tap.
- Photo section: above payment section, gallery picker (not camera-only), multiple files, uploads to Odoo as ir.attachment, thumbnail previews
- Mic button: moved into header between date block and sun/theme button. No longer fixed/floating overlay.
- Tab renamed: "7-Day" → "10-Day"
- Time label on done jobs: shows `2.5h` or `45m` LEFT of `$190/hr` — quick visual check if timer logged correctly
- `_timerStopping` guard + button disable on stop

---

## CLAUDE TOOLS IN app.py (full list as of 2026-04-18)

**Read tools:**
- search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job
- get_sales, get_sales_week (Mon-Sat), get_sales_month (Mon-Fri only, returns days dict)
- get_jobs_list, navigate_to
- odoo_query, github_read_file, github_list_dir (NEW), refresh_shared_memory

**Write tools (require confirmation):**
- update_workiz_field, update_odoo_contact, post_odoo_note, create_todo
- mark_job_done, create_workiz_job, duplicate_workiz_job
- start_task_timer, stop_task_timer, record_check_payment
- odoo_write, github_push_file, update_shared_memory

**Utility:**
- save_memory, delete_memory

**Direct API endpoints (not Claude tools):**
- POST /api/timer/start — starts Render timer
- POST /api/timer/stop — stops Render timer, creates timesheet, reverse-geocodes GPS
- POST /api/payment — records payment, creates invoice, posts chatter
- POST /api/attachment — NEW: uploads photo to Odoo SO as ir.attachment
- GET /api/upcoming — schedule lookahead (14 calendar days)
- GET /api/dashboard — today's schedule + stats

---

## KEY BEHAVIOR RULES (system prompt)

- MONTHLY JOB LISTS: always use Odoo SOs, never Workiz API with only_open
- Timer: always use task_id from session context for stop, never re-search
- Payment: customer known from session, use partner_id + so_id directly
- get_sales_week = Mon-Sat (no Sunday)
- All Render-created tasks/notes tagged [Render]

---

## TIMER SYSTEM

- Start: stores UTC start in ir.config_parameter key `render.timer.{task_id}`
- Stop: reads param, calculates elapsed, creates account.analytic.line, clears param
- Description format: `[Render Timer] 1234 Main St, Palm Desert CA | 8:15 AM – 10:32 AM`
- Voice stop (no GPS): `[Render Timer] | 8:15 AM – 10:32 AM`
- Moves task to In Progress (stage 18) on start
- Clears Odoo's own timer_start to prevent conflicts

---

## UPCOMING / SCHEDULE DISPLAY

- Left panel (mobile closed): shows today's jobs + future work days with jobs
- Future days: job-name-wrap, Solar/Window subtitle, right-justified amounts, WZ+SO pills
- 10-Day tab (desktop right panel): full 14-calendar-day lookahead, all work days with jobs
- Saved requests: localStorage, pin/star favorites, tap to reuse

---

## PHOTO ATTACHMENT

- Photo section appears above payment section when job is opened
- Gallery picker (not camera-forced), multiple files allowed
- Upload immediately on selection → Odoo ir.attachment on SO
- Thumbnail preview with ✕ to remove
- Clears when new job selected

---

### Render app GPT tools — current list
`project_render_app_tools.md`
> 20 tools available to GPT in the Render field assistant app as of 2026-04-12

Current tools in app.py (20 total):

Read tools: search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job, get_sales, get_sales_week, get_jobs_list, navigate_to

Write tools (require confirmation): update_workiz_field, update_odoo_contact, post_odoo_note, create_todo, mark_job_done, create_workiz_job, duplicate_workiz_job, start_task_timer, stop_task_timer

Utility: send_email, save_memory, delete_memory

**Key rules built into tool descriptions:**
- get_sales_week = Mon-Sat only (no Sunday), use for weekly revenue queries
- get_jobs_list = Workiz browse only, NEVER for revenue (pulls by creation date not job date)
- duplicate_workiz_job = copies all fields from most recent job, schedules on new date
- All Render-created tasks/notes tagged with [Render] breadcrumb

**How to apply:** When adding new tools, follow the pattern: Python function + TOOLS list definition + WRITE_TOOLS set (if write) + READ_TOOL_MAP or execute_write_tool handler + _describe_write entry (if write).

---

### Render app employee stats — future design decision
`project_render_employee_stats.md`
> Stats panel is owner-only on mobile; future employee stats will use a toggle button swap approach

Stats panel (`#office-panel`) is intentionally desktop/owner-only. Employees on a phone only see the schedule panel.

**When employee-facing stats are built:**
- Use a toggle button in the field panel header to swap the entire view to a fresh employee stats screen
- Start from a completely blank screen — do NOT modify or reuse the existing `#office-panel`
- This gives full design freedom for employee-appropriate metrics without touching owner layout

**Why:** DJ wants stats like revenue to remain owner-only. Employee stats (e.g. jobs completed, hours logged) may be added later as a separate view.

**How to apply:** When DJ says "add employee stats to the app", implement as option #2 (toggle/swap), not as tabs within the existing office panel.

---

### Render rolling deploys can briefly serve stale code from old instances
`project_render_rolling_deploy_stale.md`
> After a deploy "finishes", an older instance may still serve traffic for a minute. Don't trust user-reported behavior immediately after a fix push — verify via logs/instance ID.

Render's deploy lifecycle:

1. New deploy created → builds → status=live
2. New instance starts up (gets a unique instance ID like `srv-XXX-tssvt`)
3. Old instance keeps serving traffic until new one is healthy
4. Old instance is drained (graceful shutdown — finishes in-flight requests)
5. Now only the new instance serves traffic

During step 3, both instances exist. Requests can hit either one. The old instance runs the OLD code.

**Real example 2026-04-27:** Pushed search-fuzzy fix at commit `54eaf59` (deploy finished 07:10:56). DJ tested at 07:16:08 and got OLD-code results (Bob Jones for "Jon Hamm"). The request hit instance `tssvt` which was actually running pre-fix code. Subsequent test at 07:24 (different instance `smgvp`) returned the correct fix.

**Why:** When users report "it didn't work" within 1-2 minutes of a deploy, do NOT immediately assume the fix is broken. Check Render logs for `instance` label — if it differs from the one running the new code, you're seeing stale-instance behavior.

**How to apply:**
- After a deploy, wait ~2 minutes before asking the user to re-test.
- If user reports failure right after a deploy, check the deploy status (`mcp__render__list_deploys`) and confirm `status: live`. Then check the request log for `instance` label.
- If instance ID matches a known new deploy: code is suspect, debug further.
- If instance ID is from an older deploy: ask user to retry; deploy hadn't fully cut over.
- For high-confidence verification: ship a temporary `print(...)` log line, deploy, ask user to retry, pull logs filtered by `text=["[search]"]` or similar marker.

---

### Render Claude session history persists to Odoo (survives redeploys)
`project_render_session_persistence.md`
> 2026-04-26 — Render Claude conversation history moved from in-memory _sessions dict to Odoo ir.config_parameter (key=render.session.{session_id}). Survives redeploys, restarts, free-tier sleep.

**Bug discovered 2026-04-26:** Render Claude was losing all per-customer context whenever code was pushed. Root cause: `get_history` / `save_history` / `clear_history` used an in-memory dict `_sessions` that gets wiped on every Render redeploy and free-tier sleep. We pushed multiple fixes today, each one wiped Render Claude's working memory of the active customer (e.g., Kristin Acker).

**Fix (commit 455754d on saunders-render-app):** session history now persists to Odoo `ir.config_parameter` under key `render.session.{session_id}`. The three helpers (`get_history`, `save_history`, `clear_history`) now read/write Odoo. Trim is still last 40 messages with the existing tool_result-orphan protection. Per-turn cost is 1 Odoo read + 1 write — fast enough.

**System prompt also updated** (commit 455754d) with two new sections:
- **CONTEXT PRESERVATION** — pronouns default to most recently discussed customer; never re-search the active customer; UUID/partner_id/so_id stick once known.
- **NO TRIAL-AND-ERROR** — use existing tools as documented; don't retry blindly on errors; if no tool exists, plan with DJ first then execute once.

**Why:** DJ pays per Anthropic API call. Re-search burns tokens. Wrong API formats burn tokens. Lost context burns tokens twice (once for the lost work, once to re-do it).

**How to apply:**
- When asked about Render Claude memory, this is now backed by Odoo — wipes only happen if `clear_history` is explicitly called.
- If DJ wants to manually clear a session, delete the `render.session.{session_id}` ir.config_parameter row.
- If session storage grows unbounded over months, add periodic cleanup of rows with `write_date` older than X days. Not built yet — wait for evidence of pressure.
- If you want to TEST the persistence, push any change → Render redeploys → query Odoo for `render.session.*` keys to confirm history rows are still there.

---

### Render timer UI resets display on reopen (data is clean)
`project_render_timer_ui_cumulative.md`
> Field Assistant timer LOOKS like it starts over when DJ leaves a job and comes back — UI-only bug, backend correctly updates the single timesheet line with cumulative hours

**What DJ sees:** Starts timer on a job, navigates away (to check another job, look at something), comes back — timer display shows 00:00 again, not cumulative elapsed time.

**What actually happens in the backend (verified 2026-04-20 across all 7 jobs today):** Every task has exactly ONE account.analytic.line (timesheet). Resuming doesn't create duplicates — the backend finds the existing line and adds to `unit_amount`. Timesheet math is 100% accurate.

**Proof:** Barbra Balser task showed `write_date` 12 minutes after `create_date` with total = 1.0 hour, while display name range only captured the first session ("9:34–9:46 AM"). That's the backend correctly accumulating hours while the display name only reflects the first start/stop.

**Two separate display bugs inside the single UI issue:**
1. **Timer face** shows elapsed-since-last-resume instead of total accumulated seconds.
2. **Task name time range** (e.g. "Customer - Service (9:34 AM - 9:46 AM)") only reflects the first session, not the updated end on subsequent resumes.

**How to apply:**
- When DJ asks "does the timer actually restart or just look like it?" — answer: looks only, data is correct.
- Fix when building this: 
  - Timer face: on reopen, compute elapsed from `unit_amount * 3600` + (now - last-start-timestamp if running), not just (now - this-session-start).
  - Task name: strip the "(HH:MM AM - HH:MM AM)" suffix and regenerate it from actual line data on every save, OR stop auto-writing the time range into the name entirely.
- Not urgent — invoicing and payroll both pull from `unit_amount`, which is correct. This is purely cosmetic/confidence.

**Today's 7 jobs, 1 timesheet line each, zero duplicates detected.**

---

### Saunders Printing — Commercial Web-to-Print Plan
`project_saunders_printing.md`
> Full plan for Saunders Printing commercial print business — web-to-print site, file prep automation, Odoo accounting, Stripe payments

# Saunders Printing — Commercial Web-to-Print

**Decided:** 2026-04-18
**Status:** Planning complete. Nothing built yet.

---

## BUSINESS MODEL

Commercial print shop — business cards, flyers, postcards, banners, etc.
DJ has his own printer. He enters jobs, prints, and ships under Saunders Printing brand.
AI handles everything else: order taking, file checking, file prep, payment, accounting.

---

## THREE CUSTOMER PATHS

### 1. Customer uploads their own file
- Customer uploads design file on website
- Claude checks: resolution (300 DPI min), bleed (0.125" standard), color mode (RGB→CMYK), file format, safe zone
- Auto-converts to print-ready PDF
- Flags issues or approves
- Order placed, DJ receives production-ready PDF

### 2. Customer wants to design their own
- Embed Canva (free embed SDK) or simple template builder on site
- Customer designs, exports, uploads
- Same file check/prep as path 1
- V1: skip this — launch with upload + custom design only. Add self-design later.

### 3. Customer wants Saunders Printing to design it
- Customer fills out brief on site (colors, style, text, examples)
- Pays design fee upfront
- Claude drafts using DALL-E 3 / Flux
- DJ reviews and approves design
- File prepped, order fulfilled

---

## FILE PRODUCTION PROCESS (automated)

Claude handles via Python libraries:
- Resolution check: 300 DPI minimum — flag/reject low-res
- Bleed: 0.125" on all sides — add programmatically if missing
- Color mode: RGB → CMYK conversion
- Format: convert to print-ready PDF
- Safe zone: flag text/logos too close to trim edge
- Output: production-ready PDF delivered to DJ

DJ's only job: enter PDF into printer software, print, ship.

---

## PAYMENTS

- Stripe for credit card processing on site
- Odoo has native Stripe connector (included in DJ's full package)
- Customer pays on site → Stripe → bank
- Claude logs payment in Odoo automatically

---

## WEBSITE

- Platform: Odoo Website (already included in DJ's subscription)
- eCommerce native: product pages, cart, checkout, Stripe built in
- Orders flow directly into Odoo SOs automatically
- No manual order entry needed
- Design tool: Canva embed SDK (v2+), or skip for v1

---

## ODOO SETUP

- Third company: "Saunders Printing" (multi-company, same instance)
- Completely separate: chart of accounts, P&L, invoices, bank account
- Product catalog: business cards, flyers, postcards, banners — pricing tiers by quantity
- Revenue: logged per order
- Expenses: paper, ink, shipping supplies, design API costs
- Same pattern as W&SC and artwork businesses — no new seats

---

## LAUNCH STRATEGY (v1)

1. Build Odoo company + product catalog
2. Build Odoo website storefront with Stripe
3. File upload + automated file check/prep
4. "We design it" path with brief form + design fee
5. Skip self-design tool for v1

---

## DJ'S ROLE (the 5%)

1. Review and approve custom design jobs
2. Receive production-ready PDF
3. Enter job in printer software
4. Print and ship under Saunders Printing

---

## ARCHITECTURE FIT

```
One Render Service
    └── [future: Saunders admin route for order management]

One Odoo Instance
    ├── Company: Window & Solar Care (live)
    ├── Company: Artwork/Prints (planned)
    └── Company: Saunders Printing (planned)

Odoo Website
    ├── W&SC marketing site (planned)
    ├── Cheryl real estate site (planned)
    └── Saunders Printing storefront (planned)
```

---

### Saunders Render App — Architecture & State
`project_saunders_render_app.md`
> New multi-business Render app repo, login system, router structure, and deployment state as of 2026-04-19

# Saunders Render App

**Created:** 2026-04-19
**Status:** Scaffold live, login working, pointing at new repo

---

## GITHUB REPO
- **Repo:** `windowandsolarcare-hash/saunders-render-app` (private)
- **Local path:** `C:\Users\dj\Documents\Business\Saunders Render App\`
- **Branch:** `main`
- **Deploy:** Render auto-deploys on push to main

## RENDER SERVICE
- **Service name:** `wsc-field-assistant` (same service, repo changed)
- **URL:** `https://wsc-field-assistant.onrender.com`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port 8000`
- **Root directory:** blank (files at repo root)
- **Plan:** Starter ($7/month)

---

## FOLDER STRUCTURE

```
main.py                    ← entry point, mounts all routers
routers/
  auth.py                  ← login + role-based routing
  owner/
    dashboard.py           ← DJ's world (placeholder)
  tech/
    jobs.py                ← Danny's world (placeholder)
  cheryl/
    clients.py             ← Cheryl's world (placeholder)
shared/
  odoo.py                  ← Odoo RPC helper (shared by all routers)
  utils.py                 ← date/timezone helpers
static/
  login.html               ← login screen (name + PIN)
  owner/index.html
  tech/index.html
  cheryl/index.html
```

---

## LOGIN SYSTEM

- **Flow:** Name + PIN → POST /api/login → Odoo res.partner lookup → redirect by role
- **User storage:** `res.partner` in Odoo (no seats consumed)
- **Fields on res.partner:**
  - `x_render_pin` — 4-digit PIN (char, ID 19167)
  - `x_render_role` — owner / tech / cheryl (char, ID 19170)
  - `x_render_business` — wsc / cheryl / etc. (char, ID 19173)
- **Route map:** owner→/owner/, tech→/tech/, cheryl→/cheryl/

## DJ'S LOGIN RECORD
- Partner ID: 3 (Dan Saunders, original record)
- PIN: 8487
- Role: owner
- Business: wsc

---

## DEPLOY WORKFLOW (new repo)
Uses standard git push (not gh api like Odoo-Migration):
```bash
cd "C:\Users\dj\Documents\Business\Saunders Render App"
git add <file>
git commit -m "YYYY-MM-DD | filename | description"
git push origin main
```
Render auto-deploys on push. No manual trigger needed.

---

## KEY DECISIONS
- One Render service, one $7/month bill — no separate services per business
- res.partner for app users — no Odoo seats, no custom models
- Router-based separation — each business gets own router file(s)
- Old app.py (W&SC) still running on Odoo-Migration repo separately — migration to new repo is future work
- Fiduciary business (DJ's potential client) would get its own router + Odoo company, same pattern

---

### April 12 session — task/SO fixes and Phase 4 improvements
`project_session_apr12_fixes.md`
> Summary of fixes made April 12: orphaned tasks restored, SO smart button, staggered task times, Sunday tag

## Orphaned Tasks — Root Cause & Fix (April 12)

133 tasks had lost partner_id and sale_line_id (write_date = 2026-04-11 00:27, same second). Root cause not definitively identified — likely Phase 4 or sync_action_955 edge case.

**Fixed:**
- 131 tasks restored with `sale_line_id` (order line), `sale_order_id` (SO), and `partner_id` (property record with street address)
- Task partner_id must be the PROPERTY record (child partner with street), NOT the contact (parent). SOs are tied to property records.
- `sale_order_id` (not `sale_line_id`) is what drives the SO smart button (`display_sale_order_button`)
- Writing `sale_order_id` clears `partner_id` — must write partner_id AFTER sale_order_id

**Phase 4 backfill fix:** Now sets `sale_order_id` in create_vals alongside `sale_line_id`.

## Task Timer Overlap — Staggered Start/End Times

Multi-task SOs (2+ tasks for same job) previously had all tasks at the same start/end time, causing "scheduling conflict" warnings in Odoo.

**Fix:** Phase 4 now staggers time slots sequentially:
- Task 0: job_start → job_start + per_task_hrs
- Task 1: job_start + per_task_hrs → job_start + 2*per_task_hrs
- etc.

Both the update path (bulk → individual writes) and backfill create path (enumerate loop) now stagger.

**Manually fixed 10 SOs** (003902, 003754, 003935, 003917, 003956, 003913, 003947, 003907, 004277, 004425).

**Why:** DJ noticed overlap warning when clicking a task — it said another task was at the same time.

**How to apply:** If future tasks show overlap warnings for same-SO tasks, check whether stagger is working. Task sort order = sorted(task_ids) by id.

## Sunday Tag — Graveyard Job Identifier

Created `crm.tag` id=17 "Sunday" and applied to all 508 open SOs where date_order (converted to Pacific time) falls on a Sunday.

**Why:** Sunday SOs should not be invoiced — they are graveyard jobs. The tag lets DJ quickly identify them when reviewing the reactivation filter.

**How to apply:** When checking SO invoicing status, Sunday tag = graveyard = skip invoice.

## Phase 4 Changes Pushed (April 12)

Three commits to `zapier_phase4_FLATTENED_FINAL.py` on main:
1. `add sale_order_id to backfill task create_vals for SO smart button`
2. `split allocated_hours equally across all tasks for same SO`
3. `stagger task start/end times for multi-task SOs (no overlap)`

## Calendly — Cathedral City Service Event Type

Created via MCP (April 12):
- URI: `https://api.calendly.com/event_types/b7ca8953-c2ba-468d-b30e-8e7c46be7243`
- URL: `calendly.com/wasc/cathedral-city-service`
- Days: Wednesday + Thursday, 8:30 AM – 4:30 PM Pacific, 90 min
- Custom questions (Service Address, Type of Service, Additional Notes) need to be added MANUALLY in Calendly UI — API cannot set them.

## app.py — Timer Tools Added (April 12)

Added `start_task_timer` and `stop_task_timer` to Render voice assistant app.
- Both are WRITE_TOOLS (require confirmation)
- Accept task_id or task_name (ilike search, returns error if multiple match)
- Call `project.task` `action_timer_start` / `action_timer_stop`
- Pushed to GitHub main

---

### Session summary — 2026-04-20 (truck / remote control day)
`project_session_apr20_summary.md`
> What was done today across W&SC and Cheryl projects; open items to revisit

**Context:** DJ was remote-controlling from his truck all day. One session name: WSC-Auto. Worked across W&SC and Cheryl projects from the single W&SC session using absolute paths.

## W&SC FIXES TODAY

**Balser orphan task — fixed.** SO 15916 had no project.task despite tasks_count=1. Recreated task 297, linked to order line 17478. Root cause: Phase 4 task re-entry bug (see `project_phase4_task_reentry_bug.md`).

**Jose Merelies tech-gate — diagnosed, not auto-fixed.** SO 17113 failed Phase 6 tech gate because `x_studio_x_studio_workiz_tech` was blank. DJ handled tech assignment from the truck. Invoice was created twice (INV/00114, INV/00116 both paid $150) because payment button fired twice — Phase 6 correctly refused to close Workiz on both attempts.

**Timer UI bug confirmed as UI-only.** Backend timesheets are clean (see `project_render_timer_ui_cumulative.md`). 7 jobs today, 7 single timesheet lines, zero duplicates.

**Orphan SO sweep — 1 real orphan found.** SO 17066 (Wayne Geringer, Aug 20 2026) still needs task recreation. Low urgency.

## CHERYL PROJECT — SHIPPED TODAY

Project was split out of W&SC repo into its own:
- Local: `C:\Users\dj\Documents\Business\A Cheryl Real Estate`
- Repo: `windowandsolarcare-hash/cheryl-real-estate`

Built and deployed:
- `/cheryl/` dashboard (5 tiles, dark/light toggle)
- `/cheryl/clients` list view + stage picker modal
- Odoo schema: "Cheryl's Clients" tag (id 249) + 4 custom fields on res.partner (x_cheryl_stage, x_cheryl_last_use, x_cheryl_onehome_visit, x_cheryl_onehome_ref)
- 314 contacts imported from her OneHome CSV

CSV gotcha: Google Sheets CSV export had data rows shifted one column right of header row. Solved with positional-extraction parser (`@` = email, `"Last, First"` = name, MM/DD/YYYY = date, trailing digits = ref). Import script: `A Cheryl Real Estate\1_Production_Code\import_cheryl_clients.py`.

Still blocked on Cheryl: checklist items per stage, business name (for Odoo company), CRMLS Spark API access via broker.

## INFRASTRUCTURE NOTE

**PowerShell deploy script gotcha:** When pushing files inside subfolders of a new repo, the old gh-api-via-powershell script failed with a nested-JSON error (404 mixed into the SHA var). Python subprocess wrapping gh worked. If DJ hits the same shell-out-via-PowerShell issue again, switch to Python subprocess. Detail in `project_cheryl_repo_split.md`.

## SCHEDULED (SESSION-ONLY, WILL DIE IF SESSION ENDS)

At 2026-04-20 18:42 local, DJ asked for "remind me soon" about pending items. Cron job 7c3d96b9 scheduled to fire at 19:27 local — one-shot, session-only. If DJ starts a new chat before 19:27, that reminder dies. All items are already captured in memory files (pending_sync_before_payment, odoo_upsell_activity, reactivation_attempt2, pending_cursor_history_review, plus the two new memories from today), so starting fresh doesn't lose the list — just loses the automated nudge.

## NEXT SESSION SHOULD ASK

- Did Cheryl give feedback on the client list view (she tests it tonight)?
- Did DJ disable the Odoo Upsell toggle yet?
- Does DJ want to recreate SO 17066 Wayne Geringer's task now or defer?
- Does DJ want to start on the Phase 4 sync re-entry permanent fix?

---

### Unfinished work from Apr 1-2 2026 session
`project_session_apr2_unfinished.md`
> Items started but not completed in the big 184-message session — remaining open items only

## RESOLVED — DO NOT REINVESTIGATE

### 1. Bad graveyard jobs — COMPLETE
All 52 graveyard jobs verified Apr 5 2026 — all have phone numbers, all have correct SubStatus. The Apr 2 batch WAS the post-fix run. No remediation needed.
- 4 progressed (Dana Zusman, Kenneth Theriault, George Frank, Joel Mugge)
- 2 STOP (Beverly Sparks, Stacey Eisner)
- Remaining 46 awaiting customer response (API SMS Test Trigger = normal initial status)

## ALL ITEMS RESOLVED — 2026-04-05

### 2. Debbie Church price issue — DONE (marked resolved by DJ 2026-04-05)

### 3. Full reactivation rerun list — DONE (Apr 2 batch covered all customers)

**Why:** Session hit rate limit at 3:31 AM Apr 2 with these items actively in progress.

---

### SO line items with qty=0 / subtotal=0 are "soft-deleted" — ignore them
`project_so_lines_zero_means_deleted.md`
> 2026-04-28 — Odoo blocks hard delete of order lines on confirmed sale.orders ("set to 0 instead" error). DJ's workflow is to zero out the qty/price as a soft-delete. Any analysis that walks order lines (service classification, totals, line counts) MUST filter out zero-value lines or it'll see ghosts.

Odoo blocks hard-delete of `sale.order.line` records on confirmed sale.orders (state `sale` or `done`) with `UserError("You cannot remove an order line ... set the quantity to 0 instead")`. DJ's standard workflow is to zero the line out — qty=0 and price=0 — as the "soft delete."

**Why:** caused a confusing case on 2026-04-28 — Bud Piraino's SO showed `Window ⚠` in the field assistant because my code saw both Solar and Window in his order lines. But the Solar line had been zeroed out by DJ — it was effectively deleted. The naive read pulled the line name regardless of its values.

**How to apply:**
- Any code that reads `sale.order.line` for analysis (service classification, line counts, billing summaries, etc.) must include `price_subtotal` and `product_uom_qty` in the fields and skip lines where both are zero.
- Don't try to delete the line yourself either — Odoo will reject it. Set qty=0 (and price=0) instead. Same rule applies for one-off scripts.
- Pattern:

```python
lines = odoo_rpc('sale.order.line', 'read', [line_ids],
    {'fields': ['id', 'name', 'order_id', 'price_subtotal', 'product_uom_qty']}) or []
for ln in lines:
    qty = float(ln.get('product_uom_qty') or 0)
    subtotal = float(ln.get('price_subtotal') or 0)
    if qty == 0 and subtotal == 0:
        continue  # soft-deleted
    # ... process the live line
```

- This is parallel to `project_so_unlink_needs_cancel.md` (which is about the SO itself, not its lines).

**Also note:** `amount_total` on the SO already correctly excludes zero-value lines (since they sum to 0 anyway), so SO-level totals are unaffected by this. The bug only surfaces in code that reads individual lines.

---

### Odoo blocks unlink on confirmed sale.order — must cancel first
`project_so_unlink_needs_cancel.md`
> 2026-04-27 — Render Claude's odoo_write tool now auto-cancels sale.order before unlink. Odoo's _unlink_except_draft_or_cancel hook raises UserError on direct unlink of state in (sale, sent, done).

Odoo's `sale.order._unlink_except_draft_or_cancel` hook raises `UserError("You can not delete a sent quotation or a confirmed sales order. You must first cancel it.")` whenever you try to unlink an SO whose state is anything other than `draft` or `cancel`.

**To delete confirmed SOs you must:**
1. `odoo_rpc('sale.order', 'action_cancel', [[so_id]])`
2. `odoo_rpc('sale.order', 'unlink', [[so_id]])`

**Render Claude's `odoo_write` tool** auto-handles this as of commit 318a0801 (2026-04-27): when called with `model='sale.order'` + `method='unlink'`, it cancels each ID first then unlinks. So the LLM doesn't need to remember the two-step.

**Why:** This bites every time. Phase 4 doesn't have to deal with it because Phase 4 only fires on Workiz status changes — but when DJ asks Render Claude to delete a job, it tries unlink directly. Caught here when DJ asked to delete 3 SOs and got the UserError back.

**How to apply:**
- For one-off deletes via Python script: do `action_cancel` then `unlink`. The pattern I used for Judith Gordon's orphans (SOs 16767 and 16424) is the canonical example.
- For Render Claude: trust `odoo_write({model:'sale.order', method:'unlink', ids:[...]})` — the tool now handles the cancel automatically.
- Don't rely on the LLM to remember the two-step. The tool wraps it.
- Same pattern likely needed for `purchase.order` and other lifecycle models, but only add when actually hit.

---

### Task deletion on Submitted — stage filter
`project_task_deletion_stage_filter.md`
> Only delete tasks in New/Planned stages on Submitted status — never touch In Progress or Done

When a Workiz job goes back to Submitted (unscheduled), Phase 4 and sync_action_955 delete linked tasks. Fixed to only delete tasks in stage New (16) or Planned (17).

Tasks in In Progress (18) or Done (19) are protected — they have timer/timesheet data.

**Why:** DJ uses Submitted→Scheduled as a forced re-sync cycle (e.g. price update at the door). Old code deleted ALL tasks including ones with timer data, wiping timesheet records.

**How to apply:** Any task search before unlink must include `('stage_id', 'in', [16, 17])` filter. Both sync_action_955.py and zapier_phase4_FLATTENED_FINAL.py have this fix as of 2026-04-08.

---

### Odoo todo models — mail.activity vs project.task — when each is used
`project_todo_models_in_odoo.md`
> 2026-04-30 — DJ has TWO different models that act like to-dos. mail.activity is reminders attached to records (chatter). project.task with project_id=False is Odoo's "To-do" app records. Render's /api/todos must query BOTH. Bug found 2026-04-30 when Mark Sarah Fredricksen follow-ups (project.task) didn't show in Render Activities tab.

**READ when editing /api/todos, /api/followup/*, /api/todos/snooze, the create_todo tool, or any code that queries DJ's to-dos.**

## The two models

DJ's Odoo has two distinct "to-do-like" models, each used for different purposes:

### `mail.activity`
- "Next step on this record" — a reminder anchored to a specific business object via `res_model` + `res_id`
- Lives in the **chatter** of the parent record + appears in Odoo's global "Activities" filter
- Has `summary`, `note`, `date_deadline` (date), `activity_type_id`, `user_id`
- No stages, no tags, no time tracking
- Used in W&SC for: **reactivation follow-ups, follow-up SMS reminders, future-self reminders DJ creates ad-hoc**

### `project.task`
- A unit of work with stages, assignees, deadlines, tags, time tracking
- Two flavors:
  - **`project_id != False`** — task in a real project. Used by Field Service jobs (Phase 4 syncs Workiz jobs to project.tasks in `Field Service` project, id 2)
  - **`project_id = False`** — Odoo's "To-do" app records. Personal to-dos. Lives at `/odoo/to-do`.
- Has `name` (not summary), `description` (HTML), `date_deadline` (datetime), `state` (Kanban: '01_in_progress', '1_done', etc.)
- Used in W&SC for: **Field Service tasks (the schedule), personal To-dos created from Render via `create_todo` tool**

## Why Render's `create_todo` tool uses `project.task`

When Render Claude (or DJ via voice) says "create a follow-up to-do for X," the `create_todo` tool in `Saunders Render App/routers/owner/dashboard.py` writes to **`project.task`** with `project_id = False`. This is intentional — it's how Odoo's "To-do" app stores its records, so DJ sees them at `/odoo/to-do`. Using `mail.activity` instead would bury the reminder in the customer's chatter, which DJ doesn't check daily.

## The bug we hit on 2026-04-30

Render's `/api/todos` was originally built reading only `mail.activity`. When `create_todo` was later wired to use `project.task` (so to-dos appear in Odoo's To-do app), nobody updated `/api/todos` to ALSO read `project.task`. Result: the 3 Mark Sarah Fredricksen follow-ups DJ created via Render lived in `project.task`, showed up in Odoo's To-do menu, but **never appeared in Render's Activities tab**.

**Fix (commit 668d619f, 2026-04-30):** `/api/todos` now queries BOTH models, returns a merged list with a `source` field (`'activity'` or `'task'`) on each item. The `markdone` and `snooze` endpoints accept `source` to know which model to write to. Frontend passes `source` through.

## Rules going forward

When working on /api/todos or any to-do query/write code:

1. **Read both `mail.activity` AND `project.task`** in the same response. Filter project.task to:
   - `project_id = False` (Odoo To-do app records — NOT Field Service tasks)
   - `user_ids in [ODOO_USER_ID]` (DJ assigned)
   - `state not in ['1_done', '1_canceled']`
2. Each todo gets a **`source`** field: `'activity'` or `'task'`. Keep this on every record.
3. **Frontend must pass `source`** when calling write endpoints (markdone, snooze, etc.) so backend writes to the right model.
4. **Markdone semantics differ:**
   - `mail.activity`: `action_done` (or `unlink` as fallback)
   - `project.task`: `write({state: '1_done'})` (or `write({active: False})` as fallback)
5. **Snooze semantics differ:**
   - `mail.activity.date_deadline` is a **date** ('2026-04-30')
   - `project.task.date_deadline` is a **datetime** ('2026-04-30 12:00:00') — append ` 12:00:00` to avoid TZ rollover
6. **Followup-SMS modal only applies to mail.activity** — `isFollowupTodo()` predicate returns false for source='task' to suppress the "Open Follow-Up Editor" button. Task-source records get only Mark Done + Snooze.
7. **Done-list query needs both models too** (added 2026-04-30 night). `/api/todos/done` reads:
   - `mail.activity`: `active=False AND date_done >= cutoff` (with `active_test: False` context)
   - `project.task`: `project_id=False AND user_ids in [DJ] AND state='1_done' AND write_date >= cutoff`
   `write_date` is the proxy for "when completed" on tasks (most recent write is usually the state flip). Both share a `source` field.
8. **Reactivate semantics** (commit 19854da0, `/api/todos/reactivate`):
   - `mail.activity`: `write({active: True})` to un-archive (record stays present after action_done; only the `unlink` fallback would lose it permanently)
   - `project.task`: `write({state: '01_in_progress', active: True})` — `01_in_progress` is the default open state for Odoo 19 To-do app records

## Files involved

- `Saunders Render App/routers/owner/dashboard.py`:
  - `create_todo` tool — writes to project.task
  - `/api/todos` — reads both
  - `/api/todos/snooze` — handles both
  - `/api/followup/markdone` — handles both
- `Saunders Render App/static/owner/activities.html`:
  - `loadOpen` / `renderOpen` — caches `source` per todo
  - `detailMarkDone`, `detailSnooze` — pass `source` to backend
  - `isFollowupTodo` — returns false for source='task'

## Don't confuse these with project.task records that ARE Field Service jobs

`project.task` with `project_id = 2` (Field Service) is a SCHEDULED JOB on DJ's calendar, NOT a To-do. Different concept entirely:
- Field Service tasks come from Phase 4 (Workiz job → Odoo SO → action_confirm → task creation)
- They have product line items, planned start/end times, tech assignees, etc.
- DJ uses these for actual work scheduling, not reminders
- They're shown in the Render Field Assistant schedule tab, not the Activities tab

The To-do app filter (`project_id = False`) cleanly separates them.

---

### Workiz API access — local machine blocked, use Odoo as proxy
`project_workiz_api_access.md`
> Workiz API returns 403 from local machine — must proxy through Odoo server action to call Workiz from scripts

Workiz API is IP-restricted. Direct calls from a local machine return HTTP 403. Only the Render server and Odoo server can reach Workiz directly.

**Why:** Workiz restricts API access by IP. Render and Odoo are on allowed IPs. Your local dev machine is not.

**How to apply:** Any time a script needs to call Workiz (check tags, fetch job data, verify status), proxy through a temporary Odoo server action:

1. Create temp `ir.actions.server` (model_id=670 for sale.order) with the Workiz fetch code
2. Run via JSON-RPC with `active_id` set to any valid SO id
3. Use `raise UserError(result_string)` to get data back in the error response
4. Delete temp action immediately after
5. Read result from `resp['error']['data']['message']`

Auth secret is REQUIRED in all Workiz URLs — without it you get 403 even from allowed IPs:
`https://api.workiz.com/api/v1/{TOKEN}/job/get/{UUID}/?auth_secret=sec_334084295850678330105471548`

Rate limit: ~30 rapid calls before HTTP 429. Sleep 15-30 seconds between batches of 30.

From Render (app.py) and Odoo server actions: direct calls work fine — no proxy needed.

---

### Workiz delete job API
`project_workiz_delete_job_api.md`
> How to hard-delete a Workiz job via API — endpoint, required fields, and common mistakes

Workiz jobs CAN be hard-deleted via API using this pattern:

```bash
curl -s -X POST "https://api.workiz.com/api/v1/{API_TOKEN}/job/delete/{UUID}/" \
  -H "Content-Type: application/json" \
  -d '{"auth_secret": "{AUTH_SECRET}", "ID": "{UUID}"}'
```

Response on success: `{"flag":true,"msg":"Job deleted"}`

**Why:** The delete endpoint exists but requires `ID` = the job UUID in the POST body (not just in the URL). Without it you get `"ID: Field is Required"`. Also requires `api.workiz.com` base URL — using `app.workiz.com` hits a Cloudflare block.

**How to apply:**
- Use `api.workiz.com` (NOT `app.workiz.com`) for all Workiz API calls
- Pass `"ID": "UUID"` in the JSON body along with `auth_secret`
- UUID goes in both the URL path AND the body `ID` field
- Rate limit kicks in around 13 rapid deletes — add `sleep 30` between batches if deleting many jobs
- Workiz's own API docs don't mention this endpoint, and the old cleanup script incorrectly stated "Workiz doesn't have a delete API" — it does

**Checking if a job is deleted (GET behavior):**
When you GET a deleted/non-existent job, Workiz returns **HTTP 204 (No Content)** — NOT 404. Empty body.
- 200 with data → job exists
- 200 with empty data → job gone
- 204 → job gone (no content)
- 404 → job not found

Always treat both 204 and 404 as "confirmed deleted" when checking before an Odoo SO deletion.

---

### Workiz job/all/ endpoint skips unscheduled jobs — use job/get/{UUID}/ directly
`project_workiz_job_all_quirk.md`
> 2026-04-27 — discovered when trying to find a follow-up trigger job created with no JobDateTime. job/all/ paginated through 100+ jobs, never returned the new one. job/get/{UUID}/ found it instantly.

The Workiz REST API endpoint `job/all/?start_date=...&records=...` returns only **scheduled** jobs (jobs with a real JobDateTime). Jobs created with no JobDateTime — like reactivation graveyard jobs and follow-up trigger jobs — will NOT appear in `job/all/` results regardless of how far back you push `start_date`.

**Practical implication:**
- If you're hunting for a recently-created Workiz job and you don't have the UUID handy, `job/all/` will not save you for unscheduled jobs.
- `job/get/{UUID}/` works for any UUID, scheduled or not.
- The Render `tool_search_customers` lookup pulls jobs from Odoo SOs — that's the right path when you only know a customer name.

**How I found it:** 2026-04-27, I sent a follow-up text to Bev Hartin via the new follow-up flow. The launch wrote x_studio_last_followup_sent=today (proving the Workiz job was created), but `job/all/` paginated 100+ rows from start_date=2026-04-01 with zero matches for ClientId 1533. Initially looked like the Workiz create silently failed; turned out the job exists, it's just unscheduled, and the listing endpoint won't show it.

**Why:** Saves wasted scan time when debugging a "did this Workiz job get created" question for a known unscheduled JobType (Reactivation Lead, Follow Up Lead).

**How to apply:**
- Don't use `job/all/` to verify creation of an unscheduled job — verify by JobAmountDue / chatter / direct UUID lookup.
- For the follow-up flow specifically: the launch endpoint now posts the UUID + Workiz link to the contact's chatter (commit 728252f), so future sends are findable through the contact record.
- If a customer says "I never got that text," go to their res.partner chatter, find the most recent "Text sent" line, click the Workiz link to verify.

---

### Workiz scheduling toggle quirk
`project_workiz_scheduling_quirk.md`
> Workiz may require going through Submitted status before Send Confirmation - Text works after Calendly booking

When manually scheduling a Calendly-booked job in Workiz, the status change from "API SMS Test Trigger" (reactivation) directly to "Send Confirmation - Text" sometimes requires hitting Save more than once. Possible workaround: change SubStatus to Submitted first (which resets/submits the job), then come back and set "Send Confirmation - Text" — this might allow it to work in one save.

**Why:** Workiz appears to have a quirk where the scheduling toggle and status change don't always commit together in a single save when coming from the reactivation SubStatus.

**How to apply:** This is a future test item only. Current workflow (manual review → schedule → set Send Confirmation - Text) is intentional and preferred because DJ needs to: (1) verify the schedule, (2) know the job exists, (3) add pricing line items. Do not automate this away.

---

### Workiz SubStatus update requires parent Status field
`project_workiz_substatus_needs_status.md`
> Workiz API quirk — POSTing only SubStatus returns 400 "Could not update sub status with no parent status provided". Must also send Status="Pending". Auto-injected in workiz_post.

Workiz API quirk: when updating a job's `SubStatus`, the request body MUST also include the parent `Status` field. Sending only SubStatus returns:

```
400 {'error': True, 'code': 400, 'msg': 'Validation rule exception',
     'details': {'error': 'Could not update sub status with no parent status provided'}}
```

**Workiz Status model (clarified by DJ 2026-04-26):** Only `Submitted` and `Done` are true top-level Status values we use. Everything else — Scheduled, STOP, Lead, Send Confirmation - Text, Next Appointment - Text, Next Appointment 2 - Text, **even In Progress and Canceled** — lives under `Status="Pending"` as a SubStatus. Always filter and report on SubStatus.

Hit 2026-04-26 when Render Claude tried to change Kristin Acker's job from Submitted to SubStatus="Send Confirmation - Text" via update_workiz_field — workiz_post sent only `{SubStatus: 'Send Confirmation - Text'}`.

**Fixed (commit 405a31d on saunders-render-app):** `workiz_post()` in `routers/owner/dashboard.py` now auto-injects `Status="Pending"` whenever the body contains `SubStatus` and no Status:

```python
if 'SubStatus' in data and 'Status' not in data:
    data['Status'] = 'Pending'
```

**Why:** Same defense-in-depth pattern as the UUID-in-body fix — central helper, can't be forgotten by future call sites. The invariant holds because all our SubStatuses live under Pending.

**How to apply:** When building Workiz API helpers in OTHER codebases (Zapier phases, Odoo server actions), apply the same rule: any SubStatus update must also send Status="Pending". Don't forget. This is in addition to the UUID-in-body requirement (project_workiz_update_needs_uuid_in_body.md).

---

### Workiz type_of_service_2 field name
`project_workiz_type_of_service_2.md`
> The Workiz API custom field for service type is type_of_service_2, NOT type_of_service — using the wrong name causes Phase 5 to create activities instead of new jobs

The Workiz API returns and accepts the service type custom field as `type_of_service_2`, not `type_of_service`.

**Why:** This caused Phase 5 to read the field as None, fall through to the "on demand" branch, and create an Odoo activity instead of a new Workiz maintenance job. Also caused new maintenance job creation to fail with "Could not find matching value for type_of_service - Maintenance". Fixed 2026-04-01.

**How to apply:** Always read with `workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')` and write with key `type_of_service_2`. Affects Phase 4 (3 read locations) and Phase 5 (read + write). The Odoo contact field that stores this value is `x_studio_x_type_of_service`.

---

### Workiz update/delete endpoints require UUID in request body
`project_workiz_update_needs_uuid_in_body.md`
> Workiz API quirk — job/update/ needs "UUID" in body, job/delete/ needs "ID" in body. URL path is not enough. Fixed via auto-injection in workiz_post.

Workiz API quirk: `POST /job/update/{UUID}/` and `POST /job/delete/{UUID}/` both require the UUID **in the request body**, not just the URL path. The two endpoints use **different keys**:

- `job/update/{UUID}/` → body must contain `{"UUID": "<uuid>"}`
- `job/delete/{UUID}/` → body must contain `{"ID": "<uuid>"}`

Without the body field, Workiz returns:
```
400 {'error': True, 'code': 400, 'msg': 'Error Validating Fields',
     'details': {'UUID': 'Field is Required'}}
```

Hit 2026-04-26 when Render Claude called `update_workiz_field` to add a note — `workiz_post()` only put UUID in the URL path.

**Fixed (commit 7cbd848 on saunders-render-app):** `workiz_post()` in `routers/owner/dashboard.py` now auto-injects the UUID into the body using a regex on the endpoint:

```python
m = re.match(r'^job/(update|delete)/([^/]+)/?$', endpoint)
if m:
    action, juuid = m.group(1), m.group(2)
    body_key = 'UUID' if action == 'update' else 'ID'
    if body_key not in data:
        data[body_key] = juuid
```

**Why:** Two call sites already had this bug latent (`update_workiz_field`, `mark_job_done`), and any future code calling `workiz_post` for update/delete would hit it. Centralizing the fix in `workiz_post` eliminates the entire class of errors.

**How to apply:** When building Workiz API helpers in OTHER codebases (Zapier phases, Odoo server actions), apply the same rule: include UUID in body for update, ID in body for delete. Don't rely on URL path alone. Best to centralize the helper and bake in the rule.

---

### Payroll System Migration & Timeclock UI — Apr 24 Session
`session_apr24_payroll_timeclock.md`
> Complete payroll system overhaul from JSON to hr.attendance; Manage Shifts UI; Gusto Smart Import with CA OT; multi-week display; task timer coupling

## Completed Work — Apr 24

### 1. Payroll JSON → hr.attendance Migration (LIVE)
- Migrated payroll.shifts and payroll.clockin JSON blobs → Odoo hr.attendance records
- Cleaned up 4 old ir.config_parameter rows (backed up to ~/wsc-render/payroll_json_backup_2026-04-23.json)
- hr.attendance is now sole source of truth; no more dual-write to JSON
- Dan: 5 attendance rows (4 migrated + 1 test); Danny: 3 rows backfilled to match Dan's work

### 2. Manage Shifts UI (LIVE at /timeclock)
- New "✎ Manage Shifts" button on timeclock card → opens modal interface
- Date range picker (defaults to current week, editable)
- Employee picker (owner/DJ only) — view/manage Dan or Danny's shifts
- **+ Add Shift button** — retroactive entry modal (clock-in/out times + RTP checkbox)
- **Edit Shift** — modify existing shifts (employee, times, RTP flag)
- **Delete Shift** — remove shifts with confirmation
- Visual hierarchy: shifts grouped by date, with per-day subtotals
- RTP badge and "CURRENTLY OPEN" flag for live clock-ins

### 3. Gusto Smart Import CSV Export (LIVE)
- **Backend**: `/owner/api/payroll/gusto_export` endpoint produces Gusto-compatible CSV
- **Format**: one row per employee for entire pay period (not per-day)
- **Columns**: last_name, first_name, title, gusto_employee_id, regular_hours, overtime_hours, double_overtime_hours, [rest blank]
- **CA Overtime Rules** (now implemented):
  - Daily: ≤8h → regular, 8–12h → overtime, >12h → double_overtime
  - Weekly: if regular hours >40 in a week, excess becomes overtime
  - Applied per-employee, per-week; no double-counting
- **Gusto Custom Fields** added to hr.employee (4 new fields):
  - x_gusto_employee_id (the 6-char code; Dan=a5f5da, Danny=1bacc2)
  - x_gusto_first_name, x_gusto_last_name, x_gusto_title
- Download button always exports **all active employees** (ignores picker), one CSV for entire range

### 4. Multi-Week Display (LIVE)
- When range spans >1 week: "Week of 4/13 – 4/19" headers appear before each week's day groups
- Week headers: solid blue (#1e3a8a) background + right-aligned week subtotal + left accent bar
- Day headers and shift rows indent under week headers for visual nesting
- Single-week range: same as before (no week headers, just day groups)
- Grand total row at bottom shows full range sum

### 5. UI Polish
- **Time Format**: All times now 12h (7:30 AM – 2:08 PM) instead of 24h
- **Font Sizes**: Bumped smallest text from 10–11px → 12–14px (readability on mobile)
- **Manage Shifts Button**: Light blue (#60a5fa) background, white text, larger padding/font
- **Modal Backdrop**: Darker overlay (rgba(0,0,0,0.85)) + blur(4px) for clarity
- **Removed**: Raw hours subtext under each shift row (info still in day header)

### 6. Task Timer Coupling (LIVE)
- Starting a task timer now auto-clocks in user for the day if not already clocked in
- Surfaces the auto-clock-in in UI: "▶ Timer running — also clocked you in for the day"
- No blocking if auto-clock-in fails (graceful degradation)
- Stopping task timer does NOT clock out (they remain independent; stopping one task ≠ end of workday)

### 7. Multi-User Employee Resolution (LIVE)
- Removed hardcoded ODOO_EMPLOYEE_ID = 1
- New `_employee_id_from_access_code(code)` helper: 8487 → Dan, 0708 → Danny
- Timer start/stop endpoints extract access_code from request → look up correct employee
- Attendance and timesheet entries now correctly attribute to whoever is using the app
- Voice path (Render Claude) still uses DJ_EMPLOYEE_ID as fallback (single-user context; doesn't need code)

### 8. Playwright Gusto Uploader (SCAFFOLD READY)
- scripts/gusto_upload.py — skeleton for logging in → navigating → uploading CSV → capturing screenshot
- scripts/README.md — full setup guide (pip install playwright, env vars, codegen calibration)
- **Issue discovered**: Google OAuth blocks Playwright's bundled Chromium as "automation"
- **Options**: (1) try real Chrome with channel='chrome', (2) use direct Gusto password (no Google SSO), (3) persistent browser profile, (4) semi-automate (you do SSO, script clicks upload), (5) Anthropic Computer Use
- Awaiting confirmation: does your Gusto account support direct email+password, or Google SSO only?

---

## Architecture Notes

**Payroll Data Flow**:
- Clock in/out on Render app → creates hr.attendance in Odoo
- Manage Shifts UI allows retroactive edits (add/edit/delete shifts)
- /owner/api/payroll/gusto_export sums hr.attendance → Gusto Smart Import CSV
- Every employee has 4 Gusto metadata fields; export uses them for matching

**Weekly OT Logic**:
- Per-day thresholds applied first (8/12h rules)
- Then weekly 40h cap checked — if regular >40, excess → overtime
- Works for single or multi-week exports; no overlap

**Multi-User Tracking**:
- Every API call (timer, shifts, exports) derives employee from access_code in request
- Voice tools default to DJ (env var DJ_EMPLOYEE_ID)
- Timesheet/attendance entries always have correct employee_id

---

## Open Items

1. **Playwright OAuth**: Try real Chrome vs. Gusto direct password vs. persistent profile
2. **First Gusto Upload**: Once Playwright is calibrated, do real end-of-pay-period upload
3. **Test Data Cleanup**: Delete 3 test shifts (4/6, 4/8, 4/10) and Saturday 4/18 test shift (id 18) once you confirm UI works

---

## Files Deployed

**Render App** (saunders-render-app):
- routers/owner/dashboard.py — all new endpoints + Gusto export logic + multi-user timer coupling
- static/owner/timeclock.html — Manage Shifts UI + multi-week display + 12h time format
- scripts/gusto_upload.py, scripts/README.md — Playwright skeleton

**GitHub Repos**:
- saunders-render-app/docs/timeclock_usage_for_danny.md — user guide
- saunders-render-app/docs/timeclock_rollout_punch_list.md — 5-item rollout checklist (live on Odoo activities)

**Odoo Activities**:
- Activity #53 (Dan's record, due 4/30): master punch list with links
- Activity #52 (Danny's record, due 4/25): training walkthrough

---

## Why: Reasoning

- **JSON → hr.attendance**: Single source of truth simplifies future queries, auditing, and integrations
- **Manage Shifts UI**: Retroactive entry crucial for "forgot to clock in" scenarios; owner can backfill for employees
- **Gusto Smart Import format**: Gusto's time-import is one row per employee per payroll; daily CSVs require concatenation
- **CA OT rules**: California law requires both daily (8/12h) and weekly (40h) OT calculation
- **Multi-week display**: Visual week grouping makes it clear when payroll periods cross week boundaries
- **Task timer coupling**: Prevents the case where you start timing a task but forget to clock in (payroll would miss the day entirely)
- **Employee ID from access_code**: Multi-user system requires knowing who is making the request; hardcoding breaks Danny's usage

---

## How to Apply

- Use Manage Shifts to retroactively fix any missed clock-ins (ideal with employee's input on times)
- Download CSV for your pay period (week or biweekly, depending on your Gusto schedule), import to Gusto
- If Playwright calibration succeeds, automate the final upload step per punch-list item #3
- Monitor task timer auto-clock-in behavior — should be silent if already clocked in, verbal notification if it auto-clocked

---

### Session 2026-04-25 Summary
`session_apr25_summary.md`
> Summarized huge chat into 4 memory files, pushed SHARED_MEMORY.md to GitHub, cleaned up test clock-in data, synced Dan and Danny payroll records for 4/20-4/24

## What Was Done

### 1. Summarized Huge Chat (COMPLETE)
- Took the massive pasted chat that ran out of context in previous session
- Extracted all key learnings and organized into 4 focused memory files:
  1. **project_payroll_hr_attendance_retrofit.md** — full payroll migration details
  2. **project_phase_flowcharts.md** — Phase 3/4/5 routing logic and flowcharts
  3. **project_cheryl_interview_infrastructure.md** — interview setup, Whisper, templates
  4. **project_gusto_integration_status.md** — CSV export, blockers, calibration steps

### 2. Updated Memory Index & SHARED_MEMORY.md
- Updated local MEMORY.md with 4 new pointers
- Updated SHARED_MEMORY.md with comprehensive "SESSION 2026-04-24 UPDATE" section
- Changed last-updated date to 2026-04-24
- Pushed to GitHub main with commit: `2026-04-24 | SHARED_MEMORY.md | session summary: payroll retrofit, phase diagrams, cheryl interview, gusto status`

### 3. Clock-In Test Data Cleanup
- **Queried 4/6-4/18 range:** Found 4 test shifts (all Dan)
  - 4/6: 15:00→19:30 (4.5h)
  - 4/8: 16:00→22:00 (6.0h)
  - 4/10: 14:30→23:15 (8.75h)
  - 4/18: 15:00→16:00 (1.0h)
  - Total: 20.25h
- ✅ **Deleted all 4 test records** (IDs: 15, 16, 17, 1)
- ✅ **Verified Danny backfill (4/20-4/22) still exists** (IDs: 9, 10, 11)

### 4. Synced Dan ↔ Danny Payroll Records
**4/20-4/22 (Initial backfill):**
- Found mismatch: Danny's times differed from Dan's
- Updated Danny's 4/20 and 4/21 to match Dan's (Dan = source of truth)
- 4/22 already matched

**4/23-4/24 (Active shifts):**
- Found Dan had multiple entries on 4/24 including test entry (0.008h)
- **Deleted Dan's test entry (ID 18)**
- **Closed Danny's open 4/24 shift** (was 15:00→False, now 15:00→18:03)
- **Added Danny's late shift** (22:32→00:35 next day) to match Dan

**Final synced state (both employees):**
- 4/20: 14:30 → 21:08 (6.63h)
- 4/21: 14:49 → 22:39 (7.83h)
- 4/22: 15:25 → 18:31 (3.10h)
- 4/23: 15:29 → 20:07 (3.63h)
- 4/24: 15:00 → 18:03 (3.05h) + 22:32 → 00:35 next day (2.04h)

## Clarification on 90-Day Limit

**Old system (pre-retrofit):**
- ir.config_parameter JSON blobs had 90-day rolling deletion (data aged off)
- No audit trail, fragile

**New system (hr.attendance):**
- Native Odoo model = infinite history, chatter audit trail
- **NO 90-day limit** — all shifts stay in Odoo permanently
- Render app may show only current week on field tech view (intentional), but backend stores forever

## Cheryl Project Status
- Odoo company created: "Cheryl Johnson, REALTOR®" (ID 2)
- Interview infrastructure complete & tested (template, guide, Whisper working)
- 314 contacts already imported
- **Next:** Schedule 60-minute interview to capture workflow
- All Cheryl work lives in separate repo (windowandsolarcare-hash/cheryl-real-estate), not W&SC

## Items Completed This Session
✅ Summarized huge chat into organized memory files
✅ Updated and pushed SHARED_MEMORY.md to GitHub
✅ Cleaned up test clock-in data (4/6-4/18 range)
✅ Verified and synced Dan ↔ Danny records for 4/20-4/24
✅ Deleted test entries, closed open shifts, added missing shifts
✅ Confirmed Cheryl project Odoo company exists

## Open Items (Not Session Scope)
- Gusto CSV format confirmation (need exact columns from DJ's Gusto template)
- Gusto Download CSV button scope fix (omit employee_id param)
- Playwright selector calibration (user to run codegen)
- Schedule Cheryl interview

---

### Session 2026-04-26 Summary
`session_apr26_summary.md`
> Refined Cheryl interview template based on transcript analysis; 8 improvements; identified gaps in MODELS_SPEC

## What Was Done

### 1. Analyzed Two Cheryl Interview Transcripts
- Reviewed two complete audio transcriptions of Cheryl describing her real estate workflows
- Extracted pain points, workflow patterns, unmet needs

### 2. Refined INTERVIEW.md Template (COMPLETE)
- **8 improvements** to the 20-question template:
  - Q5.5: Pre-contract communication strategy (pain point: clients confused, repeating info)
  - Q18.5: Automation & triggers (she wants "here's what you should know per deal stage")
  - Q18.7: Broker & system portability (pain point: "stuff with old pictures, old broker info")
  - Revised Q2: Client segmentation vs. time allocation
  - Revised Q17: Added audit trail follow-ups (escrow compliance)
  - Revised Q18: Added tool criticality depth
  - Revised Q19: Dashboard sketch specificity
  - Updated duration: **60 min → 75–90 min**

- **File pushed to GitHub:**
  - Repo: `windowandsolarcare-hash/cheryl-real-estate`
  - File: `3_Documentation/INTERVIEW.md`
  - Commit: `60015bcb5a06f9185b81bcc51d69ef69c5ac7ead`
  - Message: "2026-04-25 | INTERVIEW.md | refined template based on Cheryl transcripts..."

### 3. Identified Gap: MODELS_SPEC vs. Reality
- **MODELS_SPEC.md** (created 2026-04-20) is transaction-focused (contracts, escrow, closing dates)
- **Cheryl's actual pain points** are communication/automation/personalization-focused:
  - Pre-contract cadence ("what info, when, how often?")
  - Personalized follow-up (solar maintenance, home value, property features)
  - Automation triggers (stage-based messaging)
  - Tool consolidation targets
  - Broker portability

### 4. Documented Findings
- Created new memory: `project_cheryl_interview_refinements.md`
- Documented 5 top pain points from transcripts
- Listed what MODELS_SPEC has vs. what it lacks
- Proposed next steps: capture interview answers, add fields to spec

## Key Findings

### Cheryl's Top 5 Pain Points (ranked by emphasis)
1. **Pre-contract communication cadence** — clients don't know what to expect, she repeats
2. **Tool fragmentation** — 7–8 tools doing overlapping things
3. **Personalized follow-up** — wants smart reminders (solar, value, features)
4. **System churn on broker switch** — data/workflows don't port
5. **Communication proof/audit trail** — needs documented evidence (escrow compliance)

### What MODELS_SPEC Needs (post-interview)
- `x_cheryl_communication_template` model (pre-contract, in-contract, post-close sequences)
- Personalization data fields (solar, lot size, school district, etc.)
- `x_cheryl_automation_rule` (trigger-based message sends)
- Tool integration metadata (MLS sync, texting, calendar)

## Open Items

- **Next:** Run full 75–90 min interview with refined template
- **After interview:** Capture answers in fork `INTERVIEW_CHERYL_[DATE].md`
- **Then:** Propose field additions to MODELS_SPEC
- **Build order:** Communication templates → Automation rules → Integration handlers

## Files Modified
- `3_Documentation/INTERVIEW.md` — refined (pushed to GitHub)
- `memory/MEMORY.md` — updated index
- `memory/project_cheryl_interview_refinements.md` — new (session notes)
- `memory/session_apr26_summary.md` — new (this file)

## Session Statistics
- Duration: 1 session
- Changes: 1 file pushed to GitHub, 2 memory files created
- Interviews analyzed: 2
- Template improvements: 8
- Gaps identified in existing spec: 5 field categories

## Next Steps (for DJ)
1. Schedule 75–90 min interview with Cheryl using updated template
2. Capture her answers in `INTERVIEW_CHERYL_[DATE].md`
3. Share answers with Claude
4. Claude proposes additions to MODELS_SPEC based on her workflow
5. Build communication + automation models

---

### Apr 27 session — Activities page, Follow-Up flow, SO cleanup methodology
`session_apr27_summary.md`
> Long session covering: built /owner/activities (4th hub card), built parallel-to-reactivation Follow-Up flow, fixed odoo_write to auto-cancel SOs before unlink, extended Phase 3 filter, deleted ~85 stale SOs, surfaced 2 paid-not-invoiced jobs.

# Apr 27 Session — Big strokes

## Built: Follow-Up flow (parallel to reactivation, but pure Render)

Architectural pivot: Reactivation uses Odoo SAs 562/563. Follow-up does NOT — entire flow lives in `dashboard.py`. DJ explicitly endorsed moving away from SA pattern when Render is the trigger surface. Eventually reactivation should be ported the same way (future work, not in this session).

Files added/changed:
- `dashboard.py` `/api/followup/{preview,launch,markdone}` endpoints
- `dashboard.py` `_build_followup_sms()` template function — edit this for copy changes
- `field.html` (then moved to) `activities.html` — modal with editable SMS, Open/Done sub-tabs
- New Odoo field `x_studio_last_followup_sent` (date) on res.partner — id 20151
- New Odoo field `x_followup_workiz_uuid` (char) on mail.activity — id 20154

Cooldown 45 days. SubStatus `Follow Up Trigger` (DJ creates the Workiz automation on this).

After successful send: posts "📨 Text sent · Workiz job UUID · link" to contact chatter, archives activity manually (skipping `action_done` which would auto-write "Call done").

See `project_followup_flow.md` for full architecture.

## Built: /owner/activities page (4th hub card)

DJ asked for an "Activities" / admin section separate from Field Assistant. Pulled the To-Dos tab out of `field.html` right panel, dropped it into a standalone `activities.html` page. Hub `index.html` now has 4 cards: Time Clock, Field Assistant, Reactivation, **Activities (emerald)**.

Activities is a placeholder for "a whole bunch of other things" DJ wants to add later — not just to-dos.

## Fixed: workiz_post lost UUID + Status auto-injection

When I deployed dashboard.py for follow-up, my local file was OLDER than the deployed version. The deploy regressed two earlier `workiz_post` quirk fixes (commits 7cbd848 + 405a31d). DJ hit a 400 on Bev Hartin Send. Patched and redeployed. See `feedback_local_vs_deployed_drift.md` — diff before pushing.

## Fixed: odoo_write tool now auto-cancels sale.order before unlink

DJ asked Render Claude to delete 3 SOs — got Odoo's `_unlink_except_draft_or_cancel` UserError. Patched the generic `odoo_write` tool in dashboard.py: when `model=sale.order` + `method=unlink`, it loops action_cancel each ID first then unlinks. Render Claude no longer needs to remember the two-step. See `project_so_unlink_needs_cancel.md`.

## Fixed: Phase 3 trigger filter extended to Follow Up Lead

Phase 3's existing graveyard skip filter only matched `JobType="Reactivation Lead"`. Extended to a tuple `("Reactivation Lead", "Follow Up Lead")` so the new follow-up flow's Workiz jobs don't bring SOs into Odoo. Phase 4 didn't need changes — it delegates to Phase 3 for missing SOs.

Commit `ed24c02e` to `Odoo-Migration` repo. Local Phase 3 file: `1_Production_Code/zapier_phase3_FLATTENED_FINAL.py`.

## SO Cleanup — 85+ deleted across two passes

**Pass 1 — historical reactivation graveyards (65 SOs)**
- Filter: `workiz_status='API SMS Test Trigger' AND JobType='Reactivation Lead'`
- Cancel-then-unlink pattern (20 cancelled from state=sale, 43 direct unlink from draft)
- Spotted 2 anomalies (Les Berkey 003376, Linda Willingham 003885) that had wrong workiz_status — DJ took care of those manually
- Bulk deleted 63

**Pass 2 — past-2026 stuck Submitted (initial scan: 66 SOs)**
- 6 Workiz=Done, Odoo=Submitted (sync gap) → wrote workiz_status=Done in Odoo, deleted 4 dups
- 3 orphans (Workiz job deleted) → bulk delete
- 18 cleanup (8 Personal Time + 10 Clark Argeris dups from a Calendly storm)

**Major discovery on the remaining 39:** payment-aware Workiz scan revealed 2 paid-not-invoiced jobs:
- 003504 Laura Gregory $275 (1/20) — Workiz JobAmountDue=$0 but never invoiced in Odoo
- 003892 Norma Gould $85 (2/3) — same

These need DJ to run the Credit-method invoice flow in Odoo. Total revenue exposure: $360.

The other 12 unpaid stuck Submitted jobs total $1,380 — DJ has to decide per-row: completed-but-not-marked-done (mark Done), or no-show/cancellation (cancel).

9 4/5-batch SOs are Workiz-deleted but had real $-amounts ($75-$220 each, total $1,075). Worth investigating whether DJ ran them through some other channel.

## Methodology I want to remember

When debugging a "stuck Submitted" SO list, the right triage is:
1. Pull all SOs matching the filter
2. For each, fetch Workiz `job/get/{UUID}/` (use Odoo proxy for IP allowlist)
3. Categorize by `JobAmountDue`:
   - `=0` and `JobTotalPrice>0` → **PAID, do not delete** — needs invoicing in Odoo
   - `>0` → genuinely unpaid, balance still due
   - `=0` and `JobTotalPrice=0` → no-money job, probably safe to delete
   - HTTP 204/404 from job/get → orphan SO, Workiz job deleted
4. Don't bulk-delete by Odoo state alone — always cross-reference Workiz first.

This came out of DJ's question "look at Workiz before deleting — credit cards generate $0 due but the job IS paid." Memory: `project_credit_card_payment_flow.md` has the rule.

## What still needs DJ to act on

- 12 unpaid past-Jan SOs ($1,380) — mark Done if completed, cancel if no-show
- 16 $0 stuck SOs — most are likely safe to delete (Jane Doe, Fred Test, Dan Saunders test, etc.)
- 9 Workiz-deleted SOs with $-amounts ($1,075) — verify whether work was done via other channel
- 2 paid-not-invoiced SOs — high priority, $360 revenue exposure

## DJ feedback captured

- "I want full automation, not copy-paste" — for follow-up. Triggered the architectural pivot.
- "Always deploy without asking" — already in `feedback_confirmation_policy.md`.
- "Pick up the UUID from the SO and look at Workiz... if zero balance that means paid by CC" — payment-aware triage rule.

## Files touched today

- `Saunders Render App/routers/owner/dashboard.py` — many edits (followup endpoints, todos, odoo_write fix, workiz_post restore, /activities route)
- `Saunders Render App/static/owner/field.html` — to-do tab removed, tab order swap, font/layout changes
- `Saunders Render App/static/owner/index.html` — 4th hub card
- `Saunders Render App/static/owner/activities.html` — new file
- `Migration to Odoo/1_Production_Code/zapier_phase3_FLATTENED_FINAL.py` — filter extension
- Several Odoo data: 65+ SO deletes, 4 SO writes, 2 new Odoo custom fields

---

### Apr 28-29 session — Field Assistant polish + Activities module Phase 2 design
`session_apr28_29_summary.md`
> Heavy session on field-assistant pill/subtitle data sources, payment UX (preselect + greyed when paid), missing /api/job/append_note endpoint, /api/todos perf, Calendly detail modal, and the design for voice-driven activity creation (scheduled SMS + reminders, Twilio approval channel).

# Apr 28-29 — Big strokes

## Field Assistant — pill, subtitle, and payment polish

- **Pill** (next to dollar amount) now shows the SO's real `tag_ids` (OK, CF, etc.) — was previously showing service-word inferences. Backend: `_resolve_so_tag_names()` batches the crm.tag lookup. Frontend: `j.tags` array.
- **Subtitle** (Window/Solar/Combo) now driven by **JobType** — but with an orange `⚠` rendered next to it when an order-line analysis disagrees. **DJ explicitly chose this design** (auto-correcting from order lines would mask the data hygiene problem; the warning surfaces it instead). Logic in `_service_labels_by_so()`.
- **"Combination" → "Combo"** for screen real estate.
- **Zero-value sale.order.line rows are skipped** — Odoo blocks hard-delete on confirmed SOs, DJ zeroes qty+price as soft-delete. See `project_so_lines_zero_means_deleted.md`.
- **Pay button preselect** — when DJ taps a job, the payment method button (Check/Cash/Zelle/Venmo/Credit) is auto-highlighted based on the customer's most-recent `account.payment`. Wrapped in try/except so a schema problem can't break the schedule. See `project_account_payment_no_ref_field.md` for the `ref` field pitfall (caused a "No jobs today" outage when first deployed).
- **Pay button paid-state** — greyed and reads `✓ Already Paid` when the SO has a posted invoice with `payment_state in ('paid', 'in_payment')`. Re-activates after DJ deletes the payment in Odoo.
- **`openJob()` now resets payment section state** — fixes the bug where stale `✅ Paid` carried over into the next job.

## /api/job/append_note — added (was a 404)

The three-dots "Add Workiz Note" button on each row was hitting an endpoint that didn't exist — every press silently failed. Built the endpoint: pulls existing JobNotes, prepends `[YYYY-MM-DD HH:MM] [Render] <note>`, writes back. Newest first.

## /api/todos optimization

Was making 30+ sequential Odoo round-trips on each refresh. Now batches partner reads into 2-3 calls. `TODOS_USE_LEGACY = True` flag for one-line rollback. The date-window filter (originally 60d) was disabled per DJ's request — most of his to-dos sit far in the future.

## Activities module — Calendly detail modal

- To-dos whose summary contains "calendly" open a plain detail modal (full activity contents) instead of the follow-up SMS modal. No SMS path on these.
- HTML notes stripped to plain text on backend (`_strip_activity_html`). Anchor URLs preserved as text so frontend `linkify()` can wrap them as clickable links — Workiz job links inside Calendly notes are now actually tappable.

## Architecture decisions for voice-driven activity creation (designed, not built)

DJ wants a "personal assistant" UX: talk into phone → system creates the right kind of activity. Decisions agreed:

- **Two starter activity types:** `scheduled_sms` (prep now, fires later) + `reminder` (surfaces on due date).
- **Voice flow:** mic → Whisper → LLM structured parse (customer / when / type / draft message) → preview card with all four fields editable → save.
- **Type is always shown as a dropdown for explicit confirmation** — no surprises.
- **Draft message stored at creation time**, not regenerated at fire time. DJ writes it while context is fresh.
- **One Workiz substatus + one automation** for all `scheduled_sms` types. Each fire = new Workiz job, so the "fires once per status" limit doesn't apply. Same pattern as the follow-up flow.
- **Render daily cron** queries Odoo for activities due today and fires them. Daily resolution acceptable.
- **Twilio for approval SMS to DJ's personal phone** (separate channel from customer texts which stay on Workiz). Pattern: outbound prompt with token → DJ replies Y/N/tomorrow → Twilio webhook hits Render → action. DJ has not yet set up the Twilio account.
- **Generalizability requirement** — same UX must work for other businesses (Cheryl, future). Activity catalog and SMS templates per business; voice/LLM/preview/cron infrastructure shared.

Full plan in `project_activities_module.md` "Voice-driven activity creation" section.

## Notable bugs caught + memories saved

- `project_account_payment_no_ref_field.md` — Odoo 19 has no `ref` field on account.payment. Use `memo`. Lesson: wrap any decorator/preselect lookup in try/except.
- `project_so_lines_zero_means_deleted.md` — Odoo blocks hard-delete of order lines on confirmed SOs; zero-value lines = soft-deleted; analysis code must skip them.
- `feedback_no_re_listing.md` — Don't re-print tables/lists across turns. Write to a working file, reference it. Saved after DJ called out the back-and-forth scrolling pain on 2026-04-27.

## Bud + Gary skipped solar today

DJ skipped Solar on Bud Piraino and Gary Marsalone because their panels looked clean. Promised both a follow-up text in 2 months. **Currently NOT scheduled** — these will be the first real test of the voice-activity flow once it's built. Bud SO=15884 (003935), Gary SO=15885 (003917). Both are now `Combination of Services` JobType candidates (their order lines confirm Solar+Window) but JobType wasn't corrected today.

## Files touched today

- `Saunders Render App/routers/owner/dashboard.py` — many edits (tag resolver, service labeler, paid-status helper, last-payment-method helper, append_note endpoint, /api/todos batching + optimization)
- `Saunders Render App/static/owner/field.html` — pill source change, subtitle + ⚠, Combo, pay button preselect + paid-grey + reset on openJob
- `Saunders Render App/static/owner/activities.html` — detail modal + linkify

---

### Apr 29 session — Window Quote Tool, dashboard fixes, activity-flow unification
`session_apr29_summary.md`
> 2026-04-29 — Big build session. New /owner/quote tool replaces AppSheets pricing app. Activities pivot: detail modal first, follow-up as a button inside. 5-second undo grace on Mark Done. Field-assistant three-dots menu fixed for non-today rows. Stats drill-down + payment-history modal. Google Places API key wired. Multiple architectural pivots.

# Apr 29 — Big strokes

## Window Quote Tool — new major feature

**See `project_quote_tool.md` for the full reference.**

- Replaces the AppSheets "Our Pricing" app DJ disliked
- New routes: `/owner/quote` and `/tech/quote` (same HTML, role detected by URL)
- Counter-based UI for 6 line types (Regular Panes $7 → Triple Sliders $35)
- Mode toggle: In&Out vs Outside Only (÷2 × 1.10)
- Difficulty: Standard / Hard +15% / Very Hard +30%
- Address autocomplete via **Google Places API (New)** — see `reference_google_cloud_apis.md` for key + project info
- Saves as Odoo `sale.order` with 3 watermarks: `client_order_ref="🔶 QUOTE ONLY"`, `job_type="Quote"`, "QUOTE ONLY" tag
- Two save paths: pick from schedule → update existing Workiz-linked SO; walk-up → auto-create partner + new SO
- Edit flow: tap saved quote → loads back into form via JSON blob in line description (with legacy text-parser fallback)

DJ pivoted the architecture **mid-session** from "Render creates new draft SOs" to "Render updates existing Workiz-linked SOs (or creates fresh for walk-ups)" — leverages existing Phase 3/4 infrastructure. The duplicate-from-prior-SO `copy()` logic I built earlier in the session was ripped out.

## Activities module — major UX pivot

Built earlier in `project_activities_module.md` and `project_activities_unified_flow.md`. Key changes today:

- **Unified routing**: ALL activities open the detail modal first (shows every populated field)
- Specialized actions (follow-up SMS) become **buttons inside** the detail modal, not separate routing branches. Predicate `isFollowupTodo(t)` decides if the button appears.
- Detail-modal Mark Done button now has a **5-second undo grace period** — button morphs to "↶ Undo (5)" countdown, tap-again or close-modal cancels. Same pattern applied to follow-up modal's "Mark Done (no send)" button.
- Detail-modal field display now includes Summary, Type, Due, Linked-to, Model, Record ID, Activity ID, full note. `fieldRow()` helper auto-skips blanks.
- "Open Follow-Up Editor →" button (renamed from "Send Follow-Up SMS →" because the latter sounded like it sent immediately).

## Activity notes — link rules

Saved as `feedback_activity_notes_self_contained.md`:
- Memory files (Claude-local) → embed content directly, name file for Claude lookup
- Anything with a public URL → real `<a href>` anchor with descriptive text, never paste raw URLs

Linkified the 30 existing follow-up activities so the Workiz UUID is now a clickable link (`https://app.workiz.com/root/job/{UUID}/`). Backend `_strip_activity_html` now emits markdown `[text](url)` for anchors with distinct inner text; frontend `linkify()` handles markdown + plain URLs cleanly.

## Field Assistant — three-dots menu fix

Pre-fix: "today" rows had 4 menu items (Workiz, Odoo SO, Property, Add Note); other days only had 2. Cause: `/api/upcoming` didn't return `partner_id` or `workiz_uuid`. Added them. Now all days show all 4.

## Field Assistant — clicking other-day rows

DJ asked. Decision: leave it (other-day clicks do nothing) until we add something to the active panel that's actually useful for non-today jobs. Active panel has timer + payment buttons that don't apply to future jobs.

## Stats tab — daily drill-down

Stats page sales rows are now tappable. Tap a day → modal shows that day's jobs (time, customer, status, $) with totals. Backend endpoint `/api/sales/day?date=YYYY-MM-DD`.

## Payment History button on open job screen

New "📜 Payment History" button below the Record Payment button. Tap → modal lists all `account.payment` records for the customer (date, method, memo, $). Walks Property→Contact for partner resolution. Backend endpoint `/api/customer/payment_history?partner_id=N`.

## Last-payment-method preselect — diagnosis

Verified the code is working correctly end-to-end (Gary Marsalone partner 24153 → contact 23031 → today's $85 Zelle payment → returns 'zelle'). The reason it "doesn't seem to work" is that most customers have **no `account.payment` records in Odoo yet** — only a handful from invoices DJ has processed in Odoo. The accounting migration (Phases 4-5) will populate this. DJ chose Path A (wait for migration, no Workiz API fallback). Saved as `project_preselect_coverage_check.md` with a 2-week reminder activity (#66) for coverage check.

## Google Cloud API key

Saved as `reference_google_cloud_apis.md`:
- Project: "Odoo" (id `gen-lang-client-0790905441`), billing already enabled
- API key "API key Render": `AIzaSyA2D5Sd7IPOi2h65G4pew7QuXAko3bOO60`, restricted to `wsc-field-assistant.onrender.com/*`, allowed APIs: Places API (New) + Maps JavaScript API
- Weather API also enabled (DJ has a future idea — not yet wired)
- Key is embedded in `quote.html` as a constant — safe because of referrer restriction

## Apps launcher discussion

Discussed but **not built**. DJ shared his Android folder showing 17 native apps. We agreed: a single ⚡ Apps button on dashboard opens a tile grid of web-linkable apps (Workiz, Odoo, Calendar, Gusto, Thumbtack Pro, Angi Pro, Yelp Biz, Nextdoor, Home Advisor, Calendly). Native-only apps (Multi Counter etc.) can't be deep-linked. Deferred — DJ went deeper on the quote tool instead.

## Activities created (Odoo mail.activity)

- **#66** — "Verify field-assistant payment preselect coverage" (initially due 42 weeks out, then DJ corrected to 2 weeks → 2026-05-13)
- **#67** — "Build Phase 4 auto-clear: drop QUOTE ONLY watermarks when Workiz status leaves Quote" (due today)
- **#68** — "Set up Workiz 'Quote' substatus + automation webhook for instant Render sync" (due today, DJ-blocked)
- **#69** — "Build 'Push to Workiz' button" (due today, DJ-blocked on target field decision)

All notes self-contained per the activity-note rule. GitHub URLs are real `<a href>` links.

## Files touched

- `Saunders Render App/routers/owner/dashboard.py` — many edits (quote endpoints, /api/upcoming address+phone, /api/sales/day, /api/customer/payment_history, _strip_activity_html markdown anchors)
- `Saunders Render App/static/owner/quote.html` — entire new file
- `Saunders Render App/static/owner/field.html` — list-modal CSS, Payment History button + handlers, three-dots menu fix (already deployed earlier)
- `Saunders Render App/static/owner/activities.html` — unified detail modal, follow-up button bridge, 5s undo grace, linkify markdown support
- `Saunders Render App/static/owner/index.html` — added Window Quote tile
- `Saunders Render App/static/tech/index.html` — added Window Quote tile
- `Saunders Render App/routers/tech/jobs.py` — added /tech/quote route

## Patterns + gotchas captured

- `feedback_activity_notes_self_contained.md` — embed runbooks; real `<a href>` for URLs
- `project_activities_unified_flow.md` — detail-first routing pattern
- `reference_google_cloud_apis.md` — Google Cloud project + API key registry
- `project_quote_tool.md` — full quote-tool reference (read first when editing /quote)
- `project_preselect_coverage_check.md` — pending coverage check post-accounting-migration
- `feedback_github_deploy_python_fallback.md` — when bash+powershell base64 chokes, use Python (this session)

## DJ-blocked items waiting for action

1. Create Workiz "Quote" substatus + automation (activity #68)
2. Confirm target Workiz field for "Push to Workiz" button (activity #69)
3. Decide whether Phase 4 auto-clear (activity #67) builds now or later

---

## Later in the session — additional polish

### Activities organization v2 — sections + type filter + search + snooze

DJ's complaint: activities list felt like an "out-of-control inbox". Built:
- **Search bar** at top with X clear button (case-insensitive on summary/customer/type/note)
- **Type filter pills**: All / Follow-Ups / To-Dos
- **Date-based sections** with colored dots + count badges:
  - 🔴 Overdue / 🟠 Today / 🔵 This Week / ⚪ Later
  - All sections start expanded; user toggles persist for the session (DJ pushed back on Later being collapsed-by-default — preferred all open)
- **Snooze chips** in detail modal — 4 options: +1 day / +3 days / +1 week / +1 month
- New backend endpoint `/api/todos/snooze` clamps past dates to today + N (so a 30-day-overdue activity snoozed 1 week becomes 1 week from today)

Filter bar hidden when on Done sub-tab.

### Quote tool list filter — bug fix

Originally filtered by `job_type='Quote'` — caught 18 historical Workiz Quote jobs going back to 2022 that DJ never created in the Render tool. Narrowed to `client_order_ref='🔶 QUOTE ONLY'` (only set by Render tool, cleared on conversion). See updated `project_quote_tool.md` for the canonical filter.

### Quote tool post-save success card

Replaced auto-reset behavior with a deliberate success card showing:
- Big total amount
- ✅ Saved/Updated — SO name
- "📊 View in Odoo" link (`https://window-solar-care.odoo.com/odoo/sales/{so_id}`)
- "📋 View in Workiz" link (only if `x_studio_x_workiz_link` populated — i.e., Workiz-linked SOs)
- "+ New Quote" button to clear and start over

`/api/quote/save` and `/api/quote/update` both now return `workiz_link` in the response.

### Field Assistant — 10-Day tab removed

Right office panel: dropped the 10-Day tab (redundant with the future days visible on the left field panel). Now: Stats / Customers / Voice only. `/api/upcoming` endpoint kept — still used by the Quote tool's "Pick from scheduled jobs".

### Bugs caught + memories

- Flegel SO S00107 walk-up save was missing watermarks — possibly a deploy-timing race. Patched manually. If the issue recurs on future saves, dig into `_apply_quote_watermark` or look for an Odoo automation that's stripping `client_order_ref` on draft SOs.
- The list-filter bug (job_type='Quote' too broad) is a good general lesson: when picking a uniqueness signal for a "did our tool create this?" filter, prefer the watermark we explicitly set rather than a field that could be set by other systems too.

### Activity #66 deadline correction

DJ asked for it 42 weeks out, then immediately corrected to 2 weeks. Updated to 2026-05-13. Future-self lesson: when DJ gives a relative date and follows up with a correction, treat the correction as authoritative without asking for re-confirmation.

---

### Apr 30 evening session — UX polish, GPS Phase 1, Re-engagement rename, regression guard, gate code, stale SOs
`session_apr30_evening_summary.md`
> Long session. Photo flow polish (Snap button, retry, save to WSC Jobs folder via File System Access API). Activities Mark Done fixes + Done tab + Reopen. record_check_payment v2 (multi-SO + tip detection + empty-SO error). Phase 5 "Follow-up" renamed to "Re-engagement" everywhere. New Render Claude tools: add_link_to_todo, delete_workiz_job. Stats drill-down + Stale SOs page with WZ+Odoo pills. Gate code on active job view. GPS Phase 1 logger (collect pings while clocked in; per-person model with redundancy). REGRESSION INCIDENT: another Claude Code chat pushed a 3565-line dashboard.py over the live 5842-line version, wiping 2277 lines. Fixed + added regression guard at 3 layers (github_push_file tool, safe_deploy.py CLI, CLAUDE.md warning).

## Big strokes

### Activities (mail.activity / project.task work)
- Mark Done now keeps DJ on the Open list (was jumping to Done) — `field.html`/`activities.html` updated
- Mark Done button text resets per activity (was sticking on "✅ Done")
- `/api/todos/done` now reads BOTH mail.activity AND project.task (commit 19854da0); new `/api/todos/reactivate` endpoint with Reopen button on every Done card
- The 3 Mark Fredricksen project.task records that were invisible → now visible

### Linked AWP PO #70 + renamed P00002 → P00101
- Activity #70 "Order screen material" now has a clickable link to the AWP PO (was empty note)
- PO renamed from P00002 to P00101 (DJ wanted the new sequence start to apply); sequence bumped to next=102 to avoid collision
- Activity note updated to match

### New Render Claude write tools
- **`add_link_to_todo(todo_query, url, label?, source?)`** (commit 97f8e7d5) — append a link to an existing to-do. Searches both mail.activity (summary) and project.task (name). CLARIFY when ambiguous.
- **`delete_workiz_job(uuid, partner_name?)`** (commit c4c2e4ff) — PERMANENT delete: Workiz API + Odoo SO unlink + project.task cleanup. **Blocks if invoice linked** to the SO. Order: tasks → SO → Workiz (Workiz fires last so Odoo failures abort safely).

### record_check_payment v2 (commit 0e6726af / 1645e679)
- **so_id is now optional** — when omitted, walks Contact↔Property partners and finds all open invoiceable SOs (state in [sale,done] AND invoice_status='to invoice')
- 0 SOs → friendly error
- 1 SO → proceeds
- >1 SOs → CLARIFY message listing them
- **Tip / amount-mismatch detection**: BLOCKS unless `acknowledge_mismatch:true` (or `tip:true`). Response on success includes a `⚠ TIP REMINDER` line if mismatch was acknowledged ("don't forget to add the tip to Workiz")
- **Empty-SO clean error** instead of opaque "No items available to invoice" Odoo trace
- **`_force_lines_deliverable(so_id)`** helper writes qty_delivered=qty_ordered on real lines before invoicing — fixes products with `service_policy='delivered_timesheet'` failing without timesheets logged

### Property partner naming quirk discovered
- Betsy Justice has 3 partners: Contact `Betsy Justice` + Property `"Betsy Justice, 255 E Avenida Granada"` + Property `"47446 Rabat Dr"` (no name on the 2nd!)
- Name-search "betsy" missed the Rabat property → wrong SO got charged
- Fix: always walk parent_id+child_ids, never name-match
- Saved as `project_property_partner_naming_quirk.md`

### Photo flow — three improvements
1. **📸 Snap Photo button** on active job (commit b76b9495) — uses `capture="environment"` to bypass the gallery chooser, opens camera direct
2. **Auto-retry** on weak signal (commit 3d1748d7) — 3 attempts, exponential backoff (1s/2s/4s)
3. **Saves a copy to phone Downloads OR a user-picked folder** (commit ec91e94d) — File System Access API. DJ picks "WSC Jobs" folder once, then silent writes thereafter. Android Gallery auto-creates the album.
- **Filename rename**: from `17775678…jpg` (device timestamp) to `WSC_JeffO_2026-04-30_165107_1.jpg` (customer + date + time + seq) — same name on phone and Odoo

### Pull-to-refresh disabled site-wide
- All 7 HTML pages got `overscroll-behavior-y: contain` so DJ's scroll gestures don't trigger Chrome's full-page reload
- field.html refresh interval kept at 5min (real fix was the gesture)

### Stats day drill-down
- New `WZ` + `S0xxxx` pills under each row (commit ae76650c) so DJ can investigate from the day-list view

### Stale SOs cleanup page
- New `/owner/stale_sos` page (commit 3c72fcc8) — filterable by year + Workiz status + customer search; rows show customer / date / job type / amount + WZ + Odoo pills
- Tile on owner hub (red-bordered 🧹 Stale SOs)
- 320 stale SOs found ($56.7k aggregate); biggest cohort = 2025 "Submitted" (190 SOs / $30k)

### Gate code on active job (commit e446d8ed)
- Between address and Navigate button: `🔑 Gate: 1234` (amber) when set, or `NO GATE CODE` (red caps) when empty
- Backend: `gate_code` added to `/api/dashboard` schedule response
- Source: `x_studio_x_gate_snapshot` on sale.order

### Re-engagement terminology rename
- Phase 5's customer cycle reminder titled "Follow-up: X — Y" → "Re-engagement: X — Y" (commit fb5de5b6)
- Phase 5 chatter prefix "[Phase 5] Re-engagement Task created..."
- create_todo lost the `[Render] Follow-up:` prefix — now uses DJ's actual phrase as title; partner_id is OPTIONAL (personal todos no longer require a customer)
- Render Claude system prompt: "follow up with X" → always create_todo (personal); "Re-engagement" reserved for Phase 5
- isFollowupTodo predicate matches both new "re-engagement" + legacy "follow up"/"reactivation" keywords
- DJ renamed Workiz SubStatus "Follow Up Trigger" → "Re-engagement Trigger" + JobType "Follow Up Lead" → "Re-engagement Lead" — Render constants updated to match (commit 02190a29)
- **Task #25 closed as obsolete** — no need to extend SMS to project.task; clean split now: mail.activity (legacy SMS only) vs project.task (cycle reminders + personal todos)

### Manage Shifts backend (commit 390bfdd2)
- Frontend was already deployed but the 5 backend endpoints (/api/payroll/shifts list + shift/create + shift/update + shift/delete + gusto_export) had never been built → "Error: load failed"
- Added all 5 endpoints + `_force_lines_deliverable`-style helpers (`_shift_id`, `_split_shift_id`, `_utc_to_pt_str`, `_pt_str_to_utc_iso`, `_round_quarter`, `_format_shift_for_ui`)
- Backed by the SAME ir.config_parameter JSON storage (no schema change)
- Surfaces the open shift (clocked-in but not out) so DJ sees live work-in-progress
- Edit-then-update on the open shift converts it to a closed shift in the JSON log + clears the clockin marker

### GPS Phase 1 — data collection (commits 38c3030a + 6d4b5d21 + 466c97d1)
- New Odoo Studio model `x_gps_ping` (id 1024): employee_id, timestamp, lat, lng, accuracy, shift_id, active_so_id, active_task_id
- POST `/api/payroll/gps_ping` endpoint
- `gps_tracker.js` shared module (window.WSC_GPS.start/stop/isActive) — used by timeclock.html AND field.html
- timeclock.html: starts watcher in updateClockUI when clockedIn=true
- field.html: polls /api/payroll/status every 60s + on visibilitychange → starts/stops watcher based on the same source-of-truth clock state
- New `/api/whoami` endpoint resolves access_code → employee_id for field.html
- Throttle: 5min OR 100m moved (whichever fires first). Battery-friendly.
- Two-person scenario: both phones ping independently with own employee_id; phase 3 will create per-person timesheets. Bonus: redundancy if one phone dies (phase 2 auto-detect "rode together today" via overlap)
- Tasks #39/40/41 queued for Phases 2-4

### REGRESSION INCIDENT — 2277 lines wiped, restored
- 22:47 UTC, commit `a6bb406e` by `windowandsolarcare@gmail.com` replaced dashboard.py with a 3565-line version (was 5842 lines), wiping Manage Shifts CRUD, GPS endpoints, Stale SOs, whoami, todos/reactivate
- Cause: a different Claude Code chat had a stale local copy and pushed it
- Restored from my (current) local in commit `ad98b65c`

### Regression guard — three layers (commit 41351838 + safe_deploy.py + CLAUDE.md update)
1. **Render Claude `github_push_file` tool** — fetches current GitHub version, refuses if new content drops >100 lines OR >25% bytes. Override with `acknowledge_regression: true`.
2. **`C:\Users\dj\safe_deploy.py`** — same guard for any Claude Code chat. CLI: `python safe_deploy.py --repo X --path Y --local Z --msg "..."`. Use `--force` to override.
3. **CLAUDE.md updated** with mandatory pre-push checklist + warning about the incident at top of Deployment section. Memory note `feedback_regression_guard_pushes.md`.

## Files touched tonight (Saunders Render App repo)

- `routers/owner/dashboard.py` — many edits (final ~290k bytes / ~5900 lines)
- `static/owner/field.html` — Snap Photo, retry, folder picker, gate code display, GPS watcher, refresh tweaks, pull-to-refresh disabled
- `static/owner/timeclock.html` — Manage Shifts integration with shared gps_tracker.js, pull-to-refresh disabled
- `static/owner/activities.html` — Mark Done UX, Reopen button, isFollowupTodo predicate updated, pull-to-refresh disabled
- `static/owner/stale_sos.html` — NEW page
- `static/owner/quote.html` — pull-to-refresh disabled
- `static/owner/reactivation.html` — pull-to-refresh disabled
- `static/owner/index.html` — Stale SOs tile + pull-to-refresh disabled
- `static/owner/gps_tracker.js` — NEW shared module
- `static/tech/index.html` — pull-to-refresh disabled

## Files touched tonight (Odoo-Migration repo)

- `1_Production_Code/zapier_phase5_FLATTENED_FINAL.py` — "Follow-up" → "Re-engagement" titles + chatter messages

## Memory files added/touched

- `project_invoice_qty_delivered_gate.md` — NEW (the Betsy Zelle case)
- `project_property_partner_naming_quirk.md` — NEW
- `project_reengagement_flow.md` — NEW (replaces project_followup_flow.md)
- `project_gps_timesheet_autofill.md` — NEW
- `feedback_regression_guard_pushes.md` — NEW
- `reference_render_claude_write_tools.md` — extended with add_link_to_todo, delete_workiz_job, record_check_payment v2, create_todo v2

## Open future tasks (parked)

- **#17** Workiz Quote substatus + webhook for instant sync (DJ-blocked on Workiz substatus + automation creation)
- **#39** Phase 2: Cluster pings into stops + match to customer properties
- **#40** Phase 3: Auto-create per-person timesheet entries from matched stops + review UI
- **#41** Phase 4: Mileage logs + native Android wrapper for background GPS

## DJ's manual / blocked items

1. Workiz "Quote" SubStatus + automation webhook for the Quote workflow (still blocked since Apr 30 morning)
2. Workiz auto-text rule for JobType=Quote (don't text customers about coming for a quote visit)
3. Workiz cell-phone area code spec for `Re-engagement Trigger` SubStatus rename — verify the automation still fires on the renamed substatus

## Things to verify after Render redeploy

- Time Clock → Manage Shifts loads (was failing for both DJ and Danny)
- Active job view shows gate code or NO GATE CODE
- Field Assistant pull-to-refresh is dead
- Stale SOs page accessible at /owner/stale_sos
- 📸 Snap Photo button works on active job

---

### Apr 29-30 evening session — PO infrastructure + Render Claude write tools + quote workflow finalized + project.task fix
`session_apr30_summary.md`
> Big session. Built end-to-end vendor PO flow (Active Window Products imported with 33 frame products, draft PO P00002, custom fiscal position + email template + aliases). Added 4 Render Claude write tools (create_purchase_order, send_purchase_order, convert_quote_to_job, push_quote_to_workiz). Locked the quote workflow architecture (don't touch Phase 3/4; watermarks distinguish quotes; manual Workiz handoff at acceptance). Fixed two bugs: /api/todos missed project.task records (50+ Phase 5 follow-ups invisible) + 30-row limit hid far-future tasks (Bud Piraino 2027-04-25).

## Big strokes

### Vendor PO infrastructure — Active Window Products end-to-end

Built fresh tonight. Active Window Products is now a fully configured vendor in Odoo:

- Vendor `res.partner` 26936, `ref='55145'` (AWP Customer ID), `supplier_rank=1`
- Address: 5431 San Fernando Road West, Los Angeles, CA 90039
- **Tax-exempt** via custom `account.fiscal.position` "Resale - Tax Exempt" (id 5) — auto-applied to all POs from AWP
- Email field is comma-separated → `j.gutierrez@activewindowproducts.com, v.campos@activewindowproducts.com` so Odoo's "Send by Email" auto-sends to both
- Two child contacts: Jaime Gutierrez (id 26937, Sales/Order) + Valerie Campos (id 26938, Customer Service Manager)
- 33 frame products imported (5/16 Screen + Lip + 1×5/16 + 3/8 Slider variants × all colors) with `product.supplierinfo` linking back to AWP — naming pattern `AWP-{sku}` (e.g. AWP-1017AL = 5/16 Almond Screen Frame)
- Foot UOM (id 20) used as `uom_id` on frame products
- Two custom fields on `res.partner`:
  - `x_default_po_template_id` — points to the vendor's preferred PO email template (AWP → template 49 "AWP Order Request")
  - `x_aliases` — comma-separated short names DJ uses (`Active, AWP, Active Window, Active Window Products`)
- Custom mail.template id 49 "AWP Order Request" with DJ's preferred Part No / Qty / Est. Price layout, customer ID 55145, Tax Exempt note, Window & Solar Care signature
- Both PDFs (Sec 1 components + Sec 11 doors) attached to vendor record as Odoo `ir.attachment` (also surface in Odoo Documents app since that module is installed)

PO sequence renumbered: next PO = **P00101** (was P00003).

Sample PO `P00002` exists (100 ft of 1017AL @ $1.017/ft = $101.70, draft, tax cleared).

See `project_awp_vendor_setup.md` for the full reference + memory rules.

### Render Claude write tools — 4 new ones

Wired into `Saunders Render App/routers/owner/dashboard.py`. All preview-first via the existing WRITE_TOOLS confirmation pattern.

| Tool | Voice triggers | What it does |
|---|---|---|
| `create_purchase_order` | "PO with Active for 100 ft 5/16 almond" / "order from AWP" | Resolves vendor by name+aliases, resolves products by SKU OR natural language ("5/16 almond" — restricted to vendor's catalog), creates draft PO. Returns CLARIFY message when ambiguous (e.g. "5/16 almond" matches Screen + Lip — DJ specifies). |
| `send_purchase_order` | "send PO P00101" | Reads vendor's `x_default_po_template_id` (or default), sends email via that template. AWP gets the custom format with Jaime+Valerie on TO. |
| `convert_quote_to_job` | "convert quote S00107" / "wrap up the Flegel quote" | Clears QUOTE ONLY watermarks (client_order_ref + tag), sets job_type from quote-line product (141→In&Out variant, 103→Outside Windows and Screens). Drops SO off the Saved Quotes list. |
| `push_quote_to_workiz` | "customer approved", "they accepted", "Bud's a go", "go ahead with Flegel's quote", "push the X quote to Workiz" | Reads quote SO + lines, prepends a [Render] block to Workiz JobNotes with priced line items, suggested JobType swap, scheduling reminder, status-change reminder. Only works when SO has a Workiz UUID. |

All four are in `WRITE_TOOLS` set so they get the confirmation flow. Each has a `describe_write_tool` preview block.

### Quote workflow architecture — locked

After deep discussion, settled on this design:

1. **Workiz job creation** with JobType=Quote, status=Submitted → Phase 3 creates draft SO in Odoo (current behavior — keep)
2. **DJ schedules the quote visit in Workiz** (status → trigger value with date) → Phase 4 fires, confirms SO normally, creates a regular `project.task` on schedule
3. **Quote visit task looks/behaves like every other job task** — same code path. Distinguishing signal is the watermarks (job_type=Quote + client_order_ref="🔶 QUOTE ONLY" + QUOTE ONLY tag), NOT the SO state
4. **At customer site, DJ uses Render Quote Tool** → "Pick from scheduled jobs" finds the SO (now visible because /api/upcoming includes draft+sale states) → enters line items → save (zeroes existing, adds quote line)
5. **Customer accepts** → DJ taps "📲 Approve & Push to Workiz" on success card OR voice-says "customer approved" → `push_quote_to_workiz` fires → Workiz JobNotes gets [Render] block with line items + 4-step checklist (add line items, change JobType, set date, change status)
6. **DJ does the manual Workiz updates** following the checklist
7. **Phase 4 fires on status change** → syncs new line items + date_order, confirms SO if not yet confirmed
8. **(Optional) DJ runs `convert_quote_to_job`** to clear watermarks → SO drops off Saved Quotes list

**Why this architecture (not gap A/B):** DJ was concerned about modifying Phase 4 — load-bearing pipeline, risk to normal jobs. By using the watermarks instead of SO state to distinguish quotes, we avoid touching Phase 3/4 entirely. Tasks for quote visits use the SAME code path as all other jobs (same look, same allocated times, same titles).

**One Workiz config DJ owes himself:** disable customer auto-text when JobType=Quote so the customer doesn't get "we'll arrive to clean your windows..." on a quote visit. JobType filter in the Workiz automation rule.

### Critical bug fix — /api/todos missed project.task records

DJ reported: 3 follow-ups for Mark & Sarah Fredricksen show in Odoo /odoo/to-do but not in Render Activities. Root cause:

- Render's `/api/todos` was only reading `mail.activity`
- Render's `create_todo` tool writes to `project.task` (because Odoo's "To-do" app uses that model with `project_id=False`)
- Phase 5's "On Demand" path also writes to `project.task` (despite an outdated docstring claiming `mail.activity`)
- So 50+ project.task to-dos were invisible in Render

Fix (commit 668d619f):
- `/api/todos` now reads BOTH models, returns merged list with a `source` field (`'activity'` or `'task'`)
- `/api/todos/snooze` and `/api/followup/markdone` accept `source` param to know which model to write to
- Frontend caches `source` per todo and passes it back on Mark Done / Snooze
- `isFollowupTodo()` returns false for `source='task'` — task records can't use the SMS follow-up flow yet (depends on `x_followup_workiz_uuid` field on mail.activity)

See `project_todo_models_in_odoo.md` for the full breakdown.

### Second bug — 30-row limit hid far-future tasks

DJ invoiced Bud Piraino (12-month "On Request" frequency). Phase 5 created task #334 due 2027-04-25. DJ couldn't find it in Render. Root cause: my `/api/todos` query had `limit=30` per source; Bud's deadline was past position 50 in date-asc order.

Fix (commit c9f64d11): limit raised 30 → 250 per source. At DJ's current ~50 todos, no perceptible load impact (~200-500ms extra at most, ~100KB more over the wire).

### Phase 5 docstring lie — fixed

Phase 5's top docstring claimed "ON DEMAND: Creates follow-up reminder in Odoo (mail.activity only)" but the actual code at line 591 uses `project.task`. Fixed (commit 85129602 in Odoo-Migration repo).

The 30 historical "Follow-up: <Name>" mail.activity records appear to be from an older Phase 5 version (before it switched to project.task). Decision: leave them in mail.activity for now — they have access to the SMS Follow-Up flow which depends on `x_followup_workiz_uuid` storage. Once we extend that flow to project.task (task #25), we can convert them safely.

### Custom Studio fields added to Odoo

- `res.partner.x_default_po_template_id` (many2one to mail.template) — vendor's default PO email template
- `res.partner.x_aliases` (char) — comma-separated alternate names for natural-language matching

Pattern is reusable for any future vendor.

### Quote tool /api/upcoming surfaces drafts now

`/api/upcoming` previously filtered `state in ['sale', 'done']`. Now filters `state in ['draft', 'sale', 'done']` so Workiz-linked draft Quote SOs appear in the Quote Tool's "Pick from scheduled jobs" picker. Each job carries a `state` field so frontend can style/badge differently.

## Files touched tonight

- `Saunders Render App/routers/owner/dashboard.py` — many edits (4 new tools, 4 new endpoints, /api/todos extended, /api/upcoming includes drafts, helpers for vendor + product resolution)
- `Saunders Render App/static/owner/quote.html` — Approve & Push button on success card; opens Workiz in new tab on success
- `Saunders Render App/static/owner/activities.html` — pass `source` through to backend; suppress follow-up modal on task-source records
- `windowandsolarcare-hash/Odoo-Migration/1_Production_Code/zapier_phase5_FLATTENED_FINAL.py` — docstring fix (project.task, not mail.activity)

## Activities on DJ's todo list — actionable status

- **Activity #66** — Verify preselect coverage post-accounting-migration (due 2026-05-13). Self-contained runbook in note.
- **Activity #68** — Set up Workiz "Quote" substatus + automation webhook (DJ-blocked — DJ creates substatus in Workiz, then ping for Render endpoint). Spec'd in task #17.
- **Activity #70** — Order screen material (due 2026-05-01).
- **Activity #71** — Pay Younger Felix the balance (due 2026-04-30).

Activity #67 (Phase 4 auto-clear) and #69 (Push to Workiz button) — both COMPLETED tonight (closed in Odoo with feedback note).

## Open future tasks (parked, ready to execute when DJ green-lights)

- **Task #17** — Workiz Quote substatus + webhook for instant sync (DJ-blocked on Workiz substatus + automation creation)
- **Task #25** — Extend SMS Follow-Up flow to project.task records (then convert the 30 historical mail.activity follow-ups to project.task for unified model)

Both have spec-grade descriptions — files, functions, acceptance criteria, blocker breakdown.

## DJ-blocked items still waiting

1. **Workiz "Quote" SubStatus + automation webhook** — DJ creates substatus + automation in Workiz UI, then I wire the endpoint
2. **Workiz auto-text rule for JobType=Quote** — DJ filters the existing customer-confirmation auto-text so it doesn't fire on quote visits
3. **Active Window Products** — actual production use of the new PO flow (verify Bud's frame color tomorrow before sending P00102, etc.)

## Memory files added/touched tonight

- `session_apr30_summary.md` — this file (covers full session)
- `project_awp_vendor_setup.md` — extended with x_default_po_template_id, x_aliases, custom fiscal position, all 33 products, AWP Order Request template id 49, comma-separated email rule
- `project_todo_models_in_odoo.md` — NEW: explains mail.activity vs project.task, why create_todo writes to project.task, the bug-fix pattern
- `project_quote_tool.md` — Saved Quotes filter narrowed to client_order_ref watermark (was too broad with job_type='Quote')
- `feedback_activity_notes_self_contained.md` — extended with the "always real `<a href>` for URLs" rule
- `reference_supplier_pricing.md` — extended with Sec 1 PDF + 33 imported products
- `reference_google_cloud_apis.md` — Google Cloud project + API key registry
- `feedback_github_deploy_python_fallback.md` — fallback for the bash+powershell base64 issue

---

### Session 2026-05-03 Summary
`session_may03_summary.md`
> Activities edit modal, sync fixes (empty items / date_order / name lookup), Render Claude tool fixes, Zelle prefix match, cron rescheduled to 4am, CRON_SECRET fix

## What was built / fixed

**Activities Edit Mode**
- `/api/todos/update` POST endpoint — edits summary/date_deadline/note on mail.activity or project.task
- activities.html detail modal: Edit / Save / Cancel buttons with inline fields

**_sync_so_with_workiz() fixes (dashboard.py)**
- Empty Workiz Items bug: default lines_match=True; only compare when workiz_active is non-empty
  Was causing cancel→delete all lines→confirm → zero-line SO → invoice failure (Linda Lusk root cause)
- date_order restore: write workiz_date back AFTER action_confirm (confirm always wipes it)
- _find_so_by_identifier(): try SO name lookup first; numeric ID only if no leading zero

**Render Claude Tools**
- sync_so_verify + process_payment_with_sync: removed RENDER_BASE_URL HTTP self-call pattern
  Both now call internal functions directly (_find_so_by_identifier, _sync_so_with_workiz, _execute_payment)
- Sync confirmation prompt now shows customer name + amount

**Zelle CSV matching**
- _fuzzy_name_match(): prefix check on first names — GREGORY.startswith(GREG) = True
  Fixes Greg/Gregory, any nickname/formal pairs

**Cron infrastructure**
- CRON_SECRET was never defined → all /api/cron/* endpoints returned 500 NameError
  Fix: CRON_SECRET = os.environ.get('CRON_SECRET', 'wsc-daily-sync-2026') added to config block
  Deployed commit fb77684d
- Daily sync cron rescheduled 7:17am → 4:17am
  New CronCreate job f31a624d | self-renewal prompt updated to "17 4 * * *"
- SHARED_MEMORY.md monitor_tick/daily_sync_log URLs must include /owner/ prefix
  Correct: https://wsc-field-assistant.onrender.com/owner/api/cron/...

## Commits this session
- 1ff8965 — activities.html edit mode
- 71f3edb — timeclock.html 2-week default (redeployed)
- 25c7190b — empty Workiz Items fix
- 3a781941 — RENDER_BASE_URL fix (direct function calls)
- efcf16fa — date_order restore after action_confirm
- d1a16e0e — Zelle prefix first-name match
- fb77684d — CRON_SECRET constant added

---

## Reference
*9 file(s)*

### API Access Levels — Odoo vs QuickBooks vs Workiz
`reference_api_access_levels.md`
> Comparison of what Claude can actually do in each system — important for knowing what's possible when DJ asks for something

## Odoo — Virtually Unlimited Access
- Connects via JSON-RPC and XML-RPC APIs
- Every model, every field, every record is accessible
- Can read, create, edit, and delete anything
- Covers: invoices, journal entries, contacts, sales orders, tasks, bank statements, assets, reports, accounting config, chart of accounts, payment journals, bank feeds, activities, documents — everything
- If Odoo can do it through its UI, Claude can do it through the API
- Only exceptions: things requiring physical browser interaction (OAuth logins, file uploads via browser dialog)
- **Bottom line: DJ can ask Claude to do anything in Odoo and expect it to be possible**

## QuickBooks — Very Limited
- Access only through the QB MCP (~8 tools)
- Reporting surface only — not a full API
- Can pull P&L and cash flow summaries, import transactions, update company profile
- Cannot: read individual transactions, edit/delete records, access balance sheet, drill down into categories, reconcile, access vendor/customer lists
- **Bottom line: QB MCP is good for a quick P&L summary only. Not useful for data migration or granular work.**

## Workiz — Moderate but IP-Restricted
- Full Workiz API exists with job CRUD endpoints (create, read, update, delete)
- IP-restricted — blocks calls from local machines (403 Forbidden)
- Claude can only reach Workiz by proxying through a temporary Odoo server action
- Covers: jobs, clients, some custom fields, job status updates
- Does NOT cover: payment history endpoints, financial reporting, full client history
- Rate limit: ~30 calls before HTTP 429 — must sleep 15-30 seconds between batches
- Auth secret required in every URL: `?auth_secret=sec_334084295850678330105471548`
- **Bottom line: Claude can read and write Workiz jobs but it's indirect and rate-limited. Payment history comes from CSV exports, not the API.**

## Practical Implication
When DJ asks "can you do X?" — the answer is almost always yes if X involves Odoo. For QB or Workiz, the answer depends on whether the specific operation is supported by their limited interfaces.

---

### Google Cloud project + API keys for Window & Solar Care
`reference_google_cloud_apis.md`
> DJ has a Google Cloud project ("Odoo", id gen-lang-client-0790905441) with billing enabled. API keys live under APIs & Services → Credentials. Each key is restricted by HTTP referrer to keep it safe to embed in frontend HTML.

DJ's Google Cloud project for W&SC integrations:

- **Account:** `windowandsolarcare@gmail.com`
- **Project name:** Odoo (yes, confusing — predates the Odoo migration project, was already there)
- **Project ID:** `gen-lang-client-0790905441`
- **Project number:** `786167717152`
- **Billing:** enabled (required for Maps Platform). $200/month free credit covers normal usage.

## Enabled APIs (as of 2026-04-29)

- **Places API (New)** — used by `/owner/quote` address autocomplete
- **Maps JavaScript API** — enabled but not yet integrated (available if we want to embed actual maps)
- **Weather API** — DJ enabled this for a future idea (not yet wired)
- **Gemini API** — pre-existing from earlier work

## API keys

### "API key Render"
- **Key:** `AIzaSyA2D5Sd7IPOi2h65G4pew7QuXAko3bOO60`
- **Application restriction:** HTTP referrer — only `https://wsc-field-assistant.onrender.com/*` can use it
- **API restriction:** Places API (New), Maps JavaScript API
- **Where used:** `Saunders Render App/static/owner/quote.html` — embedded as `GOOGLE_PLACES_KEY` constant
- **Safe to embed in frontend** because the referrer restriction means a leaked copy can't be abused from another domain.

### "Odoo" (pre-existing)
- Used for Gemini API, possibly other older integrations.
- Don't reuse for new Maps/Places work — make a dedicated, narrowly-scoped key per use case.

## Pattern for adding a new Google API integration

1. Enable the API in console.cloud.google.com (search → Enable)
2. Create a NEW API key (don't reuse) → APIs & Services → Credentials → Create credentials → API key
3. Restrict it to:
   - **Specific APIs only** (the ones the integration needs — never "all APIs")
   - **HTTP referrer** matching the deployed origin (e.g. `https://wsc-field-assistant.onrender.com/*`)
4. Save the key + restriction details in this memory file under "API keys"
5. For frontend use, embed in HTML/JS as a named constant. For backend use, store in env var on the server, never commit.

## Why per-use-case keys (not one shared key)

- Blast radius: if one integration leaks, only that key is compromised.
- Granular metering: each key's usage is visible separately in the Cloud Console → Metrics tab.
- Different referrer restrictions: Render production site needs `wsc-field-assistant.onrender.com`, but a local-dev integration needs `localhost:*`. One key can't be both narrowly-restricted and dev-friendly.

## Cost watch

- Places Autocomplete (New): ~$2.83 per 1000 sessions. DJ does ~5 quotes/day = 150/month = ~$0.42 — entirely under the $200 free credit.
- Maps JavaScript API map loads: ~$7/1000. Free tier covers thousands per month.
- If a notification hits about hitting limits, check Console → Billing → Reports for which API.

---

### PDF Reading Workaround (Windows)
`reference_pdf_reading.md`
> Poppler is installed; Read tool can't use it directly — convert to PNG first, then Read

Poppler is installed at `C:\Users\dj\poppler\poppler-24.08.0\Library\bin\pdftoppm`.

The Read tool cannot read PDFs directly on this machine (pdftoppm not in its PATH). Workaround: convert the PDF to PNG images using Bash, then Read the PNG.

**How to apply — use this exact pattern every time you need to read a PDF:**

```bash
"/c/Users/dj/poppler/poppler-24.08.0/Library/bin/pdftoppm" -png -r 150 -f 1 -l 2 "/c/path/to/file.pdf" "/c/Users/dj/tmp_pdf_page" && ls /c/Users/dj/tmp_pdf_page*
```

Then Read each PNG (e.g. `/c/Users/dj/tmp_pdf_page-01.png`), then delete temp files when done:

```bash
rm /c/Users/dj/tmp_pdf_page-*.png
```

**Notes:**
- `-f 1 -l 2` = pages 1 through 2. Adjust range as needed.
- Font warnings ("No display font for Symbol") are harmless — images still render correctly.
- Always clean up temp PNGs after reading.
- Installed 2026-04-15 via manual zip download (no admin rights needed).

---

### QuickBooks MCP — Capabilities, Limitations, and Setup Status
`reference_quickbooks_mcp.md`
> What the QB MCP can and cannot do, and the current profile configuration for Window & Solar Care

## MCP Tools Available (~8 total)
- `company-info` — returns company name and industry
- `profit-loss-quickbooks-account` — generates P&L report from QB data
- `cash-flow-quickbooks-account` — generates cash flow report
- `profit-loss-generator` — generates P&L from a provided CSV (not QB account)
- `cash-flow-generator` — generates cash flow from provided CSV
- `quickbooks-transaction-import` — imports transactions INTO QB
- `quickbooks-profile-info-update` — updates QB company profile (industry, state, name)
- `benchmarking-against-industry` — compares to industry benchmarks
- `benchmarking-quickbooks-account` — benchmarks from QB account data
- `industry-recommendation` — suggests industry classification

## What It CAN Do
- Pull P&L summary totals by category (income, expenses, net)
- Pull cash flow report
- Show monthly breakdown columns
- Import new transactions into QB
- Read company name and industry

## What It CANNOT Do (important limitations)
- Cannot retrieve individual transaction records — no list of invoices, no line-by-line payments, no customer names per transaction
- Cannot edit or delete existing QB transactions
- Cannot pull balance sheet
- Cannot access vendor lists, customer lists, or chart of accounts
- Cannot reconcile
- Cannot drill down into a category to see constituent transactions
- The P&L response is a 276K character JSON of monthly rollup columns — not transaction rows

## Current Profile Configuration (already set — do not re-set)
- **Company Name:** Window & Solar Care ✓
- **Industry:** Services to buildings and dwellings ✓
- **NAICS Code:** 561790 ✓
- **State:** CA ✓
- Set on 2026-04-15 — this persists in the QB MCP account

**Note:** The `profit-loss-quickbooks-account` tool requires `company-info` to be called first in each session to establish the connection before it will work.

## QB Financial Summary (pulled 2026-04-15, period 2020–2026)
- Total Income: $390,935
- Total Expenses: $214,159
- Net Operating Income: $176,759

## Why We're NOT Using QB MCP for the Migration
The MCP cannot export individual transactions. The actual Transaction Detail by Account CSV (downloaded directly from QB) is far more useful — it has 16,777 individual transaction rows going back to 2019. That CSV is the source of truth for expense history, not the MCP.

## QB MCP Use Cases Going Forward
Essentially none after Odoo accounting is live. Odoo will be the financial system of record. QB MCP may be useful occasionally for a quick sanity check during the migration transition period only.

---

### Render Claude write tools — what each one does + invocation rules
`reference_render_claude_write_tools.md`
> Catalog of all WRITE_TOOLS available to Render Claude in Saunders Render App. Each is in the WRITE_TOOLS set in dashboard.py and triggers a confirmation preview before execution. Use this when adding new tools or debugging which tool fires on a voice command.

**READ when adding a new write tool, debugging tool routing, or onboarding to the Render Claude codebase.**

## Pattern: every write tool has 4 wiring points

In `Saunders Render App/routers/owner/dashboard.py`:

1. **Implementation** in `execute_write_tool(tool_name, args)` — the actual Odoo/Workiz writes
2. **Preview** in `describe_write_tool(tool_name, args)` — the confirmation text DJ sees
3. **Schema** in `TOOLS = [...]` list — Anthropic native format with description + input_schema
4. **Membership** in `WRITE_TOOLS` set — tells the runtime to require confirmation

If any of those are missing, the tool either won't show, won't preview, or won't execute.

## Current write tools (as of 2026-04-30)

### Workiz writes
- `update_workiz_field` — write any field on a Workiz job + sync to SO snapshot if applicable
- `create_workiz_job` — make a new Workiz job (Phase 3-style)
- `duplicate_workiz_job` — copy an existing job with a new date (preserves all fields including gate code, pricing, notes — auto-finds source UUID from partner_id if not given)
- `mark_job_done` — set Workiz status=Done
- `delete_workiz_job` — PERMANENTLY delete Workiz job + cancel/unlink Odoo SO + delete linked tasks (added 2026-04-30 night, commit c4c2e4ff). **Blocks if any invoice is linked** to the SO. Order: Odoo tasks → Odoo SO → Workiz delete (Workiz fires last so Odoo failures abort cleanly). Phase 4 does NOT auto-clean Workiz deletes — this is the only tool that handles it.

### Odoo customer writes
- `update_odoo_contact` — patch any field on res.partner
- `post_odoo_note` — chatter post on a record
- `create_todo` — creates **`project.task`** with `project_id=False` (Odoo "To-do" app pattern). **v2 (2026-04-30, commit 1645e679)**: dropped the `[Render] Follow-up:` title prefix, made `partner_id` optional (omit for personal todos), schema only requires `note` + `days`. Title is DJ's actual phrase; partner_id auto-anchors when DJ names a real customer. System prompt rule: "follow up with X" → always create_todo.
- `add_link_to_todo` — append a clickable URL to an existing to-do (added 2026-04-30 night, commit 97f8e7d5). Resolves todo by ilike search on summary/name, handles BOTH mail.activity (writes `note`) and project.task (writes `description`). Returns CLARIFY when multiple match. Voice phrases: "link the AWP po to the order screen to-do", "attach this URL to the [name] follow-up", "stick this on activity #70".

### Odoo task/timer writes
- `start_task_timer` — Render-owned timer; bypasses Odoo's flaky native timer
- `stop_task_timer` — closes the timer + creates the timesheet entry (with GPS reverse-geocode for actual address)

### Odoo invoice/payment writes
- `record_check_payment` — creates invoice + registers payment + posts chatter; Phase 6 syncs to Workiz. **v2 (2026-04-30, commit 0e6726af)**: `so_id` is now optional — when omitted, walks Contact↔Property partners and finds all open invoiceable SOs. Returns CLARIFY if >1, friendly error if 0. **Tip detection**: BLOCKS when `amount != SO total` unless `acknowledge_mismatch:true` (or `tip:true`) is passed. On success with mismatch, response includes a TIP REMINDER for DJ to add the tip to Workiz manually. Empty SO returns clean error instead of opaque Odoo trace.

### General Odoo
- `odoo_write` — generic escape hatch for any model/method (write, create, unlink, action_*, run, message_post)

### GitHub
- `github_push_file` — push file to main branch with commit message

### Memory
- `update_shared_memory` — update SHARED_MEMORY.md on GitHub

### Render Quote Tool support (NEW 2026-04-29 / 2026-04-30)
- `create_purchase_order` — vendor PO with natural-language vendor + product resolution
- `send_purchase_order` — emails PO using vendor's `x_default_po_template_id` (or default)
- `convert_quote_to_job` — clears QUOTE ONLY watermarks + sets job_type from quote-line product
- `push_quote_to_workiz` — accepts customer-approval phrasing ("customer approved", "they accepted", "X is a go"). Prepends [Render] block to Workiz JobNotes with line items + 4-step checklist for DJ to complete in Workiz.

## Read tools (no confirmation, in READ_TOOL_MAP)

- `search_customers` — by name → partner_id, Workiz IDs, active SO info
- `get_customer_profile` — full contact profile from res.partner
- `get_job_details` — SO + tasks + Workiz refs for a partner
- `get_schedule` — jobs for a date
- `get_next_job` — next confirmed job from now
- `get_sales` / `get_sales_week` / `get_jobs_list` — sales aggregates
- `navigate_to` — generates Google Maps link
- `send_email` — Gmail draft (NOT a confirmation-required write because no business state is touched)
- `save_memory` / `delete_memory` — local memory key/value
- `odoo_query` — generic Odoo read
- `github_read_file` / `github_list_dir` — read GitHub repo
- `refresh_shared_memory` — re-pull SHARED_MEMORY.md

## Vendor + product resolution helpers (in same file)

- `_resolve_vendor_by_query(query)` — searches `res.partner` with `supplier_rank>0` matching name OR `x_aliases`. Returns dict (single best match) or None.
- `_resolve_product_for_vendor(vendor_id, part_query)` — three-pass match: (1) exact `product.supplierinfo.product_code`, (2) exact `product.product.default_code`, (3) keyword token match on product name restricted to vendor's catalog. Returns dict (unique match), list (ambiguous → caller asks for clarification), or None.

These are the helpers that make `create_purchase_order` accept "5/16 almond" and resolve it to AWP-1017AL.

## Adding a new write tool — checklist

1. Implement in `execute_write_tool` — return a string status message starting with `[ODOO]`, `[WORKIZ]`, `[GITHUB]`, etc.
2. Add a preview block in `describe_write_tool` — multi-line summary of what'll happen
3. Add schema entry in `TOOLS` list — name, description (be generous, give voice trigger phrases), input_schema with required fields
4. Add tool name to `WRITE_TOOLS` set
5. Test with a voice command — verify preview shows correctly, confirm fires execution

## Voice phrase rules (from session 2026-04-30)

DJ rarely says SKUs or technical terms. Tool descriptions should include 4-6 example phrases DJ might use, like the `push_quote_to_workiz` tool's description has:
- "customer approved the quote"
- "they accepted"
- "Bud's a go"
- "go ahead with [customer]'s quote"

Generic phrasing tells Claude when to fire each tool, even when DJ uses casual language.

## Related memory

- `project_quote_tool.md` — customer Quote Tool architecture
- `project_awp_vendor_setup.md` — AWP vendor record + custom fields
- `project_todo_models_in_odoo.md` — why create_todo writes to project.task
- `feedback_proactive_inefficiency_capture.md` — preview-first pattern philosophy

---

### Render MCP Server
`reference_render_mcp.md`
> Official Render MCP server setup — allows Claude Code to deploy, check logs, manage services directly

# Render MCP Server

**Added:** 2026-04-19
**Status:** Added to local config, needs API key + Claude Code restart to activate

## Setup
- Added via: `claude mcp add render --transport http https://mcp.render.com/sse`
- Config file: `C:\Users\dj\.claude.json` (project: Migration to Odoo)
- Official docs: https://render.com/docs/mcp-server
- GitHub: https://github.com/render-oss/render-mcp-server

## API Key
- Get from: render.com → avatar → Account Settings → API Keys
- NOT YET CONFIGURED — needs key entered after Claude Code restart

## What it can do
- Deploy services
- Check logs and deployment status
- Manage env vars
- Monitor service metrics
- Query Postgres databases

## Next step
1. Get API key from Render Account Settings
2. Restart Claude Code
3. Enter API key when prompted

---

### Render Claude tools architecture
`reference_render_tools_architecture.md`
> Where tools live, how they're structured, and how to add new ones

## File Location
`C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py`

## Tool Definition Structure

### 1. TOOLS list (line ~1962)
Array of tool definitions. Each entry:
```python
{
    "name": "tool_name",
    "description": "What the tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "integer"}
        },
        "required": ["param1"]
    }
}
```

### 2. WRITE_TOOLS set (line ~2496)
Set of tool names that require confirmation before execution:
```python
WRITE_TOOLS = {
    'tool_name_1', 'tool_name_2',
    ...
}
```

### 3. Tool handlers (line ~977+)
Series of `if tool_name ==` blocks that implement the tool logic:
```python
if tool_name == 'my_tool':
    param1 = args.get('param1')
    # do work
    return "Result message"
```

### 4. _describe_write function (line ~1895+)
Provides human-readable descriptions of what the tool will do (shown in confirmation):
```python
if tool_name == 'my_tool':
    return f"[SYSTEM] Do something\n  Details: {args.get('param1')}"
```

### 5. Tool dispatch (line ~2637+)
Checks tool name against handlers and executes.

## Adding a New Render Claude Tool — 5 Steps

1. **Add to TOOLS list** — name, description, input_schema
2. **Add to WRITE_TOOLS** (if it modifies data)
3. **Add handler** — `if tool_name == 'name':` block with logic
4. **Add description** — `if tool_name == 'name':` in _describe_write
5. **Push to GitHub main** — Render Claude loads tools on session start

## Natural Language Resolution Pattern

For tools that accept identifiers, use `_find_so_by_identifier()` helper (line ~5063):
- Tries numeric SO ID first
- Then SO name ("SO-2024-001")
- Then Workiz UUID
- **Finally: searches by customer name** and finds their most recent open invoiceable SO

This lets users say natural language like "sync Fred Jones open job" and the tool resolves everything automatically.

## Current Tools (as of 2026-05-01)

**Read-only (no confirmation):**
- search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job, get_sales, get_sales_week, get_jobs_list, navigate_to, send_email, save_memory, delete_memory, odoo_query, github_read_file, github_list_dir, start_task_timer, stop_task_timer, refresh_shared_memory

**Write tools (confirmation required):**
- update_workiz_field, update_odoo_contact, post_odoo_note, create_todo, mark_job_done, create_workiz_job, duplicate_workiz_job, record_check_payment, create_purchase_order, send_purchase_order, convert_quote_to_job, push_quote_to_workiz, add_link_to_todo, delete_workiz_job, odoo_write, github_push_file, update_shared_memory
- **NEW (2026-05-01):** sync_so_verify, process_payment_with_sync

---

### Sunday Jobs UUID Backup
`reference_sunday_jobs_backup.md`
> File location of the Sunday-tagged SO backup with Workiz UUIDs

All 506 Sunday-tagged SOs (with Workiz UUIDs) are backed up at:

- **Local:** `C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\4_Reference_Data\sunday_jobs_uuid_backup.csv`
- **GitHub:** `windowandsolarcare-hash/Odoo-Migration` → `4_Reference_Data/sunday_jobs_uuid_backup.csv`

Fields: SO_Number, Date, State, Customer, Workiz_UUID

---

### W&SC supplier pricing files — locations
`reference_supplier_pricing.md`
> Where DJ's Window & Solar Care supplier price lists live in his local Documents folder. Use these when DJ asks about screen pricing, screen-door pricing, or any other supplier cost questions.

DJ's W&SC supplier price lists are in `C:\Users\dj\Documents\Business\A Window and Solar Care\Supplies\<supplier>\`.

## Active Window Products

Folder: `C:\Users\dj\Documents\Business\A Window and Solar Care\Supplies\Active Window Products\`

- **Active Window 2025 Sec 1 Pricing - Window Screen Components.pdf** — saved 2026-04-29 from email upload `9f7db883-2025Sec1All040626.pdf`. 26 pages of **window screen component** pricing — raw frame extrusions, corners, splines, latches, clips, hardware. Pricing format: per-foot (or per-each), with 7 volume tiers (Standard L/T Carton → 25,000+). Finish codes: M/MF=Mill, A/AN=Anodized, AD=Adobe, AL=Almond, BL=Black, G/GR=Gray, T=Tan, W/WH=White, Z/BR=Bronze.
  - Frame stock by depth: 1-1/4" (1001), 1" (1002, 1003, 1025), 15/16" extruded (1004), 3/4" (1006, 1007), 3/8" slider (1019, 1005), **5/16" (1017)**, 1/4" (1008), 1/2" lip (1009), 5/16" lip (1010), 3/4" standoff (1013), 1/2" standoff (1014), 5/8" extruded standoff (1015)
  - Sample: 1017AL (5/16" Almond) = $1.017/ft single carton, $0.678/ft @ 1000-1999ft, $0.626/ft @ 10K-25K
  - Each frame line names matching corner + spline (e.g. 1017 → corner 1213M, spline .185)
- **Active Window 2025 Sec 11 Pricing - Screen Doors.pdf** — saved 2026-04-29 from email upload `3b3e6428-2025Sec11All_041926.pdf`. 19 pages of **sliding screen door** pricing (KD kits + assembled doors). Styles: Premier, Century, 1-3/4" Durango, Ateevo-Laguna. Sizes 30"-60" widths × 82" or 96" heights. Finishes: Clear Anodized / Dark Bronze Anodized / Painted (Adobe/Almond/Black/Bronze/Tan/White). Effective 4/16/2026.
  - Sample: Premier KD 30"×82" Clear = $165.27; Premier Assembled 60"×96" Bronze = ~$269
  - Premium screen-cloth upcharges: +$7 (Bettervue/Charcoal 18×14), +$22.50 (Fiberglass 20×20, Sun, Tuff), +$25 (Suntex 80% / Pet Screen)
  - SS roller upgrades: +$20-$24.50
- Other files in folder are application/credit-card forms (no pricing).

Email contact: orders@activewindowproducts.com  ·  Phone: (323) 245-5185  ·  Fax: (818) 246-5188

## Precision (PrecisionPLP.com)

Folder: `C:\Users\dj\Documents\Business\A Window and Solar Care\Supplies\Precision Screen CC App\Catalog\`

- **Window Screen Price List from Precision Catalog 2017.pdf** — 2017 (9+ years old, may be outdated). Has a useful **Window Screen W×H grid** (page 9): Almond/Bronze/Gray/White $33-$69, Mill $32-$68, sizes 1'6"×1'6" through 6'×6'. Includes vinyl pulltabs (2) + spring clips (2). Other sections cover frames, corners, spreader bars, fiberglass screening, hardware.
- **Price List from Precision Catalog 2017.pdf** — full price list (same vintage)
- **Precision Catalog 2017.pdf** — full catalog
- Section files: Section 8 Pet Accessories, Section 9 Screen Cloth, Section 10 Window Screen, Section 11 Tools

Phone: (909) 379-0123  ·  Fax: (909) 379-0169  ·  Toll Free: (866) 629-6636

## When DJ asks about supplier pricing

1. Active Window Products = screen DOORS (sliding patio doors)
2. Precision = window SCREENS (panels for windows) + frame components, hardware, screen cloth
3. Both folders also have credit-card forms, applications — those are NOT pricing.
4. If DJ uploads a new pricing PDF, save to the appropriate `Supplies/<supplier>/` folder with a clear name (e.g. `Active Window 2026 Pricing.pdf`) and update this memory file.

## Reading PDFs locally

Per `reference_pdf_reading.md`: pdftoppm.exe is at `C:/Users/dj/poppler/poppler-24.08.0/Library/bin/pdftoppm.exe` (NOT on PATH). For text extraction, `pdftotext.exe` in the same folder gives clean output via `-layout` flag — preserves the table structure these price lists use. Run from Bash:
```
"C:/Users/dj/poppler/poppler-24.08.0/Library/bin/pdftotext.exe" -layout "<pdf_path>" "/tmp/output.txt"
```
Then grep/head the .txt. The Read tool's pages= mode also works for PDFs but uses pdftoppm which fails when not on PATH.

---
