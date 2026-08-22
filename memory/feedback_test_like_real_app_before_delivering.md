---
name: feedback_test_like_real_app_before_delivering
description: "Build + TEST a feature against how the real-world app it mimics actually works, catch the obvious gaps yourself, then deliver complete — don't ship and let DJ discover missing basics"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ac2aeda5-6609-487b-94e3-132715d60520
---

When building an app that mimics a known product (e.g. the Vault = Evernote), **test it against that product's core behaviors BEFORE handing it to DJ.** Catch the obvious missing basics yourself (e.g. the Vault shipped with NO way to edit a note's text — an Evernote-101 gap DJ had to find).

**Why:** DJ's repeated experience is "build code → it's missing something obvious → I test and find it → it gets corrected → then it's just add-on, add-on, add-on by my words." He wants the completeness baked into the original build, not bolted on reactively. He wants Claude Code to be the engineer who **codes it, tests it, pushes it, expands it, and makes it a better app — THEN gives it to him for a final acceptance test**, where his role is "I like this particular thing," not "you forgot the basics."

**How to apply:**
- Before declaring a feature done, write/run a functional test pass (exercise every endpoint; create + clean up test data yourself per the TESTING WORKFLOW). For UI, reason through the real product's must-have actions (create/read/EDIT/rename/delete/organize/search/share) and verify each exists.
- Make a feature-parity checklist vs the product being copied; close the gaps in the same build.
- Then expand thoughtfully (anticipate the next obvious need) rather than waiting to be told.
- Deliver with a short "here's what I tested and what it does" so DJ runs only the final acceptance test.
See [[project_vault_evernote_drive.md]].
