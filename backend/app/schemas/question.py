from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    question_text: str = Field(min_length=1)
    question_type: str
    company_id: int
    role: str
    difficulty: str
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
    status: str

    model_config = {
        "from_attributes": True
    }
