# Claude Code - Project Handoff
**Last Updated:** 2026-03-19  
**Migration:** Cursor → Claude Code (permanent)

---

## START HERE

**Read `CLAUDE_CONTEXT.md` first.** It contains everything a new session needs.

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
- `.cursorrules` - GitHub deploy workflow, testing rules

---

**This handoff prepared for Claude Code. Cursor session ended 2026-03-19.**
