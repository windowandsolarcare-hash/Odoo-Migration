---
name: project_wayne_geringer_combined_655_open
description: "OPEN reconciliation — Wayne Geringer's two Oct 15 jobs temporarily combined to one $655 branded Zelle request; re-split when he pays"
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-10-16T02:17:41.411Z
---

**OPEN as of 2026-10-15.** Wayne Geringer (partner **23247**, 760-989-2466) had two jobs done Oct 15; DJ wanted ONE branded Zelle pay page for the combined **$655**. Because the branded Zelle page pulls a single SO's total, I TEMPORARILY combined both onto one SO. **This must be re-split once he pays.**

**Current (temporary) state:**
- SO **004337** (id 17066, 29857 Sandy Ct) = **$655** — carries its own 4 lines + a $235 "67597 Lagos Way" summary line. This is the SO behind the branded pay link `wscare.pro/pay/z-17066-0-...`.
- SO **004338** (id 17067, 67597 Lagos Way) = **$0** — single placeholder line "Combined onto 29857 Sandy Ct...".
- HUD card `operator:zelle_branded:17066*` (re-posted as `_v2` after an app crash dropped the first) holds the branded request for DJ to send.
- Neither job was invoiced at combine time.

**WHEN WAYNE PAYS $655 → re-split (restore both, then record split):**
1. Restore 17066 to $420 via POST /owner/api/job/lines: pid141 "Windows In & Out - Full Service" x1 $220; pid99 "Mirrors Cleaned" x6 $10; pid118 "Shower Enclosure" x2 $50; pid100 "Miscellaneous" x1 $40.
2. Restore 17067 to $235: pid141 "Windows In & Out - Full Service" x1 $135; pid118 "Shower Enclosure" x2 $40; pid99 "Mirrors Cleaned" x2 $10.
3. Invoice each + record the Zelle payment SPLIT: $420 → 004337, $235 → 004338. Zelle deposits straight to Chase (journal BNK1, id 6) per the corrected Zelle rule — NOT j19.
4. Delete HUD card(s) matching `operator:zelle_branded:17066*`; delete THIS memory (+ GitHub mirror) once reconciled.

Full original-line snapshot saved locally: `C:/Users/dj/_wayne_lines_snapshot.json`. Branded page amount verified $655 at combine time. See [[feedback_operator_followup_verify]].
