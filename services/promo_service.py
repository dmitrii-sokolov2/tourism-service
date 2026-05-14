from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy import select

from models.models import PromoCode

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
        promo_code = db.execute(select(PromoCode).where(PromoCode.id == promo_id)).scalars().one_or_none()

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