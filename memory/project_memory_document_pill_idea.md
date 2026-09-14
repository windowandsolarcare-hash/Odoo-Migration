---
name: project_memory_document_pill_idea
description: "PARKED IDEA (DJ 2026-09-14): add a real document UPLOAD to the memory screen (a 'document pill'), replacing the unintuitive Reference-card 'link' field, and index uploads so the memory Ask can answer 'show me the document named xxxxx'. Not approved to build — thinking-about stage."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-14T08:46:47.686Z
---

**DJ 2026-09-14 (verbatim intent):** "Put a document pill in memory. Right now it has a reference card (whatever that is — in fact it has a link field that I don't understand what it does). We just need an upload button. Question is can we get it to integrate so we simply ask 'show me this document named xxxxxxxx.'" Framed as an idea to think about, NOT a build order.

**What the current thing IS (so we answer his confusion, don't repeat it):** `static/owner/v2_memory.html` has card kinds Decision / Action-item / Meeting / **Reference**. The Reference card (fields topic / key_facts / notes / **link**, ~L272-275) and Decision cards (~L231) render a `link` value as a plain **"Open" hyperlink to an external URL**. There is NO file upload and NO indexing — "attaching a doc" today = pasting a URL to one that lives elsewhere. That's why DJ finds the link field pointless. `doc_link` (~L265-268 "Open doc") is the same pattern.

**The idea:** replace/augment the link field with a real **📄 document UPLOAD** ("document pill"), store the bytes durably (reuse the **ir.attachment** mechanism already used for voice notes `wscvn:` / recordings `wscfn:`), and **index it so the memory Ask (`/api/memory/ask`) can retrieve/open it by name** — "show me the document named xxxxx" — and, since **Google Drive auto-OCRs PDFs/images** ([[project_drive_pdf_ocr_fulltext_search]]), eventually by CONTENT too, not just filename.

**Why it's very doable + where it belongs:** the storage + OCR-search engine already exists in the **Vault** ([[project_vault_evernote_drive]] / [[project_vault_phase1_md_notes]]); the memory Ask already does relevance ranking ([[project_memory_ask_relevance]]). So this is mostly wiring an upload endpoint + adding documents to the Ask index, not new infrastructure. It pairs with two live threads: the **Vault-UI rework** (documents' natural home) and the **"Cheryl has no private document save" gap** ([[project_cheryl_library_vs_documents]]). One engine → three payoffs (memory doc-pill, Cheryl private save, Vault rework). Could also be dropped on the in-app **Idea Board** ([[project_idea_board]]) if DJ wants it in that running list rather than just memory.

**Status:** PARKED — thinking-about. No build until DJ says go. Ties to the earlier-tonight agent-memory-app proposal (request c) as part of the same "memory + documents + retrieval" family.
