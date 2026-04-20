from http.client import HTTPException

# from resources.base_resource import BaseResource
from services.tourism_services import DestinationService
from models.models import db, Destination
from sqlalchemy import select
# from flask import request
from fastapi import APIRouter, HTTPException
from schemes.destination import DestinationCreateSchema, DestinationUpdateSchema

from logger_config import destination_logger, api_logger

from exceptions.custom_exceptions import (
    DestinationNotFoundException,
    DestinationValidationException,
    DestinationNameDuplicateException
)

from validators.destination_validator import DestinationValidator
from transfer.problem_details import ProblemDetails
from jsonschema.exceptions import ValidationError

destination_logger = destination_logger
destination_router = APIRouter(prefix='/destinations')
api_logger = api_logger

destination_validator = DestinationValidator()

@destination_router.get('', status_code=200)
def get_destinations():
    try:
        api_logger.info("GET /api/v1/destinations - получение списка направлений")
        destinations = db.session.execute(select(Destination)).scalars().all()
        destination_logger.info(f"Найдено направлений: {len(destinations)}")

        return [d.to_dict() for d in destinations]
    except Exception as e:
        destination_logger.error(f"Ошибка при получении списка направлений: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail='Failed to fetch destinations')

@destination_router.post('', status_code=200)
def create_destination(payload: DestinationCreateSchema):
    try:
        api_logger.info(
            f"POST /api/v1/destinations - создание направления: {payload.name}"
        )

        data = payload.model_dump()
        DestinationService.validate_destination_data(data)

        destination = Destination(**data)

        # destination = Destination(
        #     name=payload.name,
        #     country=payload.country,
        #     description=payload.description,
        #     price=payload.price,
        #     duration_days=payload.duration_days,
        #     latitude=payload.latitude,
        #     longitude=payload.longitude,
        #     rating=payload.rating,
        #     tour_type=payload.tour_type,
        #     hotel_stars=payload.hotel_stars,
        #     transfer=payload.transfer
        # )

        db.session.add(destination)
        db.session.commit()

        destination_logger.info(
            f"Создано направление: {destination.name} (ID: {destination.id})"
        )

        return destination.to_dict()

    except (DestinationValidationException, DestinationNameDuplicateException) as e:
        db.session.rollback()

        destination_logger.error(
            f'Неожиданная ошибка при создании направления {str(e)}',
            exc_info=True
        )

        raise HTTPException(status_code=422, detail=str(e))

@destination_router.get('/{id}', status_code=200)
def get_destination(id: int):
    try:
        api_logger.info(f"GET /api/destinations/{id} - получение направления")
        destination = DestinationService.get_destination_by_id(id)
        destination_logger.debug(f"Направление найдено: {destination.name} (ID: {destination.id})")
        return destination.to_dict()

    except DestinationNotFoundException:
        destination_logger.warning(f"Направление с ID {id} не найдено")

        raise HTTPException(
            status_code=404,
            detail='Destination not found'
        )

    except Exception as e:
        destination_logger.error(
            f"Ошибка при получении направления {id}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to fetch destination'
        )

@destination_router.put('/{id}', status_code=200)
def put(id: int, payload: DestinationUpdateSchema):
    try:
        api_logger.info(f"PUT /api/v1/destinations/{id} - обновление направления")
        destination = DestinationService.get_destination_by_id(id)

        data = payload.model_dump(exclude_unset=True)
        destination_logger.debug(f"Данные для обновления направления {id}: {data}")

        DestinationService.validate_destination_data(data, destination)

        for field, value in data.items():
            setattr(destination, field, value)

        db.session.commit()

        destination_logger.info(
            f"Направление обновлено: {destination.name} (ID: {destination.id})"
        )

        return destination.to_dict()

    except DestinationNotFoundException:
        destination_logger.warning(
            f"Направление с ID {id} не найдено для обновления"
        )

        raise HTTPException(status_code=404, detail='Destination not found')

    except (DestinationValidationException, DestinationNameDuplicateException) as e:
        db.session.rollback()

        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.session.rollback()

        destination_logger.error(
            f"Неожиданная ошибка при обновлении направления {id}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to fetch destination'
        )

@destination_router.delete('/{id}', status_code=200)
def delete(id: int):
    try:
        api_logger.info(f"DELETE /api/v1/destinations/{id} - удаление направления")

        destination = DestinationService.get_destination_by_id(id)

        if destination.tours:
            count = len(destination.tours)

            destination_logger.warning(
                f"Попытка удаления направления с связанными турами: {len(destination.tours)} туров"
            )

            raise HTTPException(
                status_code=422,
                detail=f'Невозможно удалить направление. С ним связано {count} туров'
            )

        db.session.delete(destination)
        db.session.commit()

        destination_logger.info(
            f"Направление удалено: {destination.name} (ID: {destination.id})"
        )

        return {'message': 'Destination deleted successfully'}

    except DestinationNotFoundException as e:
        destination_logger.warning(f"Направление с ID {id} не найдено для удаления")

        raise HTTPException(status_code=404, detail='Destination not found')

    except Exception as e:
        db.session.rollback()
        destination_logger.error(
            f"Неожиданная ошибка при удалении направления {id}: {str(e)}", exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to delete destination'
        )