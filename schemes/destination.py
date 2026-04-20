from pydantic import BaseModel, Field
from typing import Optional

class DestinationCreateSchema(BaseModel):
    name: str
    country: str

    description: Optional[str] = ''

    price: Optional[float] = Field(default=0, ge=0)
    duration_days: Optional[int] = Field(default=1, ge=1)

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    rating: Optional[float] = Field(default=4.5, ge=0, le=5)

    tour_type: Optional[str] = 'Экскурсионный'
    hotel_stars: Optional[int] = Field(default=3, ge=1, le=5)

    transfer: Optional[bool] = False

class DestinationUpdateSchema(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None

    price: Optional[float] = Field(default=None, ge=0)
    duration_days: Optional[int] = Field(default=None, ge=1)

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    rating: Optional[float] = Field(default=None, ge=0, le=5)

    tour_type: Optional[str] = None
    hotel_stars: Optional[int] = Field(default=None, ge=1, le=5)

    transfer: Optional[bool] = None