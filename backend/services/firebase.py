import os
import uuid
from datetime import datetime, timezone

import firebase_admin
from fastapi import Header, HTTPException
from firebase_admin import auth, credentials, firestore


def _has_firebase_credentials() -> bool:
    credential_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
    return os.path.exists(credential_path)


class _MemorySnapshot:
    def __init__(self, document_id: str, data: dict | None):
        self.id = document_id
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> dict:
        return dict(self._data or {})


class _MemoryDocumentRef:
    def __init__(self, collection: "_MemoryCollection", document_id: str | None = None):
        self._collection = collection
        self.id = document_id or uuid.uuid4().hex

    def set(self, data: dict) -> None:
        stored = dict(data)
        if "created_at" in stored and not isinstance(stored["created_at"], datetime):
            stored["created_at"] = datetime.now(timezone.utc)
        self._collection._documents[self.id] = stored

    def get(self) -> _MemorySnapshot:
        return _MemorySnapshot(self.id, self._collection._documents.get(self.id))

    def update(self, data: dict) -> None:
        if self.id not in self._collection._documents:
            raise KeyError(self.id)
        self._collection._documents[self.id].update(data)

    def delete(self) -> None:
        self._collection._documents.pop(self.id, None)


class _MemoryQuery:
    def __init__(self, documents: list[tuple[str, dict]]):
        self._documents = documents

    def where(self, field: str, operator: str, value):
        if operator != "==":
            raise ValueError("Only equality filters are supported in memory mode")
        return _MemoryQuery([(doc_id, data) for doc_id, data in self._documents if data.get(field) == value])

    def order_by(self, field: str):
        return _MemoryQuery(sorted(self._documents, key=lambda item: item[1].get(field)))

    def stream(self):
        return [_MemorySnapshot(doc_id, data) for doc_id, data in self._documents]


class _MemoryCollection:
    def __init__(self):
        self._documents: dict[str, dict] = {}

    def document(self, document_id: str | None = None):
        return _MemoryDocumentRef(self, document_id)

    def where(self, field: str, operator: str, value):
        return _MemoryQuery(list(self._documents.items())).where(field, operator, value)

    def order_by(self, field: str):
        return _MemoryQuery(list(self._documents.items())).order_by(field)


class _MemoryDB:
    def __init__(self):
        self._collections: dict[str, _MemoryCollection] = {}

    def collection(self, name: str):
        if name not in self._collections:
            self._collections[name] = _MemoryCollection()
        return self._collections[name]


if _has_firebase_credentials():
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json"))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    FIREBASE_ENABLED = True
else:
    db = _MemoryDB()
    FIREBASE_ENABLED = False


def verify_token(authorization: str = Header(...)) -> dict:
    """
    Extract and verify Bearer token from Authorization header.
    Returns decoded token payload (contains uid, email, etc.)
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization.split("Bearer ")[1]
    if not FIREBASE_ENABLED:
        email = token if "@" in token else f"{token}@local"
        return {"uid": token, "email": email, "name": email.split("@")[0]}

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")