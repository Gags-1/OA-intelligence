from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
)
from app.services.submission_service import (
    create_submission,
    get_submission,
)


router = APIRouter(
    prefix="/submissions",
    tags=["submissions"],
)


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_submission_endpoint(
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db),
):
    return create_submission(db, submission_data)


@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse,
)
def get_submission_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
):
    submission = get_submission(db, submission_id)

    if submission is None:
        raise HTTPException(
            status_code=404,
            detail="Submission not found",
        )

    return submission
