from __future__ import annotations

from pydantic import BaseModel, Field


class StartRecordingRequest(BaseModel):
    date: str | None = Field(default=None, description="YYYY-MM-DD")


class SummarizeRequest(BaseModel):
    date: str | None = Field(default=None, description="YYYY-MM-DD")
    send_to_openclaw: bool = False
