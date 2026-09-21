from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    CODING = "coding"
    MCQ = "mcq"
    APTITUDE = "aptitude"
    SQL = "sql"
    SYSTEM_DESIGN = "system_design"
    INTERVIEW = "interview"

class QuestionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=1)
    question_type: QuestionType
    company_id: int
    role: str
    difficulty: Difficulty
    source: str
    source_reference: str | None = None


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    company_id: int
    role: str
    difficulty: str
    source: str
    source_reference: str | None
    status: QuestionStatus

    model_config = {
        "from_attributes": True
    }
