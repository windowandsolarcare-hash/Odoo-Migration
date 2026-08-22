---
name: project_hiring_notes_marker_parser
description: "hiring.html parseNotes — section markers (DECISION/IQ/RESUME_TEXT/etc.) must be parsed by POSITION (order-independent), not a fixed chained slice. Fixed-order chain made Individual Questions render empty."
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

2026-06-10: Individual Questions rendered **empty** on the hiring candidate detail even though the data was in Odoo `hr.applicant.applicant_notes`.

**Root cause:** `parseNotes()` in `static/owner/hiring.html` extracted the trailing `===SECTION===` blocks with a hard-coded chained slice that assumed a fixed serialize order. But stored data appears in DIFFERENT orders across versions (real example, applicant 136): `…===DECISION=== ===INDIVIDUAL_QUESTIONS=== ===RESUME_TEXT=== ===GENERAL_NOTES===`. The old code did `individualQuestions = t2.slice(iqIdx + 26)` — grabbing the IQ JSON **plus everything after it** (`\n===RESUME_TEXT===\n…`). `_renderIqQuestions` then `JSON.parse`d that contaminated string → threw → caught → rendered `[]` (empty). RESUME_TEXT and GENERAL_NOTES were silently broken for this ordering too.

**Fix (order-independent parse):** find every known marker by position, sort by index, slice each section as `[marker_end → next_marker_start]`. Head (ai/RESUME/NOTES/SCREENING) = text before the first marker.
```js
const _SECTIONS = ['DECISION','DJ_DECISION','DJ_NOTES','GENERAL_NOTES','PHONE_INTERVIEW','INDIVIDUAL_QUESTIONS','RESUME_TEXT'];
const _hits = []; _SECTIONS.forEach(nm=>{const mk='==='+nm+'==='; const i=t2.indexOf(mk); if(i!==-1)_hits.push({nm,i,len:mk.length});});
_hits.sort((a,b)=>a.i-b.i);
const _vals={}; _hits.forEach((h,idx)=>{const end=idx+1<_hits.length?_hits[idx+1].i:t2.length; _vals[h.nm]=t2.slice(h.i+h.len,end).trim();});
// individualQuestions=_vals.INDIVIDUAL_QUESTIONS||''; textMain = before _hits[0].i
```
(`RAW_JSON`/`RAW_PASTE` are still stripped from the end first, before this scan, since their content can contain `===`.)

Verified against all 5 candidates that had IQ data (136,102,141,156,109) → each parses to 4 questions. Commit aee5819f.

**Separately same session:** Individual Questions section also now opens **expanded** by default in `openDetail` (`_iqOpen=true`, iqSection display block) — the transcription update had collapsed it, which made the questions look missing even before the parse bug surfaced.

**Why:** marker order is NOT stable across serialize versions; any fixed-order parser is fragile. **How to apply:** when adding a new `===SECTION===` to applicant notes, just add its name to `_SECTIONS` — no ordering assumptions. NEVER reintroduce chained `slice(idx+len)` extraction. See [[project_hiring_interview_tracker]], [[project_hiring_interview_transcription]].
