from fastapi import APIRouter, Depends
from services.firebase_service import verify_token

router = APIRouter()


@router.get("/me")
def get_me(user: dict = Depends(verify_token)):
    """Return current user info from Firebase token."""
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "name": user.get("name", ""),
    }