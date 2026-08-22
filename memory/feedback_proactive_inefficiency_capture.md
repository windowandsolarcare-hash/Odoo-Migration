---
name: Proactive Inefficiency Capture — I Own This
description: When I discover trial-and-error patterns, repetitive failures, or inefficient processes, I MUST document and save them immediately without waiting for DJ's request. This is my responsibility, not his job to ask.
type: feedback
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
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
