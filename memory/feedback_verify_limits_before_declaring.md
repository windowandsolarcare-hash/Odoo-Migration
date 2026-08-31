---
name: feedback_verify_limits_before_declaring
description: "\"I can't do X\" is a factual claim and needs evidence, exactly like a field name does. TEST the actual path before declaring anything blocked, unavailable or too expensive. If one method failed, name the METHOD, not the capability."
metadata:
  node_type: memory
  type: feedback
---

# Never declare a limitation from a non-exhaustive check

**Type:** feedback · **Date:** 2026-08-30 · **Session:** cloud Lead · **Raised by:** DJ (3x in one day)

## The rule

**"I can't do X" is a factual claim about the world and it needs evidence, exactly like "the field
is named Y" does.** Before telling DJ something is impossible, blocked, unavailable, or too
expensive — TEST THE ACTUAL PATH. One negative result from one method is not proof the capability
is absent; it is proof that one method failed.

Never build a recommendation, a cost argument, or a scope reduction on top of an untested limit.

## Why — three failures in a single day (2026-08-30)

All three had the same shape: one incomplete check → a confident negative → advice built on it.

| I said | Reality | What the check actually proved |
|---|---|---|
| "The Run NBHOF Auto button doesn't exist — you may be misremembering" | It existed; built that same day by another session | My 8-day-old clone didn't have it |
| "Writes are blocked from cloud / the file is too large to change" | `git push` to a branch worked fine; branch → PR → merge costs diff-sized tokens | `api.github.com` REST returned 403 at the proxy |
| "No filter tool exists in this connector" | `create_filter` / `list_filters` are real Gmail connector tools | A keyword ToolSearch returned 8 results, not an exhaustive list |

**The cost is not just being wrong.** Each one changed DJ's decisions: he was told a button he
presses daily didn't exist; he offered to *grant permissions he did not need to grant* ("is there
anyway I can grant you some type of access") because I had described a wall that wasn't there;
and he was steered toward an XML-export workaround for filters. A false constraint quietly
shrinks what he thinks the system can do — and unlike a wrong field name, **nothing ever throws an
error to correct it.**

## How to apply

Before any sentence containing *can't / blocked / unavailable / not possible / too large*:

1. **Try the thing.** `git push --dry-run`, an actual tool call, a real fetch. A 10-second test
   beats a paragraph of reasoning about why it probably won't work.
2. **If one method failed, name the method, not the capability.** Say "the REST API 403s at the
   proxy" — NOT "writes are blocked." Say "this session doesn't have `create_filter`" — NOT "no
   such tool exists." The narrow statement is both true and more useful: it points at the workaround.
3. **Distinguish "absent" from "not loaded / not fetched / not in my copy."** Deferred MCP tools,
   a stale clone, and a disconnected server all look identical to a negative search. None of them
   mean the capability doesn't exist.
4. **When DJ contradicts you, he is the primary source.** He is describing his own live system.
   Re-verify before restating. See [[feedback_cloud_clone_stale_verify_from_github]].

## Related

- [[feedback_cloud_clone_stale_verify_from_github]] — the read-side twin (stale clone = confident
  wrong answer, no guard). This file generalizes it to capability claims.
- [[feedback_no_guessing_on_fields]] — same discipline applied to field names and formats.
- [[project_cloud_lead_write_path]] — the write path that actually works from cloud.
