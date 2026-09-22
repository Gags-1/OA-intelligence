from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    SEMANTIC_DUPLICATE = "semantic_duplicate"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class SubmissionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_text: str = Field(min_length=1)
    input_type: str = Field(min_length=1, max_length=30)
    source: str = Field(min_length=1, max_length=100)
    source_reference: str | None = Field(
        default=None,
        max_length=500,
    )


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int | None
    raw_text: str
    input_type: str
    source: str
    source_reference: str | None
    status: SubmissionStatus
    created_at: datetime
    updated_at: datetime
