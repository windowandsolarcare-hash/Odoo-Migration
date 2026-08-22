---
name: Cheryl Real Estate Interview Infrastructure (2026-04-24)
description: 20-question behavioral interview template, interview day guide, Whisper transcription setup on Windows, folder structure for recording/analysis
type: project
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
## Overview
Built complete infrastructure for capturing Cheryl's real estate business operations via structured 60-minute video interview. Designed to understand deal workflow (pre-interview through post-close), extract beyond-audio insights (screenshots, documents), and transcribe via OpenAI Whisper v20250625 on Windows.

**Why:** Rich qualitative data beats incomplete quantitative surveys. Video captures non-verbal cues, hesitations, alternative workarounds. Whisper avoids cost/privacy of cloud transcription APIs.

## Interview Design

### 20-Question Template
**File:** `3_Documentation/INTERVIEW.md` in local Cheryl repo

**Structure:** Deal walkthrough framed in three time windows:
1. **Pre-Close Phase** (3 questions)
   - How do leads come in? (source, volume, conversion %)
   - How do you qualify leads? (criteria, quick-reject signals)
   - What's the initial client conversation? (what docs exchanged, typical duration)

2. **During-Deal Phase** (6 questions)
   - How many tasks live in your current workflow? (CRM, spreadsheet, email tracking)
   - How do you coordinate with agents / title companies / lenders? (tools, handoff points)
   - What milestones do you track? (inspection, appraisal, clear-to-close, etc.)
   - What goes wrong most often? (blockers, rework, timeline slips)
   - How do you handle extensions / renegotiations?
   - How do clients get updates? (frequency, channel)

3. **Post-Close Phase** (2 questions)
   - What happens after close? (follow-ups, nurture, referral capture)
   - How do you celebrate / acknowledge deals? (systems, timing)

4. **System & Tools Stack** (4 questions)
   - Current CRM / system(s) - what do you like / hate?
   - Contact database - how do you organize? (tags, segments, notes)
   - Document storage - folders, naming convention?
   - Integration desires - what would save you the most time?

5. **Operational Questions** (5 questions)
   - Team size / structure?
   - Busiest season / slow season?
   - Do you do commercial or residential (or both)?
   - Geographic focus?
   - Biggest untapped opportunity (if money/time were unlimited)?

### Why This Structure
- Opens with lead gen + qualification (foundation, no tech bias)
- Deep dives into actual workflow (reveals hidden steps, duplicate entry, bottlenecks)
- Avoids pitching Odoo (let her describe what she needs first)
- Captures pain points naturally (what goes wrong > what works great)
- Ends with aspirational vision (what she wishes for) — good signal for priorities

## Interview Day Execution

### Pre-Interview Brief
**File:** `3_Documentation/INTERVIEW_DAY_GUIDE.md`

Covers:
- **Setup:** Camera position (eye level), mic placement, lighting
- **Consent:** Record the video and permission to use in analysis (not sharing externally without approval)
- **Framing:** "This is a design interview, not an interrogation. I'm here to understand your world."
- **Redirection:** If she pitches ideas or vents frustrations → acknowledge, note it, redirect to the 20 questions
- **Pacing:** 3 min per question target; 60 min total with buffer
- **Beyond-Audio:** Ask for screenshots of current system, sample client email, deal doc samples during relevant questions
- **Debrief:** After recording, 5-min verbal debrief (hypothesis before vs. after, surprises)

### Recording & Transcription Pipeline

**Whisper Setup (Windows):**
- Tool: OpenAI Whisper v20250625 CLI
- Models: small (484 MB) + medium (1.53 GB), both cached locally at `~/.cache/huggingface/...`
- Installation: `pip install openai-whisper==20250625`
- Env var: `PYTHONIOENCODING=utf-8` (required on Windows 3.14, prevents Unicode errors)
- Command: `whisper input.m4a --model medium --output_format vtt --output_dir output/`

**Why Whisper:**
- No cloud API calls (privacy, cost)
- Accurate (~95%) on English-language speech
- Runs offline on Windows GPU (fast; ~15 min to transcribe 60-min interview)
- Outputs VTT (webvtt) for timestamps + text

