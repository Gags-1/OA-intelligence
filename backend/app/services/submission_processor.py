import re
import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.question import Question
from app.models.submission import Submission
from app.services.embedding_service import generate_embedding
from app.services.vector_store import (
    search_similar_questions,
    upsert_question,
)


SEMANTIC_DUPLICATE_THRESHOLD = float(
    settings.SEMANTIC_DUPLICATE_THRESHOLD
)


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
    """
    Find an exact duplicate using the normalized text hash.

    The hash narrows down the candidates, and the normalized
    text comparison provides an explicit final verification.
    """

    question_hash = generate_question_hash(
        normalized_text
    )

    statement = select(Question).where(
        Question.normalized_text_hash == question_hash
    )

    result = db.execute(statement)

    candidates = result.scalars().all()

    for question in candidates:
        existing_normalized = normalize_question_text(
            question.question_text
        )

        if existing_normalized == normalized_text:
            return question

    return None


def find_semantic_duplicate(
    db: Session,
    question_text: str,
) -> Question | None:
    """
    Find an existing question that is semantically similar
    to the submitted question.
    """

    embedding = generate_embedding(
        question_text
    )

    similar_questions = search_similar_questions(
        embedding,
        limit=5,
    )

    if not similar_questions:
        return None

    top_match = similar_questions[0]

    if top_match.score < SEMANTIC_DUPLICATE_THRESHOLD:
        return None

    print(
        f"Semantic duplicate candidate found: "
        f"question_id={top_match.id}, "
        f"score={top_match.score:.4f}"
    )

    # Qdrant provides the question ID.
    # PostgreSQL remains the authoritative source.
    question = db.get(
        Question,
        top_match.id,
    )

    return question


def process_submission(
    db: Session,
    submission: Submission,
) -> Question:
    """
    Process a submitted question.

    Processing order:

    1. Normalize question text
    2. Generate deterministic hash
    3. Check exact duplicate
    4. Check semantic duplicate
    5. Create new question if no duplicate exists
    6. Generate embedding for the new question
    7. Store the embedding in Qdrant
    """

    submission.status = "processing"
    db.flush()

    try:
        # ---------------------------------------------------------
        # 1. Normalize question text
        # ---------------------------------------------------------

        normalized_text = normalize_question_text(
            submission.raw_text
        )

        # ---------------------------------------------------------
        # 2. Generate deterministic hash
        # ---------------------------------------------------------

        question_hash = generate_question_hash(
            normalized_text
        )

        # ---------------------------------------------------------
        # 3. Exact duplicate check
        # ---------------------------------------------------------

        existing_question = find_exact_duplicate(
            db,
            normalized_text,
        )

        if existing_question:
            submission.question_id = existing_question.id
            submission.status = "duplicate"

            db.commit()
            db.refresh(submission)

            return existing_question

        # ---------------------------------------------------------
        # 4. Semantic duplicate check
        # ---------------------------------------------------------

        semantic_duplicate = find_semantic_duplicate(
            db,
            submission.raw_text,
        )

        if semantic_duplicate:
            submission.question_id = semantic_duplicate.id
            submission.status = "semantic_duplicate"

            db.commit()
            db.refresh(submission)

            return semantic_duplicate

        # ---------------------------------------------------------
        # 5. No duplicate found — create new question
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 6. Generate embedding for new question
        # ---------------------------------------------------------

        embedding = generate_embedding(
            question.question_text
        )

        # ---------------------------------------------------------
        # 7. Store embedding in Qdrant
        # ---------------------------------------------------------

        upsert_question(
            question_id=question.id,
            question_text=question.question_text,
            embedding=embedding,
        )

        # ---------------------------------------------------------
        # 8. Finalize submission
        # ---------------------------------------------------------

        submission.question_id = question.id
        submission.status = "processed"

        db.commit()

        db.refresh(question)

        return question

    except Exception:
        db.rollback()

        submission.status = "failed"

        db.commit()
        db.refresh(submission)

        raise
