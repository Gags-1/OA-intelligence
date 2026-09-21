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

def get_questions(db: Session) -> list[Question]:
    statement = select(Question).order_by(Question.created_at.desc())

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
