from fastapi import FastAPI
from app.database.connection import engine
from app.database.base import Base
from app.models import *
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.companies.router import router as companies_router
from app.applications.router import router as applications_router
from app.rounds.router import router as rounds_router

Base.metadata.create_all(bind=engine)
app=FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(applications_router)
app.include_router(rounds_router)

@app.get("/")
def root():
    return {"message":"Placement Tracker API Running"}
