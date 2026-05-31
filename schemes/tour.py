from pydantic import BaseModel, Field
from typing import Optional

class TourUpdateSchema(BaseModel):
    destination_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    available_slots: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None

class TourCreateSchema(BaseModel):
    destination_id: int
    start_date: str
    end_date: str
    available_slots: Optional[int] = Field(default=10, ge=0)
    is_active: Optional[bool] = True