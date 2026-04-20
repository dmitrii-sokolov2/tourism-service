from schemes.tour import TourUpdateSchema, TourCreateSchema
from services.tourism_services import TourService, DestinationService
from models.models import db, Tour, Destination
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from logger_config import tour_logger, api_logger

from exceptions.custom_exceptions import (
    TourNotFoundException,
    TourValidationException, 
    TourDateException,
    DestinationNotFoundException
)

from validators.tour_validator import TourValidator
from transfer.problem_details import ProblemDetails
from jsonschema.exceptions import ValidationError

tour_router = APIRouter(prefix='/tours', tags=['tours'])
tour_logger = tour_logger
api_logger = api_logger

tour_validator = TourValidator()

@tour_router.get("")
def get_all_tours(
    sort: Optional[str] = Query(default=None),
    order: str = Query(default="asc")
):
    try:
        api_logger.info("GET /api/tours - получение списка туров")

        query = db.session.query(Tour).join(Tour.destination)

        allowed_fields = {
            "price": Destination.price,
            "name": Destination.name,
            "duration_days": Destination.duration_days,
            "start_date": Tour.start_date,
            "available_slots": Tour.available_slots,
        }

        if sort in allowed_fields:
            column = allowed_fields[sort]

            if order == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

            tours = query.all()
            tour_logger.info(f"Найдено туров: {len(tours)}")

        else:
            tours = query.all()
            tour_logger.info(f"Найдено туров: {len(tours)}")

        return [t.to_dict() for t in tours]

    except Exception as e:
        tour_logger.error(
            f"Ошибка при получении списка туров: {str(e)}",
            exc_info=True
        )

        raise HTTPException(status_code=500, detail="Failed to fetch tours")

@tour_router.post('')
def post_tour(payload: TourCreateSchema):
    try:
        api_logger.info(
            f"POST /api/tours - создание тура для направления {payload.destination_id}"
        )

        data = payload.model_dump()
        tour_logger.debug(f"Данные для создания тура: {data}")

        TourService.validate_tour_creation(data)

        destination = db.session.get(Destination, payload.destination_id)
        if not destination:
            raise HTTPException(status_code=404, detail="Destination not found")

        tour = Tour(
            destination_id=payload.destination_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            available_slots=payload.available_slots,
            is_active=payload.is_active
        )

        db.session.add(tour)
        db.session.commit()

        tour_logger.info(
            f"Создан тур: ID {tour.id} для направления '{destination.name}'"
        )

        return tour.to_dict()

    except (TourValidationException, TourDateException, DestinationNotFoundException) as e:
        db.session.rollback()
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create tour")

@tour_router.get('/{id}')
def get_tour(tour_id: int):
    try:
        api_logger.info(f"GET /api/vi/tours/{tour_id} - получение тура")
        tour = TourService.get_tour_by_id(tour_id)
        tour_logger.debug(f"Тур найден: ID {tour.id}, направление: {tour.destination.name}")

        return tour.to_dict()
    except TourNotFoundException:
        tour_logger.warning(f"Тур с ID {tour_id} не найден")
        raise HTTPException(status_code=404, detail="Tour not found")
    except Exception as e:
        tour_logger.error(f"Ошибка при получении тура {tour_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch tour")

@tour_router.put('/{id}')
def put_tour(id: int, payload: TourUpdateSchema):
    try:
        api_logger.info(f"PUT /api/tours/{id} - обновление тура")

        tour = TourService.get_tour_by_id(id)
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")

        data = payload.model_dump(exclude_unset=True)
        tour_logger.debug(f"Данные для обновления тура {id}: {data}")

        if "destination_id" in data:
            DestinationService.get_destination_by_id(data["destination_id"])

        if "start_date" in data or "end_date" in data:
            start_date = data.get("start_date", tour.start_date)
            end_date = data.get("end_date", tour.end_date)

            from datetime import datetime

            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")

                if end <= start:
                    raise TourDateException(start_date, end_date)

            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )

        for field, value in data.items():
            setattr(tour, field, value)

        db.session.commit()

        return {
            "message": "tour updated",
            "data": tour.to_dict()
        }

    except TourNotFoundException:
        raise HTTPException(status_code=404, detail="Tour not found")

    except (TourValidationException, TourDateException, DestinationNotFoundException) as e:
        db.session.rollback()
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update tour")

@tour_router.delete('/{id}')
def delete_tour(id: int):
    try:
        api_logger.info(f"DELETE /api/tours/{id} - удаление тура")
        tour = TourService.get_tour_by_id(id)

        if tour.users:
            tour_logger.warning(f"Попытка удаления тура с активными бронированиями: {len(tour.users)} бронирований")
            raise TourValidationException(
                'bookings',
                len(tour.users),
                f"Невозможно удалить тур. На него есть {len(tour.users)} активных бронирований"
            )

        db.session.delete(tour)
        db.session.commit()
        tour_logger.info(f"Тур удален: ID {tour.id}")

        return {'message': 'Tour deleted successfully'}

    except TourNotFoundException as e:
        tour_logger.warning(f"Тур с ID {id} не найден для удаления")
        raise HTTPException(status_code=404, detail="Tour not found")
    except TourValidationException as e:
        db.session.rollback()
        tour_logger.warning(f"Ошибка валидации при удалении тура {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete tour")
    except Exception as e:
        db.session.rollback()
        tour_logger.error(f"Неожиданная ошибка при удалении тура {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete tour")

@tour_router.get('/available')
def get_available():
    try:
        api_logger.info("GET /api/tours/available - получение доступных туров")
        available_tours = TourService.get_available_tours()
        tour_logger.info(f"Найдено доступных туров: {len(available_tours)}")
        return [tour.to_dict() for tour in available_tours]
    except Exception as e:
        tour_logger.error(f"Ошибка при получении доступных туров: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch available tours")