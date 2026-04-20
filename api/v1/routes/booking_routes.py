from fastapi import APIRouter, HTTPException
from services.tourism_services import UserService, TourService, BookingService
from models.models import db

from core.logging_config import setup_logging

booking_router = APIRouter(prefix='/booking', tags=["booking"])

logger = setup_logging()

@booking_router.post('/bulk')
def bulk_bookings(data): #not sure bout this
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
                db.session.commit()
                
                results.append({
                    "status": "success", 
                    "user_id": user_id, 
                    "tour_id": tour_id,
                    "message": "Бронирование успешно"
                })
            except Exception as e:
                db.session.rollback()
                results.append({
                    "status": "error", 
                    "user_id": booking.get('user_id'), 
                    "tour_id": booking.get('tour_id'),
                    "error": str(e)
                })
        
        return {"results": results}
        
    except Exception as e:
        db.session.rollback()

        return {"error": str(e)}, 500