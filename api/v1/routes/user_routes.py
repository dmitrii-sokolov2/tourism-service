from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from services.tourism_services import UserService, TourService
from models.models import User
from core.database import get_db

from logger_config import user_logger, api_logger

from exceptions.custom_exceptions import (
    UserNotFoundException, 
    UserValidationException, 
    UserEmailDuplicateException,
    TourNotFoundException,
    NoAvailableSlotsException, 
    TourNotActiveException,
    DuplicateBookingException,  
    BookingLimitException
)

from validators.user_validator import UserValidator
from schemes.user import UserCreateSchema, UserUpdateSchema, UserBulkDeleteSchema

user_router = APIRouter(prefix='/users', tags=['Users'])
user_validator = UserValidator()

@user_router.get('', status_code=200)
def get_users(db: Session = Depends(get_db)):
    try:
        api_logger.info("GET /api/v1/users - получение списка пользователей")
        users = db.execute(select(User)).scalars().all()
        user_logger.info(f"Найдено пользователей: {len(users)}")

        return [user.to_dict() for user in users]

    except Exception as e:
        user_logger.error(f"Ошибка при получении списка пользователей: {str(e)}", exc_info=True)

        raise HTTPException(status_code=422, detail="Failed to fetch users")

@user_router.post('', status_code=200)
def post_user(payload: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        data = payload.model_dump()

        api_logger.info(
            f'POST /api/v1/users - создание пользователя: {data.get("email")}'
        )

        # try:
        #     user_validator.validate_user(data, 'add')
        # except ValidationError:
        #     errors = user_validator.validate_with_details(data, 'add')
        #
        #     error_details = [
        #         {
        #             "field": ".".join(str(p) for p in err.path),
        #             "message": err.message,
        #             "value": err.instance
        #         }
        #         for err in errors
        #     ]
        #
        #     raise HTTPException(
        #         status_code=422,
        #         detail={
        #             "type": "Validation Error",
        #             "title": "Ошибка валидации данных пользователя",
        #             "errors": error_details
        #         }
        #     )
        #
        # UserService.validate_user_data(data, db)

        user = User(**data)

        db.add(user)
        db.commit()

        user_logger.info(
            f'Создан пользователь: {user.name} ({user.email}) ID: {user.id}'
        )

        return user.to_dict()

    # except (UserValidationException, UserEmailDuplicateException) as e:
    #     db.rollback()
    #
    #     raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.rollback()

        user_logger.error(
            f'Ошибка при создании пользователя: {str(e)}',
            exc_info=True
        )

        raise HTTPException(status_code=500, detail='Failed to create user')

@user_router.get('/{user_id}', status_code=200)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(f"GET /api/v1/users/{user_id} - получение пользователя")
        user = UserService.get_user_by_id(user_id, db)
        user_logger.debug(f"Пользователь найден: {user.name} (ID: {user.id})")

        return user.to_dict()

    except UserNotFoundException:
        user_logger.warning(f"Пользователь с ID {user_id} не найден")

        raise HTTPException(status_code=404, detail='User not found')

    except Exception as e:
        user_logger.error(f"Ошибка при получении пользователя {user_id}: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail='Failed to fetch user')

@user_router.put('/{user_id}', status_code=200)
def update_user(
        user_id: int,
        payload: UserUpdateSchema,
        db: Session = Depends(get_db)
):
    try:
        api_logger.info(f"PUT /api/v1/users/{user_id} - обновление пользователя")
        user = UserService.get_user_by_id(user_id, db)

        data = payload.model_dump(exclude_unset=True)

        if not data:
            raise HTTPException(
                status_code=400,
                detail='No JSON data provided'
            )

        user_logger.debug(f"Данные для обновления: {data}")

        UserService.validate_user_data(data, db, user)

        # user.name = data.get('name', user.name)
        # user.email = data.get('email', user.email)
        # user.phone = data.get('phone', user.phone)

        for key, value in data.items():
            setattr(user, key, value)

        db.commit()

        user_logger.info(
            f"Пользователь обновлен: {user.name} ({user.email}) ID: {user.id}"
        )

        return user.to_dict()

    except UserNotFoundException:
        user_logger.warning(f"Пользователь с ID {user_id} не найден для обновления")

        raise HTTPException(status_code=404, detail='User not found')

    except (UserValidationException, UserEmailDuplicateException) as e:
        db.rollback()
        user_logger.warning(f"Ошибка валидации при обновлении пользователя {user_id}: {str(e)}")

        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        db.rollback()
        user_logger.error(
            f'Неожиданная ошибка при обновлении пользователя {user_id}: {str(e)}',
            exc_info=True
        )

        raise HTTPException(status_code=500, detail='Failed to update user')

@user_router.delete('/{user_id}', status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(f"DELETE /api/v1/users/{user_id} - удаление пользователя")

        user = UserService.get_user_by_id(user_id, db)

        db.delete(user)
        db.commit()

        user_logger.info(
            f"Пользователь удален: {user.name} ({user.email}) ID: {user.id}"
        )

        return {'message': 'User deleted successfully'}

    except UserNotFoundException:
        user_logger.warning(f"Пользователь с ID {user_id} не найден для удаления")

        raise HTTPException(status_code=404, detail='User not found')

    except Exception as e:
        db.rollback()
        user_logger.error(
            f'Ошибка при удалении пользователя {user_id}: {str(e)}',
            exc_info=True
        )

        raise HTTPException(status_code=500, detail='Failed to delete user')

@user_router.delete('/bulk-delete', status_code=204)
def bulk_delete_users(
        payload: UserBulkDeleteSchema,
        db: Session = Depends(get_db)
):
    try:
        user_ids = payload.user_ids

        api_logger.info(
            f"DELETE /api/v1/users/bulk-delete - массовое удаление: {user_ids}"
        )

        users = db.execute(select(User).where(User.id.in_(user_ids))).scalars().all()

        found_ids = {user.id for user in users}
        missing_ids = [uid for uid in user_ids if uid not in found_ids]

        if missing_ids:
            user_logger.warning(f'Пользователи не найдены: {missing_ids}')

            raise HTTPException(
                status_code=404,
                detail=f'Users {missing_ids} not found'
            )

        users_with_bookings = [
            user.id for user in users if user.booked_tours
        ]

        if users_with_bookings:
            user_logger.warning(
                f'Пользователи с активными бронированиями: {users_with_bookings}'
            )

            raise HTTPException(
                status_code=422,
                detail=f'Cannot delete users {users_with_bookings}, they have active bookings'
            )

        stmt = delete(User).where(User.id.in_(user_ids))
        result = db.execute(stmt)

        db.commit()

        user_logger.info(
            f'Удалено пользователей: {result.rowcount}'
        )

        return {
            'message': f'Successfully deleted {result.rowcount} users',
        }

    except HTTPException:
        db.rollback()

        raise

    except Exception as e:
        db.rollback()

        user_logger.error(
            f"Ошибка при массовом удалении: {str(e)}",
            exc_info=True
        )

        raise HTTPException(status_code=500, detail='Failed to delete user')

@user_router.post('/{user_id}/book-tour/{tour_id}', status_code=200)
def post(user_id: int, tour_id: int, db: Session = Depends(get_db)):
    try:
        api_logger.info(
            f"POST /api/v1/users/{user_id}/book-tour/{tour_id} - бронирование тура"
        )

        user = UserService.get_user_by_id(user_id, db)
        tour = TourService.get_tour_by_id(tour_id, db)

        user_logger.debug(
            f"Бронирование: пользователь {user.name}, тур {tour.id}"
        )

        from services.tourism_services import ThreadSafeBookingService

        ThreadSafeBookingService.thread_safe_booking(user, tour)

        db.commit()

        user_logger.info(
            f"Тур забронирован: пользователь {user.name} (ID: {user.id}), тур {tour.id}"
        )

        return {
            'message': 'Тур успешно забронирован (потокобезопасно)',
            'user': user.to_dict(),
            'tour': tour.to_dict(),
            'remaining_slots': tour.available_slots
        }

    except (UserNotFoundException, TourNotFoundException):
        db.rollback()

        raise HTTPException(status_code=404, detail='User or Tour not found')

    except (
        NoAvailableSlotsException,
        TourNotActiveException,
        DuplicateBookingException,
        BookingLimitException
    ) as e:
        db.rollback()

        user_logger.warning(f'Ошибка бронирования: {str(e)}')

        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    except Exception as e:
        db.rollback()
        user_logger.error(
            f"Неожиданная ошибка при бронировании: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail='Failed to book tour'
        )