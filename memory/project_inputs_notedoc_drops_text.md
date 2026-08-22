---
name: project_inputs_notedoc_drops_text
description: "Inputs box (/api/capture, myday.py) 'Note / doc' route was saving only the AI-extracted `note` fragment, not the full typed line — so a line the AI read as customer_note ('Quechan Casino Resort - Full Arch Dentist' → customer=Quechan…, note=Full Arch Dentist) lost the customer half. Fixed 2026-08-06: document route now uses `text` (raw) first."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T14:44:27.972Z
---

**DJ 2026-08-06:** typed "Quechan Casino Resort - Full Arch Dentist" in the Inputs box, tapped **Note / doc**, and the saved note was titled + bodied just **"Full Arch Dentist"** — the casino part vanished. He couldn't find his "casino note" because there's no "casino" in it.

**How the logic actually works (so it's understood):**
- **Note SAVE (`notes.py` create_note / update):** for TYPED notes the body is saved **VERBATIM** and the **title = the user's first line** (AI only picks FOLDER + TAGS; it does NOT summarize/rename typed notes — AI titling only for pasted URL articles). So it never invents a title for typed text.
- **Inputs box (`myday.py` `/api/capture`):** the AI CLASSIFIES + SPLITS the input into type + fields (task/customer_note{customer,note}/document/search). For DJ's line it chose customer_note: customer="Quechan Casino Resort", note="Full Arch Dentist".

**Bug:** the `document` (Note/doc) destination used **`_d = note or title or text`** — i.e. the AI's trimmed `note` field — in BOTH the `_mk()` alt-builder (~L465) and the main `typ=='document'` block (~L496). So overriding a customer_note-classified line to a plain doc saved only the `note` fragment, dropping `customer`.
**Fix 2026-08-06:** both → **`_d = text or note or title`** (a plain doc saves the WHOLE typed line). Pushed myday.py.

**Cleanup done:** updated the kept note (Drive doc 1iD2FT0hCHB44BOR_Y_M37xvsYM5NpoVNY8LhNPB1i6o) title+body → "Quechan Casino Resort - Full Arch Dentist" via PATCH /owner/api/notes/<id>/update; trashed the 7:14 duplicate "Full Arch Dentistry" (1OepiAyDEM19Nsodcl3S5drK5TpsMzoDaUL-SJv4TvZ0) via POST .../delete.

**Note storage reminder:** app Notes/Vault save to **Google Drive** (Quick Notes folder, Google Docs) via notes.py — NOT Odoo. Search Drive (fullText/title), not Odoo, to find a note.
