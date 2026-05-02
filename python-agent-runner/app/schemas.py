from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


class RunStatus(str, Enum):
    ACCEPTED = "accepted"
    DRAFTED = "drafted"
    NEEDS_REVISION = "needs_revision"
    COMPLETED = "completed"
    FAILED = "failed"


class EditorDecisionStatus(str, Enum):
    ACCEPT = "accept"
    REVISE = "revise"
    REJECT = "reject"


class RunRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    audience: str | None = Field(default=None, max_length=200)
    angle: str | None = Field(default=None, max_length=300)

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("topic must not be blank")
        return cleaned


class SourceRecord(BaseModel):
    source_id: str = Field(default_factory=lambda: f"src_{uuid4().hex}")
    title: str = Field(..., min_length=1)
    url: HttpUrl
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    excerpt: str = Field(..., min_length=1)
    provider: str = "placeholder"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DraftRecord(BaseModel):
    draft_id: str = Field(default_factory=lambda: f"draft_{uuid4().hex}")
    run_id: str
    topic: str
    title: str
    body: str
    source_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FactCheckIssue(BaseModel):
    check: str
    message: str
    severity: str = "warning"


class FactCheckReport(BaseModel):
    passed: bool
    issues: list[FactCheckIssue] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EditorDecision(BaseModel):
    status: EditorDecisionStatus
    summary: str
    required_revisions: list[str] = Field(default_factory=list)
    optional_notes: list[str] = Field(default_factory=list)


class FinalStoryRecord(BaseModel):
    run_id: str
    status: RunStatus
    topic: str
    draft: DraftRecord
    sources: list[SourceRecord]
    fact_check: FactCheckReport
    editor_decision: EditorDecision
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunResponse(BaseModel):
    run_id: str
    status: RunStatus
    story: FinalStoryRecord

