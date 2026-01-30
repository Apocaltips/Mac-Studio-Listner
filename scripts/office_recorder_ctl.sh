#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${OFFICE_RECORDER_BASE_URL:-http://127.0.0.1:8787}"
CMD="${1:-status}"
DATE="${2:-$(date +%F)}"

case "$CMD" in
  start)
    curl -sS -X POST "$BASE_URL/api/recording/start" \
      -H "Content-Type: application/json" \
      -d "{\"date\":\"$DATE\"}"
    ;;
  stop)
    curl -sS -X POST "$BASE_URL/api/recording/stop"
    ;;
  status)
    curl -sS "$BASE_URL/api/recording/status"
    ;;
  transcribe)
    curl -sS -X POST "$BASE_URL/api/day/$DATE/transcribe"
    ;;
  summarize)
    curl -sS -X POST "$BASE_URL/api/day/$DATE/summarize" \
      -H "Content-Type: application/json" \
      -d '{"send_to_openclaw": false}'
    ;;
  send-summary)
    curl -sS -X POST "$BASE_URL/api/day/$DATE/summarize" \
      -H "Content-Type: application/json" \
      -d '{"send_to_openclaw": true}'
    ;;
  *)
    echo "Usage: office_recorder_ctl.sh {start|stop|status|transcribe|summarize|send-summary} [YYYY-MM-DD]" >&2
    exit 1
    ;;
esac
