from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import EmailStr
from redis_om import EmbeddedJsonModel, Field, JsonModel


class RedisUser(EmbeddedJsonModel):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: EmailStr = Field(index=True)
    password: str = Field()
    registered_at: datetime = Field(index=True)
    confirmed: bool = Field()
    role: str = Field()

class RedisSpecialization(EmbeddedJsonModel):
    id: Optional[int] = Field(index=True)
    name: Optional[str] = Field(index=True)
    image: Optional[str] = Field()

class RedisQualification(EmbeddedJsonModel):
    qualifications_name: Optional[List[str]] = Field(index=True)
    procurement_year: Optional[List[str]] = Field(index=True)
    institute_name: Optional[List[str]] = Field(index=True)

class RedisSlot(EmbeddedJsonModel): 
    id: Optional[int] = Field(index=True)
    day: Optional[str] = Field(index=True)
    start: Optional[str] = Field() 
    end: Optional[str] = Field() 
    consultation_fee: Optional[int] = Field()
    appointment_duration: Optional[int] = Field()
    num_slots: Optional[int] = Field()

class RedisDoctor(JsonModel):
    id: int = Field(index=True)
    user: RedisUser
    # Indexed for full text search 
    description: str = Field(index=True, full_text_search=True)
    image: str = Field()
    rating: int = Field(index=True)
    specializations: Optional[RedisSpecialization]
    qualifications: Optional[RedisQualification]
    slot: Any
