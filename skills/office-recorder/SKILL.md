---
name: office-recorder
version: 1
description: Control the local Office Recorder (start, stop, status, transcribe, summarize, pipeline).
tags: [audio, recording, summary, local]
tools: [exec]
---

# Office Recorder Control

You are running on the Mac Studio with local access to the Office Recorder project.

Goals:
- Interpret user commands like "start recording", "stop recording", "status", "transcribe", "summarize", "pipeline".
- Run the local control script via the Exec tool.

Rules:
- Use this base path:
  - If $OFFICE_RECORDER_HOME is set, use it.
  - Otherwise assume ~/Mac-Studio-Listner.
- Always call the control script with one of: start, stop, status, schedule-status, transcribe, summarize, pipeline, send-summary.
- Keep responses short and confirm the action.

Example Exec commands:
- bash -lc "cd $OFFICE_RECORDER_HOME && ./scripts/office_recorder_ctl.sh start"
- bash -lc "cd $OFFICE_RECORDER_HOME && ./scripts/office_recorder_ctl.sh stop"
- bash -lc "cd $OFFICE_RECORDER_HOME && ./scripts/office_recorder_ctl.sh status"
- bash -lc "cd $OFFICE_RECORDER_HOME && ./scripts/office_recorder_ctl.sh pipeline"
- bash -lc "cd $OFFICE_RECORDER_HOME && ./scripts/office_recorder_ctl.sh schedule-status"
- bash -lc "cd $OFFICE_RECORDER_HOME && ./scripts/office_recorder_ctl.sh send-summary"
