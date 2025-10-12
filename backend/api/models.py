"""
Pydantic модели для TaskFlowAI API
"""

from pydantic import BaseModel
from typing import Optional


class MessageRequest(BaseModel):
    text: str


class TaskRequest(BaseModel):
    content: str
    category: Optional[str] = None
    due_string: Optional[str] = None
    priority: Optional[int] = 1
    parent_id: Optional[str] = None
    is_recurring: Optional[bool] = False


class TaskUpdate(BaseModel):
    content: Optional[str] = None
    due_string: Optional[str] = None
    priority: Optional[int] = None
