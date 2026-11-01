from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["Applications"])


def get_owned_application(db: Session, application_id: UUID, user: User) -> Application:
    # Missing -> 404; exists but owned by another user -> 403 (user decision,
    # CPT-11). The LLD on Confluence still says 404 for not-owned.
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this application")
    return application


def require_company(db: Session, company_id: UUID) -> None:
    if db.query(Company).filter(Company.id == company_id).first() is None:
        raise HTTPException(status_code=422, detail="Company does not exist")


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Application).filter(Application.user_id == current_user.id)
    if status is not None:
        query = query.filter(Application.status == status)
    return query.all()


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company(db, data.company_id)
    application = Application(**data.model_dump(), user_id=current_user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_application(db, application_id, current_user)


@router.put("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: UUID,
    data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_owned_application(db, application_id, current_user)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("company_id") is not None:
        require_company(db, changes["company_id"])
    for field, value in changes.items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_owned_application(db, application_id, current_user)
    db.delete(application)
    db.commit()
    return Response(status_code=204)