### Folder Structure (Per Interview)

```
4_Reference_Data/interviews/[CHERYL_DATE]/
├── debrief.md                 # 7-point post-interview checklist
├── hypothesis_before.txt      # What I thought about her workflow (pre-interview)
├── hypothesis_after.txt       # What I learned (post-interview, post-transcribe)
├── audio_notes.md             # Key phrases, timestamps, quotes to pull
├── Cheryl_Interview_[DATE].m4a # Raw video
├── Cheryl_Interview_[DATE].vtt # Whisper transcript with timestamps
├── screenshots/               # PNG/JPG of her current system
├── documents/                 # Sample client contracts, emails, PDFs
└── ANALYSIS.md               # Synthesis (not required, optional deeper analysis)
```

### Debrief Checklist (7 Points)
1. **Biggest surprise** — something you didn't expect
2. **Biggest pain point** — where she expressed most frustration
3. **Biggest opportunity** — gap between current + aspirational
4. **Who is she** — role title, how long in real estate, size of portfolio
5. **Her world** — residential / commercial, single-family / multi, geographic focus
6. **Tech stack** — current CRM, storage, integrations
7. **Next action** — what does she want to do with this analysis?

## Implementation

**Local Tools Installed:**
- `C:\Users\dj\bin\ffmpeg.exe` — media conversion (ffmpeg.com → download "essentials" build)
- `C:\Users\dj\bin\ffprobe.exe` — media inspection (bundled with ffmpeg)
- `whisper.exe` v20250625 — transcription (pip installs to `~/.local/bin/` on Windows)
- Models cached: `~/.cache/huggingface/hub/models--openai--whisper-*.../...` (~2 GB total)

**Persistent Env Vars (set once):**
```powershell
[Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'User')
```

**End-to-End Test (2026-04-22):**
- Recorded 3-min test video (iPhone camera)
- Transcribed with `whisper test.m4a --model small`
- Output: VTT file with timestamps, accurate transcription
- Time: ~30 seconds for 3-min video on GPU

## How to Apply

**Before Interview:**
1. Set up camera + mic (phone on tripod OK)
2. Review 20-question template + circle topics most relevant to Cheryl
3. Print `INTERVIEW_DAY_GUIDE.md` for reference
4. Create interview folder: `4_Reference_Data/interviews/cheryl_[DATE]/`
5. Write hypothesis_before.txt (what you think you'll learn)

**During Interview:**
1. Record video (iPhone voice memo → export as .m4a, or use camera app)
2. Ask the 20 questions (can skip 1-2 if time constrained)
3. Capture screenshots (ask her to show you her current CRM, send them as files after)
4. Note timestamps for key phrases (side notes during interview)
5. Verbal debrief immediately after (5 min, capture hypothesis_after.txt)

**After Interview:**
1. Transcribe: `whisper interview.m4a --model medium --output_format vtt --output_dir output/`
2. Read transcript, extract key quotes to audio_notes.md with timestamps
3. Write ANALYSIS.md (if deeper synthesis needed)
4. Upload to GitHub (Cheryl repo, not W&SC repo)

## Known Behaviors

- **Whisper hallucination:** Sometimes repeats phrases or adds text not in audio. Review transcript manually.
- **Background noise:** Whisper handles it well but loud noise may reduce accuracy. Test at interview location.
- **Privacy:** Whisper stays local; no audio sent to cloud. Can delete raw video after transcription.
- **Timestamp precision:** VTT output has 1-second precision. Sufficient for finding soundbites.

## Current Status (2026-04-22)
✅ Template created
✅ Interview guide created
✅ Folder structure established
✅ Whisper setup tested end-to-end
✅ Models cached locally
⏳ **Waiting on:** Scheduling interview with Cheryl (when is she available?)

## Reference Docs
- OpenAI Whisper: https://github.com/openai/whisper
- ffmpeg documentation: https://ffmpeg.org/documentation.html
- WebVTT spec: https://www.w3.org/TR/webvtt/
