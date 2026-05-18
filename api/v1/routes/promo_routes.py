from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.promo_service import PromoService
<<<<<<< Updated upstream
from schemes.promocode import PromoCreateSchema, PromoUpdateSchema, PromoResponseSchema
=======
from schemes.promocode import (
    PromoCreateSchema,
    PromoUpdateSchema,
    PromoResponseSchema,
    PromoValidateSchema,
    PromoValidateResponseSchema
)
>>>>>>> Stashed changes
from models.models import PromoCode

promo_router = APIRouter(prefix='/promo', tags=['Promo'])

@promo_router.post(
    '',
    response_model=PromoResponseSchema,
<<<<<<< Updated upstream
    status_code=200
=======
    status_code=201
>>>>>>> Stashed changes
)
def create_promo_code(
        payload: PromoCreateSchema,
        db: Session = Depends(get_db)
):
    try:
        data = payload.model_dump()

        promo_code = PromoCode(**data)

        PromoService.create_promo(promo_code, db)

<<<<<<< Updated upstream
=======
        return promo_code

>>>>>>> Stashed changes
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=str(e))

@promo_router.get(
    '',
    response_model=list[PromoResponseSchema],
    status_code=200
)
def get_promo_codes(db: Session = Depends(get_db)):
    promo_codes = PromoService.get_promo_list(db)

    return promo_codes

@promo_router.get(
    '/active',
<<<<<<< Updated upstream
    response_model=PromoResponseSchema,
=======
    response_model=list[PromoResponseSchema],
>>>>>>> Stashed changes
    status_code=200
)
def get_available_promo_codes(db: Session = Depends(get_db)):
    promo_codes = PromoService.get_available_promo_codes(db)

    return promo_codes

@promo_router.get(
    '/{promo_id}',
    response_model=PromoResponseSchema,
    status_code=200
)
def get_promo_code(promo_id: int, db: Session = Depends(get_db)):
    promo_code = PromoService.get_promo_code(promo_id, db)

    return promo_code

@promo_router.put(
    '/{promo_id}',
    response_model=PromoResponseSchema,
    status_code=200
)
def update_promo_code(
        promo_id: int,
        payload: PromoUpdateSchema ,
        db: Session = Depends(get_db)
):
    update_data = payload.model_dump(exclude_unset=True)

    promo_code = PromoService.update_promo(
        promo_id,
        update_data,
        db
    )

    return promo_code

@promo_router.delete(
    '/{promo_id}',
    status_code=204
)
def delete_promo_code(promo_id: int, db: Session = Depends(get_db)):
    try:
        PromoService.delete_promo(promo_id, db)

<<<<<<< Updated upstream
        return {"message": "Promo code deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@promo_router.post('/validate', status_code=200)
def validate_promo_code(data: PromoCreateSchema, db: Session = Depends(get_db)):
    pass
=======
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=str(e))

@promo_router.post(
    '/validate',
    response_model=PromoValidateResponseSchema,
    status_code=200
)
def validate_promo_code(
        payload: PromoValidateSchema,
        db: Session = Depends(get_db)
):
    response = PromoService.validate_promo(payload, db)

    return response


>>>>>>> Stashed changes

# @promo_router.post('/apply', status_code=200) #in bookings router