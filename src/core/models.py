from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing import List, Dict, Optional, Annotated, Any
from datetime import datetime

# Helper for ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    classi: List[str] = []
    watched_teachers: List[str] = []
    endpoint: str = "margherita"
    telegram_chat_id: Optional[str] = None
    fuzzy_teacher_matching: bool = False
    last_sostituzioni: Dict[str, Any] = {}
    last_notification: Dict[str, datetime] = {}

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
