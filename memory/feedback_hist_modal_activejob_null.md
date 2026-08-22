---
name: feedback_hist_modal_activejob_null
description: Add Note from historical modal — activeJob nulled by setTimeout before user taps Save
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 09632d9d-9a6c-46b5-8708-84d98257a4aa
---

Never add a setTimeout that clears `activeJob` after calling `openNoteModal()`. `submitNote()` checks `if (!activeJob) return` at the top — if the timeout fires before the user taps Save, the save silently does nothing.

**Why:** This exact bug existed: `histAddNote()` set `activeJob` then did `setTimeout(() => { activeJob = null; }, 100)`. Since the user needs time to type, `activeJob` was always null by the time they hit Save.

**How to apply:** When passing context to a modal via a global variable (`activeJob`, `activePartner`, etc.), clear it ONLY inside the submit handler after the operation completes — never on a timer.
