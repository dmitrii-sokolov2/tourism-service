from fastapi import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemes.booking import BookingToursSchema
from services.tourism_services import UserService, TourService, BookingService
from core.database import get_db

from logging import getLogger

booking_router = APIRouter(prefix='/booking', tags=["booking"])

logger = getLogger(__name__)

@booking_router.post('/bulk')
def bulk_bookings(
        payload: BookingToursSchema,
        db: Session = Depends(get_db)
):
    try:
        results = []

        for booking in payload.tours:
                user_id = booking.user_id
                tour_id = booking.tour_id

                user = UserService.get_user_by_id(user_id, db)
                tour = TourService.get_tour_by_id(tour_id, db)

                BookingService.create_booking(user, tour)

                db.commit()

                results.append({
                    "status": "success",
                    "user_id": user_id,
                    "tour_id": tour_id,
                    "message": "Бронирование успешно"
                })
        return results

    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=str(e))


