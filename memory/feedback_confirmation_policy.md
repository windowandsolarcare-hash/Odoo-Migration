---
name: Confirmation policy
description: When to ask DJ for confirmation vs. just do it
type: feedback
---

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
