# Office Recorder

Local, always-on office audio capture with end-of-day transcription and summaries. Designed for Mac Studio workstations and on-prem processing.

## Mac Studio Setup

Follow `MAC_STUDIO_SETUP.md` for step-by-step install and launchd auto-start.

## Features
- One-click recording for the whole day (chunked audio segments).
- Local transcription (faster-whisper) and conversation batching.
- Daily summary with topics, decisions, and action items.
- Local web UI plus CLI control script.
- Optional OpenClaw webhook for sending the daily overview.
- Optional auto schedule (start/stop by time window).
- Optional diarization (speaker separation) module.

## Quick Start (Mac Studio)

### 1) Install dependencies

```bash
brew install ffmpeg
```

```bash
cd office-recorder/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure audio + LLM

Copy the environment template:

```bash
cp .env.example .env
```

List audio devices (Mac):

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

Set `OFFICE_RECORDER_AUDIO_INPUT` in `.env` (e.g., `:0` or `:Scarlett 2i2`).

For local LLM, install and run Ollama or LM Studio. Example with Ollama:

```bash
ollama pull llama3.1:70b
```

Update `.env`:

```
OFFICE_RECORDER_LLM_BASE_URL=http://localhost:11434
OFFICE_RECORDER_LLM_MODEL=llama3.1:70b
```

### 3) Run the server

```bash
python -m office_recorder
```

Open the UI:

```
http://127.0.0.1:8787
```

## Control Script

Use the control script for quick CLI actions:

```bash
./scripts/office_recorder_ctl.sh start
./scripts/office_recorder_ctl.sh stop
./scripts/office_recorder_ctl.sh status
./scripts/office_recorder_ctl.sh transcribe
./scripts/office_recorder_ctl.sh summarize
```

Make it executable on macOS:

```bash
chmod +x ../scripts/office_recorder_ctl.sh
```

## OpenClaw Integration

Use the `skills/office-recorder/SKILL.md` skill. The skill triggers the control script via OpenClaw Exec. Configure Exec to allow the script path and run on the Mac Studio host.

## Data Layout

All data is stored in `~/OfficeRecorder` by default:

```
OfficeRecorder/
  2026-01-30/
    audio/
    transcripts/
    summaries/
    session.json
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
