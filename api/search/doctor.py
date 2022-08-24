from redis_om import (JsonModel, Field, EmbeddedJsonModel)
from typing import Optional, List
from pydantic import EmailStr
from datetime import datetime, date

class User(EmbeddedJsonModel):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: EmailStr = Field(index=True)
    password: str = Field()
    registered_at: datetime = Field(index=True)
    confirmed: bool = Field()
    role: str = Field()

class Specialization(EmbeddedJsonModel):
    id: int = Field(index=True)
    name: str = Field(index=True)
    image: str = Field()

class Qualification(EmbeddedJsonModel):
    qualifications_name: List[str] = Field(index=True)
    procurement_year: List[str] = Field(index=True)
    institute_name: List[date] = Field(index=True)

class Slot(EmbeddedJsonModel): 
    id: int = Field(index=True)
    day: str = Field(index=True)
    start: str = Field() 
    end: str = Field() 
    consultation_fee: int = Field()
    appointment_duration: int = Field()
    num_slots: int = Field()

class Doctor(JsonModel):
    id: int = Field(index=True)
    user: User
    # Indexed for full text search 
    description: str = Field(index=True, full_text_search=True)
    image: str = Field()
    rating: int = Field(index=True)
    specializations: Specialization
    qualifications: Qualification
    slot: Slot
