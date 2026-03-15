
from resources.base_resource import BaseResource
from services.tourism_services import TourService, DestinationService
from models import db, Tour, Destination
from sqlalchemy import select
from flask import request

# Импорты для логирования
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

# Настройка логирования
tour_logger = tour_logger
api_logger = api_logger

# Инициализация валидатора
tour_validator = TourValidator()

class TourListResource(BaseResource):
    def get(self):
        try:
            api_logger.info("GET /api/tours - получение списка туров")
            tours = db.session.execute(select(Tour)).scalars().all()
            tour_logger.info(f"Найдено туров: {len(tours)}")
            return [t.to_dict() for t in tours]
        except Exception as e:
            tour_logger.error(f"Ошибка при получении списка туров: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch tours")
    
    def post(self):
        try:
            if not request.data:
                api_logger.warning("Пустой запрос к /api/tours")
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
            
            api_logger.info(f"POST /api/tours - создание тура для направления {data.get('destination_id')}")
            
            try:
                tour_validator.validate_tour(data, 'add')
                tour_logger.debug("Валидация JSON схемы пройдена успешно")
            except ValidationError as e:
                errors = tour_validator.validate_with_details(data, 'add')
                error_details = []
                
                for error in errors:
                    error_details.append({
                        "field": ".".join(str(path) for path in error.path),
                        "message": error.message,
                        "value": error.instance
                    })
                
                tour_logger.warning(f"Ошибка валидации данных тура: {error_details}")
                
                problem_details = ProblemDetails(
                    type="Validation Error",
                    title="Ошибка валидации данных тура",
                    status=422,
                    detail="Данные не прошли валидацию",
                    instance=request.path,
                    errors=error_details
                )
                return problem_details.to_dict(), 422
            
            TourService.validate_tour_creation(data)
            destination = db.session.get(Destination, data.get('destination_id'))
            if not destination:
                raise DestinationNotFoundException(data.get('destination_id'))
            
            tour = Tour(
                destination_id=data.get('destination_id'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                available_slots=data.get('available_slots', 10),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(tour)
            db.session.commit()
            tour_logger.info(f"Создан тур: ID {tour.id} для направления '{destination.name}'")
            
            return tour.to_dict(), 201
            
        except (TourValidationException, TourDateException, DestinationNotFoundException) as e:
            db.session.rollback()
            tour_logger.warning(f"Ошибка валидации при создании тура: {str(e)}")
            return self.handle_exception(e, "Tour validation failed")
        except Exception as e:
            db.session.rollback()
            tour_logger.error(f"Неожиданная ошибка при создании тура: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to create tour")

class TourResource(BaseResource):
    def get(self, id):
        try:
            api_logger.info(f"GET /api/tours/{id} - получение тура")
            tour = TourService.get_tour_by_id(id)
            tour_logger.debug(f"Тур найден: ID {tour.id}, направление: {tour.destination.name}")
            return tour.to_dict()
        except TourNotFoundException as e:
            tour_logger.warning(f"Тур с ID {id} не найден")
            return self.handle_exception(e, "Tour not found")
        except Exception as e:
            tour_logger.error(f"Ошибка при получении тура {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch tour")
    
    def put(self, id):
        try:
            api_logger.info(f"PUT /api/tours/{id} - обновление тура")
            tour = TourService.get_tour_by_id(id)
            
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
            
            tour_logger.debug(f"Данные для обновления тура {id}: {data}")
            
            # ВАЛИДАЦИЯ ПО JSON СХЕМЕ
            try:
                tour_validator.validate_tour(data, 'update')
                tour_logger.debug("Валидация JSON схемы пройдена успешно")
            except ValidationError as e:
                errors = tour_validator.validate_with_details(data, 'update')
                error_details = []
                
                for error in errors:
                    error_details.append({
                        "field": ".".join(str(path) for path in error.path),
                        "message": error.message,
                        "value": error.instance
                    })
                
                tour_logger.warning(f"Ошибка валидации при обновлении тура: {error_details}")
                
                problem_details = ProblemDetails(
                    type="Validation Error",
                    title="Ошибка валидации данных тура",
                    status=422,
                    detail="Данные не прошли валидацию",
                    instance=request.path,
                    errors=error_details
                )
                return problem_details.to_dict(), 422
            
            if 'destination_id' in data and data['destination_id'] != tour.destination_id:
                DestinationService.get_destination_by_id(data['destination_id'])
            
            if 'start_date' in data or 'end_date' in data:
                start_date = data.get('start_date', tour.start_date)
                end_date = data.get('end_date', tour.end_date)
                
                from datetime import datetime
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if end <= start:
                        raise TourDateException(start_date, end_date)
                except ValueError:
                    raise TourValidationException('dates', f"{start_date}/{end_date}", "Некорректный формат дат. Используйте YYYY-MM-DD")
            
            if 'available_slots' in data and data['available_slots'] < 0:
                raise TourValidationException('available_slots', data['available_slots'], "Количество мест не может быть отрицательным")
            
            tour.destination_id = data.get('destination_id', tour.destination_id)
            tour.start_date = data.get('start_date', tour.start_date)
            tour.end_date = data.get('end_date', tour.end_date)
            tour.available_slots = data.get('available_slots', tour.available_slots)
            tour.is_active = data.get('is_active', tour.is_active)
            
            db.session.commit()
            tour_logger.info(f"Тур обновлен: ID {tour.id}")
            
            return tour.to_dict()
            
        except TourNotFoundException as e:
            tour_logger.warning(f"Тур с ID {id} не найден для обновления")
            return self.handle_exception(e, "Tour not found")
        except (TourValidationException, TourDateException, DestinationNotFoundException) as e:
            db.session.rollback()
            tour_logger.warning(f"Ошибка валидации при обновлении тура {id}: {str(e)}")
            return self.handle_exception(e, "Tour validation failed")
        except Exception as e:
            db.session.rollback()
            tour_logger.error(f"Неожиданная ошибка при обновлении тура {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to update tour")
    
    def delete(self, id):
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
            return self.handle_exception(e, "Tour not found")
        except TourValidationException as e:
            db.session.rollback()
            tour_logger.warning(f"Ошибка валидации при удалении тура {id}: {str(e)}")
            return self.handle_exception(e, "Cannot delete tour")
        except Exception as e:
            db.session.rollback()
            tour_logger.error(f"Неожиданная ошибка при удалении тура {id}: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to delete tour")

class AvailableToursResource(BaseResource):
    def get(self):
        try:
            api_logger.info("GET /api/tours/available - получение доступных туров")
            available_tours = TourService.get_available_tours()
            tour_logger.info(f"Найдено доступных туров: {len(available_tours)}")
            return [tour.to_dict() for tour in available_tours]
        except Exception as e:
            tour_logger.error(f"Ошибка при получении доступных туров: {str(e)}", exc_info=True)
            return self.handle_exception(e, "Failed to fetch available tours")