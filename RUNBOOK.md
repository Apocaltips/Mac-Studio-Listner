# Daily Runbook

1. Arrive at office -> open UI -> click Start Recording (or text OpenClaw "start recording").
2. End of day -> click Stop Recording.
3. Run Transcribe Today -> wait for completion.
4. Run Summarize Today (or pipeline) -> review summary.
5. Optional: send summary via OpenClaw webhook.

Optional automations:
- Enable auto schedule in `.env` to start/stop on a time window.
- Enable diarization for speaker separation (requires extra deps).

## Quick CLI
```bash
./scripts/office_recorder_ctl.sh start
./scripts/office_recorder_ctl.sh stop
./scripts/office_recorder_ctl.sh transcribe
./scripts/office_recorder_ctl.sh summarize
```
