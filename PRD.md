# PRD — Office Recorder

## 1) Summary
Build a local, always-on recording system for a shared office room that captures full-day audio, splits it into manageable segments, transcribes locally, batches conversations, and delivers a daily summary of topics, decisions, and action items. Control must be available via a local web UI and via OpenClaw text commands ("start recording", "stop recording").

**Recommendation choices**
- **Platform**: Local web app on the Mac Studio (fastest build + easy access in any browser).
- **Transcription**: On-prem only (no cloud). Use faster-whisper (local) with optional upgrade to whisper.cpp/Metal.
- **OpenClaw control**: Skill + Exec tool calling local control script; optional webhook delivery for summaries.
- **Start/Stop**: Manual one-click start + optional schedule (not in v1, design-ready).
- **Speaker handling**: Start without diarization; add diarization (whisperX + pyannote) as Phase 2.
- **Retention**: Keep raw audio 30–90 days, transcripts/summaries longer; all local with configurable pruning.
- **Compute split**: Record on Mac Studio A (attached to mic interface), transcribe/summarize on Mac Studio B after hours to avoid daytime CPU load.

## 2) Goals
- Capture all in-room conversations during work hours with minimal friction.
- Provide reliable transcription and daily summaries without sending data off-prem.
- Enable quick control via UI + OpenClaw text commands.
- Keep the system stable for full-day sessions (8–12 hours).

## 3) Non-Goals
- Real-time transcription/summary during the day (out of scope for v1).
- Full speaker identification with names (out of scope for v1; requires diarization + enrollment).
- Cloud storage or cloud LLM use (explicitly avoided in v1).

## 4) Personas
- **Founders / partners**: Need a daily digest of discussions, decisions, and action items.
- **Visitors**: Must be informed via consent/signage; expect recordings to be local and private.

## 5) User Stories
1. As a founder, I click “Start Recording” and the room records all day without mic fiddling.
2. As a founder, I can text OpenClaw “start recording” and it starts immediately.
3. As a founder, I get a daily summary with topics, decisions, and action items.
4. As a founder, I can review the raw transcript per day if needed.

## 6) Functional Requirements
### 6.1 Recording
- Start/stop recording from UI and from OpenClaw command.
- Continuous recording for full day without file size issues (segment every N minutes).
- Store audio as WAV (16 kHz mono) or FLAC.
- Save session metadata (start time, device, format, sample rate).

### 6.2 Transcription
- Batch transcription for a given day.
- Use local whisper model (faster-whisper).
- Store transcript per segment and a merged transcript.

### 6.3 Conversation Batching
- Group transcript segments into conversation blocks.
- Default rules: new block when silence gap > 7 minutes or block length exceeds max words.

### 6.4 Summaries
- Produce JSON summary and Markdown summary per day.
- Daily summary includes: overview, top topics, decisions, action items (with owner/due if mentioned), questions, risks, follow-ups.
- Optional delivery via OpenClaw webhook.

### 6.5 OpenClaw Integration
- Provide a custom skill file to map “start recording / stop recording / status / summarize” to local API calls.
- Support sending daily summary via OpenClaw webhook (if configured).

### 6.6 Admin/Config
- Environment variables for mic input, sample rate, segmentation, LLM endpoint, and retention.
- Optional retention job (Phase 2) to prune raw audio after X days.

## 7) Non-Functional Requirements
- **Local-only data**: No external upload or cloud processing.
- **Reliability**: Must tolerate a full day of continuous capture.
- **Performance**: Recording must be lightweight; transcription can be scheduled after hours.
- **Security**: Data stored locally; optional disk encryption recommended.

## 8) System Architecture
### 8.1 Components
- **Recorder Service**: ffmpeg-based audio capture with segmenting.
- **API Server**: FastAPI for control and pipeline orchestration.
- **Transcriber**: faster-whisper (local) producing segment JSON.
- **Summarizer**: Local LLM via OpenAI-compatible API (Ollama/LM Studio).
- **UI**: Local web dashboard (Start/Stop, pipeline buttons, summary view).
- **OpenClaw Skill**: Maps text commands to local control script.

### 8.2 Data Flow
1. Start recording ? ffmpeg segments audio into `/OfficeRecorder/YYYY-MM-DD/audio`.
2. Transcribe ? JSON per segment in `/transcripts`.
3. Batch ? conversation blocks based on time gaps.
4. Summarize ? daily JSON + Markdown in `/summaries`.
5. Optional OpenClaw webhook ? summary overview text.

## 9) Privacy & Consent
- All participants informed of recording with signage.
- Ensure clear internal policy for visitors.
- Local data only; define retention (e.g., 90 days audio, 1 year transcript).

## 10) Metrics
- Recording uptime (hours recorded/day).
- Transcription completion time.
- Summary delivery success rate.
- “Missed decision” feedback from founders.

## 11) Risks & Mitigations
- **Mic misconfigured**: Provide device listing and test recording flow.
- **Long audio files**: Segment files every 5 minutes.
- **Model drift**: Allow model updates and prompt tuning.
- **No diarization**: Add Phase 2 diarization module.

## 12) Phase Plan
- **Phase 1 (MVP)**: Recording + transcription + summary + OpenClaw commands + UI.
- **Phase 2**: Diarization + auto-schedule + retention pruning + analytics.

## 13) Acceptance Criteria
- Start/stop recording from UI and OpenClaw text.
- Successfully record a full business day without failure.
- Generate a daily summary with topics and action items.
- All artifacts stored locally.
