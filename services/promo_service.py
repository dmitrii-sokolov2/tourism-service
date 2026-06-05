from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy import select

from datetime import datetime, UTC

from models.models import PromoCode, UserTour
from schemes.promocode import PromoValidateSchema

class PromoService:
    @staticmethod
    def create_promo(promo_code: PromoCode, db: Session) -> dict:
        db.add(promo_code)
        db.commit()
        db.refresh(promo_code)

        return promo_code

    @staticmethod
    def get_promo_list(db: Session) -> list[PromoCode]:
        promo_codes = db.execute(select(PromoCode)).scalars().all()

        return [promo for promo in promo_codes]

    @staticmethod
    def get_available_promo_codes(db: Session) -> list[PromoCode]:
        promo_codes = db.execute(
            select(PromoCode).where(PromoCode.is_active)
        ).scalars().all()

        return [promo for promo in promo_codes]

    @staticmethod
    def get_promo_code(promo_id: int, db: Session) -> PromoCode:
        promo_code = db.execute(
            select(PromoCode).where(PromoCode.id == promo_id)
        ).scalars().one_or_none()

        if promo_code is None:
            raise HTTPException(
                status_code=404,
                detail='Promo code does not exist'
            )

        return promo_code

    @staticmethod
    def update_promo(promo_id: int, update_data : dict, db: Session) -> PromoCode:
        promo_code = db.execute(
            select(PromoCode).where(PromoCode.id == promo_id)
        ).scalars().one_or_none()

        if promo_code is None:
            raise HTTPException(
                status_code=404,
                detail='Promo code does not exist'
            )

        for key, value in update_data.items():
            setattr(promo_code, key, value)

        db.commit()
        db.refresh(promo_code)

        return promo_code

    @staticmethod
    def delete_promo(promo_id: int, db: Session):
        promo_code = db.execute(
            select(PromoCode).where(PromoCode.id == promo_id)
        ).scalars().one_or_none()

        if promo_code is None:
            raise HTTPException(
                status_code=404,
                detail='Promo code does not exist'
            )

        db.delete(promo_code)

        db.commit()

    @staticmethod
    def validate_promo(
        promo: PromoCode,
        price: float
    ) -> dict:
        if not promo.is_active:
            raise HTTPException(
                status_code=400,
                detail="Promo code is inactive"
            )

        if (
            promo.expires_at is not None
            and promo.expires_at < datetime.utcnow()
        ):
            raise HTTPException(
                status_code=400,
                detail="Promo code is expired"
            )

        if (
            promo.usage_limit is not None
            and promo.used_count >= promo.usage_limit
        ):
            raise HTTPException(
                status_code=400,
                detail="Promo usage limit exceeded"
            )

        if (
            promo.min_price is not None
            and price < promo.min_price
        ):
            raise HTTPException(
                status_code=400,
                detail="Minimum price not reached"
            )

        if promo.discount_percent is not None:
            discount_value = (
                price * promo.discount_percent
            ) / 100

        else:
            discount_value = promo.discount_amount or 0

        final_price = max(
            price - discount_value,
            0
        )

        return {
            "original_price": price,
            "final_price": final_price,
            "discount_value": discount_value
        }
