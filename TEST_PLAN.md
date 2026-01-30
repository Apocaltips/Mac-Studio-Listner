# Test Plan - Office Recorder

## Unit Tests
- Batching logic groups segments by gap and max words.
- Storage creates correct day directories.
- Transcript offset logic uses segment index.

## Integration Tests (Manual)
1. Recording start/stop
   - Start recording from UI.
   - Verify audio segments appear in `~/OfficeRecorder/YYYY-MM-DD/audio`.
   - Stop recording and confirm ffmpeg stops.
2. Transcription
   - Run Transcribe Today.
   - Verify JSON transcripts created per segment.
3. Summarization
   - Run Summarize Today or pipeline.
   - Verify `summary.json` and `summary.md` generated.
4. OpenClaw control
   - Send "start recording" and "stop recording" via OpenClaw.
   - Validate state changes in UI.
5. Long-run stability
   - Record 8+ hours.
   - Check segment count matches expected duration.
6. Schedule
   - Enable schedule for a short window.
   - Confirm auto-start and auto-stop fire within one minute.
7. Diarization (optional)
   - Enable diarization and install deps.
   - Verify transcript segments include a "speaker" field.

## Reliability Checks
- Unplug/replug mic mid-recording to confirm errors are logged and UI shows status.
- System restart mid-recording: ensure `recorder_state.json` is cleared and can start cleanly.

## Security/Privacy
- Confirm data is only stored locally.
- Validate retention policy (manual cleanup or scheduled job).
