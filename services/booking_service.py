from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy import select

from models.models import (
    UserTour,
    PromoCode,
    User,
    Tour
)
from schemes import booking
from services.promo_service import PromoService
from schemes.promocode import PromoValidateSchema
from exceptions.custom_exceptions import NoAvailableSlotsException, TourNotActiveException, DuplicateBookingException, \
    BookingLimitException
from logger_config import user_logger, tour_logger

class BookingService:
    MAX_BOOKINGS_PER_USER = 5

    @staticmethod
    def create_booking(
            user_id: int,
            tour_id: int,
            db: Session
    ) -> UserTour:
        user = db.get(User, user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        tour = db.get(Tour, tour_id)

        if not tour:
            raise HTTPException(
                status_code=404,
                detail="Tour not found"
            )

        if tour.available_slots <= 0:
            raise NoAvailableSlotsException(
                tour.id,
                tour.available_slots
            )

        if not tour.is_active:
            raise TourNotActiveException(tour.id)

        exists = db.query(UserTour).filter_by(
            user_id=user_id,
            tour_id=tour_id
        ).first()

        if exists:
            raise DuplicateBookingException(user_id, tour_id)

        count = db.query(UserTour).filter_by(user_id=user_id).count()

        if count >= BookingService.MAX_BOOKINGS_PER_USER:
            raise BookingLimitException(
                user.id,
                count,
                BookingService.MAX_BOOKINGS_PER_USER
            )

        tour.available_slots -= 1

        booking = UserTour(
            user_id=user_id,
            tour_id=tour_id
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        user_logger.info(
            f"Пользователь {user.name} забронировал тур {tour.id}"
        )

        tour_logger.info(
            f"Тур {tour.id} забронирован пользователем {user.name}"
        )

        return booking


    @staticmethod
    def apply_promo(data: dict, booking_id: int, db: Session):
        booking = db.get(
            UserTour,
            booking_id
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        promo = db.execute(
            select(PromoCode).where(
                PromoCode.code == data["code"]
            )
        ).scalar_one_or_none()

        if not promo:
            raise HTTPException(
                status_code=404,
                detail="Promo code not found"
            )

        price = booking.tour.destination.price

        result = PromoService.validate_promo(
            promo,
            price
        )

        booking.promo_code_id = promo.id
        promo.used_count += 1

        db.commit()
        db.refresh(booking)

        return {
            "booking_id": booking.id,
            "promo_id": promo.id,
            "promo_code": promo.code,
            "original_price": result["original_price"],
            "final_price": result["final_price"],
            "discount_value": result["discount_value"],
            "status": booking.status
        }

    @staticmethod
    def get_booking_list(db: Session) -> list[UserTour]:
        bookings = db.execute(
            select(UserTour).order_by(UserTour.id)
        ).scalars().all()

        return [booking for booking in bookings]

    @staticmethod
    def get_booking_by_id(booking_id: int, db: Session) -> UserTour:
        booking = db.execute(
            select(UserTour).where(UserTour.id == booking_id)
        ).scalars().one_or_none()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        return booking
