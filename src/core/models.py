from pydantic import BaseModel, Field, EmailStr, BeforeValidator, model_validator
from typing import List, Dict, Optional, Annotated, Any, Union
from datetime import datetime

# Helper for ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class Subscription(BaseModel):
    name: str
    sede: str = "margherita"

    def __eq__(self, other):
        if isinstance(other, Subscription):
            return self.name == other.name and self.sede == other.sede
        return False

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    classi: List[Subscription] = []
    watched_teachers: List[Subscription] = []
    endpoint: str = "margherita" # Deprecated, kept for backward compatibility logic
    telegram_chat_id: Optional[str] = None
    fuzzy_teacher_matching: bool = False
    last_sostituzioni: Dict[str, Any] = {}
    last_notification: Dict[str, datetime] = {}

    @model_validator(mode='before')
    @classmethod
    def upgrade_legacy_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Upgrade classi
            if "classi" in data:
                new_classi = []
                for item in data["classi"]:
                    if isinstance(item, str):
                        new_classi.append({"name": item, "sede": data.get("endpoint", "margherita")})
                    else:
                        new_classi.append(item)
                data["classi"] = new_classi
            
            # Upgrade watched_teachers
            if "watched_teachers" in data:
                new_teachers = []
                for item in data["watched_teachers"]:
                    if isinstance(item, str):
                        new_teachers.append({"name": item, "sede": data.get("endpoint", "margherita")})
                    else:
                        new_teachers.append(item)
                data["watched_teachers"] = new_teachers
        return data

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
