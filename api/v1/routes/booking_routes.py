from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.tourism_services import UserService, TourService, BookingService
from core.database import get_db

from logging import getLogger

booking_router = APIRouter(prefix='/booking', tags=["booking"])

logger = getLogger(__name__)

@booking_router.post('/bulk')
def bulk_bookings(data, db: Session = Depends(get_db)):
    try:
        bookings = data.get('bookings', [])
        results = []
        for booking in bookings:
            try:
                user_id = booking['user_id']
                tour_id = booking['tour_id']
                
                user = UserService.get_user_by_id(user_id)
                tour = TourService.get_tour_by_id(tour_id)
                
                result = BookingService.create_booking(user, tour)
                db.commit()
                
                results.append({
                    "status": "success", 
                    "user_id": user_id, 
                    "tour_id": tour_id,
                    "message": "Бронирование успешно"
                })
            except Exception as e:
                db.rollback()
                results.append({
                    "status": "error", 
                    "user_id": booking.get('user_id'), 
                    "tour_id": booking.get('tour_id'),
                    "error": str(e)
                })
        
        return {"results": results}
        
    except Exception as e:
        db.rollback()

        return {"error": str(e)}, 500