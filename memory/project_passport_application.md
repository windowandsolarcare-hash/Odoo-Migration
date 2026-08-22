---
name: project_passport_application
description: "DJ's U.S. passport application — first since one ~20yr ago that is now LOST. DS-11 + DS-64 filled (fillable PDFs in Downloads), needs in-person filing."
metadata:
  node_type: memory
  type: project
  originSessionId: ed913ff2
---

**DJ is applying for a U.S. passport (2026-06-27/28).** His last one was issued ~20 years ago and is **LOST** → he needs **Form DS-11** (in person; renewal-by-mail DS-82 not allowed since the old one is >15 yrs and lost) **+ Form DS-64** (Statement Regarding a Lost or Stolen Passport).

**Both fillable PDFs prepared and pre-filled, saved at `C:\Users\dj\Downloads\`:**
- `DS-11_Daniel_Saunders_FILLABLE.pdf` — official 04-2025 DS-11 (from eforms.state.gov/Forms/ds11_pdf.PDF), filled via PyMuPDF (form fields preserved). Filled: name **Saunders III / Daniel / Joseph** (04-2025 form has NO suffix box → "III" placed with the surname; suffix could move if the acceptance agent prefers), email windowandsolarcare@gmail.com, occupation Business Owner, employer "A Window and Solar Care, LLC", U.S. Passport Book + Regular Book checked, "Ever issued?" = Yes, "name on most recent passport" = Daniel Joseph Saunders III, **Book Status = Lost**, mailing address **32569 San Miguelito Drive, Thousand Palms, CA 92276** (from the LLC IRS registration — [[project_wsc_llc_formation]]).
- `DS-64_Daniel_Saunders_FILLABLE.pdf` — name, email, "Passport Book → Lost", "submitting with new application = Yes" pre-filled.

**STILL needs DJ to supply (not in any system — must come from him):** DOB, sex, place of birth, SSN, phone, height/hair/eye color, both parents' info, marital status, emergency contact; on the DS-64: where/when lost + police-report Y/N.

**Filing:** DS-11 + DS-64 together **IN PERSON** at a passport acceptance facility (book appt). Don't sign DS-11 until the agent says so. Bring **certified birth certificate** (citizenship proof, since the lost passport can't serve that), photo ID + photocopy, 2x2 photo. Fees ~$130 book + $35 execution.

**Technique note (reusable):** to fill a government fillable PDF — download official PDF, `fitz`(PyMuPDF) `page.widgets()` to enumerate fields, set `w.field_value` + `w.update()`, `doc.save()`. Checkboxes/radios: set to the exact on-state string from `w.button_states()['normal']` (e.g. DS-64 'Book#20Lost_1'). Render a region to PNG + Read it to visually verify layout (caught that the 04-2025 DS-11 has no suffix box, contradicting secondary web guides).
