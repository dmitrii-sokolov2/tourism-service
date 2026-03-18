from flask_restful import Resource
from flask import request
from resources.base_resource import BaseResource
from services.tourism_services import UserService, BookingService, TourService
from models.models import User
from core.extensions import db
from sqlalchemy import select, delete

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
from transfer.problem_details import ProblemDetails
from jsonschema.exceptions import ValidationError

user_validator = UserValidator()

class UserListResource(BaseResource):
    def get(self):
        try:
            api_logger.info("GET /api/users - получение списка пользователей")
            users = db.session.execute(select(User)).scalars().all()
            user_logger.info(f"Найдено пользователей: {len(users)}")
            return [user.to_dict() for user in users]
        except Exception as e:
            user_logger.error(f"Ошибка при получении списка пользователей: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch users")

    def post(self):
        try:
            if not request.data:
                api_logger.warning("Пустой запрос к /api/users")
                return {
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "Request body is empty or Content-Type is not application/json",
                    "instance": request.path
                }, 400
            try:
                data = request.get_json()
            except Exception as e:
                api_logger.warning(f"Ошибка парсинга JSON: {str(e)}")
                return {
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "Invalid JSON format",
                    "instance": request.path
                }, 400
            if data is None:
                api_logger.warning("JSON данные отсутствуют или равны null")
                return {
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "No JSON data provided",
                    "instance": request.path
                }, 400
            
            api_logger.info(f"POST /api/users - создание пользователя: {data.get('email')}")
            
            try:
                user_validator.validate_user(data, 'add')
                user_logger.debug("Валидация JSON схемы пройдена успешно")
            except ValidationError as e:
                errors = user_validator.validate_with_details(data, 'add')
                error_details = []
                
                for error in errors:
                    error_details.append({
                        "field": ".".join(str(path) for path in error.path),
                        "message": error.message,
                        "value": error.instance
                    })
                
                user_logger.warning(f"Ошибка валидации данных пользователя: {error_details}")
                
                problem_details = ProblemDetails(
                    type="Validation Error",
                    title="Ошибка валидации данных пользователя",
                    status=422,
                    detail="Данные не прошли валидацию",
                    instance=request.path,
                    errors=error_details
                )
                return problem_details.to_dict(), 422
            
            UserService.validate_user_data(data)
            
            user = User(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', '')
            )
            
            db.session.add(user)
            db.session.commit()
            user_logger.info(f"Создан пользователь: {user.name} ({user.email}) ID: {user.id}")
            
            return user.to_dict(), 201
            
        except (UserValidationException, UserEmailDuplicateException) as e:
            db.session.rollback()
            user_logger.warning(f"Ошибка валидации при создании пользователя: {str(e)}")
            return self.handle_exception(e, "User validation failed")
        except Exception as e:
            db.session.rollback()
            user_logger.error(f"Неожиданная ошибка при создании пользователя: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to create user")

class UserResource(BaseResource):
    def get(self, id):
        try:
            api_logger.info(f"GET /api/users/{id} - получение пользователя")
            user = UserService.get_user_by_id(id)
            user_logger.debug(f"Пользователь найден: {user.name} (ID: {user.id})")
            return user.to_dict()
        except UserNotFoundException as e:
            user_logger.warning(f"Пользователь с ID {id} не найден")
            return self.handle_exception(e, "User not found")
        except Exception as e:
            user_logger.error(f"Ошибка при получении пользователя {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch user")
    
    def put(self, id):
        try:
            api_logger.info(f"PUT /api/users/{id} - обновление пользователя")
            user = UserService.get_user_by_id(id)
            
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
            
            user_logger.debug(f"Данные для обновления: {data}")
            
            # Валидируем данные с учетом существующего пользователя
            UserService.validate_user_data(data, user)
            
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            
            db.session.commit()
            user_logger.info(f"Пользователь обновлен: {user.name} ({user.email}) ID: {user.id}")
            
            return user.to_dict()
        except UserNotFoundException as e:
            user_logger.warning(f"Пользователь с ID {id} не найден для обновления")
            return self.handle_exception(e, "User not found")
        except (UserValidationException, UserEmailDuplicateException) as e:
            db.session.rollback()
            user_logger.warning(f"Ошибка валидации при обновлении пользователя {id}: {str(e)}")
            return self.handle_exception(e, "User validation failed")
        except Exception as e:
            db.session.rollback()
            user_logger.error(f"Неожиданная ошибка при обновлении пользователя {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to update user")
    
    def delete(self, id):
        try:
            api_logger.info(f"DELETE /api/users/{id} - удаление пользователя")
            user = UserService.get_user_by_id(id)
                
            db.session.delete(user)
            db.session.commit()
            user_logger.info(f"Пользователь удален: {user.name} ({user.email}) ID: {user.id}")
            
            return {'message': 'User deleted successfully'}
        except UserNotFoundException as e:
            user_logger.warning(f"Пользователь с ID {id} не найден для удаления")
            return self.handle_exception(e, "User not found")
        except Exception as e:
            db.session.rollback()
            user_logger.error(f"Ошибка при удалении пользователя {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to delete user")

