from fastapi import APIRouter

router = APIRouter(tags=["health"])


# PUBLIC_INTERFACE
@router.get("/", summary="Health Check", description="Simple endpoint to verify service is up.")
def health_check():
    """Return health status."""
    return {"message": "Healthy"}
