from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.application import Application
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter(
    prefix="/companies", tags=["Companies"], dependencies=[Depends(get_current_user)]
)


def get_company_or_404(db: Session, company_id: UUID) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()


@router.post("", response_model=CompanyRead, status_code=201)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    return get_company_or_404(db, company_id)


@router.put("/{company_id}", response_model=CompanyRead)
def update_company(company_id: UUID, data: CompanyUpdate, db: Session = Depends(get_db)):
    company = get_company_or_404(db, company_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    company = get_company_or_404(db, company_id)
    if db.query(Application).filter(Application.company_id == company_id).first():
        raise HTTPException(status_code=409, detail="Company is referenced by an application")
    db.delete(company)
    db.commit()
    return Response(status_code=204)
