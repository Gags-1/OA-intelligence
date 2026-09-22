import re
import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.submission import Submission


def normalize_question_text(text: str) -> str:
    """
    Normalize question text for deterministic comparisons.

    This is intentionally conservative.
    We don't want normalization to accidentally change
    the meaning of a programming question.
    """

    text = text.strip()

    # Convert multiple whitespace characters into one space
    text = re.sub(r"\s+", " ", text)

    # Case-insensitive comparison
    text = text.lower()

    return text


def generate_question_hash(normalized_text: str) -> str:
    """
    Generate a deterministic SHA-256 hash from normalized text.
    """

    return hashlib.sha256(
        normalized_text.encode("utf-8")
    ).hexdigest()


def find_exact_duplicate(
    db: Session,
    normalized_text: str,
) -> Question | None:

    question_hash = generate_question_hash(
        normalized_text
    )

    statement = select(Question).where(
        Question.normalized_text_hash == question_hash
    )

    result = db.execute(statement)

    candidates = result.scalars().all()

    # Hash gives us candidate rows.
    # We still verify normalized text to make the comparison explicit.
    for question in candidates:
        existing_normalized = normalize_question_text(
            question.question_text
        )

        if existing_normalized == normalized_text:
            return question

    return None


def process_submission(
    db: Session,
    submission: Submission,
) -> Question:

    # Submission has entered the processing stage.
    submission.status = "processing"
    db.flush()

    try:
        normalized_text = normalize_question_text(
            submission.raw_text
        )

        question_hash = generate_question_hash(
            normalized_text
        )

        existing_question = find_exact_duplicate(
            db,
            normalized_text,
        )

        # Existing question found.
        if existing_question:
            submission.question_id = existing_question.id
            submission.status = "duplicate"

            db.commit()
            db.refresh(submission)

            return existing_question

        # No duplicate found — create a new question.
        question = Question(
            question_text=submission.raw_text.strip(),
            normalized_text_hash=question_hash,
            question_type="unknown",
            company_id=1,
            role="unknown",
            difficulty="unknown",
            source=submission.source,
            source_reference=submission.source_reference,
            status="pending",
        )

        db.add(question)
        db.flush()

        submission.question_id = question.id
        submission.status = "processed"

        db.commit()

        db.refresh(question)

        return question

    except Exception:
        # Roll back the failed transaction.
        db.rollback()

        # Mark the submission as failed in a fresh transaction.
        submission.status = "failed"

        db.commit()
        db.refresh(submission)

        raise
