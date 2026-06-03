from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy import select

from models.models import UserTour, PromoCode
from services.promo_service import PromoService
from schemes.promocode import PromoValidateSchema

class BookingService:
    @staticmethod
    def apply_promo(data: dict, booking_id: int, db: Session):
        booking = db.get(
            UserTour,
            booking_id
        )

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        promo = db.get(
            PromoCode,
            data['promo_id']
        )

        if not promo:
            raise HTTPException(status_code=404, detail="PromoCode not found")

        validate_data = PromoValidateSchema(**data)
        PromoService.validate_promo(validate_data, db)

        booking.promo_code_id = promo.id
        promo.used_count += 1

        db.commit()
        db.refresh(booking)

        return {
            "booking_id": booking.id,
            "promo_id": promo.id,
            "promo_code": promo.code,
            "discount_percent": promo.discount_percent,
            "status": booking.status
        }
