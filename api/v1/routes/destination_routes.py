from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.tourism_services import DestinationService
from models.models import Destination
from schemes.destination import DestinationCreateSchema, DestinationUpdateSchema
from logger_config import destination_logger, api_logger
from core.database import get_db

from exceptions.custom_exceptions import (
    DestinationNotFoundException,
    DestinationValidationException,
    DestinationNameDuplicateException
)

from validators.destination_validator import DestinationValidator

destination_logger = destination_logger
destination_router = APIRouter(prefix='/destinations')
api_logger = api_logger

destination_validator = DestinationValidator()

@destination_router.get('', status_code=200)
def get_destinations(db: Session = Depends(get_db)):
    try:
        api_logger.info("GET /api/v1/destinations - получение списка направлений")
        destinations = db.execute(select(Destination)).scalars().all()
        destination_logger.info(f"Найдено направлений: {len(destinations)}")

        return [d.to_dict() for d in destinations]
    except Exception as e:
        destination_logger.error(f"Ошибка при получении списка направлений: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail='Failed to fetch destinations')

@destination_router.post('', status_code=200)
def create_destination(
        payload: DestinationCreateSchema,
        db: Session = Depends(get_db)
):
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

        db.add(destination)
        db.commit()

        destination_logger.info(
            f"Создано направление: {destination.name} (ID: {destination.id})"
        )

        return destination.to_dict()

    except (DestinationValidationException, DestinationNameDuplicateException) as e:
        db.rollback()

        destination_logger.error(
            f'Неожиданная ошибка при создании направления {str(e)}',
            exc_info=True
        )

        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@destination_router.get('/{destination_id}', status_code=200)
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(f"GET /api/destinations/{destination_id} - получение направления")
        destination = DestinationService.get_destination_by_id(destination_id, db)
        destination_logger.debug(f"Направление найдено: {destination.name} (ID: {destination.id})")

        return destination.to_dict()

    except DestinationNotFoundException:
        destination_logger.warning(f"Направление с ID {destination_id} не найдено")

        raise HTTPException(
            status_code=404,
            detail='Destination not found'
        )

    except Exception as e:
        destination_logger.error(
            f"Ошибка при получении направления {destination_id}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to fetch destination'
        )

@destination_router.put('/{destination_id}', status_code=200)
def update_destination(
        destination_id: int,
        payload: DestinationUpdateSchema,
        db: Session = Depends(get_db)
):
    try:
        api_logger.info(f"PUT /api/v1/destinations/{destination_id} - обновление направления")
        destination = DestinationService.get_destination_by_id(destination_id, db)

        data = payload.model_dump(exclude_unset=True)
        destination_logger.debug(f"Данные для обновления направления {destination_id}: {data}")

        DestinationService.validate_destination_data(data, destination)

        for field, value in data.items():
            setattr(destination, field, value)

        db.commit()

        destination_logger.info(
            f"Направление обновлено: {destination.name} (ID: {destination.id})"
        )

        return destination.to_dict()

    except DestinationNotFoundException:
        destination_logger.warning(
            f"Направление с ID {destination_id} не найдено для обновления"
        )

        raise HTTPException(status_code=404, detail='Destination not found')

    except (DestinationValidationException, DestinationNameDuplicateException) as e:
        db.rollback()

        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.rollback()

        destination_logger.error(
            f"Неожиданная ошибка при обновлении направления {destination_id}: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to fetch destination'
        )

@destination_router.delete('/{destination_id}', status_code=200)
def delete_destination(destination_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(f"DELETE /api/v1/destinations/{destination_id} - удаление направления")

        destination = DestinationService.get_destination_by_id(destination_id, db)

        if destination.tours:
            count = len(destination.tours)

            destination_logger.warning(
                f"Попытка удаления направления с связанными турами: {len(destination.tours)} туров"
            )

            raise HTTPException(
                status_code=422,
                detail=f'Невозможно удалить направление. С ним связано {count} туров'
            )

        db.delete(destination)
        db.commit()

        destination_logger.info(
            f"Направление удалено: {destination.name} (ID: {destination.id})"
        )

        return {'message': 'Destination deleted successfully'}

    except DestinationNotFoundException:
        destination_logger.warning(
            f"Направление с ID {destination_id} не найдено для удаления"
        )

        raise HTTPException(status_code=404, detail='Destination not found')

    except Exception as e:
        db.rollback()
        destination_logger.error(
            f"Неожиданная ошибка при удалении направления {destination_id}: {str(e)}", exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to delete destination'
        )

@destination_router.get('/coordinates', status_code=200)
def get_destinations_coordinates(db: Session = Depends(get_db)):
    try:
        destinations = db.execute(select(Destination)).scalars().all()
        result = []

        for dest in destinations:
            if dest.latitude and dest.longitude:
                price_in_rubles = int(dest.price * 50) if dest.price else 35000

                result.append({
                    'id': dest.id,
                    'name': dest.name,
                    'country': dest.country,
                    'lat': float(dest.latitude),
                    'lng': float(dest.longitude),
                    'tours': len(dest.tours),
                    'price': f'{price_in_rubles}'  # Теперь 1200 → 60000
                })

        if not result:
            result = [
                {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5,
                 'price': '60000', 'rating': 4.8, 'tour_type': 'Экскурсионный', 'hotel_stars': 4, 'transfer': True},
                {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3,
                 'price': '90000', 'rating': 4.9, 'tour_type': 'Гастрономический', 'hotel_stars': 5, 'transfer': True},
                {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8,
                 'price': '45000', 'rating': 4.7, 'tour_type': 'Пляжный', 'hotel_stars': 4, 'transfer': False}
            ]

        return result

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

        test_data = [
            {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5,
             'price': '60000', 'rating': 4.8, 'tour_type': 'Экскурсионный', 'hotel_stars': 4, 'transfer': True},
            {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3,
             'price': '90000', 'rating': 4.9, 'tour_type': 'Гастрономический', 'hotel_stars': 5, 'transfer': True},
            {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8,
             'price': '45000', 'rating': 4.7, 'tour_type': 'Пляжный', 'hotel_stars': 4, 'transfer': False}
        ]
        return test_data

    except Exception as e:
        print(f"Ошибка в /api/destinations/coordinates: {str(e)}")
        import traceback
        traceback.print_exc()

        test_data = [
            {'id': 1, 'name': 'Париж', 'country': 'Франция', 'lat': 48.8566, 'lng': 2.3522, 'tours': 5, 'price': '60000'},
            {'id': 2, 'name': 'Токио', 'country': 'Япония', 'lat': 35.6762, 'lng': 139.6503, 'tours': 3, 'price': '90000'},
            {'id': 3, 'name': 'Бали', 'country': 'Индонезия', 'lat': -8.3405, 'lng': 115.0920, 'tours': 8, 'price': '45000'}
        ]
        return test_data