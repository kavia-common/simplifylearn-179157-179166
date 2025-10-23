from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import get_api_router
from src.core.config import get_settings
from src.db import Base
from src.db.session import engine, get_db

settings = get_settings()

app = FastAPI(
    title="ExplainLike5 Backend API",
    description="API for submitting topics and serving simplified explanations.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Service health and diagnostics"},
        {"name": "topics", "description": "Topic management"},
        {"name": "explanations", "description": "Explanations management"},
    ],
)

# CORS configuration
# Always include localhost:3000 plus any configured origins
allow_origins = ["http://localhost:3000"]
if settings.CORS_ORIGINS:
    if settings.CORS_ORIGINS.strip() == "*":
        allow_origins = ["*"]
    else:
        cfg = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
        allow_origins = list(set(allow_origins + cfg))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    Initialize database tables on application startup.
    """
    # Create all tables based on models metadata
    Base.metadata.create_all(bind=engine)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Simple endpoint to verify service is up.")
def health_check(db=Depends(get_db)):
    """
    Health check endpoint.

    Parameters:
    - None

    Returns:
    - A JSON object indicating health status.
    """
    # Touch the DB session to ensure DB layer is healthy/initialized
    _ = db
    return {"message": "Healthy"}

# Include sub-routers
app.include_router(get_api_router())
