from fastapi import APIRouter

from .health import router as health_router
from .explanations import router as explanations_router

# PUBLIC_INTERFACE
def get_api_router() -> APIRouter:
    """Create the root API router and include feature routers."""
    api_router = APIRouter()
    api_router.include_router(health_router)
    api_router.include_router(explanations_router)
    return api_router
