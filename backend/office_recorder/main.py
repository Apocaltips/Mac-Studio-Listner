from __future__ import annotations

from pathlib import Path
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .models import StartRecordingRequest, SummarizeRequest
from .openclaw import send_hook_message
from .recording import RecorderManager
from .storage import Storage
from .transcription import Transcriber, transcribe_day
from .summarization import Summarizer, summarize_day
from .utils import read_json, today_str


config = load_config()
storage = Storage(config.data_dir)
recorder = RecorderManager(config, storage)
transcriber = Transcriber(config)
summarizer = Summarizer(config)

app = FastAPI(title="Office Recorder", version="0.1.0")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/recording/status")
def recording_status() -> dict[str, object]:
    return recorder.status()


@app.post("/api/recording/start")
def recording_start(payload: StartRecordingRequest) -> dict[str, object]:
    state = recorder.start(payload.date)
    return {"running": True, "state": state.__dict__}


@app.post("/api/recording/stop")
def recording_stop() -> dict[str, object]:
    return recorder.stop()


@app.get("/api/days")
def list_days() -> dict[str, list[str]]:
    return {"days": storage.list_days()}


@app.post("/api/day/{date_str}/transcribe")
def transcribe(date_str: str, background_tasks: BackgroundTasks) -> dict[str, object]:
    background_tasks.add_task(transcribe_day, storage, transcriber, date_str)
    return {"queued": True, "date": date_str}


@app.post("/api/day/{date_str}/summarize")
def summarize(date_str: str, payload: SummarizeRequest, background_tasks: BackgroundTasks) -> dict[str, object]:
    def _run() -> None:
        summary = summarize_day(storage, summarizer, date_str)
        if payload.send_to_openclaw:
            text = summary.get("daily_summary", {}).get("overview") or "Daily summary ready."
            send_hook_message(config, text)

    if payload.send_to_openclaw and (not config.openclaw_hook_url or not config.openclaw_hook_token):
        raise HTTPException(status_code=400, detail="OpenClaw webhook not configured")

    background_tasks.add_task(_run)
    return {"queued": True, "date": date_str}


@app.post("/api/day/{date_str}/pipeline")
def pipeline(date_str: str, payload: SummarizeRequest, background_tasks: BackgroundTasks) -> dict[str, object]:
    def _run() -> None:
        transcribe_day(storage, transcriber, date_str)
        summary = summarize_day(storage, summarizer, date_str)
        if payload.send_to_openclaw:
            text = summary.get("daily_summary", {}).get("overview") or "Daily summary ready."
            send_hook_message(config, text)

    if payload.send_to_openclaw and (not config.openclaw_hook_url or not config.openclaw_hook_token):
        raise HTTPException(status_code=400, detail="OpenClaw webhook not configured")

    background_tasks.add_task(_run)
    return {"queued": True, "date": date_str}


@app.get("/api/day/{date_str}/summary")
def get_summary(date_str: str) -> dict[str, object]:
    path = storage.summary_path(date_str)
    if not path.exists():
        raise HTTPException(status_code=404, detail="summary_not_found")
    return {"summary": read_json(path)}


@app.get("/api/day/{date_str}/summary.md")
def get_summary_markdown(date_str: str) -> FileResponse:
    path = storage.summary_markdown_path(date_str)
    if not path.exists():
        raise HTTPException(status_code=404, detail="summary_not_found")
    return FileResponse(path)


@app.post("/api/day/today/summarize")
def summarize_today(payload: SummarizeRequest, background_tasks: BackgroundTasks) -> dict[str, object]:
    return summarize(today_str(), payload, background_tasks)
