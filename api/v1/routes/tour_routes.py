from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.tourism_services import TourService, DestinationService
from models.models import Tour, Destination
from core.database import get_db
from schemes.tour import TourCreateSchema
from logger_config import tour_logger, api_logger

from exceptions.custom_exceptions import (
    TourNotFoundException,
    TourValidationException, 
    TourDateException,
    DestinationNotFoundException
)

from validators.tour_validator import TourValidator
from jsonschema.exceptions import ValidationError

tour_router = APIRouter(prefix='/tours', tags=['Tours'])
tour_logger = tour_logger
api_logger = api_logger

tour_validator = TourValidator()

@tour_router.get('', status_code=201)
def get_tours(db: Session = Depends(get_db)):
    try:
        api_logger.info("GET /api/v1/tours - получение списка туров")
        tours = db.execute(select(Tour)).scalars().all()
        tour_logger.info(f"Найдено туров: {len(tours)}")

        return [t.to_dict() for t in tours]

    except Exception as e:
        tour_logger.error(f"Ошибка при получении списка туров: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail=str(e))

@tour_router.get('/available', status_code=200)
def get_available_tours(db: Session = Depends(get_db)):
    try:
        api_logger.info("GET /api/v1/tours/available - получение доступных туров")
        available_tours = TourService.get_available_tours(db)
        tour_logger.info(f"Найдено доступных туров: {len(available_tours)}")

        return [tour.to_dict() for tour in available_tours]

    except Exception as e:
        tour_logger.error(f"Ошибка при получении доступных туров: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail='Failed to fetch available tours')

@tour_router.post('', status_code=200)
def post_tour(payload: TourCreateSchema, db: Session = Depends(get_db)):
    try:
        api_logger.info(
            f'POST /api/v1/tours - создание тура для направления {payload.destination_id}'
        )

        data = payload.model_dump()

        try:
            tour_validator.validate_tour(data, 'add')

        except ValidationError:
            errors = tour_validator.validate_with_details(data, 'add')

            error_details = [
                {
                    "field": ".".join(str(p) for p in err.path),
                    "message": err.message,
                    "value": err.instance
                }
                for err in errors
            ]

            raise HTTPException(status_code=422, detail=error_details)

        TourService.validate_tour_creation(data, db)

        destination = db.get(Destination, data.get('destination_id'))

        if not destination:
            raise HTTPException(status_code=404, detail=f'Destination {payload.destination_id} not found')

        tour = Tour(**data)

        db.add(tour)
        db.commit()

        tour_logger.info(
            f"Создан тур: ID {tour.id} для направления '{destination.name}'"
        )

        return tour.to_dict()

    except (TourValidationException, TourDateException) as e:
        db.rollback()

        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        tour_logger.error(
            f'Ошибка при создании тура: {str(e)}',
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to create tour'
        )

@tour_router.get('/{tour_id}', status_code=200)
def get_tour(tour_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(f"GET /api/v1/tours/{tour_id} - получение тура")

        tour = TourService.get_tour_by_id(tour_id, db)

        tour_logger.debug(
            f"Тур найден: ID {tour.id}, направление: {tour.destination.name}"
        )

        return tour.to_dict()

    except TourNotFoundException:
        tour_logger.warning(f"Тур с ID {tour_id} не найден")

        raise HTTPException(status_code=404, detail=f'Tour {tour_id} not found')

    except Exception as e:
        tour_logger.error(
            f"Ошибка при получении тура {tour_id}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(status_code=500, detail='Failed to fetch tour')

@tour_router.put('/{tour_id}', status_code=200)
def update_tour(
        tour_id: int,
        payload: TourCreateSchema,
        db: Session = Depends(get_db)
):
    try:
        api_logger.info(f"PUT /api/v1/tours/{tour_id} - обновление тура")

        tour = TourService.get_tour_by_id(tour_id, db)

        data = payload.model_dump(exclude_unset=True)

        if not data:
            raise HTTPException(
                status_code=400,
                detail='No data provided for update'
            )

        tour_logger.debug(f"Данные для обновления тура {tour_id}: {data}")

        try:
            tour_validator.validate_tour(data, 'update')
        except ValidationError:
            errors = tour_validator.validate_with_details(data, 'update')
            error_details = [
                {
                    "field": ".".join(str(p) for p in err.path),
                    "message": err.message,
                    "value": err.instance
                }
                for err in errors
            ]

            raise HTTPException(
                status_code=422,
                detail={
                    "type": "Validation Error",
                    "title": "Ошибка валидации данных тура",
                    "errors": error_details
                }
            )

        if 'destination_id' in data and data['destination_id'] != tour.destination_id:
            DestinationService.get_destination_by_id(data['destination_id'], db)

        if 'start_date' in data or 'end_date' in data:
            from datetime import datetime

            start_date = data.get('start_date', tour.start_date)
            end_date = data.get('end_date', tour.end_date)

            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')

                if end <= start:
                    raise TourDateException(start_date, end_date)

            except ValueError:
                raise TourValidationException(
                    'dates',
                    f"{start_date}/{end_date}",
                    "Некорректный формат дат. Используйте YYYY-MM-DD"
                )

        if 'available_slots' in data and data['available_slots'] < 0:
            raise TourValidationException(
                'available_slots',
                data['available_slots'],
                "Количество мест не может быть отрицательным")

        # tour.destination_id = data.get('destination_id', tour.destination_id)
        # tour.start_date = data.get('start_date', tour.start_date)
        # tour.end_date = data.get('end_date', tour.end_date)
        # tour.available_slots = data.get('available_slots', tour.available_slots)
        # tour.is_active = data.get('is_active', tour.is_active)

        for key, value in data.items():
            setattr(tour, key, value)

        db.commit()
        tour_logger.info(f"Тур обновлен: ID {tour.id}")

        return tour.to_dict()

    except TourNotFoundException as e:
        tour_logger.warning(f"Тур с ID {tour_id} не найден для обновления")

        raise HTTPException(status_code=404, detail=f'Tour {tour_id} not found')

    except (TourValidationException, TourDateException, DestinationNotFoundException) as e:
        db.rollback()
        tour_logger.warning(f"Ошибка валидации при обновлении тура {tour_id}: {str(e)}")

        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.rollback()
        tour_logger.error(
            f"Неожиданная ошибка при обновлении тура {tour_id}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(status_code=500, detail='Failed to fetch tour')

@tour_router.delete('/{tour_id}', status_code=204)
def delete_tour(tour_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(f"DELETE /api/v1/tours/{tour_id} - удаление тура")
        tour = TourService.get_tour_by_id(tour_id, db)

        if tour.users:
            tour_logger.warning(f"Попытка удаления тура с активными бронированиями: {len(tour.users)} бронирований")

            raise TourValidationException(
                'bookings',
                len(tour.users),
                f"Невозможно удалить тур. На него есть {len(tour.users)} активных бронирований"
            )

        db.delete(tour)
        db.commit()
        tour_logger.info(f"Тур удален: ID {tour.id}")

        return {'message': 'Tour deleted successfully'}

    except TourNotFoundException as e:
        tour_logger.warning(f"Тур с ID {tour_id} не найден для удаления")

        raise HTTPException(status_code=404, detail=f'Tour {tour_id} not found')

    except TourValidationException as e:
        db.rollback()
        tour_logger.warning(f"Ошибка валидации при удалении тура {tour_id}: {str(e)}")

        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.rollback()
        tour_logger.error(f"Неожиданная ошибка при удалении тура {tour_id}: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail='Failed to fetch tour')

