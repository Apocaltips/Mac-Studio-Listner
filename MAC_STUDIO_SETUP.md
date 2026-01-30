# Mac Studio Setup Guide

This guide gets Office Recorder running on your Mac Studio with local microphones and local LLM processing.

## First-Run Checklist

- [ ] Install ffmpeg and Python deps.
- [ ] Select the correct mic input in `.env`.
- [ ] Start the server and load the UI.
- [ ] Record a 2-minute test and confirm audio files appear.
- [ ] Run Transcribe Today and Summarize Today.
- [ ] Optional: enable auto schedule.
- [ ] Optional: enable diarization (speaker separation).

Screenshot placeholders (drop your captures here):
- UI overview: `docs/screenshots/ui-overview.png`
- Mic selection in macOS: `docs/screenshots/mic-selection.png`

## 1) Prereqs

- macOS (Mac Studio)
- Homebrew installed
- Python 3.10+ installed

Install ffmpeg:

```bash
brew install ffmpeg
```

## 2) Audio Device Setup

List audio devices (macOS):

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

Pick the correct input index or device name for your studio mic / Scarlett interface.

Update `backend/.env`:

```
OFFICE_RECORDER_AUDIO_BACKEND=avfoundation
OFFICE_RECORDER_AUDIO_INPUT=:0
```

Mic selection hints:
- Scarlett interfaces usually appear as "Scarlett" or "USB Audio".
- Wireless mic receivers appear as their USB device name.
- If levels are low, check the gain on the Scarlett and macOS input volume.

## 3) Install Python deps

```bash
cd ~/Mac-Studio-Listner/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Configure the environment

```bash
cp .env.example .env
```

Update `.env` for your mic input and local LLM:

```
OFFICE_RECORDER_AUDIO_INPUT=:0
OFFICE_RECORDER_LLM_BASE_URL=http://localhost:11434
OFFICE_RECORDER_LLM_MODEL=llama3.1:70b
```

## 5) Run the server

```bash
python -m office_recorder
```

Open the UI:

```
http://127.0.0.1:8787
```

## 6) Optional: Auto-start on login (launchd)

A sample LaunchAgent is in `macos/launchd/office-recorder.plist`.

Steps:

```bash
mkdir -p ~/Library/LaunchAgents
cp macos/launchd/office-recorder.plist ~/Library/LaunchAgents/
launchctl load -w ~/Library/LaunchAgents/office-recorder.plist
```

## 7) Optional: Auto schedule (start/stop)

Enable schedule in `.env`:

```
OFFICE_RECORDER_SCHEDULE_ENABLED=true
OFFICE_RECORDER_SCHEDULE_START=09:00
OFFICE_RECORDER_SCHEDULE_END=18:00
OFFICE_RECORDER_SCHEDULE_DAYS=mon,tue,wed,thu,fri
OFFICE_RECORDER_SCHEDULE_TZ=local
OFFICE_RECORDER_SCHEDULE_AUTO_STOP=true
```

## 8) Optional: Diarization (speaker separation)

Install diarization deps:

```bash
pip install -r requirements-diarization.txt
```

Then enable in `.env`:

```
OFFICE_RECORDER_DIARIZATION_ENABLED=true
OFFICE_RECORDER_DIARIZATION_BACKEND=whisperx
OFFICE_RECORDER_DIARIZATION_DEVICE=auto
OFFICE_RECORDER_DIARIZATION_MODEL=pyannote/speaker-diarization
OFFICE_RECORDER_DIARIZATION_HF_TOKEN=<your_hf_token>
```

## 9) Verify

- Click Start Recording in the UI.
- Confirm audio segments appear in `~/OfficeRecorder/YYYY-MM-DD/audio`.
- Run Transcribe Today + Summarize Today.

## 10) Two-Mac Studio split (recommended)

- Mac Studio A: recording service + mic interface.
- Mac Studio B: transcription/summarization after hours (copy day folder via network share).

## Troubleshooting
- No audio files: check `OFFICE_RECORDER_AUDIO_INPUT` and mic routing in macOS sound settings.
- Summary fails: ensure your local LLM is running and `OFFICE_RECORDER_LLM_BASE_URL` is correct.
