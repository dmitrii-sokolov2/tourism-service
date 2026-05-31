# Главное приложение
from app import app

# Модели базы данных
from models.models import User, Destination, Tour
from core.extensions import db

# API ресурсы
from api.v1.routes.user_routes import (
    UserListResource, UserResource, UserBulkDeleteResource, UserBookTourResource
)
from api.v1.routes.destination_routes import (
    DestinationListResource, DestinationResource
)
from api.v1.routes.tour_routes import (
    TourListResource, TourResource, AvailableToursResource
)

# Сервисы бизнес-логики
from services.tourism_services import (
    UserService, TourService, DestinationService, BookingService
)

# Исключения из папки exceptions
from exceptions.custom_exceptions import (
    TourismBaseException,
    UserNotFoundException, UserEmailDuplicateException, UserValidationException,
    DestinationNotFoundException, DestinationNameDuplicateException, DestinationValidationException,
    TourNotFoundException, TourValidationException, TourDateException,
    NoAvailableSlotsException, TourNotActiveException, DuplicateBookingException, BookingLimitException
)

# Валидаторы из папки validators
from validators.user_validator import UserValidator
from validators.tour_validator import TourValidator
from validators.destination_validator import DestinationValidator

# ProblemDetails из папки transfer
try:
    from transfer.problem_details import ProblemDetails
except ImportError:
    # Альтернативный способ импорта
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'transfer'))
    from transfer.problem_details import ProblemDetails

__all__ = [
    # Приложение и БД
    'app', 'db',
    
    # Модели
    'User', 'Destination', 'Tour',
    
    # Ресурсы API
    'UserListResource', 'UserResource', 'UserBulkDeleteResource', 'UserBookTourResource',
    'DestinationListResource', 'DestinationResource',
    'TourListResource', 'TourResource', 'AvailableToursResource',
    
    # Сервисы
    'UserService', 'TourService', 'DestinationService', 'BookingService',
    
    # Формат ошибок
    'ProblemDetails',
    
    # Исключения
    'TourismBaseException',
    'UserNotFoundException', 'UserEmailDuplicateException', 'UserValidationException',
    'DestinationNotFoundException', 'DestinationNameDuplicateException', 'DestinationValidationException',
    'TourNotFoundException', 'TourValidationException', 'TourDateException',
    'NoAvailableSlotsException', 'TourNotActiveException', 'DuplicateBookingException', 'BookingLimitException',
    
    # Валидаторы
    'UserValidator', 'TourValidator', 'DestinationValidator'
]

# Добавить в __all__
'ThreadSafeBookingService'