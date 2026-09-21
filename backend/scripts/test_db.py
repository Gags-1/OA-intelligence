from app.core.database import SessionLocal
from app.models.company import Company
from app.models.question import Question


db = SessionLocal()

try:
    company = Company(name="Google")

    db.add(company)
    db.commit()
    db.refresh(company)

    print(f"Created company: {company.id} - {company.name}")

    question = Question(
        question_text="Given an array of integers, find the longest subarray whose sum equals K.",
        question_type="coding",
        company_id=company.id,
        role="SDE",
        difficulty="medium",
        source="student_submission",
        source_reference=None,
        status="pending",
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    print(f"Created question: {question.id}")

finally:
    db.close()
