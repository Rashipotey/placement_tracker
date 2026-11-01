from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.applications.router import get_owned_application
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.round import Round
from app.models.user import User
from app.schemas.round import RoundCreate, RoundRead, RoundUpdate

router = APIRouter(prefix="/applications/{application_id}/rounds", tags=["Rounds"])


def get_round_or_404(db: Session, application_id: UUID, round_id: UUID) -> Round:
    round_ = (
        db.query(Round)
        .filter(Round.id == round_id, Round.application_id == application_id)
        .first()
    )
    if round_ is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return round_


@router.get("", response_model=list[RoundRead])
def list_rounds(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_application(db, application_id, current_user)
    return db.query(Round).filter(Round.application_id == application_id).all()


@router.post("", response_model=RoundRead, status_code=201)
def create_round(
    application_id: UUID,
    data: RoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_application(db, application_id, current_user)
    round_ = Round(**data.model_dump(), application_id=application_id)
    db.add(round_)
    db.commit()
    db.refresh(round_)
    return round_


@router.get("/{round_id}", response_model=RoundRead)
def get_round(
    application_id: UUID,
    round_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_application(db, application_id, current_user)
    return get_round_or_404(db, application_id, round_id)


@router.put("/{round_id}", response_model=RoundRead)
def update_round(
    application_id: UUID,
    round_id: UUID,
    data: RoundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_application(db, application_id, current_user)
    round_ = get_round_or_404(db, application_id, round_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(round_, field, value)
    db.commit()
    db.refresh(round_)
    return round_


@router.delete("/{round_id}", status_code=204)
def delete_round(
    application_id: UUID,
    round_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_owned_application(db, application_id, current_user)
    round_ = get_round_or_404(db, application_id, round_id)
    if application.round_id == round_.id:
        application.round_id = None
        db.flush()
    db.delete(round_)
    db.commit()
    return Response(status_code=204)
