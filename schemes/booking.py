from pydantic import BaseModel

class BookingTour(BaseModel):
    user_id: int
    tour_id: int

class BookingToursSchema(BaseModel):
    tours: list[BookingTour]
