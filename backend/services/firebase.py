import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import HTTPException, Header

# Initialize Firebase Admin SDK
# Expects serviceAccountKey.json in the backend/ folder
cred = credentials.Certificate(
    os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
)
firebase_admin.initialize_app(cred)

db = firestore.client()


def verify_token(authorization: str = Header(...)) -> dict:
    """
    Extract and verify Bearer token from Authorization header.
    Returns decoded token payload (contains uid, email, etc.)
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization.split("Bearer ")[1]
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")