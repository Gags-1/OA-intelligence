from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate
from app.queue.sqs import SQSQueue


def create_submission(
    db: Session,
    submission_data: SubmissionCreate,
) -> Submission:

    submission = Submission(
        raw_text=submission_data.raw_text,
        input_type=submission_data.input_type,
        source=submission_data.source,
        source_reference=submission_data.source_reference,
        company_id=submission_data.company_id,
        role=submission_data.role,
        difficulty=submission_data.difficulty,
        status="pending",
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    queue = SQSQueue()

    queue.send_submission_job(
        submission.id,
    )

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