class UserBulkDeleteResource(BaseResource):
    def delete(self):
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
                
            user_ids = data.get('user_ids', [])
            api_logger.info(f"DELETE /api/users/bulk-delete - массовое удаление: {user_ids}")
            
            if not user_ids:
                raise UserValidationException('user_ids', user_ids, "Список ID пользователей не может быть пустым")
            
            non_existent_users = []
            for user_id in user_ids:
                user = db.session.get(User, user_id)
                if not user:
                    non_existent_users.append(user_id)
            
            if non_existent_users:
                user_logger.warning(f"Пользователи не найдены: {non_existent_users}")
                raise UserNotFoundException(
                    non_existent_users, 
                    f"Пользователи с ID {non_existent_users} не найдены"
                )
            
            users_with_bookings = []
            for user_id in user_ids:
                user = db.session.get(User, user_id)
                if user.booked_tours:
                    users_with_bookings.append(user_id)
            
            if users_with_bookings:
                user_logger.warning(f"Пользователи с активными бронированиями: {users_with_bookings}")
                raise UserValidationException(
                    'bookings',
                    users_with_bookings,
                    f"Невозможно удалить пользователей {users_with_bookings}. У них есть активные бронирования"
                )
            
            stmt = delete(User).where(User.id.in_(user_ids))
            result = db.session.execute(stmt)
            db.session.commit()
            
            user_logger.info(f"Массовое удаление завершено: удалено {result.rowcount} пользователей")
            
            return {'message': f'Successfully deleted {result.rowcount} users'}
            
        except (UserNotFoundException, UserValidationException) as e:
            db.session.rollback()
            user_logger.warning(f"Ошибка валидации при массовом удалении: {str(e)}")
            return self.handle_exception(e, "Bulk delete validation failed")
        except Exception as e:
            db.session.rollback()
            user_logger.error(f"Неожиданная ошибка при массовом удалении: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to delete users")

class UserBookTourResource(BaseResource):
    def post(self, user_id, tour_id):
        try:
            api_logger.info(f"POST /api/users/{user_id}/book-tour/{tour_id} - бронирование тура")
            user = UserService.get_user_by_id(user_id)
            tour = TourService.get_tour_by_id(tour_id)
            
            user_logger.debug(f"Бронирование: пользователь {user.name}, тур {tour.id}")
            
            from services.tourism_services import ThreadSafeBookingService
            booking_result = ThreadSafeBookingService.thread_safe_booking(user, tour)
            
            db.session.commit()
            user_logger.info(f"Тур забронирован: пользователь {user.name} (ID: {user.id}), тур {tour.id}")
            
            return {
                'message': 'Тур успешно забронирован (потокобезопасно)',
                'user': user.to_dict(),
                'tour': tour.to_dict(),
                'remaining_slots': tour.available_slots
            }
            
        except (UserNotFoundException, TourNotFoundException, 
                NoAvailableSlotsException, TourNotActiveException,
                DuplicateBookingException, BookingLimitException) as e:
            db.session.rollback()
            user_logger.warning(f"Ошибка бронирования: {str(e)}")
            return self.handle_exception(e, "Booking validation failed")
        except Exception as e:
            db.session.rollback()
            user_logger.error(f"Неожиданная ошибка при бронировании: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to book tour")