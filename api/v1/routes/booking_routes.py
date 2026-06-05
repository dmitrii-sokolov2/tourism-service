from fastapi import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemes.booking import (
    BookingToursSchema,
    BookingApplySchema,
    BookingApplyResponseSchema
)
from services.tourism_services import UserService, TourService #, BookingService
from services.booking_service import BookingService
from schemes.booking import BookingTour
from core.database import get_db

from logging import getLogger

booking_router = APIRouter(prefix='/booking', tags=["booking"])

logger = getLogger(__name__)

@booking_router.get('', status_code=200)
def get_bookings(db: Session = Depends(get_db)):
    bookings = BookingService.get_booking_list(db)

    return bookings

@booking_router.get('/{booking_id}', status_code=200)
def get_booking(
        booking_id: int,
        db: Session = Depends(get_db)
):
    return BookingService.get_booking_by_id(booking_id, db)

@booking_router.post('', status_code=201)
def create_booking(payload: BookingTour, db: Session = Depends(get_db)):
    try:
        booking = BookingService.create_booking(
            payload.user_id,
            payload.tour_id,
            db
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    return booking

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

@booking_router.post(
    '/{booking_id}/apply-promo',
    response_model=BookingApplyResponseSchema,
    status_code=200
)
def apply_promo(
    booking_id: int,
    payload: BookingApplySchema,
    db: Session = Depends(get_db)
):
    # try:
    data = payload.model_dump()
    booking = BookingService.apply_promo(data, booking_id, db)
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=400, detail=str(e))


    return booking