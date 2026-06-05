from pydantic import BaseModel

class BookingTour(BaseModel):
    user_id: int
    tour_id: int

class BookingToursSchema(BaseModel):
    tours: list[BookingTour]

class BookingApplySchema(BaseModel):
    code: str


class BookingApplyResponseSchema(BaseModel):
    booking_id: int

    promo_id: int
    promo_code: str

    discount_percent: int | None = None
    discount_amount: float | None = None

    original_price: float
    final_price: float
    discount_value: float

    status: str