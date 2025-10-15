from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.models import user, organization, account, journal
from app.api.routes import auth, organizations, accounts, journals, reports

# Ensure models are imported before create_all
user  # noqa
organization  # noqa
account  # noqa
journal  # noqa

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"]) 
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"]) 
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"]) 
app.include_router(journals.router, prefix="/journals", tags=["journals"]) 
app.include_router(reports.router, prefix="/reports", tags=["reports"]) 

# Create tables if not exist
from app.models.base import Base  # noqa: E402

Base.metadata.create_all(bind=engine)


@app.get("/healthz")
def healthcheck():
    return {"status": "ok", "environment": settings.environment}
