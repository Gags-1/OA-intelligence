from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.question import Question
from app.schemas.question import QuestionCreate


def create_question(
    db: Session,
    question_data: QuestionCreate,
) -> Question:
    question = Question(
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        company_id=question_data.company_id,
        role=question_data.role,
        difficulty=question_data.difficulty,
        source=question_data.source,
        source_reference=question_data.source_reference,
        status="pending",
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question

def get_questions(
    db: Session,
    company_id: int | None = None,
    role: str | None = None,
    difficulty: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> list[Question]:

    statement = select(Question)

    if company_id is not None:
        statement = statement.where(
            Question.company_id == company_id
        )

    if role is not None:
        statement = statement.where(
            Question.role == role
        )

    if difficulty is not None:
        statement = statement.where(
            Question.difficulty == difficulty
        )

    statement = (
        statement
        .order_by(
            Question.created_at.desc(),
            Question.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def get_question(
    db: Session,
    question_id: int,
) -> Question | None:
    statement = select(Question).where(
        Question.id == question_id
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()
