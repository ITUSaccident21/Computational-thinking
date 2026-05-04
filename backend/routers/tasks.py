from fastapi import APIRouter, Depends, HTTPException
from services.firebase_service import verify_token, db
from schemas.task import TaskCreate, TaskUpdate, TaskOut
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

router = APIRouter()


@router.post("/", response_model=TaskOut)
def create_task(task: TaskCreate, user: dict = Depends(verify_token)):
    """Add a new task for the current user."""
    doc_ref = db.collection("tasks").document()
    data = {
        "uid": user["uid"],
        "title": task.title,
        "done": False,
        "created_at": SERVER_TIMESTAMP,
    }
    doc_ref.set(data)
    return TaskOut(id=doc_ref.id, title=task.title, done=False, uid=user["uid"])


@router.get("/")
def get_tasks(user: dict = Depends(verify_token)):
    """Get all tasks belonging to the current user."""
    docs = (
        db.collection("tasks")
        .where("uid", "==", user["uid"])
        .order_by("created_at")
        .stream()
    )
    result = []
    for doc in docs:
        d = doc.to_dict()
        result.append({
            "id": doc.id,
            "title": d.get("title", ""),
            "done": d.get("done", False),
            "uid": d.get("uid", ""),
        })
    return result


@router.patch("/{task_id}")
def update_task(task_id: str, update: TaskUpdate, user: dict = Depends(verify_token)):
    """Toggle done status of a task."""
    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only allow owner to update
    if doc.to_dict().get("uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    doc_ref.update({"done": update.done})
    return {"id": task_id, "done": update.done, "message": "Updated"}


@router.delete("/{task_id}")
def delete_task(task_id: str, user: dict = Depends(verify_token)):
    """Delete a task."""
    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Task not found")

    if doc.to_dict().get("uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    doc_ref.delete()
    return {"message": "Deleted"}