from pydantic import BaseModel
from typing import Optional


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    done: bool


class TaskOut(BaseModel):
    id: str
    title: str
    done: bool
    uid: str