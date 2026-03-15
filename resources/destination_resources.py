from resources.base_resource import BaseResource
from services.tourism_services import DestinationService
from models import db, Destination
from sqlalchemy import select
from flask import request

# Импорты для логирования - ДОБАВЛЕНО
from logger_config import destination_logger, api_logger

from exceptions.custom_exceptions import (
    DestinationNotFoundException,
    DestinationValidationException,
    DestinationNameDuplicateException
)

from validators.destination_validator import DestinationValidator
from transfer.problem_details import ProblemDetails
from jsonschema.exceptions import ValidationError

# Настройка логирования - ОБНОВЛЕНО
destination_logger = destination_logger
api_logger = api_logger

# Инициализация валидатора
destination_validator = DestinationValidator()

class DestinationListResource(BaseResource):
    def get(self):
        try:
            api_logger.info("GET /api/destinations - получение списка направлений")
            destinations = db.session.execute(select(Destination)).scalars().all()
            destination_logger.info(f"Найдено направлений: {len(destinations)}")
            return [d.to_dict() for d in destinations]
        except Exception as e:
            destination_logger.error(f"Ошибка при получении списка направлений: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch destinations")
    
    def post(self):
        try:
            if not request.data:
                api_logger.warning("Пустой запрос к /api/destinations")
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
            
            api_logger.info(f"POST /api/destinations - создание направления: {data.get('name')}")
            
            # ВАЛИДАЦИЯ ПО JSON СХЕМЕ
            try:
                destination_validator.validate_destination(data, 'add')
                destination_logger.debug("Валидация JSON схемы пройдена успешно")
            except ValidationError as e:
                errors = destination_validator.validate_with_details(data, 'add')
                error_details = []
                
                for error in errors:
                    error_details.append({
                        "field": ".".join(str(path) for path in error.path),
                        "message": error.message,
                        "value": error.instance
                    })
                
                destination_logger.warning(f"Ошибка валидации данных направления: {error_details}")
                
                problem_details = ProblemDetails(
                    type="Validation Error",
                    title="Ошибка валидации данных направления",
                    status=422,
                    detail="Данные не прошли валидацию",
                    instance=request.path,
                    errors=error_details
                )
                return problem_details.to_dict(), 422
            
            # СУЩЕСТВУЮЩАЯ ЛОГИКА
            DestinationService.validate_destination_data(data)
            
            destination = Destination(
                name=data.get('name'),
                country=data.get('country'),
                description=data.get('description', ''),
                price=data.get('price', 0),
                duration_days=data.get('duration_days', 1)
            )
            
            db.session.add(destination)
            db.session.commit()
            destination_logger.info(f"Создано направление: {destination.name} (ID: {destination.id})")
            
            return destination.to_dict(), 201
            
        except (DestinationValidationException, DestinationNameDuplicateException) as e:
            db.session.rollback()
            destination_logger.warning(f"Ошибка валидации при создании направления: {str(e)}")
            return self.handle_exception(e, "Destination validation failed")
        except Exception as e:
            db.session.rollback()
            destination_logger.error(f"Неожиданная ошибка при создании направления: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to create destination")

class DestinationResource(BaseResource):
    def get(self, id):
        try:
            api_logger.info(f"GET /api/destinations/{id} - получение направления")
            destination = DestinationService.get_destination_by_id(id)
            destination_logger.debug(f"Направление найдено: {destination.name} (ID: {destination.id})")
            return destination.to_dict()
        except DestinationNotFoundException as e:
            destination_logger.warning(f"Направление с ID {id} не найдено")
            return self.handle_exception(e, "Destination not found")
        except Exception as e:
            destination_logger.error(f"Ошибка при получении направления {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch destination")
    
    def put(self, id):
        try:
            api_logger.info(f"PUT /api/destinations/{id} - обновление направления")
            destination = DestinationService.get_destination_by_id(id)
            
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
            
            destination_logger.debug(f"Данные для обновления направления {id}: {data}")
            
            # ВАЛИДАЦИЯ ПО JSON СХЕМЕ
            try:
                destination_validator.validate_destination(data, 'update')
                destination_logger.debug("Валидация JSON схемы пройдена успешно")
            except ValidationError as e:
                errors = destination_validator.validate_with_details(data, 'update')
                error_details = []
                
                for error in errors:
                    error_details.append({
                        "field": ".".join(str(path) for path in error.path),
                        "message": error.message,
                        "value": error.instance
                    })
                
                destination_logger.warning(f"Ошибка валидации при обновлении направления: {error_details}")
                
                problem_details = ProblemDetails(
                    type="Validation Error",
                    title="Ошибка валидации данных направления",
                    status=422,
                    detail="Данные не прошли валидацию",
                    instance=request.path,
                    errors=error_details
                )
                return problem_details.to_dict(), 422
            
            # СУЩЕСТВУЮЩАЯ ЛОГИКА
            DestinationService.validate_destination_data(data, destination)
            
            destination.name = data.get('name', destination.name)
            destination.country = data.get('country', destination.country)
            destination.description = data.get('description', destination.description)
            destination.price = data.get('price', destination.price)
            destination.duration_days = data.get('duration_days', destination.duration_days)
            
            db.session.commit()
            destination_logger.info(f"Направление обновлено: {destination.name} (ID: {destination.id})")
            
            return destination.to_dict()
            
        except DestinationNotFoundException as e:
            destination_logger.warning(f"Направление с ID {id} не найдено для обновления")
            return self.handle_exception(e, "Destination not found")
        except (DestinationValidationException, DestinationNameDuplicateException) as e:
            db.session.rollback()
            destination_logger.warning(f"Ошибка валидации при обновлении направления {id}: {str(e)}")
            return self.handle_exception(e, "Destination validation failed")
        except Exception as e:
            db.session.rollback()
            destination_logger.error(f"Неожиданная ошибка при обновлении направления {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to update destination")
    
    def delete(self, id):
        try:
            api_logger.info(f"DELETE /api/destinations/{id} - удаление направления")
            destination = DestinationService.get_destination_by_id(id)
                
            # Проверяем, есть ли связанные туры
            if destination.tours:
                destination_logger.warning(f"Попытка удаления направления с связанными турами: {len(destination.tours)} туров")
                raise DestinationValidationException(
                    'tours', 
                    len(destination.tours), 
                    f"Невозможно удалить направление. С ним связано {len(destination.tours)} туров"
                )
            
            db.session.delete(destination)
            db.session.commit()
            destination_logger.info(f"Направление удалено: {destination.name} (ID: {destination.id})")
            
            return {'message': 'Destination deleted successfully'}
            
        except DestinationNotFoundException as e:
            destination_logger.warning(f"Направление с ID {id} не найдено для удаления")
            return self.handle_exception(e, "Destination not found")
        except DestinationValidationException as e:
            db.session.rollback()
            destination_logger.warning(f"Ошибка валидации при удалении направления {id}: {str(e)}")
            return self.handle_exception(e, "Cannot delete destination")
        except Exception as e:
            db.session.rollback()
            destination_logger.error(f"Неожиданная ошибка при удалении направления {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to delete destination")