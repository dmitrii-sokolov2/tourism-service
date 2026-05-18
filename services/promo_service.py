from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy import select
<<<<<<< Updated upstream

from models.models import PromoCode
=======
from datetime import datetime

from models.models import PromoCode
from schemes.promocode import PromoValidateSchema
>>>>>>> Stashed changes

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
            select(PromoCode).where(PromoCode.is_available)
        ).scalars().all()

        return [promo for promo in promo_codes]

    @staticmethod
    def get_promo_code(promo_id: int, db: Session) -> PromoCode:
<<<<<<< Updated upstream
        promo_code = db.execute(select(PromoCode).where(PromoCode.id == promo_id)).scalars().one_or_none()
=======
        promo_code = db.execute(
            select(PromoCode).where(PromoCode.id == promo_id)
        ).scalars().one_or_none()
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
        db.commit()
=======
        db.commit()

    @staticmethod
    def validate_promo(
            payload: PromoValidateSchema,
            db: Session
    ) -> dict:
        promo = db.execute(
            select(PromoCode).where(
               PromoCode.code == payload.code
            )
        ).scalars().one_or_none()

        if promo is None:
            raise HTTPException(
                status_code=404,
                detail='Promo code does not exist'
            )

        if not promo.is_available:
            raise HTTPException(
                status_code=400,
                detail='Promo code is inactive'
            )

        if promo.expires_at and promo.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail='Promo code is expired'
            )

        if (
            promo.usage_limit is not None
            and promo.used_count >= promo.usage_limit
        ):
            raise HTTPException(
                status_code=400,
                detail='Promo usage limit exceeded'
            )

        if (
            promo.min_price is not None
            and promo.min_price > payload.price
        ):
            raise HTTPException(
                status_code=400,
                detail='Promo minimum price exceeded'
            )

        discount_value = 0

        if promo.discount_percent:
            discount_value = (
                payload.price * promo.discount_percent
            ) // 100

        elif promo.discount_amount:
            discount_value = promo.discount_amount

        final_price = max(
            payload.price - discount_value,
            0
        )

        return {
            'valid': True,
            'code': promo.code,
            'original_price': payload.price,
            'final_price': final_price,
            'discount_percent': promo.discount_percent,
            'discount_amount': promo.discount_amount,
            'discount_value': discount_value
        }
>>>>>>> Stashed changes
