---
name: Activity notes are self-contained — never link to local memory files
description: When creating an Odoo mail.activity that future-you (or future-Claude) needs to act on, embed the relevant runbook content directly in the HTML note. Don't rely on links to local memory files — file:// URLs are blocked by browsers, and DJ reads activities on his phone where the dev machine isn't reachable.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
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
