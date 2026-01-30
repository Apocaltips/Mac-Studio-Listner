# Mac Studio Setup Guide

This guide gets Office Recorder running on your Mac Studio with local microphones and local LLM processing.

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

Notes:
- If using a Scarlett interface, the input device may be named "Scarlett 2i2" or similar.
- If using wireless mics, select the receiver as the input device.

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

## 7) Verify

- Click Start Recording in the UI.
- Confirm audio segments appear in `~/OfficeRecorder/YYYY-MM-DD/audio`.
- Run Transcribe Today + Summarize Today.

## 8) Two-Mac Studio split (recommended)

- Mac Studio A: recording service + mic interface.
- Mac Studio B: transcription/summarization after hours (copy day folder via network share).

## Troubleshooting
- No audio files: check `OFFICE_RECORDER_AUDIO_INPUT` and mic routing in macOS sound settings.
- Summary fails: ensure your local LLM is running and `OFFICE_RECORDER_LLM_BASE_URL` is correct.
