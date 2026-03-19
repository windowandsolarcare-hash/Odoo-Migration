# Claude Code - Project Instructions
**Last Updated:** 2026-03-19
**Migration:** Cursor → Claude Code (permanent)

---

## START HERE

**Read `CLAUDE_CONTEXT.md` first.** It contains everything a new session needs.
**Also read `MASTER_PROJECT_CONTEXT.md`** — the Technical Bible (correct field names, API syntax, current project structure).

---

## QUICK REFERENCE

**Project:** Workiz ↔ Odoo sync for Window & Solar Care
**Owner:** DJ Sanders
**Repo:** windowandsolarcare-hash/Odoo-Migration (main only)
**Deploy:** `gh api` to push files - NO git commands

---

## CRITICAL RULES

1. **Zapier:** Code in GitHub. Zapier fetches on every run. Push to main = deploy.
2. **Odoo Server Actions:** NO imports, NO docstrings, NO env.user.message_post in webhooks
3. **Odoo Webhook payload:** Often already dict - check `isinstance(payload, str)` before json.loads
4. **Workiz STOP:** Filter on SubStatus (not Status). Status stays "Pending"
5. **Property search:** Use `x_studio_x_studio_record_category` = "Property", NOT type="other"
6. **Testing:** YOU create/cleanup test data via API. User never does manually

---

## GITHUB DEPLOYMENT WORKFLOW

**We use `gh` (GitHub CLI), NOT `git` commands!**
**We push directly to `main` branch - Zapier reads from main!**

```powershell
$repo = "windowandsolarcare-hash/Odoo-Migration"
$filePath = "1_Production_Code/zapier_phase3_FLATTENED_FINAL.py" # Example path
$date = Get-Date -Format "yyyy-MM-dd"

# Step 1: Get current SHA (skip if new file)
$sha = gh api "repos/$repo/contents/$filePath" --jq '.sha' 2>&1
if ($LASTEXITCODE -eq 0) {
    $sha = $sha.Trim()
}

# Step 2: Convert file to base64
$localFile = "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\$filePath"
$content = Get-Content $localFile -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)

# Step 3: Create payload
if ($LASTEXITCODE -eq 0) {
    # Existing file - include SHA
    $payload = @{
        message = "$date | filename | description of change"
        content = $base64
        sha = $sha
        branch = "main"
    } | ConvertTo-Json -Depth 10
} else {
    # New file - no SHA
    $payload = @{
        message = "$date | filename | description of change"
        content = $base64
        branch = "main"
    } | ConvertTo-Json -Depth 10
}

# Step 4: Push to GitHub main
$payload | gh api "repos/$repo/contents/$filePath" --method PUT --input -
```

### Code Modification Workflow
1. Read the current local version first
2. Make the requested changes
3. Save locally
4. Push to GitHub main using the PowerShell script above
5. Confirm to user: what was changed, file name, and that it's on GitHub main
6. Zapier auto-fetches latest code on next trigger (NO manual Zapier update needed)

### GitHub Commit Standards
- Format: `YYYY-MM-DD | filename | description of change`
- Example: `2026-03-19 | zapier_phase4 | Fixed property search field name`

---

## PLATFORM MIGRATION RULE

**When migrating code between platforms (Zapier → Odoo, Odoo → Zapier, etc.):**

**NEVER:**
- Simplify, optimize, or "clean up" existing code
- Strip down features, logging, or field mappings
- Remove ANY functionality that exists in the original

**ALWAYS:**
- Copy ALL functionality exactly (1:1 functional duplicate)
- Preserve ALL fields, logs, chatter posts, activity details
- Only change what's technically required for the new platform:
  - Remove `import` statements for Odoo safe_eval
  - Adjust API call format
  - Variable naming (only if platform requires it)

**Why:** This code represents months of development. Every detail exists for a reason. Platform migrations are NOT opportunities to refactor — they are pure translations with minimum technical changes only.

---

## TESTING WORKFLOW

**YOU create and cleanup ALL test data via API. User never manually creates/deletes.**

### Process
1. Make code changes locally
2. Push to GitHub main (using gh api workflow above)
3. **YOU create test data via API** (don't ask user to do it):
   - Workiz jobs: Use `test_create_workiz_job.py`
   - Odoo data: Create via Odoo JSON-RPC API
4. Trigger/monitor Zapier (webhook or manual)
5. Verify results in Odoo/Workiz
6. **YOU cleanup test data via API**:
   - Workiz: Use `test_cleanup_workiz_job.py <uuid>`
   - Odoo: Use `test_cleanup_odoo_data.py --so/--invoice/--payment`
7. Report results to user

### Scripts Available
- `2_Testing_Tools/test_create_workiz_job.py`
- `2_Testing_Tools/test_cleanup_workiz_job.py`
- `2_Testing_Tools/test_cleanup_odoo_data.py`
- `2_Testing_Tools/TEST_FRAMEWORK.md`

### User's Role in Testing
- Approve or reject test results ONLY
- Never manually creates or deletes test data

---

## CODEBASE ORGANIZATION

- **1_Production_Code/** — The active scripts running the business
- **2_Testing_Tools/** — API test scripts
- **3_Documentation/** — Active manuals
- **4_Reference_Data/** — CSVs and mappings
- **z_ARCHIVE_DEPRECATED/** — Old files

---

## COMMUNICATION STYLE

- Be concise — DJ is experienced, skip basic explanations
- Always confirm what branch you committed to
- If something fails, explain exactly why and give the fix
- Never ask "would you like me to..." for things clearly part of the task — just do them
- When done with a task, give a short summary: what changed, where it lives, next step

---

## CONVERSATION ADDITIONS (March 2026)

- **STOP Odoo webhook:** URL https://window-solar-care.odoo.com/web/hook/f64d0bc1-54fd-45a1-b645-0dcae6ae1728 - Workiz must send here
- **Reactivation CRM Activity:** Format `{campaign} | {date} | Job #{so_name} | {primary_service}` for x_name; x_description = actual SMS text
- **Contact link on SO:** Related field `partner_shipping_id.parent_id` in Odoo Studio
- **Add-on pricing:** base_price < $70 = no inflation, no $85 floor
- **Phase 5 next date:** Use completed job's JobDateTime, not datetime.now()
- **Phase 5 last_date_cleaned:** Populate on new maintenance jobs
- **Orphaned future jobs:** Leave alone (no auto-delete)
- **Graveyard job:** Always create new (don't reuse existing future job)

---

## FILES TO READ

- `CLAUDE_CONTEXT.md` - Full context (dense, complete)
- `MASTER_PROJECT_CONTEXT.md` - Technical bible, field mappings
- `3_Documentation/BUSINESS_WORKFLOW.md` - Business processes
- `.cursorrules` - Legacy Cursor rules (superseded by this file)

---

**This handoff prepared for Claude Code. Cursor session ended 2026-03-19.**
