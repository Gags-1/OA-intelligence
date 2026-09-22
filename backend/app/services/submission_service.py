from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate


def create_submission(
    db: Session,
    submission_data: SubmissionCreate,
) -> Submission:

    submission = Submission(
        raw_text=submission_data.raw_text,
        input_type=submission_data.input_type,
        source=submission_data.source,
        source_reference=submission_data.source_reference,
        status="received",
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission


def get_submission(
    db: Session,
    submission_id: int,
) -> Submission | None:

    statement = select(Submission).where(
        Submission.id == submission_id
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()
